import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_file_priority import choose_file_settings

class FilePriorityTests(unittest.TestCase):
    def test_file_values_win_over_process_values(self):
        with patch.dict('os.environ', {'DASHSCOPE_API_KEY':'environment-value', 'DASHSCOPE_WORKSPACE_ID':'ws-environment'}):
            result = choose_file_settings({'DASHSCOPE_API_KEY':'file-value','DASHSCOPE_WORKSPACE_ID':'ws-file'})
        self.assertEqual(result, ('file-value', 'ws-file'))

    def test_missing_file_key_does_not_fall_back_to_environment(self):
        with patch.dict('os.environ', {'DASHSCOPE_API_KEY':'environment-value'}):
            result = choose_file_settings({'DASHSCOPE_WORKSPACE_ID':'ws-file'})
        self.assertEqual(result, (None, 'ws-file'))

if __name__ == '__main__': unittest.main()
