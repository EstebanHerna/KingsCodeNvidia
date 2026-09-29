# Member A v0.2 progress — 2026-09-29

Status: PARTIAL. Branch feat/member-a-corpus-v02-locator, based on the RTX 4090 retrieval freeze 60ebf7e. Historical GPU reports and v0.1 remain preserved; benchmark v1/Search V2 were not rerun or retuned.

Implemented in this working branch:
- Productized explicit statutory/case locator as an additive candidate source and exposed CLI opt-in; default public profile keeps AUTO graph expansion disabled while explicit ON preserves bounded behavior.
- Reconciled the 4090 runs, locks, corpus hashes, and R1-QWEN through R8 evidence in reports/member_a_v02/gpu_reconciliation.json.
- Started a separate corpus-v0.2 snapshot. Four official documents currently parse provisionally into 72 passages, 33 nodes and 29 structural edges; one PDF remains blocked on image-only first page. Semantic edges remain in review queue and are not retrieval-certified.
- Added schema support for RETRIEVAL_GOLD, END_TO_END_ONLY, TECHNICAL_PILOT_ONLY, and alternative minimal evidence sets.
- Added benchmark source manifest, split policy, exact duplicate report, exposure ledger and international candidate inventory. The independent benchmark is not populated: zero independent retrieval-gold items and zero sealed evaluation items. The old 12-case, corpus-derived technical pilot is not selectable and must not justify tuning. Its prior DEV metrics in reports/member_a_v02/benchmark_v2_dev.json are pilot-only (Evidence Completeness@8=1.000, Recall@10=1.000, MRR@10=0.875, nDCG@10=0.9051); they are not a baseline for unseen legal questions. Independent-v2 baseline and failure distribution are unavailable.
- The prior audit branch contains six confirmed defect families. Corpus-v0.2 fixes with source-backed regression fixtures are still outstanding; v0.1 is untouched.

Independent source research: the ICFES portal and two indexed ICFES assessment PDFs were unavailable (404 during direct verification). The official SIRNA microsite confirms the bar exam guide, but publicly extractable assessment items were not verified. The international inventory tracks five candidates; it makes no unverified applicability claim and contains zero benchmark items.

No independent benchmark baseline or failure distribution exists. Consequently no retrieval experiment is justified yet. Exact next step: resolve an accessible official assessment item source, ingest item/source provenance and duplicate families, author/review retrieval gold against source passages, assign families to DEV/VALIDATION before any tuning, then execute one untuned baseline and failure taxonomy. Continue audit-driven corpus-v0.2 fixes only with regression fixtures and primary source evidence.

Verification passed: python -m unittest discover -s tests -v ran 210 tests, OK; python tools/benchmark_v2.py check verified 10 manifest hashes without parsing pilot holdout; tools/verify_member_a_v02.py passed twice with 19 official files, 326 raw/clean v0.1 files, 14 v0.2 hashes and deterministic retrieval. The independent v2 baseline was not run because there are zero independent retrieval-gold items. Keep this branch separate; no PR or merge to main.
