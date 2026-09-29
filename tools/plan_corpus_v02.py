"""Reproducible acquisition priorities from source inventory/graph, never gold."""
from collections import Counter, defaultdict
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT, file_hash, read_json, read_jsonl, write_json
from kingscode.legal_locator import LegalLocator, LegalReference


def plan(corpus=ROOT / "corpus"):
    manifest=read_json(corpus / "manifest.json")
    backlog=read_json(ROOT / "reports/acquisition_backlog_v06.json")
    targets=read_json(ROOT / "reports/member_a_v02/target_review_v07.json")["targets"]
    nodes=read_jsonl(corpus / "graph/nodes.jsonl")
    edges=read_jsonl(corpus / "graph/edges.jsonl")
    incoming, outgoing, evidence = Counter(), Counter(), defaultdict(set)
    for e in edges:
        incoming[e['target']]+=1;outgoing[e['source']]+=1
        evidence[e['target']].add(e['evidence_passage_id'])
        evidence[e['source']].add(e['evidence_passage_id'])
    external=[n for n in nodes if not n.get('resolved',False) or n['node_id'].startswith('external:')]
    document_locator=LegalLocator([dict(d,passage_id=d['doc_id']) for d in manifest['documentos']])
    ranked=[]
    for n in external:
        ident=n['node_id']
        existing=list(document_locator.resolve_documents(LegalReference(ident.removeprefix('external:'))))
        ranked.append({'node_id':ident,'label':n.get('label'),'priority_band':'P2',
                       'incoming_edges':incoming[ident],'outgoing_edges':outgoing[ident],
                       'distinct_evidence_passages':len(evidence[ident]),
                       'evidence_passage_ids':sorted(evidence[ident])[:10],
                       'official_resolution':'unverified','legal_authority_score':None,
                       'existing_canonical_documents':existing,
                       'next_action':'verify_and_link_existing_document_in_v02' if existing else 'resolve_official_primary_before_acquisition',
                       'note':'Citation frequency is an acquisition signal, not legal authority. Verify relation subject; v0.7 audit found attachment defects.'})
    ranked.sort(key=lambda x:(-x['incoming_edges'],-x['distinct_evidence_passages'],x['node_id']))
    result={'version':'corpus-v0.2-acquisition-plan-v1','seed':0,'snapshot_sha256':file_hash(corpus/'manifest.json'),
            'ordering':'P0 existing targets; P1 court gaps; P2 descending incoming edges, distinct evidence passages, node ID. No arbitrary weighted score.',
            'historical_backlog_counts':backlog['counts'],'historical_backlog_total':len(backlog['targets']),
            'P0_targets':targets,'P1_court_gaps':[
              {'court':'Corte Suprema Civil','basis':'SC targets in existing backlog; exact official landings found','next':'Resolve primary judgment PDF, do not ingest a vote clarification instead.'},
              {'court':'Corte Suprema Laboral','basis':'SL targets in existing backlog','next':'Acquire exact SL648-2018; distinguish fichas/edictos from full judgments.'},
              {'court':'Corte Suprema Penal','basis':'SP targets in existing backlog','next':'Initial exact primary PDFs in config/corpus_v02_sources.json.'},
              {'court':'Consejo de Estado','basis':'No decision represented in v0.1 inventory; administrative/tax coverage gap','official_discovery':'https://www.consejodeestado.gov.co/','next':'Curator chooses unification/cited decisions tied to coverage or v2 human review; no random bulk acquisition.','status':'SAFE_DEFER exact identifiers and primary sources still required'}],
            'P2_external_node_count':len(external),'P2_ranked_nodes':ranked,
            'P3_temporal_fields':['publication_date','effective_from','effective_to','modified_by','repealed_by','status_source','historical_version'],
            'P3_rule':'Null/unknown unless official source proves the exact assertion; a mention of amendment is not enough.',
            'P4_specialized_sources':{'administrative':['Consejo de Estado','Funcion Publica','SUIN'],'tax':['DIAN','Consejo de Estado tributario'],'labor':['CSJ Laboral','MinTrabajo'],'criminal':['CSJ Penal','official criminal procedure legislation'],'civil_family_commercial':['CSJ Civil','Corte Constitucional','Supersociedades'],'markets_data_IP':['SIC','Comunidad Andina','Superfinanciera when relevant']},
            'P5_international':'Selective Colombian relevance only: CAN, ILO ratified by Colombia, or instruments referenced in Colombian decisions. Verify applicability/ratification; no generic international corpus.',
            'deferred_experiments':['Qwen retrieval 4B','BGE-M3 multifunction','ALIA retrieval','hard-negative reranker tuning','QLoRA','JEV','free multi-agent systems','decoder tuning'],
            'gpu_work':False,'v01_mutation':False}
    write_json(ROOT/'reports/member_a_v02/corpus_v02_acquisition_plan.json',result)
    return {'status':'planned','targets':len(targets),'external_nodes':len(external),'top_external_nodes':[r['node_id'] for r in ranked[:10]]}


if __name__=='__main__':print(json.dumps(plan(),ensure_ascii=False,indent=2))
