#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('publisher', ROOT / 'scripts/publish_install_docs.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


class PublishingTests(unittest.TestCase):
    def test_exact_copies_and_allowlist(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'out'
            manifest = publisher.build(ROOT, output, 'a' * 40)
            self.assertEqual(set(p.name for p in output.iterdir()), {*publisher.FILES, 'manifest.json'})
            self.assertEqual(manifest['source_commit'], 'a' * 40)
            for name in publisher.FILES:
                self.assertEqual((ROOT / name).read_bytes(), (output / name).read_bytes())

    def test_reject_invalid_sources(self):
        for invalid in ('[missing](./INSTALL.dev.md)', 'https://devconnector.springbrand.ai/mcp', 'v1.2.0-dev.1'):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as tmp:
                source = Path(tmp) / 'source'
                source.mkdir()
                for name in publisher.FILES:
                    (source / name).write_text(invalid if name == 'INSTALL.md' else 'production')
                with self.assertRaises(ValueError):
                    publisher.build(source, Path(tmp) / 'out', 'a' * 40)

    def test_refuse_non_main_publish(self):
        with patch.dict('os.environ', {'GITHUB_REF': 'refs/tags/v1.0.0'}, clear=True):
            with self.assertRaises(ValueError):
                publisher.publish(Path('/unused'), 'a' * 40)

    def test_stale_run_never_uploads(self):
        env = {'GITHUB_REF': 'refs/heads/main', 'GITHUB_ACTIONS': 'true', 'AWS_ACCESS_KEY_ID': 'test', 'AWS_SECRET_ACCESS_KEY': 'test'}
        with patch.dict('os.environ', env, clear=True), patch.object(publisher.subprocess, 'check_output', return_value='b' * 40 + '\trefs/heads/main'), patch.object(publisher.subprocess, 'run') as upload:
            with self.assertRaises(ValueError):
                publisher.publish(Path('/unused'), 'a' * 40)
            upload.assert_not_called()

    def test_upload_order_and_no_bucket_deletion(self):
        env = {'GITHUB_REF': 'refs/heads/main', 'GITHUB_ACTIONS': 'true', 'AWS_ACCESS_KEY_ID': 'test', 'AWS_SECRET_ACCESS_KEY': 'test'}
        with patch.dict('os.environ', env, clear=True), patch.object(publisher.subprocess, 'check_output', return_value='a' * 40 + '\trefs/heads/main'), patch.object(publisher.subprocess, 'run') as upload, patch.object(publisher, 'verify') as verify:
            publisher.publish(Path('/docs'), 'a' * 40)
            commands = [call.args[0] for call in upload.call_args_list]
            self.assertEqual(len(commands), 5)
            self.assertTrue(all(command[:3] == ['aws', 's3', 'cp'] for command in commands))
            self.assertEqual(commands[-2][3], '/docs/INSTALL.md')
            self.assertEqual(commands[-1][3], '/docs/manifest.json')
            verify.assert_called_once()

    def test_workflow_publication_guards(self):
        workflow = (ROOT / '.github/workflows/publish-install-docs.yml').read_text()
        for required in ("needs: validate", "github.ref == 'refs/heads/main'",
                         "vars.INSTALL_DOCS_AUTO_PUBLISH == 'true'",
                         "cancel-in-progress: false", "secrets.R2_ACCESS_KEY_ID",
                         "python3 tests/test_release_identity.py"):
            self.assertIn(required, workflow)
        self.assertNotIn('pull_request_target:', workflow)

    def test_public_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'out'
            publisher.build(ROOT, output, 'a' * 40)
            with patch.object(publisher, 'urlopen') as fetch, patch.object(publisher.time, 'sleep'):
                fetch.return_value.__enter__.return_value.read.return_value = b'wrong'
                with self.assertRaises(ValueError):
                    publisher.verify(output)


if __name__ == '__main__':
    unittest.main()
