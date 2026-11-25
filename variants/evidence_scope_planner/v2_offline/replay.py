"""Compare saved aligner outputs with both planners; offline, no model calls."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
V1 = HERE.parent / 'v1_offline'
CASES = ('promotion', 'susan', 'transition', 'career_history', 'skydiving')
RUNS = {'v1': 'fixed_five_20261120', 'v2': 'v2_paired_20261120', 'v3': 'v3_paired_20261120'}


def module(directory, name, label):
    spec = importlib.util.spec_from_file_location(label, directory / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2)


def original_source_matches(source, memory=False):
    """Check actual on-disk source object rather than trusting copied source text."""
    ref = source.get('source_ref', '').split(' [', 1)[0]
    file, marker, pointer = ref.partition('#')
    try:
        obj = json.loads((PROJECT / file).read_text(encoding='utf-8'))
        if memory:
            matches = [x for x in obj['api_snapshot']['results'] if x.get('id') == source.get('source_id')]
            return len(matches) == 1 and matches[0].get('memory') == source.get('text')
        if not marker:
            return False
        for segment in pointer.strip('/').split('/'):
            segment = segment.replace('~1', '/').replace('~0', '~')
            obj = obj[int(segment)] if isinstance(obj, list) else obj[segment]
        return isinstance(obj, str) and obj.count(source.get('text', '')) == 1 and bool(source.get('text'))
    except (OSError, KeyError, IndexError, ValueError, TypeError):
        return False


def quote_audit(artifact, projection):
    payload = artifact['input']
    memory = payload['source_texts']['memory']
    sources = {s['source_id']: s for s in [memory, *payload['source_texts'].get('messages', [])]}
    old_units = {u['unit_id']: u for u in payload['old_units']}
    new_units = {u['unit_id']: u for u in payload['new_units']}
    records = (artifact['result'].get('parsed') or {}).get('records') or []
    audits=[]
    for idx, record in enumerate(records):
        raw = next((x for x in projection if x.get('raw_record') == record), {})
        for side in ('old', 'new'):
            ids = record.get(side + '_unit_ids') or []
            units = old_units if side == 'old' else new_units
            for qidx, q in enumerate(record.get(side + '_quotes') or []):
                quote = q.get('quote') if isinstance(q,dict) else q
                explicit = q.get('source_id') if isinstance(q,dict) else None
                if explicit:
                    candidates = [explicit] if explicit in sources else []
                else:
                    possible = {units[u].get('source_id') or (memory['source_id'] if side == 'old' else None)
                                for u in ids if u in units}
                    candidates = [sid for sid in possible if sid in sources and isinstance(quote,str)
                                  and sources[sid].get('text','').count(quote) == 1]
                sid = candidates[0] if len(candidates)==1 else None
                source = sources.get(sid, {})
                count = source.get('text','').count(quote) if isinstance(quote,str) and quote else 0
                side_ok = bool(source) and (sid == memory['source_id'] or source.get('side') == 'old') if side == 'old' else bool(source) and source.get('side') == 'new' and source.get('speaker') == 'user'
                verified_ref = original_source_matches(source, memory=(sid == memory['source_id'])) if sid else False
                # This is source resolution, not a semantic conclusion.
                resolved = raw.get('resolved_' + side + '_quotes') or []
                retained_text = any(x.get('quote') == quote for x in resolved if isinstance(x, dict))
                projected = any(x.get('quote') == quote and x.get('source_id') == sid and sid for x in resolved if isinstance(x,dict))
                scalar = bool(quote and raw.get(side + '_quote') == quote)
                scalar_id = raw.get('old_quote_source_id') if side == 'old' else raw.get('source_id')
                scalar_valid = bool(scalar and sid and scalar_id == sid and side_ok and count == 1 and verified_ref)
                audits.append({'record_index':idx,'side':side,'quote_index':qidx,'quote':quote,
                               'explicit_source_id':explicit,'candidate_source_ids':sorted(candidates),
                               'source_id':sid,'source_ref':source.get('source_ref'),
                               'source_side_ok':side_ok,'unique_in_source':count==1,
                               'source_matches_disk':verified_ref, 'retained_text_in_resolved_list':retained_text,
                               'resolved_in_projection_list':bool(projected), 'retained_as_scalar':scalar, 'scalar_source_valid':scalar_valid})
    return audits


def audit_counts(audits):
    return {'raw_quotes':len(audits), 'source_resolved':sum(bool(x['source_id']) for x in audits),
            'unique_correct_side_on_disk':sum(bool(x['source_id'] and x['source_side_ok'] and x['unique_in_source'] and x['source_matches_disk']) for x in audits),
            'list_text_retained':sum(x['retained_text_in_resolved_list'] for x in audits),
            'list_resolved_with_source':sum(x['resolved_in_projection_list'] for x in audits),
            'scalar_projection':sum(x['retained_as_scalar'] for x in audits),
            'scalar_source_valid':sum(x['scalar_source_valid'] for x in audits),
            'source_unresolved_in_list':sum(not x['resolved_in_projection_list'] for x in audits)}


def load_units(data):
    return [{**u, 'memory_id':data['memory_id'], 'source_ref':data['old_memory_source_ref']} for u in data['units']]


def main():
    HERE.joinpath('results').mkdir(exist_ok=True)
    engines={v:(module(path,'adapter',v+'_adapter'),module(path,'scope_planner',v+'_planner'))
             for v,path in [('planner_v1',V1),('planner_v2',HERE)]}
    for case in CASES:
        data=json.loads((HERE/'fixtures'/f'{case}.json').read_text(encoding='utf-8'))
        result={'case_id':case,'human_alignment':{},'models':{}}
        for engine,(_,planner) in engines.items():
            human_data = (json.loads((V1/'fixtures'/f'{case}.json').read_text(encoding='utf-8'))
                          if engine == 'planner_v1' else data)
            result['human_alignment'][engine]=planner.build_scope_plan(human_data['old_memory'],load_units(human_data),human_data['sources'],human_data['alignments'])
        for version,run in RUNS.items():
            path=PROJECT/'variants/evidence_aligner/runs'/run/(case+'.json')
            artifact=json.loads(path.read_text(encoding='utf-8'))
            records=(artifact['result'].get('parsed') or {}).get('records') or []
            model={'artifact':str(path.relative_to(PROJECT)),'upstream_status':artifact['result'].get('status'),
                   'raw_record_count':len(records),'engines':{}}
            for engine,(adapter,planner) in engines.items():
                args=adapter.load_aligner_case(path)
                plan=planner.build_scope_plan(*args)
                audit=quote_audit(artifact,args[3])
                model['engines'][engine]={'projection':args[3],'plan':plan,'quote_audit':audit,'counts':audit_counts(audit),
                    'projected_record_count':sum(1 for record in records if any(x.get('raw_record') == record for x in args[3]))}
            result['models'][version]=model
        (HERE/'results'/f'{case}.json').write_text(dump(result)+'\n',encoding='utf-8')
        print(case,'completed')


    # Synthetic check: the evidence explicitly orders the policy change.
    old = '上海、南京两家门店的堂食、外带均实行旧政策。'
    new = '此前均实行旧政策，现上海门店的外带改用新政策。'
    units = [{'id':'policy','quote':old,'fact':'两家门店两种服务的旧政策',
              'memory_id':'synthetic-memory','source_ref':'synthetic:old'}]
    sources = [{'source_id':'synthetic-new','text':new,'source_ref':'synthetic:new',
                'speaker':'user','side':'new'}]
    evidence = [{'source_id':'synthetic-new','quote':new,'side':'new'}]
    alignment = [{'unit_id':'policy','relation':'change','old_subject':'门店',
                  'new_subject':'门店','old_attribute':'政策','new_attribute':'政策',
                  'old_value':'旧政策','new_value':'新政策','old_quote':old,
                  'new_quote':new,'source_id':'synthetic-new','modality':'asserted',
                  'semantic_support':'supported','semantic_basis':evidence,
                  'temporal_order':{'relation':'after','basis':evidence,'explanation':'新句明确此前实行旧政策、现改为新政策。'},
                  'old_conditions':{'kind':'finite','dimensions':{'门店':['上海','南京'],'服务':['堂食','外带']}},
                  'new_conditions':{'kind':'finite','dimensions':{'门店':['上海'],'服务':['外带']}}}]
    demo=engines['planner_v2'][1].build_scope_plan(old,units,sources,alignment)
    assert len(demo['modify'])==1 and len(demo['preserve'])==3, demo
    (HERE/'results'/'multidimensional.json').write_text(dump(demo)+'\n',encoding='utf-8')
    print('multidimensional: 1 modify, 3 preserve')

if __name__=='__main__':main()
