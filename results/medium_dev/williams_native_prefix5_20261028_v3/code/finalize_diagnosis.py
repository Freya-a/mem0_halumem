"""Render reviewed diagnostics. No online calls; semantic decisions remain explicitly assisted."""
import collections,csv,json,sys
from pathlib import Path
from protection_map import locate
from target_locators import OLD,NEW
from semantic_assessments import ASSESS
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'scripts'))
import medium_dev_run as r
run=Path(__file__).resolve().parents[1];dest=run/'development_diagnosis_v1'
assert set(ASSESS)==set(range(1,25))
runtime=r.data.read(dest/'runtime_verification.json');protections=r.data.read(dest/'protection_observations.json')
assert not any(x['verdict']=='requires_semantic_review' for x in protections),'Resolve every changed matched protection before final report'
labels={'full':'核心新状态完整保存','partial':'核心新状态部分覆盖','missing':'核心新状态未保存','repeat_preserved':'重复确认核心保留','repeat_partial':'重复确认部分覆盖','associated_full':'关联方法计划保存','associated_partial':'关联方法计划部分覆盖'}
results=[]
for n in range(1,25):
    e=r.data.read(dest/f'target_{n:02d}_evidence.json');verdict=ASSESS[n]
    before=locate(e['before'],OLD[n]);after=locate(e['after'],NEW[n])
    prot=[x for x in protections if x['target_number']==n]
    results.append(dict(number=n,target_id=e['target_id'],user_uuid=e['review']['user_uuid'],review_class=e['review']['review_class'],
        original_session_index=e['original_target']['original_session_index_zero_based'],session_group=e['review']['session_group_id'],
        verdict=verdict,old_related_memory=before,old_recall={i:i in e['recalled_ids'] for i in before},
        new_related_memory=after,protections=prot,evidence=f'target_{n:02d}_evidence.json'))
primary=[x for x in results if x['review_class'] in ('接受','修订后接受')]
repeat=[x for x in results if x['review_class']=='重复确认'];associated=[x for x in results if x['review_class']=='归并']
assert (len(primary),len(repeat),len(associated))==(19,4,1)
stored=[x for x in protections if x['before_matches']]
loss=[x for x in stored if x['verdict']=='confirmed_partial_loss'];unlocated=[x for x in protections if not x['before_matches']]
counts=collections.Counter(x['verdict']['state'] for x in primary)
planned=sum(len(x['matched'])+len(x['unexecuted_plans']) for x in runtime['sessions'])
matched=sum(len(x['matched']) for x in runtime['sessions'])
actual=sum(runtime['actual_operations'].values())
same=sum(x['same_text_updates'] for x in runtime['sessions'])
unique_groups={x['session_group'] for x in results}
session_index={(x['user_uuid'],x['original_index']):x for x in runtime['sessions']}
metrics=dict(primary_denominator=19,primary_states=dict(counts),repeat_denominator=4,repeat_states=dict(collections.Counter(x['verdict']['state'] for x in repeat)),associated_denominator=1,
    associated_states=dict(collections.Counter(x['verdict']['state'] for x in associated)),target_session_groups=len(unique_groups),
    target_rows=24,old_related_fragment_present=sum(bool(x['old_related_memory']) for x in results),
    old_at_least_one_related_fragment_recalled=sum(any(x['old_recall'].values()) for x in results),old_any_recall_denominator=sum(bool(x['old_related_memory']) for x in results),
    protection_candidate_rows=176,protection_candidate_rows_with_located_stored_fragment=len(stored),protection_unlocated_before=len(unlocated),
    confirmed_loss_candidate_rows=len(loss),confirmed_loss_denominator=len(stored),
    planned_mutations=planned,actual_mutations=actual,same_text_updates=same,distinct_target_contexts=len(unique_groups))
r.atomic(dest/'target_decisions.json',dict(method='LLM-assisted semantic review of saved logs, not user-confirmed gold labels or blind review',metrics=metrics,targets=results))
table=[dict(number=x['number'],target_id=x['target_id'],review_class=x['review_class'],new_state=x['verdict']['state'],
    old_related_ids=json.dumps(list(x['old_related_memory'])),old_recall=json.dumps(x['old_recall']),
    protected_stored=sum(bool(p['before_matches']) for p in x['protections']),protected_loss=sum(p['verdict']=='confirmed_partial_loss' for p in x['protections']),
    note=x['verdict']['note'],unknown=x['verdict']['unknown']) for x in results]
