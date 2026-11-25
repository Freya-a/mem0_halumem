#!/usr/bin/env python3
"""Supplement invalid HaluMem scores with the unchanged official scoring functions."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import copy
import csv
import fcntl
import json
import os
from pathlib import Path
import sqlite3
import sys
import time

import medium_full as base
from medium_full_evaluation import metric_rows

ROOT = base.ROOT
EVAL = ROOT / 'results/medium_full/medium_qwen_005/halumem_evaluation'
SOURCE = EVAL / 'results/memzero-full/memzero_eval_stat_result.json'
INPUT = EVAL / 'results/memzero-full/memzero_eval_results.jsonl'
OUT = EVAL / 'supplement_20261123_v1'
SECTIONS = ('memory_integrity_records','memory_accuracy_records','memory_update_records','question_answering_records')


def require(test, message):
    if not test: raise ValueError(message)


def invalid_jobs(baseline):
    return [(section,i) for section in SECTIONS for i,row in enumerate(baseline[section]) if row.get('is_valid') is False]


def case_args(section, record, session):
    if section == 'memory_integrity_records':
        require(any(x['memory_content']==record['memory_content'] for x in session['memory_points']), 'Integrity input mismatch')
        return ('\n'.join(session['extracted_memories']),record['memory_content'])
    if section == 'memory_accuracy_records':
        require(record['memory_content'] in session['extracted_memories'], 'Accuracy input mismatch')
        dialogue=[]
        for turn in session['dialogue']:
            dialogue.append(f"[{turn['timestamp']}]{turn['role']}: {turn['content']}")
            if turn['role']=='assistant':dialogue.append('')
        gold='\n'.join(m['memory_content'] for m in session['memory_points'] if m['memory_source']!='interference')
        return ('\n'.join(dialogue),gold,record['memory_content'])
    if section == 'memory_update_records':
        require(any(x.get('index')==record.get('index') and x['memory_content']==record['memory_content']
                    and x.get('memories_from_system')==record.get('memories_from_system') for x in session['memory_points']), 'Update input mismatch')
        return ('\n'.join(record['memories_from_system']),record['memory_content'],'\n'.join(record['original_memories']))
    if section == 'question_answering_records':
        require(any(x['question']==record['question'] and x.get('system_response')==record.get('system_response')
                    and x.get('evidence')==record.get('evidence') for x in session.get('questions',[])), 'QA input mismatch')
        return (record['question'],record['answer'],'\n'.join(x['memory_content'] for x in record['evidence']),record['system_response'])
    raise ValueError('Unknown scoring section')


def normalize(section, parsed):
    require(isinstance(parsed,dict),'Scorer did not return an object')
    if section=='memory_integrity_records':return {'memory_integrity_score':int(parsed['score'])}
    if section=='memory_accuracy_records':return {'memory_accuracy_score':int(parsed['accuracy_score']),
        'is_included_in_golden_memories':parsed.get('is_included_in_golden_memories','false')}
    if section=='memory_update_records':
        label=parsed.get('evaluation_result');require(label in ('Correct','Hallucination','Omission','Other'),'Invalid update label')
        return {'memory_update_type':label}
    if section=='question_answering_records':
        label=parsed.get('evaluation_result');require(label in ('Correct','Hallucination','Omission'),'Invalid QA label')
        return {'result_type':label}
    raise ValueError('Unknown scoring section')


def merge_scores(original, rows):
    result=copy.deepcopy(original)
    for section,index,encoded in rows:
        require(original[section][index].get('is_valid') is False, 'Refusing to replace an originally valid score')
        result[section][index].update(json.loads(encoded))
    return result


def inputs():
    manifest=base.read_json(EVAL/'input_manifest.json'); status=base.read_json(EVAL/'scoring_status.json')
    require(base.digest(INPUT)==manifest['input_sha256'],'Original scorer input changed')
    require(base.digest(SOURCE)==status['official_result_sha256'],'Original scorer result changed')
    for name,sha in manifest['official_source_sha256'].items():
        require(base.digest(ROOT/'HaluMem/eval'/name)==sha,f'Official scoring file changed: {name}')
    baseline=base.read_json(SOURCE)
    with INPUT.open(encoding='utf-8') as f: users={u['uuid']:u for line in f if (u:=json.loads(line))}
    return baseline,users,manifest


def setup():
    baseline,users,manifest=inputs()
    jobs=invalid_jobs(baseline)
    require(jobs, 'There are no invalid records to supplement')
    for section,i in jobs:
        rec=baseline[section][i]
        case_args(section,rec,users[rec['uuid']]['sessions'][rec['ssession_id']])
    OUT.mkdir(mode=0o700,parents=False,exist_ok=False)
    db=sqlite3.connect(OUT/'progress.sqlite3')
    db.execute('CREATE TABLE jobs (section TEXT NOT NULL, idx INTEGER NOT NULL, status TEXT NOT NULL, result TEXT, error_type TEXT, PRIMARY KEY(section,idx))')
    db.executemany('INSERT INTO jobs(section,idx,status) VALUES (?,?,?)',[(s,i,'pending') for s,i in jobs]);db.commit();db.close()
    base.atomic_json(OUT/'manifest.json',{'input_sha256':base.digest(INPUT),'baseline_score_sha256':base.digest(SOURCE),
        'official_source_sha256':manifest['official_source_sha256'],'model':'qwen-plus-2025-12-01',
        'jobs':len(jobs),'originally_valid_preserved':True})
    print(f'Prepared {len(jobs)} invalid scores; no API requests.',flush=True)


def summarize(db):
    return dict(db.execute('SELECT status,count(*) FROM jobs GROUP BY status').fetchall())


def run():
    baseline,users,manifest=inputs();meta=base.read_json(OUT/'manifest.json')
    require(meta['input_sha256']==base.digest(INPUT) and meta['baseline_score_sha256']==base.digest(SOURCE),'Supplement input changed')
    require(meta['official_source_sha256']==manifest['official_source_sha256'],'Official source changed')
    settings=base.load_environment(ROOT/'.env.server.medium-full');base.configure_qa(settings)
    require(os.environ['OPENAI_MODEL']==meta['model'],'Judging model changed')
    previous=base.read_json(EVAL/'score_config.json')['judge']
    require(all(os.environ.get(k)==v for k,v in previous.items()), 'Judging configuration differs from original scoring')
    sys.path.insert(0,str(ROOT/'HaluMem/eval'))
    import eval_tools
    fns={'memory_integrity_records':eval_tools.evaluation_for_memory_integrity,
         'memory_accuracy_records':eval_tools.evaluation_for_memory_accuracy,
         'memory_update_records':eval_tools.evaluation_for_update_memory,
         'question_answering_records':eval_tools.evaluation_for_question}
    db=sqlite3.connect(OUT/'progress.sqlite3');db.execute('PRAGMA journal_mode=WAL')
    require(not db.execute("SELECT 1 FROM jobs WHERE status='started' LIMIT 1").fetchone(),
            'Interrupted in-flight jobs require inspection before retry')
    def invoke(section,index):
        rec=baseline[section][index];session=users[rec['uuid']]['sessions'][rec['ssession_id']]
        try:return normalize(section,fns[section](*case_args(section,rec,session))),None
        except Exception as exc:return None,{'type':type(exc).__name__,'status_code':getattr(exc,'status_code',None)}
    def submit(pool,section,index):
        db.execute("UPDATE jobs SET status='started' WHERE section=? AND idx=? AND status='pending'",(section,index));db.commit()
        return pool.submit(invoke,section,index)
    def finish(job,result):
        section,index=job;value,error=result
        db.execute('UPDATE jobs SET status=?,result=?,error_type=? WHERE section=? AND idx=?',
                   ('valid' if error is None else 'failed',json.dumps(value,ensure_ascii=False) if value is not None else None,
                    json.dumps(error) if error else None,section,index));db.commit()
        return error
    first=db.execute("SELECT section,idx FROM jobs WHERE status='pending' ORDER BY rowid LIMIT 1").fetchone()
    if first:
        # This is a real pending scoring item, not an extra paid test request.
        with ThreadPoolExecutor(max_workers=1) as pool:
            error=finish(first,submit(pool,*first).result())
        print('First pending item:', 'valid' if error is None else error['type'],flush=True)
        if error is not None:
            db.close();raise RuntimeError('First scoring item failed; stopped before bulk requests')
    pending=iter(db.execute("SELECT section,idx FROM jobs WHERE status='pending' ORDER BY rowid").fetchall())
    paused=False;done=0
    with ThreadPoolExecutor(max_workers=10) as pool:
        tasks={}
        def fill():
            while len(tasks)<10 and not paused:
                try:job=next(pending)
                except StopIteration:break
                tasks[submit(pool,*job)]=job
        fill()
        while tasks:
            finished,_=wait(tasks,return_when=FIRST_COMPLETED)
            for future in finished:
                job=tasks.pop(future);error=finish(job,future.result());done+=1
                if error and error.get('status_code') in (401,402,403):paused=True
            if done%100<10:print('Progress:',summarize(db),flush=True)
            fill()
    counts=summarize(db)
    print('Scoring checkpoint:',counts,flush=True)
    if counts.get('pending',0) or counts.get('started',0) or counts.get('failed',0):
        db.close();raise RuntimeError('Supplement incomplete; inspect checkpoint before retrying failed items')
    merged=merge_scores(baseline,db.execute("SELECT section,idx,result FROM jobs WHERE status='valid'").fetchall());db.close()
    for x in merged['overall_score']['memory_type_accuracy'].values():
        x.update(memory_integrity_acc=0,memory_update_acc=0,total_num=0,memory_acc=0)
    import evaluation
    evaluation.aggregate_eval_results(merged)
    output=OUT/'memzero_eval_stat_result.json';base.atomic_json(output,merged)
    with (OUT/'metrics.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['stage','metric','all','valid']);w.writeheader();w.writerows(metric_rows(merged['overall_score']))
    base.atomic_json(OUT/'status.json',{'status':'completed','result_sha256':base.digest(output),'supplemented':counts.get('valid',0)})
    print('Supplement completed:',OUT,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--prepare',action='store_true');g.add_argument('--run',action='store_true')
    args=p.parse_args()
    try:
        if args.prepare:
            setup()
        else:
            with (OUT/'.lock').open('a') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                run()
    except Exception as exc:
        print('Supplement stopped:',type(exc).__name__,str(exc),file=sys.stderr,flush=True);sys.exit(1)
