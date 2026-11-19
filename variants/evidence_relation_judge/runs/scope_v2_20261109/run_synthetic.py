"""Run manually constructed interface fixtures; no model calls or writes."""
from copy import deepcopy
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent
COMP=HERE.parent.parent
sys.path.insert(0,str(COMP/'part2_scope_judge'))
from test_scope_planner import correction_sample, sample
from scope_planner import plan_scope

cases=[]
def record(name,req,rel,expected):
    output=plan_scope(req,rel)
    row=output['results'][0]
    actual={'modifications':len(row['modifications']),'additions':len(output['additions']),
            'pending':[x['code'] for x in row['pending']],
            'interval_relation':row['time']['interval_relation'],
            'facttrack':row['facttrack']}
    cases.append({'id':name,'input_origin':('saved promotion v4/v2 with hand-added synthetic periods' if name.startswith('sourced_interval_') else 'hand-authored synthetic v4/v2-shaped fixture; no model output'),
                  'human_expected':expected,'actual':actual,'complete_output':output})

req,rel=correction_sample()
record('explicit_correction',req,rel,{'modifications':1,'old':'blue','new':'green','protected':'I enjoy hiking','valid_end':'unknown'})
req,rel=correction_sample(evidence='My favorite color is green now.')
record('unanchored_change',req,rel,{'modifications':0,'reason':'no explicit correction or established boundary'})
req,rel=correction_sample(); req['new_evidence'].append({'source_id':'new-2','speaker':'user','text':'Correction: my favorite color is red, not blue.'})
record('conflicting_corrections',req,rel,{'modifications':0,'pending':'conflicting_corrections'})
req,rel=correction_sample(memory='My favorite color is blue; My favorite color is blue.')
record('ambiguous_old',req,rel,{'modifications':0,'reason':'old assertion occurs twice'})
req,rel=correction_sample(); req['new_evidence'].append({'source_id':'new-2','speaker':'user','text':req['new_evidence'][0]['text']})
record('duplicate_evidence',req,rel,{'modifications':1,'additions':1,'source_ids':['new-1','new-2']})
req,rel=sample()
req['source_context'][0]['text']+=' Old period 2024-01-01 through 2024-08-01.'
req['new_evidence'][0]['text']+=' New period 2024-05-01 through 2024-12-01.'
req['time_info']=[{'side':'old','kind':'valid_period','start':'2024-01-01','end':'2024-08-01','source_id':'old-context-1','quote':'Old period 2024-01-01 through 2024-08-01.'},
                  {'side':'new','kind':'valid_period','start':'2024-05-01','end':'2024-12-01','source_id':'dialogue-0','quote':'New period 2024-05-01 through 2024-12-01.'}]
record('sourced_interval_overlap',req,rel,{'modifications':0,'interval_relation':'overlap','facttrack_path':'original_overlap_true','note':'validity interpretation remains unverified'})
req,rel=sample()
req['source_context'][0]['text']+=' Old period 2024-01-01 through 2024-12-31.'
req['new_evidence'][0]['text']+=' New period 2025-01-01 through 2025-12-31.'
req['time_info']=[{'side':'old','kind':'valid_period','start':'2024-01-01','end':'2024-12-31','source_id':'old-context-1','quote':'Old period 2024-01-01 through 2024-12-31.'},
                  {'side':'new','kind':'valid_period','start':'2025-01-01','end':'2025-12-31','source_id':'dialogue-0','quote':'New period 2025-01-01 through 2025-12-31.'}]
record('sourced_interval_sequential',req,rel,{'modifications':0,'interval_relation':'before','boundary':'window_candidate','facttrack_order':'block_check_pre_order','note':'window conditional on comparable, mutually exclusive states'})
with (HERE/'synthetic_for_report.json').open('x',encoding='utf8') as f:json.dump(cases,f,ensure_ascii=False,indent=2);f.write('\n')
for case in cases:
 a=case['actual'];print(case['id'],'modifications',a['modifications'],'additions',a['additions'],'interval',a['interval_relation'])
