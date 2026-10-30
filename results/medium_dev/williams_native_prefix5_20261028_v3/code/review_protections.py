"""Bind every frozen protection candidate to saved evidence, with explicit unresolved cases."""
import json,sys
from pathlib import Path
from protection_map import patterns,locate
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'scripts'))
import medium_dev_run as r
run=Path(__file__).resolve().parents[1];dest=run/'development_diagnosis_v1'
records=[]
for n in range(1,25):
    e=r.data.read(dest/f'target_{n:02d}_evidence.json')
    for j,p in enumerate(json.loads(e['review']['candidate_protections']),1):
        pats=patterns(p['proposition'],e['review']['user_uuid']);b=locate(e['before'],pats);a=locate(e['after'],pats)
        changed=[dict(id=i,before=t,after=e['after'].get(i)) for i,t in b.items() if e['after'].get(i)!=t]
        state='stored_fragment_preserved' if b and not changed else ('requires_semantic_review' if b else 'not_located_before')
        note='仅表示已定位片段保留，不证明候选的全部复合含义或原证据日期已存储。'
        if (n,j)==(9,1):state='stored_fragment_preserved';note='Likes改为Appreciates；历史传统、佛手柑、怀旧理由均保留，无语义损伤。'
        if (n,j)==(14,1):state='confirmed_partial_loss';note='旧平静/优雅等理由原文在before；after波斯猫记忆被改写，完整after未保留平静理由，新对话未撤销。至少平静属性确认损伤。'
        if n==8 and j==1:state='stored_fragment_preserved';note='旧安全承诺在新模拟体验记忆中仍以values safety表达；并未删除安全原则。'
        if n==8 and j==2:state='confirmed_partial_loss';note='新记忆保留过去回避与safety concerns，但省略旧high injury risk具体历史理由。整体after未在其他记忆补回；属历史理由细节部分缩减，不等于安全原则全丢。'
        if n==8 and j in (3,4,5):state='stored_fragment_preserved';note='主瑜伽记忆保留并新增regularly，思维清晰/柔韧性均在。另删泛化的健康/转型瑜伽条目，不导致本候选核心属性丢失；before未明确regularly的部分不当成既有完整入库。'
        if (n,j) in {(17,4),(18,1),(20,1)}:state='stored_fragment_preserved';note='Blockchain Tech高级开发人员由当前表达改为previously worked；雇主与职级仍在，符合转型历史处理。'
        if (n,j) in {(17,7),(18,7),(19,2),(20,8)}:state='stored_fragment_preserved';note='16,800 USD储蓄前后数值、币种和储蓄属性相同，只改变格式；未作为月收入混写。原对话时间并未作为事件日期编码。'
        if (n,j)==(19,1):state='stored_fragment_preserved';note='17,000 USD月收入保留并明确为转型前，数值币种属性未改变；原对话的精确日期在before已未显式编码。'
        if (n,j)==(20,2):state='stored_fragment_preserved';note='政治资助及薪资、储蓄可定位片段仍在；工资改为过去式、储蓄格式变化、旧技术工作转为历史。复合候选的来源日期和全部财务含义不保证完整入库。'
        if (n,j)==(24,1):state='stored_fragment_preserved';note='公司启动/成立信息仍在；此前获客计划本未保存。被删具体12月20日是助手提出，缺充分用户确认，不作为已确认历史的有效保护损伤。'
        if (n,j)==(24,2):state='confirmed_partial_loss';note='此前Blockchain Tech高级开发的已存历史缩减为Formerly worked in technology；用户已确认的雇主与高级职位细节丢失。收入和储蓄独立记录仍在。'
        if n==24 and j in (4,5):state='stored_fragment_preserved';note='包含Sandra/Mary的network表述改为key network contacts；两人的独立朋友身份原文仍保留，未观察到关系损伤。'
        records.append(dict(target_number=n,candidate_index=j,proposition=p['proposition'],locator_patterns=pats,
            before_matches=b,after_matches=a,before_recalled={i:i in e['recalled_ids'] for i in b},changes=changed,
            before_coverage='related_stored_fragment' if b else 'not_located',verdict=state,note=note))
assert len(records)==176
r.atomic(dest/'protection_observations.json',records)
for x in records:
    if x['verdict'] in ('requires_semantic_review','not_located_before'):
        print(json.dumps(dict(n=x['target_number'],j=x['candidate_index'],p=x['proposition'],v=x['verdict'],changes=x['changes']),ensure_ascii=False))
