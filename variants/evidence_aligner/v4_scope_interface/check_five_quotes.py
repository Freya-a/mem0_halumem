"""Read-only reproduction of five unresolved model-v1/v2 quote bindings."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
CASES = [('skydiving', 'fixed_five_20261120', 0),
         ('skydiving', 'fixed_five_20261120', 1),
         ('skydiving', 'fixed_five_20261120', 2),
         ('susan', 'fixed_five_20261120', 0),
         ('susan', 'v2_paired_20261120', 2)]


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    for case, run, index in CASES:
        artifact = read_json(ROOT / 'variants/evidence_aligner/runs' / run / (case + '.json'))
        payload = artifact['input']
        memory = payload['source_texts']['memory']
        record = artifact['result']['parsed']['records'][index]
        item = record['old_quotes'][0]
        source_id, quote = item['source_id'], item['quote']
        if source_id == memory['source_id']:
            source = memory
            before = read_json(ROOT / source['source_ref'])
            rows = [x for x in before['api_snapshot']['results'] if x['id'] == source_id]
            assert len(rows) == 1 and rows[0]['memory'] == memory['text']
            source_text = rows[0]['memory']
        else:
            candidates = [m for m in payload['source_texts']['messages'] if m['source_id'] == source_id]
            assert len(candidates) == 1
            source = candidates[0]
            path, pointer = source['source_ref'].split('#', 1)
            pointer = pointer.split(' [', 1)[0]
            obj = read_json(ROOT / path)
            for part in pointer.strip('/').split('/'):
                obj = obj[int(part)] if isinstance(obj, list) else obj[part]
            source_text = obj
            assert source['text'] in source_text
        assert source_text.count(quote) == 1
        offset = source_text.index(quote)
        units = [u for u in payload['old_units'] if u['unit_id'] in record['old_unit_ids']]
        assert len(units) == len(record['old_unit_ids'])
        linked = []
        for u in units:
            fragments = []
            for uq in u['memory_quotes']:
                assert memory['text'].count(uq) == 1
                start = memory['text'].index(uq)
                fragments.append({'quote': uq, 'memory_span': [start, start + len(uq)],
                                  'model_quote_is_inside_unit': quote in uq})
            linked.append({'unit_id': u['unit_id'], 'fragments': fragments})
        assert not any(f['model_quote_is_inside_unit'] for u in linked for f in u['fragments'])
        print(json.dumps({'case': case, 'saved_run': run, 'record_index': index,
                          'source_id': source_id, 'source_ref': source['source_ref'],
                          'quote': quote, 'unique_source_span': [offset, offset + len(quote)],
                          'linked_old_units': linked}, ensure_ascii=False))


if __name__ == '__main__':
    main()
