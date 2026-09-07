#!/usr/bin/env python3
"""Offline safety checks for the isolated migration CLI (no native host required)."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import smoke_workbuddy_migration as probe


class MigrationSafetyTests(unittest.TestCase):
    def invoke(self, config, url='https://plugin.springbrand.ai/releases/test/workbuddy/package.zip'):
        with patch.object(sys, 'argv', ['probe', '--config', str(config), '--manifest', '/absent', '--url', url]):
            probe.main()

    def test_existing_directory_is_not_modified(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            (target / 'keep').write_text('untouched')
            with self.assertRaisesRegex(ValueError, 'new isolated directory'):
                self.invoke(target)
            self.assertEqual([p.name for p in target.iterdir()], ['keep'])
            self.assertEqual((target / 'keep').read_text(), 'untouched')

    def test_real_config_descendants_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(Path, 'home', return_value=Path(temp)):
            target = Path(temp) / '.workbuddy-ai/new-probe'
            with self.assertRaisesRegex(ValueError, 'new isolated directory'):
                self.invoke(target)
            self.assertFalse(target.exists())

    def test_invalid_destination_rejected_before_config_creation(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'new'
            for url in ('http://plugin.springbrand.ai/releases/x.zip',
                        'https://github.com/example/package.zip',
                        'https://plugin.springbrand.ai/channels/production/workbuddy.zip'):
                with self.assertRaisesRegex(ValueError, 'immutable official R2'):
                    self.invoke(target, url)
            self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
