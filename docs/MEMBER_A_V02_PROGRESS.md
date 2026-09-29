# Member A v0.2 progress — 2026-09-29

Status: PARTIAL. Branch `feat/member-a-corpus-v02-locator`, checkpoint `9d160f8fc9771c233e7105756fdb65ced74390eb`. Do not merge to `main`.

The completed G02, C01, P02 and P01 v0.2-only parser repairs, query-view/locator and retrieval-diagnostic work remain intact. Corpus v0.1 and the official starter pack remain untouched. Corpus v0.2 still contains four provisional documents, 72 passages, 33 nodes, 29 structural edges and zero active semantic edges. No corpus expansion or retrieval architecture change was justified by independent DEV evidence.

## Benchmark acquisition

Official ICFES indexing confirms the requested Gestión del Conflicto 2026 and Comunicación Jurídica 2021 question booklets. Direct original URLs, browser-compatible requests, the official toolbox landing navigation, and official current-module booklet candidates returned HTTP 404 in this runtime. This status is `RUNTIME_ACQUISITION_BLOCKED`; it does not establish that the official sources are unavailable. Search/index renderings were used only to discover official resources, never as question bytes.

The item sources are recorded in `benchmarks/kingscode_ir_v2/source_manifest.jsonl`: Gestión del Conflicto 2026 is DEV; Comunicación Jurídica 2021 and 2026 are separate VALIDATION candidates. The May 2026 Gestión URL is an official orientation guide, not a question booklet, and is not eligible for item intake. Current counts: independent items extracted 0; END_TO_END_ONLY 0; accepted RETRIEVAL_GOLD 0; NEEDS_HUMAN_REVIEW 0; sealed evaluation 0. No baseline is selectable.

A hash-gated local intake utility is ready. Place bytes in ignored `tmp/official-source-intake/` and run:
`python tools/benchmark_source_intake.py --source-id ICFES-GESTION-CONFLICTO-2026 --file tmp/official-source-intake/<file>.pdf --sha256 <64-hex-sha256>`
Use `ICFES-COMUNICACION-JURIDICA-2021` or `ICFES-COMUNICACION-JURIDICA-2026` for validation material. The May Gestión PDF is a guide, so it is excluded from question intake. The helper verifies the exact hash and PDF framing before reporting readiness; it does not claim source authenticity or redistribution rights. No questions are emitted or stored by the helper.

## Graph and identity review

G01 review rejected the seven known candidate edges whose target was the enclosing passage/section rather than the different legal provision named by the official text. Exact quote, official URL and SHA-256 of each containing source are recorded in `reports/member_a_v02/g01_relation_review_v02.json`. The seven replacement claims remain unresolved because the cited instruments' own primary bytes are not acquired. Active semantic edges remain zero; no graph expansion is enabled from this review.

D01 now has a regression asserting that equal content hashes do not collapse distinct canonical legal document IDs. The broader provenance and repeated-boilerplate audit remains open; the test does not mark D01 fixed.

## Verification and next action

Final verification: three complete passes overall; the latest pass includes the intake-source/guide correction and reports: 226 tests PASS; `python tools/benchmark_v2.py check` PASS (10 hashes; holdout not parsed; selection disabled); `python tools/verify_member_a_v02.py` PASS (19 official files, 326 v0.1 raw/clean files, 18 v0.2 hashes). The CPU snapshot check is not GPU metric replay. GPU, benchmark-v1, Search V2, target 4090 and holdout remain unrun. Do not tune before at least 10 accepted independent retrieval-gold items.

Next exact action: obtain the official PDFs and independent hashes, place them in `tmp/official-source-intake/`, verify with `tools/benchmark_source_intake.py`, then inspect current use terms and create exact, locally retained DEV/VALIDATION item records with source provenance. In parallel, acquire the seven G01 cited primary instruments before accepting any replacement edge.
