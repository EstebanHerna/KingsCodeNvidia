"""Verify KC-COL-IR v0.1 source correction, frozen sampling and evidence gates."""
from __future__ import annotations
import hashlib, json, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks/kc_col_ir_v0.1"
RAW = ROOT / "tmp/kc_col_ir_v0.1/raw/jep-primary"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def verify() -> dict:
    manifest=json.loads((BENCH/"manifest.json").read_text(encoding="utf-8"))
    sources=read_jsonl(BENCH/"source_manifest.jsonl")
    questions=read_jsonl(BENCH/"questions/dev.jsonl")
    legacy=read_jsonl(BENCH/"questions/reproducibility_externado_2011.jsonl")
    gold=read_jsonl(BENCH/"gold/dev.jsonl")
    dispositions=read_jsonl(BENCH/"review/jep_2026_dispositions.jsonl")
    expansion_meta=json.loads((BENCH/"review/expansion_batch_1.json").read_text(encoding="utf-8"))
    expansion_queue=read_jsonl(BENCH/"review/expansion_batch_1_queue.jsonl")
    expansion_questions=read_jsonl(BENCH/"review/expansion_batch_1_questions.jsonl")
    expansion_dispositions=read_jsonl(BENCH/"review/expansion_batch_1_dispositions.jsonl")
    acquisitions=read_jsonl(BENCH/"review/primary_source_acquisitions.jsonl")
    sample=json.loads((BENCH/"sampling_manifest.json").read_text(encoding="utf-8"))
    old_sample=json.loads((BENCH/"sampling_manifest_externado_2011.json").read_text(encoding="utf-8"))
    required={"source_id","institution","institution_family","title","year","source_type","official_url","final_url","host","sha256","bytes_verified","question_count","question_format","answer_key_available","area","intended_role","split","access_status","copyright_status","exposure_status"}
    if any(required-row.keys() for row in sources): raise ValueError("Source manifest has missing contract fields")
    source_ids=[r["source_id"] for r in sources]
    if len(source_ids)!=len(set(source_ids)): raise ValueError("Duplicate source_id")
    allowed_types={"INSTITUTIONAL_QUESTION_BANK","INSTITUTIONAL_ASSESSMENT","OFFICIAL_EXAM","TOPIC_GUIDE","METHODOLOGY_GUIDE","OFFICIAL_ACADEMIC_LEGAL_COMPETITION","UNIVERSITY_MOOT_CLARIFICATION_RESPONSES"}
    if any(r["source_type"] not in allowed_types for r in sources): raise ValueError("Unknown source type")
    allowed={"universidad_libre_preparatorios":{"VALIDATION","VALIDATION_CANDIDATE","COVERAGE_ONLY"},"externado_preparatorios":{"REPRODUCIBILITY_ONLY","COVERAGE_ONLY"},"jep_concurso_universitario_2026":{"DEV_CANDIDATE","PROVENANCE_ONLY"},"jep_concurso_universitario_2025":{"PROVENANCE_ONLY"},"javeriana_moot_seguros_2026":{"VALIDATION_CANDIDATE"},"externado_asobancaria_moot_financiero_2025":{"SEALED_FUTURE"}}
    for r in sources:
        if r["institution_family"] in allowed and r["split"] not in allowed[r["institution_family"]]: raise ValueError(f"Invalid split for {r['institution_family']}")
        if r["bytes_verified"] and not r["sha256"]: raise ValueError("Verified bytes missing SHA-256")
    if sha(BENCH/"source_manifest.jsonl")!=manifest["source_manifest_sha256"]: raise ValueError("Source manifest hash mismatch")
    if sha(BENCH/"questions/dev.jsonl")!=manifest["question_manifest_sha256"]: raise ValueError("Question manifest hash mismatch")
    if sha(BENCH/"sampling_manifest.json")!=manifest["sampling_manifest_sha256"]: raise ValueError("Sampling manifest hash mismatch")
    if sha(BENCH/"questions/reproducibility_externado_2011.jsonl")!=manifest["legacy_reproducibility_questions_sha256"]: raise ValueError("Legacy reproducibility question hash mismatch")
    if sha(BENCH/"sampling_manifest_externado_2011.json")!=manifest["legacy_reproducibility_sampling_sha256"]: raise ValueError("Legacy sampling manifest hash mismatch")
    if len(questions)!=30 or len(dispositions)!=30 or len(legacy)!=old_sample["selected_count"]: raise ValueError("Unexpected frozen candidate or reproducibility queue size")
    qids=[q["question_id"] for q in questions]; dids=[d["question_id"] for d in dispositions]
    if len(qids)!=len(set(qids)) or len(dids)!=len(set(dids)) or set(qids)!=set(dids): raise ValueError("Question/disposition identity mismatch")
    bynum={str(q["source_item_number"]):q for q in questions}
    if len(bynum)!=30: raise ValueError("Duplicate source item number in frozen batch")
    if sample.get("selection_recomputed_after_review") is not False or sample.get("source_year")!=2026 or sample.get("source_family")!="jep_concurso_universitario_2026": raise ValueError("Current source metadata or frozen selection status invalid")
    old_basis=sample.get("selection_provenance",{})
    if old_basis.get("original_source_family")!="jep_concurso_universitario_2025" or old_basis.get("original_source_document")!="JEP-CUJ-2025-PREGUNTAS" or old_basis.get("original_selection_sha256")!=sample.get("selection_sha256"): raise ValueError("Original deterministic selection basis not preserved")
    if old_basis.get("original_selected_item_numbers")!=sample.get("selected_item_numbers"): raise ValueError("Frozen item-number list changed")
    if {q["source_family"] for q in questions}!={"jep_concurso_universitario_2026"}: raise ValueError("DEV candidate family is not corrected to CUJ 2026")
    if any(q["question_id"]!=f"JEP-CUJ-2026-Q{int(q['source_item_number']):03d}" or q.get("legacy_question_id")!=f"JEP-CUJ-2025-Q{int(q['source_item_number']):03d}" for q in questions): raise ValueError("Question ID migration/legacy trace is invalid")
    if {q["source_id"] for q in questions}!={"JEP-CUJ-2026-PREGUNTAS"} or any(q["source_year"]!=2026 for q in questions): raise ValueError("Candidate source metadata is not CUJ 2026")
    if any(q.get("question_text_sha256")!=q.get("source_question_sha256") for q in questions): raise ValueError("Question text hash mismatch in candidate metadata")
    if any("proposed_minimal_evidence_sets" in q for q in questions): raise ValueError("Ambiguous candidate evidence-set field; use external/corpus split")
    if any("minimal_evidence_sets" in d for d in dispositions): raise ValueError("Ambiguous disposition evidence-set field; use external/corpus split")
    if len(gold)!=manifest["counts"].get("accepted_retrieval_gold"): raise ValueError("Accepted-gold count mismatch")
    gold_ids=[g.get("question_id") for g in gold]
    if len(gold_ids)!=len(set(gold_ids)) or not set(gold_ids)<=set(qids)|{r["question_id"] for r in expansion_questions}: raise ValueError("Gold IDs must be unique frozen candidates")
    disp_by_id={d["question_id"]:d for d in dispositions+expansion_dispositions}; gold_by_id={g["question_id"]:g for g in gold}
    statuses={"ACCEPTED_RETRIEVAL_GOLD","REJECTED_NOT_RETRIEVAL","REJECTED_INSUFFICIENT_AUTHORITATIVE_ANSWER","PENDING_PRIMARY_EVIDENCE","PENDING_TEMPORAL_REVIEW"}
    if any(d.get("review_status") not in statuses for d in dispositions): raise ValueError("Unknown review status")
    question_by_id={q["question_id"]:q for q in questions+expansion_questions}
    for d in dispositions:
        q=question_by_id[d["question_id"]]
        if q.get("review_status")!=d.get("review_status") or q.get("temporal_review_status")!=d.get("temporal_review_status"):
            raise ValueError("Question candidate review status differs from disposition ledger")
        if d.get("review_status")=="ACCEPTED_RETRIEVAL_GOLD" and q.get("temporal_review_status") not in {"CURRENTLY_SUPPORTABLE","HISTORICAL_ONLY","NOT_APPLICABLE"}:
            raise ValueError("Accepted candidate has unresolved temporal status")
        if d.get("retrieval_performance_used") is not False or "retrieval_results" in d or "rankings" in d: raise ValueError("Retrieval output contaminated source review")
        if d["review_status"]=="ACCEPTED_RETRIEVAL_GOLD" and d["question_id"] not in gold_by_id: raise ValueError("Accepted disposition missing gold record")
        if d["question_id"] in gold_by_id and d["review_status"]!="ACCEPTED_RETRIEVAL_GOLD": raise ValueError("Gold/disposition disagreement")
    for qid,g in gold_by_id.items():
        if g.get("review_status")!="ACCEPTED_RETRIEVAL_GOLD" or g.get("temporal_review_status") not in {"CURRENTLY_SUPPORTABLE","HISTORICAL_ONLY","NOT_APPLICABLE"}: raise ValueError(f"Gold status/temporal review invalid: {qid}")
        units=g.get("external_evidence_units",[]); unit_ids={u.get("external_evidence_unit_id") for u in units}
        if not unit_ids or any(not u.get("source_id") or not u.get("sha256") or not u.get("source_url") or not u.get("page") for u in units): raise ValueError(f"External evidence unit incomplete: {qid}")
        if any(not s or not set(s)<=unit_ids for s in g.get("external_minimal_evidence_sets",[])): raise ValueError(f"External minimal evidence set invalid: {qid}")
        if not g.get("external_minimal_evidence_sets"): raise ValueError(f"No external gold evidence: {qid}")
        if g.get("corpus_coverage") not in {"COMPLETE","PARTIAL","MISSING","AMBIGUOUS"}: raise ValueError(f"Coverage status invalid: {qid}")
        if g["corpus_coverage"]=="MISSING" and (g.get("corpus_minimal_evidence_sets") or g.get("gold_document_ids")): raise ValueError(f"Missing corpus coverage claims corpus IDs: {qid}")
        if g.get("legacy_question_id")!=disp_by_id[qid].get("legacy_question_id"): raise ValueError(f"Legacy question mapping mismatch: {qid}")
    counts={s:sum(d["review_status"]==s for d in dispositions) for s in statuses}
    expected_ids={"JEP-CUJ-2026-Q"+n.zfill(3) for n in ("9","12","13","25","30","31","37","43","45","49")}
    if set(gold_ids)!=expected_ids: raise ValueError("Accepted-gold packet set differs from the reviewed primary set")
    if counts["ACCEPTED_RETRIEVAL_GOLD"]!=9: raise ValueError(f"Unexpected original-batch accepted gold count: {counts}")
    if expansion_meta.get("status")!="FROZEN_BEFORE_CONTENT_REVIEW" or expansion_meta.get("selection_before_content_review") is not True or expansion_meta.get("expansion_content_read_before_freeze") is not False or expansion_meta.get("retrieval_executed") is not False: raise ValueError("Expansion was not verifiably frozen before content review")
    if len(expansion_queue)!=10 or len(expansion_questions)!=10 or len(expansion_dispositions)!=10: raise ValueError("Expansion batch must have exactly ten frozen, reviewed items")
    expnums=expansion_meta["expansion_item_numbers"]
    expansion_pool=read_jsonl(ROOT/"tmp/kc_col_ir_v0.1/pool/jep_cuj_2026_full_pool.jsonl")
    expansion_ranked=sorted((hashlib.sha256((r["legacy_source_family"]+r["legacy_source_document"]+r["source_item_number"]).encode()).hexdigest(),r) for r in expansion_pool)
    deterministic_next=[str(r["source_item_number"]) for _,r in expansion_ranked[30:40]]
    selection_digest=hashlib.sha256(json.dumps(expnums,ensure_ascii=False,separators=(",",":")).encode("utf-8")).hexdigest()
    if expansion_meta.get("pool_sha256")!=sample.get("pool_artifact_sha256") or expansion_meta.get("pool_size")!=62 or expnums!=deterministic_next or expansion_meta.get("original_selected_item_numbers")!=sample.get("selected_item_numbers") or expansion_meta.get("combined_reviewed_candidate_item_numbers")!=sample.get("selected_item_numbers")+expnums or expansion_meta.get("expansion_selection_sha256")!=selection_digest: raise ValueError("Expansion deterministic pre-review selection proof mismatch")
    if len(expnums)!=10 or set(expnums)&set(sample["selected_item_numbers"]): raise ValueError("Expansion overlaps or changes the original 30")
    if [r["source_item_number"] for r in expansion_queue]!=expnums or [r["source_item_number"] for r in expansion_questions]!=expnums: raise ValueError("Expansion queue order differs from frozen manifest")
    if [r["question_id"] for r in expansion_dispositions]!=[r["question_id"] for r in expansion_questions]: raise ValueError("Expansion disposition coverage/order mismatch")
    qpool={str(r["source_item_number"]):r for r in read_jsonl(ROOT/"tmp/kc_col_ir_v0.1/pool/jep_cuj_2026_full_pool.jsonl")}
    for row, disp in zip(expansion_questions, expansion_dispositions):
        official=qpool[row["source_item_number"]]
        qhash=hashlib.sha256(official["question_text"].encode("utf-8")).hexdigest()
        ahash=hashlib.sha256(official["official_response"].encode("utf-8")).hexdigest()
        if row["question_text_sha256"]!=qhash or row["official_response_sha256"]!=ahash: raise ValueError(f"Expansion source hash mismatch: {row['question_id']}")
        if disp["review_status"]!=row["review_status"] or disp.get("retrieval_performance_used") is not False: raise ValueError(f"Expansion disposition inconsistency: {row['question_id']}")
    exp_counts={s:sum(r["review_status"]==s for r in expansion_dispositions) for s in statuses}
    if exp_counts["ACCEPTED_RETRIEVAL_GOLD"]!=1 or len(dispositions)+len(expansion_dispositions)!=40: raise ValueError("Expansion review counts do not reconcile")
    if any(not a.get("source_id") or not a.get("sha256") or len(a["sha256"])!=64 or not a.get("source_url") or a.get("bytes") is None or not a.get("signature") or not a.get("final_url") or not a.get("retrieved_at_utc") or not a.get("document_identity") for a in acquisitions): raise ValueError("Acquired source provenance incomplete")
    acq_ids=[a["source_id"] for a in acquisitions]
    if len(acq_ids)!=len(set(acq_ids)): raise ValueError("Duplicate acquired source identity")
    archive=next(a for a in acquisitions if a["source_id"]=="JEP-CUJ-2026-EXPEDIENTE-ZIP")
    archive_path=RAW/"expediente_concurso_jep_2026.zip"
    if not archive_path.exists() or sha(archive_path)!=archive["sha256"] or archive["sha256"]!="3f9dc1765e8ea18588c13a48e1785b506f6a0c06eef3743057e2d34097d9b101" or archive["bytes"]!=157859322: raise ValueError("CUJ 2026 archive identity/hash/size mismatch")
    member_manifest=json.loads((RAW/"expediente_2026_acquisition.json").read_text(encoding="utf-8"))
    if member_manifest.get("member_count")!=18 or member_manifest.get("zip_integrity")!="testzip returned None": raise ValueError("CUJ 2026 ZIP integrity record invalid")
    members=[a for a in acquisitions if a.get("parent_archive_source_id")==archive["source_id"]]
    if len(members)!=18: raise ValueError("Expected all 18 ZIP members in acquisition ledger")
    archived={a.get("member_index"):a for a in members}
    if set(archived)!=set(range(1,19)): raise ValueError("ZIP member inventory indices incomplete")
    with zipfile.ZipFile(archive_path) as zf:
        if zf.testzip() is not None or len(zf.infolist())!=18: raise ValueError("CUJ 2026 ZIP CRC/member-count check failed")
        for m in member_manifest["members"]:
            entry=archived[m["member_index"]]
            if entry["sha256"]!=m["sha256"] or entry["bytes"]!=m["uncompressed_bytes"] or entry["source_member_name"]!=m["archive_member_name_utf8_recovered"]: raise ValueError("2026 member ledger differs from archive manifest")
            data=zf.read(zf.infolist()[m["member_index"]-1])
            if hashlib.sha256(data).hexdigest()!=m["sha256"]: raise ValueError(f"ZIP member hash mismatch at {m['member_index']}")
    old_archive=next(a for a in acquisitions if a["source_id"]=="JEP-CUJ-2025-EXPEDIENTE-ZIP")
    old_members=[a for a in acquisitions if a.get("parent_archive_source_id")==old_archive["source_id"]]
    if len(old_members)!=22 or old_archive.get("review_use")!="NOT_SOURCE_FOR_CUJ_2026_GOLD" or any(a.get("review_use")!="NOT_SOURCE_FOR_CUJ_2026_GOLD" for a in old_members): raise ValueError("2025 packet not correctly isolated as provenance only")
    externado=next(s for s in sources if s["source_id"]=="EXTERNADO-PRIVADO-I-PROCESAL-CIVIL-2011")
    if externado["split"]!="REPRODUCIBILITY_ONLY" or externado["exposure_status"]!="ACQUIRED_HASHED_MECHANICAL_POOL_REPRODUCIBILITY_ONLY": raise ValueError("Externado must stay reproducibility-only")
    pool_path=ROOT/"tmp/kc_col_ir_v0.1/pool/jep_cuj_2026_full_pool.jsonl"
    if not pool_path.exists() or sha(pool_path)!=sample["pool_artifact_sha256"]: raise ValueError("Frozen JEP pool missing or hash mismatch")
    pool=read_jsonl(pool_path)
    if len(pool)!=62 or any(r["source_family"]!="jep_concurso_universitario_2026" or r["source_year"]!=2026 or r["legacy_source_family"]!="jep_concurso_universitario_2025" for r in pool): raise ValueError("JEP full pool metadata correction invalid")
    ranked=sorted((hashlib.sha256((r["legacy_source_family"]+r["legacy_source_document"]+r["source_item_number"]).encode()).hexdigest(),r) for r in pool)
    expected={str(int(r["source_item_number"])) for _,r in ranked[:30]}
    if expected!=set(bynum) or expected!=set(sample["selected_item_numbers"]): raise ValueError("Original deterministic selection membership changed")
    old_path=ROOT/"tmp/kc_col_ir_v0.1/pool/externado_procesal_full_pool.jsonl"
    if not old_path.exists() or sha(old_path)!=old_sample["pool_artifact_sha256"]: raise ValueError("Externado reproducibility pool missing or changed")
    oldrows=read_jsonl(old_path); oldrank=sorted((hashlib.sha256((r["source_family"]+r["source_document"]+r["source_item_number"]).encode()).hexdigest(),r) for r in oldrows)
    old_expected={"EXTERNADO-PRIVADO-I-PROCESAL-CIVIL-2011-Q"+r["source_item_number"].zfill(3) for _,r in oldrank[:30]}
    if old_expected!={r["question_id"] for r in legacy}: raise ValueError("Externado reproducibility sample changed")
    controlled=read_jsonl(BENCH/"review/controlled_cuj2026_v1_coverage.jsonl")
    competitive=read_jsonl(BENCH/"review/competitive_corpus_v01_coverage.jsonl")
    if len(controlled)!=10 or len(competitive)!=10 or any(r["controlled_corpus_coverage"]!="COMPLETE" for r in controlled) or any(r["competitive_corpus_coverage"]!="MISSING" for r in competitive): raise ValueError("Dual corpus coverage profile counts are invalid")
    if any(r["profile_id"]!="KC-COL-IR-CUJ2026-CONTROLLED-v1" for r in controlled): raise ValueError("Controlled coverage profile identity mismatch")
    controlled_docs=read_jsonl(BENCH/"review/controlled_cuj2026_v1_documents.jsonl")
    valid_docs={d["doc_id"] for d in controlled_docs}
    valid_pages={f"CUJ2026-P{d['member_index']:02d}-{p:04d}-{d['source_member_sha256'][:12]}" for d in controlled_docs for p in range(1,d["page_count"]+1) if p not in d.get("empty_pages",[])}
    mappings=read_jsonl(BENCH/"review/controlled_cuj2026_v1_mapping.jsonl")
    expected_mapping_keys={(g["question_id"],u["external_evidence_unit_id"]) for g in gold for u in g["external_evidence_units"]}
    if {(r["question_id"],r["external_evidence_unit_id"]) for r in mappings}!=expected_mapping_keys: raise ValueError("Controlled mapping does not cover every external evidence unit exactly once")
    if {r["question_id"] for r in controlled}!={g["question_id"] for g in gold} or {r["question_id"] for r in competitive}!={g["question_id"] for g in gold}: raise ValueError("Dual coverage ledger question IDs differ from accepted gold")
    if any(r["external_evidence_unit_id"] in set(r["controlled_passage_ids"]) for r in mappings): raise ValueError("External evidence ID masquerades as a passage ID")
    if any(r["controlled_document_id"] not in valid_docs or not set(r["controlled_passage_ids"])<=valid_pages for r in mappings): raise ValueError("Controlled mapping references nonexistent document/page")
    ncomplete=sum(g["corpus_coverage"]=="COMPLETE" for g in gold)
    if manifest["gold_gate"]["minimum_accepted_retrieval_gold"]!=10 or manifest["gold_gate"]["unlocked"]!=(len(gold)>=10): raise ValueError("Gold gate state inconsistent")
    if manifest["ranking_gate"]["minimum_complete_corpus_gold"]!=10 or manifest["ranking_gate"]["ranking_n"]!=ncomplete or manifest["ranking_gate"]["unlocked"]!=(ncomplete>=10): raise ValueError("Ranking gate state inconsistent")
    if manifest["cuda_ready"] or manifest["baseline_gate"]["unlocked"]: raise ValueError("CUDA/ranking baseline must remain locked")
    if manifest["validation_exposure"]["parsed"] or manifest["validation_exposure"]["retrieval_performance_inspected"]: raise ValueError("Javeriana validation must remain unparsed/uninspected")
    return {"status":"PASS","sources":len(sources),"jep_pool":len(pool),"primary_dev_annotation_batch":len(questions),"expansion_batch_1":len(expansion_questions),"externado_reproducibility_batch":len(legacy),"review_dispositions":counts,"expansion_dispositions":exp_counts,"acquired_source_artifacts":len(acquisitions),"expediente_2026_members":len(members),"accepted_retrieval_gold":len(gold),"competitive_corpus_coverage_counts":{s:sum(r["competitive_corpus_coverage"]==s for r in competitive) for s in ("COMPLETE","PARTIAL","MISSING","AMBIGUOUS")},"controlled_corpus_coverage_counts":{s:sum(r["controlled_corpus_coverage"]==s for r in controlled) for s in ("COMPLETE","PARTIAL","MISSING","AMBIGUOUS")},"ranking_n":ncomplete,"validation_performance_inspected":False,"cuda_ready":False,"selection_sha256":sample["selection_sha256"],"zip_integrity":"PASS"}

if __name__=="__main__": print(json.dumps(verify(),ensure_ascii=False,indent=2))
