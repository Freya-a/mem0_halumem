"""Scan dated text in the already replayed 28 input.json files, not metadata timestamps."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3] / 'results/medium_dev/williams_native_prefix5_20261028_v3/users'
pattern = re.compile(r'\b(?:19|20)\d\d\b|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d', re.I)
files = sorted(ROOT.glob('*/session_*/input.json'))
matches = []
for path in files:
    data = json.loads(path.read_text(encoding='utf-8'))
    for index, message in enumerate(data.get('raw_dialogue', [])):
        if pattern.search(message.get('content', '')):
            matches.append({'file': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'pointer': '/raw_dialogue/' + str(index), 'role': message.get('role'), 'text': message['content']})
output = {'scope': '28 replayed prefix-five session input files; raw_dialogue content only; regex scan, not full development dataset',
          'file_count': len(files), 'matched_message_count': len(matches), 'matches': matches}
with Path(sys.argv[1]).open('x', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2); f.write('\n')
print('files:', len(files), 'dated messages:', len(matches))
