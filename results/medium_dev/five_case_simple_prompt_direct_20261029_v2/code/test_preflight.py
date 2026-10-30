import json
import tempfile
import unittest
from pathlib import Path
import runner

class PreflightTests(unittest.TestCase):
    def test_copy_rejects_tampered_backup(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); src=root/'backup'; src.mkdir(); (src/'history.db').write_bytes(b'changed')
            (src/'ready.json').write_text(json.dumps({'files_sha256':{'history.db':'0'*64}}))
            with self.assertRaisesRegex(ValueError, 'hash'):
                runner.copy_backup(src,root/'case')
            self.assertFalse((root/'case'/'history.db').exists())

    def test_prompt_must_equal_frozen_base_plus_addendum(self):
        runner.validate_prompt('base\n\nextra\n','base','extra\n')
        with self.assertRaises(ValueError):
            runner.validate_prompt('different','base','extra\n')

if __name__ == '__main__': unittest.main()
