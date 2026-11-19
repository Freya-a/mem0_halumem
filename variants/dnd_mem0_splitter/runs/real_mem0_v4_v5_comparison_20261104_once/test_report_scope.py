"""Check actual report references without invoking a model or changing artifacts."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent


class ReportScopeTests(unittest.TestCase):
    def test_historical_pair_references_are_explicit_in_review_and_report(self):
        reviews = json.loads((ROOT / 'semantic_reviews.json').read_text())
        historical = [c['versions']['v4'] for c in reviews['cases']]
        ambiguous = re.compile(r'(?<!历史 v3/v4 )两版(?:本)?')
        text = json.dumps(historical, ensure_ascii=False)
        self.assertIsNone(ambiguous.search(text),
                          'Historical pair is ambiguous in the current v4/v5 review')
        self.assertIsNone(ambiguous.search((ROOT / 'COMPARISON_REPORT.md').read_text()))
        self.assertIsNone(ambiguous.search((ROOT / 'fact_review.csv').read_text()))
        self.assertIsNone(ambiguous.search((ROOT / 'supports_review.csv').read_text()))


if __name__ == '__main__':
    unittest.main()
