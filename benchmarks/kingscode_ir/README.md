# KingsCode internal legal retrieval benchmark v1

This is an **internal Member A retrieval benchmark**, derived deterministically from the official-corpus snapshot. It is not the official 50-question development set and does not contain expected answers, `legal_basis`, or generation targets.

## Layout

- `questions/{dev,validation,holdout}.jsonl`: retrieval-safe inputs only. The retrieval runner passes only `question` text to `Retriever.retrieve`.
- `gold/{dev,validation,holdout}.jsonl`: canonical document/fragment identifiers, direct-evidence records, and source spans. These files are loaded only after rankings have been produced.
- `authoring/review_queue.jsonl`: source-derived authoring packets for cases that need a human-written semantic/temporal question. They are **not benchmark cases**.
- `manifests/benchmark_manifest.json`: immutable snapshot identity, split counts, hashes, derivation policy, and holdout-protection policy.

## Data generation policy

All populated v1 cases use deterministic Spanish templates over verified corpus metadata and exact official passages. No closed model and no agent-generated legal question is used. Cases without faithful deterministic phrasing are placed in the review queue with `needs_human_question_text=true`.

## Split policy

The benchmark target is 200 cases: 120 development, 40 validation, and 40 holdout. The holdout may only be evaluated through a predeclared baseline or a post-selection confirmation; it must never guide parameter choice. The official 50 remains separate and is only an external milestone after internal selection.

## Gold semantics

`gold_document_ids` and `gold_fragment_ids` use v0.6 canonical identifiers. Each evidence item is `direct` or `supporting`; v1 generated cases use only direct evidence. `gold_spans` point to exact clean-text offsets of the official source passage. A case is rejected if any canonical ID or span cannot be resolved against the frozen corpus snapshot.

## Running

```powershell
.venv/Scripts/python.exe tools/build_retrieval_benchmark.py --check
.venv/Scripts/python.exe tools/evaluate_retrieval_benchmark.py --variant R0 --split dev
```

The evaluator records provenance and refuses to send gold fields into retrieval. Neural variants require separately recorded GPU prerequisites and are not inferred from CPU/BM25 results.
