# KC-COL-IR-v0.1

Independent, cross-institution Colombian legal retrieval benchmark. DEV is
restricted to Universidad Externado de Colombia; Universidad Libre belongs to
the isolated VALIDATION family; ICFES/SIRNA are SEALED/FUTURE. Sources that
contain only syllabus topics are coverage-only.

## Current acquisition checkpoint

The verified local Externado acquisition contains the 2011 Private I / Civil
Procedure question bank (270 numbered items mechanically detected) and the
2025/2026 Labor and Social Security preparatory topic bank (225 bullets, not
counted as independent questions). The first is the only question-bearing
source acquired in this checkpoint. Its extracted text and the source PDFs
stay under ignored `tmp/kc_col_ir_v0.1/`; the Git manifest contains provenance,
hashes and counts, not the bank wording. Mechanical extraction is not yet
human-verified for exact wording or options.

The first deterministic batch is 30 candidate IDs selected from the complete
numbered pool using SHA-256 of
`institution_family + source_document + source_item_number`, sorted
ascending, with a 30-item cap. See `sampling_manifest.json`. Retrieval has not
been run. Each candidate is `NEEDS_HUMAN_REVIEW`; none is retrieval gold yet.
The 2011 source predates major procedural reforms, so all candidates begin as
`UNCERTAIN` until their legal basis receives independent temporal review.

Universidad Libre URLs are registered as `VALIDATION_CANDIDATE`, but this
checkpoint did not acquire or parse their bytes. There are zero counted
validation questions and no validation retrieval exposure. Other institutions
are discovery-only; access restrictions are not bypassed.

## Files and privacy

- `source_manifest.jsonl`: one provenance row per discovered document.
- `questions/dev.jsonl`: metadata-only annotation queue; no source question
  wording is redistributed in this repository.
- `gold/dev.jsonl`: empty until independent evidence review is completed.
- `manifest.json`: frozen acquisition and split status.
- `CUDA_HANDOFF.md`: first-session run card; CUDA_READY remains false until
  at least 10 independent DEV gold records are accepted.

Source-bank wording remains in local ignored acquisition artifacts. Confirm
reproduction/redistribution permission before publishing extracted wording.
