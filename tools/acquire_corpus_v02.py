"""Acquire the fixed initial v0.2 batch; never read or write the v0.1 corpus.

The result is a provisional engineering corpus, not a competitive freeze.
Each source needs human structural/legal review before acceptance.
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT, file_hash, indexable, normalize, read_json, write_json, write_jsonl
from kingscode.acquisition import fetch, soup_from_bytes
from kingscode.corpus import parse_document, blocks_from_pdf
from kingscode.retrieval import BM25Index

OUT=ROOT/'corpora/corpus-v0.2'


def source_identity(data, source):
    text=' '.join(blocks_from_pdf(data)[0]) if data.startswith(b'%PDF-') else soup_from_bytes(data).get_text(' ',strip=True)
    flat=re.sub(r'\s+','',normalize(text[:18000]))
    kind,number,year=source['canonical_body']
    if kind=='jurisprudencia':
        m=re.fullmatch(r'([A-Za-z]+)-?(\d+)',number)
        pattern=m[1].lower()+r'-?0*'+str(int(m[2]))+r'(?:-|de|/)'+str(year)
    else:
        pattern=kind+r'0*'+str(int(number))+r'(?:de|/)'+str(year)
    if not re.search(pattern,flat):raise ValueError('Exact primary identity not found near source heading; no substitution')
    return {'method':'exact_number_year_primary_text_heading','pattern':pattern,'matched':True}


def acquire():
    if OUT.resolve()==(ROOT/'corpus').resolve():raise ValueError('v0.1 mutation forbidden')
    if (OUT/'manifest.json').exists():raise FileExistsError('Initial v0.2 snapshot exists; review before extending, no overwrite')
    records,all_passages,all_nodes,all_edges,review_edges=[],[],[],[],[]
    for s in read_json(ROOT/'config/corpus_v02_sources.json')['sources']:
        record=dict(s,status='pending')
        suffix='.pdf' if '.pdf' in s['url'].lower() else '.html'
        path=OUT/'raw'/(s['doc_id']+suffix)
        try:
            transport=fetch(s['url'],path)
            record.update(**transport,status='downloaded_not_accepted',raw_path=path.relative_to(ROOT).as_posix())
            data=path.read_bytes()
            identity=source_identity(data,s)
            kind,number,year=s['canonical_body']
            area='Derecho laboral' if number.startswith('SL') else 'Derecho penal' if number.startswith('SP') else 'Derecho administrativo'
            meta={**s,**transport,'norm_number':number,'year':int(year),'areas':[area],
                  'court':'Corte Suprema de Justicia' if s['source_type']=='decision' else None}
            clean,ps,nodes,edges,info=parse_document(meta,data)
            clean_path=OUT/'clean'/(s['doc_id']+'.txt');clean_path.parent.mkdir(parents=True,exist_ok=True)
            clean_path.write_text(clean,encoding='utf-8',newline='\n')
            for p in ps:
                p['review_status']='provisional_source_verified_structure_pending'
                p['corpus_version']='corpus-v0.2-initial'
            record.update(**transport,status='parsed_provisional',identity=identity,raw_path=path.relative_to(ROOT).as_posix(),
                          clean_path=clean_path.relative_to(ROOT).as_posix(),clean_sha256=file_hash(clean_path),
                          passages=len(ps),review_status='human_structure_and_scope_review_pending',layout_review='not_performed',
                          temporal_status='unknown',parser='legal-blocks-1.2 reused; known defects tracked separately',
                          institution=meta['court'] or 'Funcion Publica',areas=[area])
            all_passages.extend(ps);all_nodes.extend(nodes)
            # The audit found wrong subjects on semantic edges. Keep proposed
            # relations in an explicit review queue, outside active adjacency.
            all_edges.extend(e for e in edges if e['relation']=='CONTIENE')
            review_edges.extend(dict(e,status='unverified_semantic_relation') for e in edges if e['relation']!='CONTIENE')
        except Exception as exc:
            record.update(status='blocked',error_type=type(exc).__name__,error=str(exc),action='Inspect official source/format; never disable TLS or replace identity')
            if path.exists():record.update(raw_path=path.relative_to(ROOT).as_posix(),raw_sha256=file_hash(path))
        records.append(record)
        print(s['doc_id'],record['status'],flush=True)
    write_jsonl(OUT/'passages.jsonl',all_passages)
    write_jsonl(OUT/'graph/nodes.jsonl',all_nodes)
    write_jsonl(OUT/'graph/edges.jsonl',all_edges)
    write_jsonl(OUT/'graph/review_queue.jsonl',review_edges)
    BM25Index([p for p in all_passages if indexable(p)]).save(OUT/'index/bm25.json',file_hash(OUT/'passages.jsonl'))
    manifest={'version':'corpus-v0.2-initial','status':'provisional_not_competitive_freeze','documents':records,
              'n_documents':sum(r['status']=='parsed_provisional' for r in records),'n_passages':len(all_passages),
              'n_indexed':sum(indexable(p) for p in all_passages),'n_nodes':len(all_nodes),'n_edges':len(all_edges),
              'semantic_edges_pending_review':len(review_edges),'dense_built':False,'v01_included':False,
              'snapshot_policy':'Separate bounded additions only; v0.1 is not copied/rebuilt here.',
              'hashes':{p.relative_to(OUT).as_posix():file_hash(p) for p in sorted(OUT.rglob('*')) if p.is_file()}}
    write_json(OUT/'manifest.json',manifest)
    write_json(ROOT/'reports/member_a_v02/acquisition_result.json',manifest)
    return {'status':manifest['status'],'documents':manifest['n_documents'],'passages':len(all_passages),'blocked':[r['doc_id'] for r in records if r['status']=='blocked']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--initial-batch',action='store_true',required=True);p.parse_args()
    print(json.dumps(acquire(),ensure_ascii=False,indent=2))
