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


## 2026-09-29 — KC-COL-IR-v0.1 cross-institution acquisition checkpoint

- Added the independent benchmark under `benchmarks/kc_col_ir_v0.1/`, separate from benchmark-v1 and the existing v2 technical pilot. The 17-row source inventory assigns Externado to DEV, Universidad Libre to VALIDATION_CANDIDATE, ICFES/SIRNA to SEALED_FUTURE, and guide-only sources to COVERAGE_ONLY.
- Acquired and SHA-256 verified two official Externado PDFs. The 2011 Externado Private I / Civil Procedure bank contains 270 distinct mechanically numbered candidate items. Its full text extraction and source PDFs are local under ignored `tmp/kc_col_ir_v0.1/`; question wording is not committed. Extraction has corrupted accent glyphs, so the candidate pool is frozen for QA only, not asserted as exact final transcription. The 2025 Labor PDF has 225 topic bullets and contributes zero independent items.
- Before any retrieval call, selected 30 of the 270 items in ascending SHA-256(`source_family + source_document + source_item_number`) order. All remain `NEEDS_HUMAN_REVIEW`, temporal status `UNCERTAIN`; zero accepted retrieval gold.
- Registered Universidad Libre's 2021 labor/public/private/penal URLs as isolated validation sources. Their HTTP responses were generic HTML, not PDFs; only signatures/status were checked. No validation text was extracted and no retrieval performance or gold was inspected. The 2026 thematic-bank announcement is coverage/methodology context, not 2021 question evidence.
- Added a dedicated runner with the C0 BM25, C1 Qwen dense, C2 hybrid/RRF, C3 hybrid/Qwen reranker configuration, identical depth and graph OFF; it hard-fails unless 10 accepted independent DEV golds are frozen. Runner has not been executed for retrieval. `CUDA_HANDOFF.md` is NOT READY (`CUDA_READY=false`): corpus/index hashes and current final SHA must be filled after the gate.
- Added `tools/verify_kc_col_ir_v01.py`; it verifies split-family isolation, inventory hashes, ignored pool hash, deterministic sampling, zero gold leakage and the closed baseline gate. Verification passes.
- G01: reject the seven wrong containing-passage targets; the seven replacement-effect claims remain unresolved/inactive. D01 content-dedup regression passes while the broader provenance audit remains open. G02/C01/P02/P01 remain fixed. Corpus v0.1 and Member B remain untouched.
- Next exact task: human-verify the 30 local source items/options against the original PDF and primary law, assign temporal status independently of retrieval, and accept at least 10 complete minimal-evidence packets before any baseline.


## 2026-09-29 — Cambio de prioridad DEV a fuentes recientes

- La cola primaria de `benchmarks/kc_col_ir_v0.1/questions/dev.jsonl` se reemplazó por 30 ítems deterministas del conjunto oficial JEP publicado en `/preguntas`. El HTML UTF-8 se preserva localmente con hash; pool completo de 62 y wording/respuestas permanecen ignorados fuera de Git. No se ha ejecutado retrieval ni seleccionado por rendimiento.
- Corrección de fecha: `/preguntas` corresponde a la tercera edición 2025; el sitio anuncia la cuarta edición 2026 pero no se verificaron preguntas 2026. La lista requiere filtro humano: hay aclaraciones fácticas, temas jurídicos/estratégicos y respuestas que remiten a expediente/jurisprudencia; algunas cuestiones jurídicas no reciben respuesta de fondo.
- Externado 2011 conserva intactos sus 30 IDs, regla de muestreo y 270 candidatos en archivos `reproducibilidad_externado_2011`; deja de ser DEV primario.
- Javeriana Seguros 2026 queda validation candidate. Se comprobó firma y SHA-256 de un PDF oficial de respuestas; no se extrajo texto ni se midió retrieval. La página indica que algunas respuestas deben inferirse del caso o son parte del análisis propio. Un segundo URL candidato respondió HTML y no se cuenta como PDF adquirido.
- Estado: 0 gold aceptados, 30 JEP por revisar, validación no parseada/no inspeccionada, `CUDA_READY=false`. Próximo paso: revisión humana de pregunta exacta, carácter implícito, evidencia mínima primaria y temporalidad para JEP; no correr baseline hasta >=10 gold válidos.
