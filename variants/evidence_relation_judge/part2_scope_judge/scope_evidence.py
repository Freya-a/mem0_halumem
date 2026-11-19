"""Validate source linkage for model-proposed field and exclusivity candidates."""
from copy import deepcopy

FIELDS=('subject','object','attribute','value','conditions','modality')


def validate_field_evidence(extracted, request, fact):
    memory=request['split_result']['memory_text']; mid=request['split_result']['memory_id']
    sources={'old':{s['source_id']:s['text'] for s in request.get('source_context',[])},
             'new':{s['source_id']:s['text'] for s in request.get('new_evidence',[])}}
    sources['old'][mid]=memory
    proposed=extracted.get('field_evidence',{})
    if not isinstance(proposed,dict): proposed={}
    out={}; issues=[]
    for side in ('old','new'):
        out[side]={}
        fields=proposed.get(side,{})
        if not isinstance(fields,dict): fields={}
        for field in FIELDS:
            refs=fields.get(field,[])
            valid=[]; invalid=[]
            if not isinstance(refs,list): refs=[refs]
            for ref in refs:
                if not isinstance(ref,dict): invalid.append(ref); continue
                sid=ref.get('source_id'); quote=ref.get('quote'); text=sources[side].get(sid)
                present=isinstance(quote,str) and bool(quote) and isinstance(text,str) and quote in text
                if present and side=='old':
                    present=any(e.get('source_id')==sid and quote in e.get('quote','') for e in fact.get('evidence',[]))
                if present: valid.append(deepcopy(ref))
                else: invalid.append(deepcopy(ref))
            status='invalid' if invalid else ('literal_quote_verified' if valid else 'missing')
            out[side][field]={'status':status,'refs':valid,'invalid_refs':invalid,'semantic_verified':False}
            if invalid: issues.append({'code':'field_evidence_invalid','side':side,'field':field,'invalid_refs':invalid})
    return out,issues


def assess_exclusivity(extracted, request, fact):
    """Keep an attributed exclusivity proposal separate from semantic truth."""
    proposal=extracted.get('exclusivity')
    default={'candidate':'unknown','semantic_verified':False,'evidence_status':'not_provided'}
    if proposal is None: return default,[]
    if not isinstance(proposal,dict):
        return default,[{'code':'exclusivity_evidence_invalid','reason':'invalid proposal'}]
    label=proposal.get('candidate','unknown'); refs=proposal.get('evidence',[])
    if label not in ('mutually_exclusive','not_exclusive','unknown') or not isinstance(refs,list):
        return default,[{'code':'exclusivity_evidence_invalid','reason':'invalid label or references'}]
    sources={s['source_id']:s['text'] for s in request.get('source_context',[])+request.get('new_evidence',[])}
    sources[request['split_result']['memory_id']]=request['split_result']['memory_text']
    invalid=[]
    for ref in refs:
        sid=ref.get('source_id') if isinstance(ref,dict) else None
        quote=ref.get('quote') if isinstance(ref,dict) else None
        text=sources.get(sid)
        if not isinstance(quote,str) or not quote or not isinstance(text,str) or quote not in text:
            invalid.append(deepcopy(ref))
        elif sid not in {x['source_id'] for x in request.get('new_evidence',[])} and not any(e.get('source_id')==sid and quote in e.get('quote','') for e in fact.get('evidence',[])):
            invalid.append(deepcopy(ref))
    if invalid or (label!='unknown' and not refs):
        return {**default,'raw_candidate':deepcopy(proposal),'evidence_status':'invalid'},[{'code':'exclusivity_evidence_invalid','invalid_refs':invalid}]
    return {'candidate':label,'semantic_verified':False,'evidence_status':'literal_quote_verified' if refs else 'not_provided',
            'reason':proposal.get('reason'), 'evidence_refs':deepcopy(refs)},[]
