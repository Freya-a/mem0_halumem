#!/usr/bin/env python3
"""Offline, standard-library-only dataset and evidence boundary."""
from __future__ import annotations
import csv
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
DEV = ROOT / 'diagnosis/medium_dev'
DATA = ROOT / 'HaluMem/data/HaluMem-Medium.jsonl'
KNOWN_USER = '2f1f897e-d67f-dbc5-6a7b-b7634a9e294f'
DATE_FORMAT = '%b %d, %Y, %H:%M:%S'
STATUS = '自动初标，待人工核验'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def flag(value):
    return value is True or isinstance(value, str) and value.strip().lower() == 'true'


def ordered(user):
    return sorted(enumerate(user['sessions']), key=lambda x: datetime.strptime(x[1]['start_time'], DATE_FORMAT))


def session_input(user, index, ordinal):
    s = user['sessions'][index]
    d = s['dialogue']
    times = [datetime.strptime(m['timestamp'], DATE_FORMAT) for m in d]
    require(bool(d) and times == sorted(times), f'Empty/unordered dialogue {user["uuid"]}:{index}')
    require(len(d) == 2 * s['dialogue_turn_num'], 'Incomplete dialogue')
    require(times[0] == datetime.strptime(s['start_time'], DATE_FORMAT), 'Start mismatch')
    require(times[-1] == datetime.strptime(s['end_time'], DATE_FORMAT), 'End mismatch')
    require(all(m['role'] in ('user', 'assistant') and isinstance(m['content'], str) for m in d), 'Invalid message')
    return dict(user_uuid=user['uuid'], original_session_index_zero_based=index,
                chronological_session_ordinal_one_based=ordinal, start_time=s['start_time'], end_time=s['end_time'],
                raw_dialogue=d, messages=[dict(role=m['role'], content=m['content']) for m in d])


def load_data(path=DATA):
    import uuid
    users = {}
    with Path(path).open(encoding='utf-8') as f:
        for line, raw in enumerate(f, 1):
            u = json.loads(raw)
            uuid.UUID(u['uuid'])
            require(u['uuid'] not in users, 'Duplicate UUID')
            users[u['uuid']] = (line, u)
            previous_end = None
            for ordinal, (index, s) in enumerate(ordered(u), 1):
                session_input(u, index, ordinal)
                start = datetime.strptime(s['start_time'], DATE_FORMAT)
                previous_end = datetime.strptime(s['end_time'], DATE_FORMAT)
    require(len(users) == 20, 'Expected 20 Medium users')
    return users


def evidence(user, session, message):
    m = user['sessions'][session]['dialogue'][message]
    require(m['role'] == 'user', 'Evidence must be original user speech')
    return dict(session_index_zero_based=session, message_index_zero_based=message,
                json_pointer=f'/sessions/{session}/dialogue/{message}', role=m['role'],
                timestamp=m['timestamp'], quote=m['content'])


