import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from splitter import build_extraction_prompt
from prompt_v2 import build_extraction_prompt_v2

class PromptV2Tests(unittest.TestCase):
    def test_v2_preserves_original_prompt_and_includes_inputs(self):
        args = {'memory_id':'m', 'memory_text':'Speaker likes tea.', 'source_context':None}
        result=build_extraction_prompt_v2(**args)
        self.assertTrue(result.startswith(build_extraction_prompt(**args)))
        self.assertIn('Speaker likes tea.', result)
    def test_v2_explicitly_addresses_quote_attribution_and_causation(self):
        result=build_extraction_prompt_v2('m','A sentence.',None).lower()
        for text in ('verbatim', 'attribution', 'cause', 'condition', 'unresolved', 'duplicate', 'valid_time'):
            self.assertIn(text,result)

if __name__ == '__main__': unittest.main()
