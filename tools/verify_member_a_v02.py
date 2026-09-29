"""Read-only snapshot/integration verification. No rebuild, labels or GPU."""
from pathlib import Path
import json
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT,file_hash,read_json,read_jsonl,write_json
from kingscode.retrieval import Retriever,retrieve
from kingscode.benchmark_v2 import check


def verify():
    official={}
    for line in (ROOT/'docs/OFFICIAL_SHA256.txt').read_text(encoding='utf-8-sig').splitlines():
        if line.strip():
            expected,name=line.split('  ',1)
            if file_hash(ROOT/name)!=expected:raise ValueError('Official changed: '+name)
            official[name]=expected
    # B-owned paths (kingscode/reasoning, config/reasoning.json) are excluded: B's
    # own merged work legitimately changes them and B verifies them with its tests.
    # Everything official/historical stays pinned to the 60ebf7e GPU freeze.
    source_diff=subprocess.check_output(['git','diff','60ebf7e','--',
                                         'config/models.lock.json','config/neural.json','data','schema','scripts','benchmarks/kingscode_ir',
                                         'tools/gpu_search_v2_dev.py','tools/gpu_search_v2_validation.py','reports/gpu_freeze_4090',
                                         'reports/benchmark/search_v2','reports/benchmark/search_v2_validation'],cwd=ROOT)
    if source_diff:raise ValueError('Protected B/official/historical GPU/benchmark/model files changed')
    snapshot=read_json(ROOT/'corpus/manifest.json')
    actual={}
    for name,expected in {**snapshot['hashes'],'index/bm25.json':snapshot['bm25_sha256']}.items():
        actual[name]=file_hash(ROOT/'corpus'/name)
        if actual[name]!=expected:raise ValueError('Historical corpus changed: '+name)
    # Recheck every acquired raw/clean body, not only the passage manifest.
    for d in snapshot['documentos']:
        for key,hash_key in (('raw_path','source_sha256'),('clean_path','sha256')):
            if file_hash(ROOT/d[key])!=d[hash_key]:raise ValueError('Trace changed: '+d['doc_id'])
    query='Ley 1564 de 2012 artículo 90'
    legacy=Retriever()
    explicit_legacy=Retriever(exact_locator=False)
    legacy_rows=legacy.retrieve(query,8,'off')
    if legacy_rows!=explicit_legacy.retrieve(query,8,'off'):raise ValueError('Legacy mismatch')
    public=retrieve(query,8,'off')
    replay=retrieve(query,8,'off')
    if public!=replay:raise ValueError('Public locator replay differs')
    if not public or not all('locator' in p for p in public):raise ValueError('Public locator profile missing')
    required={'passage_id','doc_id','text','norm_name','source_url','hierarchy_path','graph_node_ids','scores'}
    if any(not required<=p.keys() for p in public):raise ValueError('A/B passage contract incomplete')
    v02=read_json(ROOT/'corpora/corpus-v0.2/manifest.json')
    for name,expected in v02['hashes'].items():
        if file_hash(ROOT/'corpora/corpus-v0.2'/name)!=expected:raise ValueError('v0.2 artifact mismatch: '+name)
    result={'status':'PASS','scope':'CPU read-only snapshot/API verification; not GPU metric replay',
            'official_files_unchanged':len(official),'v01_raw_clean_files_unchanged':2*len(snapshot['documentos']),
            'v01_core_hashes':actual,'protected_git_diff_empty':True,'legacy_compatible':True,
            'public_retrieve_deterministic':True,'public_passage_contract':sorted(required),
            'v02_hashes_verified':len(v02['hashes']),'benchmark_v2':check(),
            'gpu_executed':False,'holdout_executed':False,'old_rebuild_verifier':'Not run: rebuild/official-50 replay are outside this phase.'}
    write_json(ROOT/'reports/member_a_v02/verification.json',result)
    return result


if __name__=='__main__':print(json.dumps(verify(),ensure_ascii=False,indent=2))
