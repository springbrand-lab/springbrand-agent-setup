#!/usr/bin/env python3
"""Release packaging and safe publication regression tests (no network)."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_release_package as builder
import publish_release_package as publisher


class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tag = 'v' + (builder.ROOT / 'VERSION').read_text().strip()
        cls.files = {p.relative_to(builder.ROOT).as_posix(): (p.read_bytes(), p.stat().st_mode)
                     for base in ['skills', 'hooks', 'plugins/springbrand-workbuddy', '.codebuddy-plugin']
                     for p in (builder.ROOT / base).rglob('*') if p.is_file()}
        cls.files['VERSION'] = ((builder.ROOT / 'VERSION').read_bytes(), 0o644)

    def test_production_tag_only(self):
        for tag in ('main', '../x', 'v1.2.0-beta.10-dev.1', 'v1.2.0-dev.1', 'v1.2.0;pwd'):
            with self.assertRaises(ValueError): builder.validate_tag(tag)
        for tag in ('v1.2.0', 'v1.2.0-beta.10'): builder.validate_tag(tag)

    def test_reproducible_complete_archive(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(builder, 'release_files', return_value=('a'*40, self.files)):
            a, b = Path(temp)/'a', Path(temp)/'b'
            manifest = builder.build(self.tag, a)
            builder.build(self.tag, b)
            self.assertEqual((a/'springbrand-workbuddy.zip').read_bytes(), (b/'springbrand-workbuddy.zip').read_bytes())
            with zipfile.ZipFile(a/'springbrand-workbuddy.zip') as archive:
                self.assertEqual(len(archive.namelist()), len(manifest['files']))
                self.assertTrue(archive.getinfo('springbrand/plugins/springbrand-workbuddy/hooks/user-prompt-submit').external_attr >> 16 & 0o111)
                for name, (data, _) in builder.package_files(self.files, self.tag).items():
                    self.assertEqual(archive.read('springbrand/'+name), data)

    def changed(self, name, change):
        files = copy.deepcopy(self.files)
        data, mode = files[name]
        files[name] = (change(data), mode)
        return files

    def test_tag_version_mismatch(self):
        with self.assertRaises(ValueError): builder.package_files(self.files, 'v0.0.1')

    def test_no_remote_plugin_source(self):
        files = self.changed('.codebuddy-plugin/marketplace.json', lambda d: d.replace(b'./plugins/springbrand-workbuddy', b'https://github.com/example/plugin'))
        with self.assertRaises(ValueError): builder.package_files(files, self.tag)

    def test_no_dev_endpoint_or_extra_auth(self):
        name = 'plugins/springbrand-workbuddy/.mcp.json'
        files = self.changed(name, lambda d: d.replace(b'connector.springbrand', b'devconnector.springbrand'))
        with self.assertRaises(ValueError): builder.package_files(files, self.tag)
        obj = json.loads(self.files[name][0]); obj['mcpServers']['springbrand']['headers'] = {'Authorization': 'not-a-real-token'}
        files = self.changed(name, lambda _: json.dumps(obj).encode())
        with self.assertRaises(ValueError): builder.package_files(files, self.tag)

    def test_mirror_drift_and_missing_reference_rejected(self):
        name = 'plugins/springbrand-workbuddy/skills/springbrand-platform/references/plugin-discovery.md'
        files = self.changed(name, lambda d: d+b'\nDrift')
        with self.assertRaises(ValueError): builder.package_files(files, self.tag)
        files = copy.deepcopy(self.files); del files[name]
        with self.assertRaises(ValueError): builder.package_files(files, self.tag)

    def test_hook_must_be_executable(self):
        files = copy.deepcopy(self.files); name = 'plugins/springbrand-workbuddy/hooks/user-prompt-submit'
        files[name] = (files[name][0], 0o644)
        with self.assertRaises(ValueError): builder.package_files(files, self.tag)

    def test_immutable_collision_and_idempotency(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'file'; path.write_bytes(b'release')
            with patch.object(publisher, 'read_object', return_value=b'other'), patch.object(publisher, 'aws') as aws:
                with self.assertRaises(ValueError): publisher.put(path, 'releases/test')
                aws.assert_not_called()
            with patch.object(publisher, 'read_object', return_value=b'release'), patch.object(publisher, 'aws') as aws:
                publisher.put(path, 'releases/test'); aws.assert_not_called()
            with patch.object(publisher, 'read_object', return_value=None), patch.object(publisher, 'aws') as aws:
                publisher.put(path, 'releases/test')
                self.assertIn('--if-none-match', aws.call_args.args)

    def test_failed_verification_never_promotes(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(builder, 'release_files', return_value=('a'*40, self.files)):
            out=Path(temp)/'release'; builder.build(self.tag, out)
            with patch.dict('os.environ', {'AWS_ACCESS_KEY_ID':'test','AWS_SECRET_ACCESS_KEY':'test', 'GITHUB_ACTIONS':'true', 'GITHUB_REF':'refs/heads/main','WORKBUDDY_R2_PRODUCTION_ENABLED':'true'}), patch.object(publisher, 'put') as put, patch.object(publisher, 'verify', side_effect=ValueError('bad download')):
                with self.assertRaises(ValueError): publisher.publish(out, self.tag, promote=True)
                self.assertEqual(put.call_count, 1)
                self.assertTrue(put.call_args.args[1].startswith('releases/'))

    def test_production_gate_fails_before_any_io(self):
        with patch.dict('os.environ', {}, clear=True), patch.object(publisher, 'put') as put:
            with self.assertRaisesRegex(ValueError, 'gated Actions'): publisher.publish(Path('/absent'), self.tag, promote=True)
            put.assert_not_called()


if __name__ == '__main__': unittest.main()
