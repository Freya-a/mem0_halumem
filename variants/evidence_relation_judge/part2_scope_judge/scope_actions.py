"""Conservative local correction candidates and exact-text deduplication.

Every output is review-only. Pattern matching establishes source and location,
not that the speaker's assertion or the proposed interpretation is true.
"""
from copy import deepcopy
import re

_CORRECTION = re.compile(
    r'(?:^|(?<=\.)\s+)\s*Correction:\s*my\s+(?P<attribute>[a-z][a-z ]{0,50}?)\s+is\s+'
    r'(?P<new>[a-z][a-z -]{0,40}?),\s*not\s+(?P<old>[a-z][a-z -]{0,40}?)\s*\.(?=\s|$)',
    re.IGNORECASE,
)


def _dedupe_key(text):
    text=' '.join(text.split())
    # Merge a leading greeting only; never treat arbitrary substrings as duplicates.
    return re.sub(r'^(?:Hey|Hi|Hello),\s+', '', text, flags=re.IGNORECASE)


def deduplicate_additions(items):
    """Merge case-sensitive identical content after whitespace and an optional leading greeting."""
    result=[]; positions={}
    for item in items:
        key=_dedupe_key(item['text'])
        ref={'source_id':item['source_id'],'quote':item['quote'],'kind':item['kind']}
        if 'support_status' in item: ref['support_status']=item['support_status']
        if key not in positions:
            copy=deepcopy(item)
            copy['kinds']=[item['kind']]
            copy['evidence_refs']=[ref]
            copy['dedupe']='exact_text_after_whitespace_and_optional_leading_greeting'
            positions[key]=len(result); result.append(copy)
        else:
            entry=result[positions[key]]
            if item['kind'] not in entry['kinds']: entry['kinds'].append(item['kind'])
            if ref not in entry['evidence_refs']: entry['evidence_refs'].append(ref)
    return result


def explicit_correction(memory, fact, sources, fragment_match):
    """Find explicit paired 'my X is NEW, not OLD' correction in a full clause.

    Require an unambiguous, v4-sourced old clause in the complete memory and a
    user-authored correction; do not infer time or generalize beyond this form.
    """
    proposals=[]
    if fragment_match.get('start') is None or fragment_match.get('end') is None:
        return [], [], []
    for source in sources:
        if source.get('speaker') != 'user': continue
        for match in _CORRECTION.finditer(source['text']):
            old=match.group('old').strip(); new=match.group('new').strip(); attr=match.group('attribute').strip()
            if old.casefold()==new.casefold(): continue
            clause=re.compile(r'(?i)(?:^|(?<=[.;]))\s*(?P<assertion>my\s+' + re.escape(attr) + r'\s+is\s+(?P<old>' + re.escape(old) + r'))(?=\s*(?:[.;]|$))')
            found=list(clause.finditer(memory))
            if len(found)!=1: continue
            m=found[0]; start,end=m.span('old'); assertion_start,assertion_end=m.span('assertion')
            if memory[assertion_start:assertion_end].casefold() not in fact.get('raw_subfact','').casefold():
                continue
            if not any(e.get('source_type')=='memory' and e.get('quote') and
                       any(i <= assertion_start and assertion_end <= i+len(e['quote'])
                           for i in range(len(memory)) if memory.startswith(e['quote'],i))
                       for e in fact.get('evidence',[])):
                continue
            proposals.append({'start':start,'end':end,'old':memory[start:end],'new':new,
                              'attribute':attr,'assertion':memory[assertion_start:assertion_end],
                              'source_id':source['source_id'],'quote':match.group().strip()})
    if not proposals: return [], [], []
    grouped={}
    for p in proposals: grouped.setdefault((p['start'],p['end']),[]).append(p)
    # Multiple affected spans or incompatible values must be reviewed jointly.
    if len(grouped)!=1 or len({p['new'].casefold() for p in proposals})!=1:
        return [], [], [{'code':'conflicting_corrections','candidates':deepcopy(proposals)}]
    first=proposals[0]; start,end=first['start'],first['end']
    patch={'kind':'modify_candidate','status':'needs_review','span':{'start':start,'end':end},
           'old_text':first['old'],'proposed_text':first['new'],
           'attribute_candidate':first['attribute'],'relation_candidate':'explicit_correction',
           'semantic_correctness':'not_checked','time_effect':{'state':'unknown'},
           'conditions':['human verifies subject, attribute, polarity, temporal scope and dependent clauses',
                         'original memory hash and source quotes remain unchanged',
                         'candidate is not an authorization to write'],
           'evidence_refs':[{'source_id':fact['source_memory_id'],'quote':first['assertion'],'source_type':'memory'}]+
               [{'source_id':p['source_id'],'quote':p['quote'],'source_type':'new'} for p in proposals],
           'reason':'explicit same-phrase correction; literal evidence does not establish semantic correctness'}
    protection=[]
    for a,b in ((0,start),(end,len(memory))):
        if a<b:
            protection.append({'text':memory[a:b],'span':{'start':a,'end':b},
                               'reason':'retain original context around candidate; semantic dependencies require review',
                               'evidence_refs':[{'source_type':'memory','source_id':fact['source_memory_id'],'quote':memory[a:b]}]})
    return [patch],protection,[]


