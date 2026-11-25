"""Render saved model output; independent human reviews never enter the planner."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
CASES = ('susan', 'promotion', 'career_history', 'transition', 'skydiving')
CATEGORIES = ('modify', 'preserve', 'uncertain', 'add', 'editable_spans', 'protected_facts')
VERDICTS = {'supported', 'partially_supported', 'unsupported', 'uncertain'}


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(obj):
    return hashlib.sha256(canonical(obj).encode('utf-8')).hexdigest()


def verify_saved_source(source, project=PROJECT, *, memory=False):
    """Verify a copied source text against its original local file and pointer.

    This verifies the source object only. Unique quote location and linked-unit
    membership are independently checked in the saved interface validation.
    """
    out = {'source_id': source.get('source_id'), 'source_ref': source.get('source_ref'),
           'status': 'invalid', 'reason': None}
    try:
        ref = source.get('source_ref')
        if not isinstance(ref, str) or not ref:
            raise ValueError('source_ref missing')
        path, marker, pointer = ref.partition('#')
        data = json.loads((Path(project) / path).read_text(encoding='utf-8'))
        if memory:
            rows = [x for x in data['api_snapshot']['results'] if x.get('id') == source.get('source_id')]
            if len(rows) != 1 or rows[0].get('memory') != source.get('text'):
                raise ValueError('memory ID or text does not match original snapshot')
        else:
            if not marker:
                raise ValueError('JSON pointer missing')
            parts = pointer.split(' [', 1)[0].strip('/').split('/')
            parent = data
            for part in parts[:-1]:
                part = part.replace('~1', '/').replace('~0', '~')
                parent = parent[int(part)] if isinstance(parent, list) else parent[part]
            last = parts[-1].replace('~1', '/').replace('~0', '~')
            value = parent[int(last)] if isinstance(parent, list) else parent[last]
            if not isinstance(value, str) or value != source.get('text'):
                raise ValueError('source text differs from original pointer')
            if source.get('speaker') is not None and isinstance(parent, dict) and parent.get('role') != source.get('speaker'):
                raise ValueError('speaker differs from original dialogue')
        out['status'] = 'verified'
    except (OSError, KeyError, IndexError, ValueError, TypeError) as exc:
        out['reason'] = str(exc)
    return out


def lookup_review(reviews, index, obj):
    """Never accept a model self-judgment or a review for changed content."""
    entry = reviews.get(str(index), {}) if isinstance(reviews, dict) else {}
    if (entry.get('sha256') == digest(obj) and entry.get('verdict') in VERDICTS
            and isinstance(entry.get('reason'), str) and entry['reason'].strip()):
        return entry
    return {'verdict': 'not_reviewed', 'reason': '没有匹配该内容哈希的独立审核'}


def summarize(artifacts, reviews, safe_results=None):
    stats = {'case_count': len(artifacts), 'request_attempts': 0, 'model_responses': 0,
             'structured_passed': 0, 'quote_passed_cases': 0, 'basis_passed_cases': 0,
             'coverage_passed_cases': 0, 'complete_validation_passed': 0,
             'quote_checks': Counter(), 'record_reviews': Counter(),
             'action_reviews': Counter(), 'plans': Counter(),
             'safe_plans': Counter(), 'safe_action_reviews': Counter()}
    for a in artifacts:
        stats['request_attempts'] += (a.get('call') or {}).get('attempts', 0)
        # Match runner's manifest: a provider completion is a decoded provider
        # object, not a possibly textual HTTP error body. The backend may have
        # received a completion and then failed to parse it.
        stats['model_responses'] += int(isinstance(a.get('provider_response'), dict))
        res = a.get('result') or {}
        v = res.get('validation') or {}
        stats['structured_passed'] += int(v.get('schema_status', v.get('status')) == 'passed')
        stats['quote_passed_cases'] += int(v.get('quote_status') == 'passed')
        stats['basis_passed_cases'] += int(v.get('basis_status') == 'passed')
        stats['coverage_passed_cases'] += int(v.get('coverage_status') == 'passed')
        stats['complete_validation_passed'] += int(v.get('status') == 'passed')
        for q in v.get('quote_checks', []):
            stats['quote_checks'][q.get('status', 'unknown')] += 1
        human = reviews.get(a.get('case_id'), {}) if isinstance(reviews, dict) else {}
        for i, rec in enumerate((res.get('parsed') or {}).get('records', [])):
            stats['record_reviews'][lookup_review(human.get('records', {}), i, rec)['verdict']] += 1
        for cat in CATEGORIES:
            for i, item in enumerate((res.get('plan') or {}).get(cat, [])):
                stats['plans'][cat] += 1
                review = lookup_review(human.get('actions', {}).get(cat, {}), i, item)
                stats['action_reviews'][cat + ':' + review['verdict']] += 1
        safe = (safe_results or {}).get(a.get('case_id'), {})
        for cat in CATEGORIES:
            for i, item in enumerate((safe.get('safe_plan') or {}).get(cat, [])):
                stats['safe_plans'][cat] += 1
                review = lookup_review(human.get('safe_actions', {}).get(cat, {}), i, item)
                stats['safe_action_reviews'][cat + ':' + review['verdict']] += 1
    return {k: dict(v) if isinstance(v, Counter) else v for k, v in stats.items()}


def render_case(artifact, expected, case_review, safe=None):
    out = [f"## {artifact.get('case_id', '?')}", '', '**请求与来源**', '', '```json',
           json.dumps({'call': artifact.get('call'), 'usage': artifact.get('usage')}, ensure_ascii=False, indent=2), '```', '']
    payload = artifact.get('prepared_input') or {}
    texts = payload.get('source_texts') or {}
    memory = texts.get('memory') or {}
    selected = {u.get('source_id') for u in payload.get('new_units', []) if isinstance(u, dict)}
    sources = [m for m in texts.get('messages', []) if m.get('source_id') in selected]
    source_checks = [verify_saved_source(memory, memory=True)] if memory else []
    source_checks.extend(verify_saved_source(s) for s in sources)
    out += ['旧记忆：' + json.dumps(memory, ensure_ascii=False), '',
            '输入所选新单元：' + json.dumps(payload.get('new_units', []), ensure_ascii=False), '',
            '所选新证据及来源：' + json.dumps(sources, ensure_ascii=False), '',
            '原始本地文件与来源指针核验（不替代引文唯一和关联单元检查）：' + json.dumps(source_checks, ensure_ascii=False), '',
            '独立人工预期：' + json.dumps(expected, ensure_ascii=False), '']
    result = artifact.get('result') or {}
    if not result.get('parsed'):
        return '\n'.join(out + ['模型响应未形成可审计的解析记录；无规划结论。', ''])
    out += ['**接口和逐引文校验**（引用定位不等于语义支持）', '', '```json',
            json.dumps(result.get('validation') or {}, ensure_ascii=False, indent=2), '```', '']
    for i, record in enumerate((result.get('parsed') or {}).get('records', [])):
        review = lookup_review(case_review.get('records', {}), i, record)
        out += [f'**模型记录 {i}**', '', '```json', json.dumps(record, ensure_ascii=False, indent=2), '```',
                '独立语义审核：' + json.dumps(review, ensure_ascii=False), '']
    plan = result.get('plan') or {}
    out += ['**未经独立审核补全的模型直接规划结果**', '']
    for cat in CATEGORIES:
        items = plan.get(cat, [])
        out.append(f'- {cat}（{len(items)}）：')
        for i, item in enumerate(items):
            review = lookup_review(case_review.get('actions', {}).get(cat, {}), i, item)
            out.append('  - 输出：' + json.dumps(item, ensure_ascii=False) + '；独立审核：' + json.dumps(review, ensure_ascii=False))
    out += ['', '规划器引文位置和原因：', '', '```json',
            json.dumps(plan.get('quote_checks', []), ensure_ascii=False, indent=2), '```', '']
    if safe is not None:
        out += ['**事后离线适配保护重算**（未再次调用模型；没有覆盖首次结果）', '',
                '状态与散列：' + json.dumps({'status': safe.get('status'), 'provenance': safe.get('provenance')}, ensure_ascii=False), '']
        for cat in CATEGORIES:
            items = (safe.get('safe_plan') or {}).get(cat, [])
            out.append(f'- {cat}（{len(items)}）：')
            for i, item in enumerate(items):
                review = lookup_review(case_review.get('safe_actions', {}).get(cat, {}), i, item)
                out.append('  - 输出：' + json.dumps(item, ensure_ascii=False) + '；独立审核：' + json.dumps(review, ensure_ascii=False))
        out += ['', '事后规划器引用检查：', '', '```json',
                json.dumps((safe.get('safe_plan') or {}).get('quote_checks', []), ensure_ascii=False, indent=2), '```', '']
    out += ['**与原文和人工预期的差异：** ' + str(case_review.get('overall') or '尚未逐案独立审核。'), '']
    return '\n'.join(out)


def main():
    parser = argparse.ArgumentParser(description='Offline report from saved run, no model calls')
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--reviews', type=Path, default=HERE / 'human_reviews.json')
    args = parser.parse_args()
    run = args.run_dir.resolve()
    manifest = json.loads((run / 'manifest.json').read_text(encoding='utf-8'))
    artifacts = [json.loads((run / f'{case}.json').read_text(encoding='utf-8')) for case in CASES]
    reviews = json.loads(args.reviews.read_text(encoding='utf-8')) if args.reviews.exists() else {}
    cases_review = reviews.get('cases', {})
    safe_results = {case: json.loads((run / 'offline_safe' / f'{case}.json').read_text(encoding='utf-8'))
                    for case in CASES if (run / 'offline_safe' / f'{case}.json').exists()}
    stats = summarize(artifacts, cases_review, safe_results)
    out = ['# 五案对齐与范围规划小样本报告', '',
           '独立语义审核以模型原始记录的 SHA-256 绑定，不从模型自述或引文命中自动生成。未审或不匹配项标为 not_reviewed；这不是正式论文准确率。模型直接规划结果维持 semantic_support=unknown，不注入人工预期。', '',
           '**运行信息与统计**', '', '```json', json.dumps({'manifest': manifest, 'statistics': stats}, ensure_ascii=False, indent=2), '```', '',
           '结构通过、引用定位、语义支持和规划结果是独立指标。模型原始响应与请求详情保存在每案 JSON；原始证据、来源指针和全部位置见各案校验。', '']
    if safe_results:
        out += ['首次请求所用代码与提示词的冻结快照保存在 `frozen_at_call/`；首次直接规划结果未改动。`offline_safe/` 使用事后加保护的适配器对同一回复纯离线重算，保存 adapter/planner/响应/输入散列；它没有额外调用模型，也不能补齐未知范围或推断语义。', '']
    for artifact in artifacts:
        case = artifact['case_id']
        expected_path = PROJECT / 'variants/evidence_scope_planner/v2_offline/fixtures' / f'{case}.expected.json'
        expected = json.loads(expected_path.read_text(encoding='utf-8')) if expected_path.exists() else {}
        out.append(render_case(artifact, expected, cases_review.get(case, {}), safe_results.get(case)))
    out += ['## 旧版五条引用核对', '', '逐条来源、单元绑定和可复现实验见 [FIVE_QUOTES.md](../../FIVE_QUOTES.md)。', '']
    (run / 'REPORT.md').write_text('\n'.join(out), encoding='utf-8')
    (run / 'review_summary.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(stats, ensure_ascii=False))

if __name__ == '__main__':
    main()
