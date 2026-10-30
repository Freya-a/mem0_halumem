#!/usr/bin/env python3
"""Read-only review packets and deliberately incomplete official-scoring export."""
from __future__ import annotations
from pathlib import Path
import json
import re
import medium_dev_data as data

CATEGORIES = ['旧命题未入库','召回不足','应改未改','越界修改','有效知识损伤','证据不足']


def review_rows(targets, user_out, completed_override=None):
    rows = []
    for t in targets:
        ordinal = t['chronological_session_ordinal_one_based']
        folder = user_out / f'session_{ordinal:03d}'
        completed = (completed_override >= ordinal) if completed_override is not None else ((user_out / 'checkpoint.json').exists() and data.read(user_out / 'checkpoint.json')['completed_ordinal'] >= ordinal)
        before = data.read(folder / 'before.json') if (folder / 'before.json').exists() else None
        after = data.read(folder / 'after.json') if (folder / 'after.json').exists() else None
        ops_path = folder / ('actual_operations.json' if (folder / 'actual_operations.json').exists() else 'actual_operations_partial.json')
        ops = data.read(ops_path) if ops_path.exists() else []
        recalls = data.read(folder / 'recall_candidates.json') if (folder / 'recall_candidates.json').exists() else []
        recalled_ids = sorted({str(p['id']) for e in recalls if e['kind']=='recall_output' for p in e['candidates']})
        # Exact text matches are hints only: paraphrases and composite memories need human review.
        prior = before['database_points_with_vectors'] if before else []
        hints = [str(p['id']) for p in prior if p['payload']['data'].casefold().strip().rstrip('.') == t['old_proposition'].casefold().strip().rstrip('.')]
        mapping = dict(target_id=t['target_id'], session_group_id=t['session_group_id'], related_target_ids=t['related_target_ids'],
                       status='待人工审查' if completed else ('会话未提交' if folder.exists() else '未运行'), target=t,
                       old_proposition_actual_memory_ids=[], old_exact_text_hint_ids=hints,
                       recalled_memory_ids=recalled_ids, actual_operations=ops,
                       actual_operation_sequences=[r['sequence'] for r in ops],
                       correspondence='会话共享候选操作；须人工确认逐命题对应，不能将全部操作归因于每个目标',
                       old_memory_presence='待人工语义核实' if before else '未运行',
                       old_memory_recalled='待人工确认旧命题ID后比对',
                       expected_new_state_satisfied='待人工语义核实' if after else '未运行',
                       allowed_scope_violated='待人工核实', valid_knowledge_damaged='待人工核实',
                       candidate_protections=[dict(**g, actual_memory_ids=[], evaluable='待before快照核实；未入库不可评估',
                                                  preserved_after='待人工核实') for g in t['candidate_protections']],
                       review_category_choices=CATEGORIES, review_categories=[], human_notes='',
                       evidence_paths={name:str((folder/name).relative_to(user_out.parent.parent)) for name in
                                       ['input.json','before.json','after.json','extracted_facts.json','recall_candidates.json',
                                        'update_model_io.json','full_operation_plan.json','execution_results.json','actual_operations.json']})
        rows.append(mapping)
    return rows


def make_review(manifest, run):
    rows=[]
    for uid in manifest['selected_users']:
        rows.extend(review_rows([t for t in manifest['targets'] if t['user_uuid']==uid],run/'users'/uid))
    # Archive each format independently, including CSV-only human edits.
    packet=run/'review_pending.json'
    import shutil
    for prior in [packet,run/'review_pending.csv']:
        if prior.exists():
            archive=run/'review_archive';archive.mkdir(exist_ok=True)
            dest=archive/f'{prior.stem}.{data.digest(prior)}{prior.suffix}'
            if not dest.exists():shutil.copy2(prior,dest)
    data.dump(packet,rows)
    data.write_table(run/'review_pending.csv',rows)
    return rows


def export_user_name(source):
    # Evaluation metadata only. Never pass persona_info into Memory.add.
    if source.get('user_name'):
        return source['user_name']
    match=re.search(r'Name:\s*(.*?); Gender:',source.get('persona_info',''))
    data.require(match is not None,'Official export requires a source-grounded user_name')
    return match.group(1).strip()


def export_official(manifest, users, run):
    """Schema bridge only. Do not silently invent retrieval or QA predictions."""
    records=[]
    for p in manifest['prefixes']:
        uid=p['user_uuid']; source=users[uid][1]; user_out=run/'users'/uid
        cp=data.read(user_out/'checkpoint.json') if (user_out/'checkpoint.json').exists() else {'completed_ordinal':0}
        record={'uuid':uid,'user_name':export_user_name(source), 'sessions':[],
                '_status':'partial_development_export_NOT_READY_FOR_OFFICIAL_SCORING',
                '_qa_status':'not_run_questions_omitted', '_required_next_step':'collect official memory-point retrieval without feeding labels into ingestion; run QA separately if requested'}
        for n,(index,s) in enumerate(data.ordered(source)[:cp['completed_ordinal']],1):
            folder=user_out/f'session_{n:03d}'
            extracted=data.read(folder/'extracted_facts.json')
            facts=[fact for e in extracted for fact in (e.get('parsed') or {}).get('facts',[])]
            # Official adapter records add-return memories; preserve that convention and raw facts separately.
            add=data.read(folder/'add_return.json')['return_value']
            out={k:v for k,v in s.items() if k not in ('questions','persona_info')}
            out.update(extracted_memories=[r['memory'] for r in add['results']],
                       _raw_extracted_facts=facts, _original_session_index_zero_based=index,
                       add_dialogue_duration_ms=data.read(folder/'verification.json')['add_elapsed_seconds']*1000,
                       _update_retrieval_status='not_run_memories_from_system_missing',
                       _snapshot_path=str((folder/'after.json').relative_to(run)))
            record['sessions'].append(out)
        records.append(record)
    dest=run/'export';dest.mkdir(exist_ok=True)
    (dest/'halumem_official_schema_partial.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records))
    data.dump(dest/'export_status.json',dict(official_scoring_ready=False,qa_run=False,scoring_run=False,
        missing=['memory_points[*].memories_from_system via official retrieval protocol','questions[*].context/system_response if QA is requested'],
        warning='此导出仅供后续适配；直接运行官方scorer会跳过更新评分并产生不完整结果。不可报告官方分数。'))