def combine_additions(rows):
    """Deduplicate within this request across fact rows, preserving all provenance."""
    flattened=[]
    for row in rows:
        for item in row['additions']:
            for ref in item.get('evidence_refs',[]):
                flattened.append({'text':item['text'], 'source_id':ref['source_id'],'quote':ref['quote'],
                                  'kind':ref['kind'],'semantic_correctness':'not_checked','fact_index':row['fact_index'], **({'support_status':ref['support_status']} if 'support_status' in ref else {})})
    result=deduplicate_additions(flattened)
    for item in result:
        key=_dedupe_key(item['text'])
        item['fact_indices']=list(dict.fromkeys(x['fact_index'] for x in flattened if _dedupe_key(x['text'])==key))
        item.pop('fact_index',None)
    return result


def combine_modifications(rows):
    """Merge identical proposals; suppress overlapping or inconsistent proposals."""
    entries=[(row,patch) for row in rows for patch in row['modifications']]
    conflict=set()
    for i,(_,left) in enumerate(entries):
        la,lb=left['span']['start'],left['span']['end']
        for j in range(i+1,len(entries)):
            right=entries[j][1]; ra,rb=right['span']['start'],right['span']['end']
            same=(la,lb,left['old_text'],left['proposed_text'])==(ra,rb,right['old_text'],right['proposed_text'])
            if la<rb and ra<lb and not same: conflict.update((i,j))
    for i in sorted(conflict):
        row,patch=entries[i]
        if patch in row['modifications']: row['modifications'].remove(patch)
        row['pending'].append({'code':'overlapping_modifications','candidate':deepcopy(patch)})
        row['protected']=[{'text':row['memory_text'],'reason':'overlapping candidate modifications require joint review',
                           'evidence_refs':[{'source_type':'memory','source_id':row['memory_id'],'quote':row['memory_text']}]}]
    result=[]; grouped={}
    for i,(row,patch) in enumerate(entries):
        if i in conflict: continue
        key=(patch['span']['start'],patch['span']['end'],patch['old_text'],patch['proposed_text'])
        if key not in grouped:
            group=deepcopy(patch);group['fact_indices']=[];group['memory_id']=row['memory_id'];group['memory_sha256']=row['memory_sha256']
            grouped[key]=group;result.append(group)
        group=grouped[key]
        if row['fact_index'] not in group['fact_indices']: group['fact_indices'].append(row['fact_index'])
        for ref in patch['evidence_refs']:
            if ref not in group['evidence_refs']: group['evidence_refs'].append(deepcopy(ref))
    return result


def local_protection_candidates(memory, fact, scope, modifications):
    """Identify literally repeated, cited dimensions without assuming their semantics."""
    result=[]
    for field in ('subject','object','attribute','conditions'):
        item=scope.get('field_comparisons',{}).get(field,{})
        if item.get('comparison')!='same_text': continue
        old=item.get('old'); new=item.get('new'); provenance=item.get('source_refs',{})
        old_refs=provenance.get('old',{}); new_refs=provenance.get('new',{})
        if old_refs.get('status')!='literal_quote_verified' or new_refs.get('status')!='literal_quote_verified': continue
        if not any(old in x['quote'] for x in old_refs['refs']) or not any(new in x['quote'] for x in new_refs['refs']): continue
        positions=[i for i in range(len(memory)) if memory.startswith(old,i)]
        if len(positions)!=1: continue
        start=positions[0]; end=start+len(old)
        if old not in fact.get('raw_subfact',''): continue
        if any(start < m['span']['end'] and m['span']['start'] < end for m in modifications): continue
        if any(start < p['span']['end'] and p['span']['start'] < end for p in result): continue
        result.append({'kind':'protected_candidate','text':old,'span':{'start':start,'end':end},
                       'dimension':field,'semantic_correctness':'not_checked',
                       'reason':'same literal field appears in both cited sides; verify its role and dependencies',
                       'evidence_refs':deepcopy(old_refs['refs']+new_refs['refs'])})
    return result