with (dest/'target_decisions.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(table[0]));writer.writeheader();writer.writerows(table)
plines=['# 176条保护候选逐项证据','', '定位规则只提供候选ID；非完全相同文本的变化已单独作语义复核。复合候选的相关存量不等于其全部细节已入库，未定位项不纳入损伤分母。','']
for x in protections:
    plines += [f'## 目标{x["target_number"]} / 保护{x["candidate_index"]}：{x["proposition"]}',
        f'结论：{x["verdict"]}。{x["note"]}','', '更新前：']
    plines += [f'- `{i}` ({"已召回" if x["before_recalled"][i] else "未召回"})：{t}' for i,t in x['before_matches'].items()] or ['- 未定位相关存量；不判保留成功或本次损伤。']
    plines += ['更新后：']+[f'- `{i}`：{t}' for i,t in x['after_matches'].items()]+['']
(dest/'protection_review.md').write_text('\n'.join(plines)+'\n')
lines=['# 原生Mem0开发诊断报告（24项目标）','',
    '日期：2026-10-28。run_id：`williams_native_prefix5_20261028_v3`。审核版本：`human_review_v1_20261028`。本报告为LLM辅助运行后语义诊断，尚未经用户逐项确认；不覆盖或回写已冻结的人工审核。','',
    '已完成3位用户28个完整会话、990条原始消息。Williams续跑剩余6会话，已完成5会话未重输；Martin、Donald各从独立空库运行9、8会话。模型配置、原生提示词、top-5检索及更新执行逻辑未改动；没有加入改进模块、QA或额外评判模型调用。','',
    '## 只读核查与运行可信度','',
    '[只读审计证据](../read_only_audit/result.json)确认v1/v2路径独立，均0实际写入；v3首before为空，失败启动没有污染正式知识库。已核对前5会话产物哈希、向量库、history及检查点一致，并用临时库副本核查，未改动原证据。','',
    '第2会话的UPDATE临时ID19已在提供商原始响应中，旧映射只有0–14；原生查表在操作插桩之前抛KeyError，原生逐操作捕获后跳过。SDK原始文本与Observer原样返回文本相同；冻结源码重新生成的抽取及更新提示词逐字相等，召回映射按原候选顺序生成。Observer和APIAudit只记录并原样转发参数、结果及异常；没有重写模型输出。该结论基于源码及已存数据流证据，不声称进行过一轮新的未插桩在线反事实实验。','',
    '续跑保留正常返回的原生Memory.add的实际状态及其吞掉的异常。外层严格运行器拒绝记录保存在各error.json，附observed_anomaly.json后提交带异常观测检查点；没有补写记忆、修正临时ID、回滚或重试会话。此为外层记录政策，不是原生修复。','',
    '最终检查：所有28会话实际add输入逐项等于原始dialogue的role/content，完整助手消息保留；没有把persona、memory_points、original_memories、人工审核答案、保护标签或QA答案输入被测模型，也未预填知识。所有提交哈希、会话前后连续性、history重放及磁盘副本持久化核验通过。见[runtime_verification.json](runtime_verification.json)。','',
    '## 口径与分母','',
    '原始24条按审核分为19个接受/修订主目标、4个重复确认、1个归并条目。19个是诊断子目标数，合属16个目标会话情境，存在用户内和共享会话关联，不能当19或24次统计独立实验。“完整”要求本审核核心新增语义在整个after中明确可表达；“部分”表示只保存了部分核心或缺少关键关系。补充细化不要求旧正文删除，亦不以UPDATE事件判成功。审核中另存的补充及关联方法计划单列，不回填官方分母。','',
    '| 指标 | 分子 / 分母 | 说明 |','|---|---:|---|',
    '| 完整会话输入 | 28 / 28 | 包含原有5个已提交会话，未重输 |',
    '| 完整原始消息 | 990 / 990 | 对照固定3用户前缀 |',
    f'| 有记录的目标会话情境 | {len(unique_groups)} / 16 | 共同会话内的子目标共享一次输入与操作 |',
    f'| 主目标核心完整保存 | {counts.get("full",0)} / 19 | 不含重复确认或归并条目 |',
    f'| 主目标核心部分覆盖 | {counts.get("partial",0)} / 19 | 不并入完整保存分子 |',
    f'| 主目标核心未保存 | {counts.get("missing",0)} / 19 | 与部分覆盖区分 |',
    f'| 重复确认核心保留 | {sum(x["verdict"]["state"]=="repeat_preserved" for x in repeat)} / 4 | 第2、5、6、15条；不要求新增语义 |',
    f'| 关联方法计划完整保存 | {sum(x["verdict"]["state"]=="associated_full" for x in associated)} / 1 | 第20条，不新增独立转型样本 |',
    '| 时间状态候选的新阶段明确保存 | 2 / 2 | 第7、10条的共同旧状态已实际入库；按整体知识判断 |',
    '| 时间状态候选的旧当前记录显式历史化 | 0 / 2 | 旧语句仍在，不能因此断言下游时间消歧完成 |',
    f'| 更新前定位到相关旧知识片段 | {metrics["old_related_fragment_present"]} / 24 | 完整旧命题覆盖与相关片段不是同一指标；详见逐项限定 |',
    f'| 至少一条相关旧片段被召回 | {metrics["old_at_least_one_related_fragment_recalled"]} / {metrics["old_any_recall_denominator"]} | 仅限before有相关片段的条目，不代表召回全部充分 |',
    f'| 保护候选中可定位相关存量 | {len(stored)} / 176 | 含复合候选的部分覆盖及跨目标重复 |',
    f'| 确认存量部分损伤 | {len(loss)} / {len(stored)} | 分母仅可定位存量候选；不是全部候选均完整入库 |',
    f'| before未定位保护候选 | {len(unlocated)} / 176 | 不判保留成功或本次损伤 |',
    f'| 计划变更实际落地 | {matched} / {planned} | 具有文本的ADD/UPDATE/DELETE，一一对应核验；NONE另计 |',
    f'| 计划变更未落地 | {planned-matched} / {planned} | 4个会话的原生无效临时ID；实际额外未计划操作0项 |',
    f'| 含计划/实际差异的会话 | {len(runtime["plan_actual_mismatches"])} / 28 | 异常均保留实际状态并标记 |',
    f'| 同文UPDATE | {same} / {runtime["actual_operations"].get("UPDATE",0)} | 文本未变，向量及元数据仍可能被写入；不当作语义更新成功 |','',
    '保护计数按“目标×保护候选”记账，不是唯一事实数；共176行、116种原始保护表述，后者仍非语义唯一事实数。完整逐条before/after/召回ID见[protection_review.md](protection_review.md)和[protection_observations.json](protection_observations.json)。确认损伤还按实际用户、会话及记忆ID去重列在下文。','',
    '第7和10条为预指定时间状态替换候选，两者before均有相关旧当前阶段。它们的新阶段保存与旧当前记录显式历史化分别评价；本次只做单方法开发诊断，没有多方法共同快照比较。第24条的旧获客计划不能推导“尚无任何客户”，不加入严格纠错分母。','',
    '## 24项目标汇总','', '|序号|用户 / 原始会话|审核类型|新状态判断|before相关ID / 已召回|保护损伤 / 可定位候选|','|---:|---|---|---|---:|---:|']
names={'2f1':'Martin','1b8':'Williams','348':'Donald'}
for x in results:
    ps=x['protections'];lines.append(f'|[{x["number"]}](#target-{x["number"]})|{names[x["user_uuid"][:3]]} s{x["original_session_index"]}|{x["review_class"]}|{labels[x["verdict"]["state"]]}|{len(x["old_related_memory"])} / {sum(x["old_recall"].values())}|{sum(p["verdict"]=="confirmed_partial_loss" for p in ps)} / {sum(bool(p["before_matches"]) for p in ps)}|')
lines+=['','## 逐项证据与未知项','']
for x in results:
    n=x['number'];lines += [f'<a id="target-{n}"></a>',f'### {n}. {x["target_id"]}',f'判定：**{labels[x["verdict"]["state"]]}**。{x["verdict"]["note"]}', '', '更新前相关实际记忆：']
    lines += [f'- `{i}`（{"已召回" if x["old_recall"][i] else "未召回"}）：{t}' for i,t in x['old_related_memory'].items()] or ['- 未定位；不能归因于该次召回或更新。']
    lines += ['', '更新后相关实际记忆：']+[f'- `{i}`：{t}' for i,t in x['new_related_memory'].items()]
    s=session_index[(x['user_uuid'],x['original_session_index'])]
    lines += ['', f'本会话计划：{s["planned"]}；实际：{s["actual"]}；未执行计划{len(s["unexecuted_plans"])}项、同文UPDATE {s["same_text_updates"]}项。这是同会话共享记录，不把全部操作归因给本目标。',
        f'保护候选：可定位相关存量 {sum(bool(p["before_matches"]) for p in x["protections"])} / {len(x["protections"])}；确认部分损伤 {sum(p["verdict"]=="confirmed_partial_loss" for p in x["protections"])} / {sum(bool(p["before_matches"]) for p in x["protections"])}。复合候选是否完整入库及逐项召回另见保护表。',
        f'未知/范围限定：{x["verdict"]["unknown"]}',f'证据：[完整前后及操作](target_{n:02d}_evidence.json)；[便于浏览的前快照与差异](target_{n:02d}_evidence.md)；[保护候选逐项](protection_review.md)。','']
lines += ['## 原生异常及计划/实际差异','', 'v1/v2启动失败各一次，均发生在首次抽取请求，0写入；正式v3范围不含这两次失败命名空间。以下为正式28会话中的操作差异，全部保存实际状态，没有重试。','']
for d in runtime['plan_actual_mismatches']:
    lines += [f'### {d["user_uuid"]} / 原始sessions[{d["ordinal"]-1}]',f'计划：{d["planned"]}；实际：{d["actual"]}；同文UPDATE：{d["same_text_updates"]}。']
    for p in d['unexecuted_plans']:lines.append(f'- 未落地：临时ID `{p.get("id")}`，{p["event"]}，{p.get("text")}；解析到旧UUID：{p.get("resolved_existing_memory_id")}。')
    lines+=['']
lines += ['## 保护内容损伤与解释边界','']
for p in loss:lines += [f'- 目标{p["target_number"]} / 保护{p["candidate_index"]}：{p["proposition"]}。{p["note"]}']
lines += ['', '全会话合法更新依据完整原始对话判定，不把其他有依据的新信息算越界；旧收入、职称、健康与职业阶段的当前有效性和历史真实性分开。保护结论只核查after可用知识，history保存旧文本不等于当前记忆库已保留相同可检索知识。对于复合候选未入库的细节和精确事件时间，本报告不虚构完整性。','',
    '额外观察：Williams第9条所在会话把Name is Williams Daniel改成Name is Williams，属姓名细节缩减；也把“成为知名导演”的目标收窄为制作历史准确电影。Martin较早的原始sessions[3]把全球健康倡议目标概括为医疗可及性职业动机，后续before已无建立该倡议的细节。Martin sessions[6]新写入Is a software engineer，该会话原始对话未出现software；原生抽取提示词示例中有Is a Software engineer，存在示例影响的可能，但仅凭记录无法证明因果。Martin sessions[8]把金毛偏好升级成养犬事实，且将模拟体验泛化至极限运动；Donald sessions[7]新增家庭支持，原对话主要由助手提出，缺充分用户确认。以上另行解释，不混入176保护分母。完整助手消息照原文输入；被保存的助手断言不等于已获用户确认。','',
    '## 复核入口与可重复验证','',
    '- [逐项目JSON](target_decisions.json) / [CSV](target_decisions.csv)：语义结论、未知项及ID。',
    '- [运行核验](runtime_verification.json)：28会话消息数、快照、全部计划和实际操作差异。',
    '- `../users/<UUID>/session_XXX/`：完整原始输入、含向量快照、召回候选、模型输入输出、全计划、实际history、异常、持久化和检查点。',
    '- `../human_review_version/`：冻结审核副本；原始manifest/profile/run_record仍绑定原版本。',
    '- `../pre_continuation/`：续跑前5会话检查点及状态；本轮没有重输前5会话。旧`RESULT_SHA256SUMS`中的checkpoint路径指向当时的状态；续跑后当前checkpoint已推进，旧哈希对应此处的`user_checkpoint.json`，不是现在的checkpoint文件。',
    '- `../development_console.log`：顺序运行及带异常提交；各用户最终checkpoint分别11、9、8。','',
    '验证命令（不调用模型）：`conda run -n mem0_halumem python results/medium_dev/williams_native_prefix5_20261028_v3/code/collect_diagnosis.py`。该命令只读取现有运行资料，在临时副本上开库，并再生成离线评价证据。源码哈希及冻结审核应保持不变。','',
    '本开发子集含已调试用户、用户内时序关联和共享会话目标；不能报告为无偏总体性能或独立样本显著性。未运行全量QA、官方评分、后续召回问答或改进模块，未知下游回答质量。']
(dest/'NATIVE_MEM0_DIAGNOSIS.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(metrics,ensure_ascii=False,indent=2))