def build_artifacts(dataset=DATA):
    users = load_data(dataset)
    picked = [KNOWN_USER] + random.Random(42).sample(sorted(set(users) - {KNOWN_USER}), 2)
    recipes = read(DEV / 'recipes.json')
    targets = []
    for r in recipes['targets']:
        uid, si, pi = r['user_uuid'], r['session_index'], r['point_index']
        require(uid in picked, 'Unexpected recipe user')
        line, user = users[uid]
        order = {i: n for n, (i, _) in enumerate(ordered(user), 1)}
        mp = user['sessions'][si]['memory_points'][pi]
        require(flag(mp['is_update']), 'Recipe is not an annotated update candidate')
        old = [evidence(user, i, m) for i, m in r['old_evidence']]
        new = [evidence(user, si, m) for m in r['new_evidence']]
        require(bool(old) and bool(new) and all(order[e['session_index_zero_based']] < order[si] for e in old), 'Old evidence not earlier')
        guards = [dict(proposition=p, evidence=evidence(user, i, j),
                       runtime_evaluability='待运行前实际记忆核实；不得假定已入库')
                  for p, i, j in recipes['candidate_protections'][uid] + r.get('extra_protections',[])]
        tid = f'{uid}:s{si:03d}:m{pi:03d}'
        targets.append(dict(target_id=tid, user_uuid=uid, dataset_line_one_based=line,
                            original_session_index_zero_based=si, memory_point_index_zero_based=pi,
                            annotation_index=mp.get('index'), chronological_session_ordinal_one_based=order[si],
                            annotation_json_pointer=f'/sessions/{si}/memory_points/{pi}', annotation=mp,
                            category=r['category'], old_proposition=r['old_proposition'], old_dialogue_evidence=old,
                            new_dialogue_evidence=new, expected_new_state=r['expected_new_state'],
                            allowed_modification_scope=r['allowed_modification_scope'], interpretation_note=r['interpretation_note'],
                            candidate_protections=guards, annotation_status=STATUS,
                            session_group_id=f'{uid}:s{si:03d}', related_target_ids=[]))
    for t in targets:
        t['related_target_ids'] = [x['target_id'] for x in targets if x['session_group_id'] == t['session_group_id'] and x != t]
    prefixes = []
    for uid in picked:
        line, user = users[uid]
        ts = [t for t in targets if t['user_uuid'] == uid]
        last = max(t['chronological_session_ordinal_one_based'] for t in ts)
        sessions = [session_input(user, i, n) for n, (i, _) in enumerate(ordered(user)[:last], 1)]
        require(all(datetime.strptime(a['end_time'], DATE_FORMAT) <= datetime.strptime(b['start_time'], DATE_FORMAT) for a,b in zip(sessions, sessions[1:])), 'Selected prefix has overlapping sessions')
        prefixes.append(dict(user_uuid=uid, dataset_line_one_based=line, target_count=len(ts),
                             first_chronological_ordinal_one_based=1, last_chronological_ordinal_one_based=last,
                             original_session_indices_zero_based=[s['original_session_index_zero_based'] for s in sessions],
                             full_sessions_required=last, messages_required=sum(len(s['messages']) for s in sessions),
                             start_time=sessions[0]['start_time'], end_time=sessions[-1]['end_time']))
    insufficient = []
    for r in recipes['insufficient_evidence']:
        _, user = users[r['user_uuid']]
        si, pi = r['session_index'], r['point_index']
        insufficient.append(dict(**r, annotation=user['sessions'][si]['memory_points'][pi], annotation_status=STATUS,
                                 target_session_dialogue=user['sessions'][si]['dialogue'],
                                 decision='excluded_insufficient_evidence'))
    selected = {(t['user_uuid'], t['original_session_index_zero_based'], t['memory_point_index_zero_based']) for t in targets}
    excluded = {(r['user_uuid'], r['session_index'], r['point_index']) for r in insufficient}
    ledger = []
    for uid in picked:
        for si, s in ordered(users[uid][1])[:18]:
            for pi, mp in enumerate(s.get('memory_points', [])):
                if flag(mp.get('is_update')):
                    k = (uid, si, pi)
                    ledger.append(dict(user_uuid=uid, session_index=si, point_index=pi,
                                       memory_content=mp['memory_content'], decision=('selected_pending_human_review' if k in selected else
                                       'excluded_insufficient_evidence' if k in excluded else 'not_selected_unverified_or_redundant_quota'),
                                       note='Unselected is not a claim of insufficient evidence or Mem0 failure.'))
    manifest = dict(schema_version=1, name='HaluMem-Medium-development-v1', status='fixed_pending_human_review',
                    dataset_relative_path=str(DATA.relative_to(ROOT)), dataset_sha256=digest(dataset), dataset_bytes=Path(dataset).stat().st_size,
                    seed=42, selected_users=picked, previously_debugged_users=[KNOWN_USER],
                    rules_sha256=digest(DEV / 'SELECTION_RULES.md'), recipes_sha256=digest(DEV / 'recipes.json'),
                    total_targets=len(targets), target_session_groups=len({t['session_group_id'] for t in targets}),
                    categories=dict(Counter(t['category'] for t in targets)),
                    target_shortfall=max(0, 20-len(targets)), human_verified_targets=0, model_run_status='未运行',
                    prefixes=prefixes, targets=targets)
    require(len(selected) == len(targets) and 20 <= len(targets) <= 30, 'Duplicate targets or target shortfall; review instead of padding')
    require(all(p['target_count'] == 8 for p in prefixes), 'Quota mismatch')
    return manifest, insufficient, ledger


def write_table(path, rows):
    with Path(path).open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        for r in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in r.items()})


def validate_manifest(path=DEV / 'manifest.json', dataset=DATA):
    saved = read(path)
    expected, _, _ = build_artifacts(dataset)
    require(saved == expected, 'Frozen manifest differs from data/rules/recipes; create a reviewed new version')
    return saved, load_data(dataset)


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build', action='store_true')
    a = p.parse_args()
    manifest, insufficient, ledger = build_artifacts()
    if a.build:
        # Refuse changing an existing fixed set silently.
        if (DEV / 'manifest.json').exists():
            require(read(DEV / 'manifest.json') == manifest, 'Manifest already frozen; version instead of overwrite')
        dump(DEV / 'manifest.json', manifest)
        dump(DEV / 'insufficient_evidence.json', insufficient)
        dump(DEV / 'candidate_ledger.json', ledger)
        dump(DEV / 'prefix_ranges.json', manifest['prefixes'])
        write_table(DEV / 'initial_annotations.csv', manifest['targets'])
        lines=['# 固定目标索引（全部自动初标，待人工核验）', '',
               '会话和memory point均为0基原始数组索引。完整原文、候选保护命题及允许范围见CSV/manifest；同会话仅输入一次。', '',
               '| 用户 | 会话/point | 类别 | 旧命题 | 预期新状态 | 早期证据→当前证据 |',
               '|---|---|---|---|---|---|']
        for t in manifest['targets']:
            refs=lambda es: ', '.join(e['json_pointer'] for e in es)
            lines.append('| '+ ' | '.join([t['user_uuid'],str(t['original_session_index_zero_based'])+'/'+str(t['memory_point_index_zero_based']),t['category'],t['old_proposition'],t['expected_new_state'],refs(t['old_dialogue_evidence'])+' → '+refs(t['new_dialogue_evidence'])])+' |')
        (DEV/'TARGETS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
        dump(DEV / 'data_validation.json', dict(status='passed_offline', dataset_sha256=manifest['dataset_sha256'],
             users=20, sessions=sum(len(u['sessions']) for _, u in load_data().values()),
             target_count=manifest['total_targets'], groups=manifest['target_session_groups'],
             dataset_warnings=[{'user_uuid':uid,'previous_original_index':a,'next_original_index':b, 'warning':'overlapping_sessions_outside_selected_prefixes'} for uid,(_,u) in load_data().items() for (a,sa),(b,sb) in zip(ordered(u),ordered(u)[1:]) if datetime.strptime(sb['start_time'],DATE_FORMAT)<datetime.strptime(sa['end_time'],DATE_FORMAT)],
             model_calls=0, memory_databases_constructed=0))
    else:
        validate_manifest()
    print(json.dumps({k: manifest[k] for k in ['dataset_sha256','selected_users','total_targets','target_session_groups','categories','prefixes']}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
