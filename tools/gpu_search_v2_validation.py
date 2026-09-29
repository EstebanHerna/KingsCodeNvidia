from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(r"C:\Users\ls.contreras\KingsCodeGPU\KingsCodeNvidia")
CORPUS = REPO / "tmp" / "benchmark_corpus_v1"
OUT_ROOT = REPO / "reports" / "benchmark" / "search_v2_validation"

sys.path.insert(0, str(REPO))

from kingscode.common import normalize, write_json, write_jsonl
from kingscode.metadata import canonical_document_id
from kingscode.metadata_experiments import (
    metadata_features,
    locator_boost,
    parse_reference,
)
from kingscode.neural import QwenReranker
from kingscode.retrieval import Retriever
from kingscode.retrieval_benchmark import (
    _assert_clean_tree,
    _direct_gold,
    _gold_after_ranking,
    _matches_at_k,
    _safe_questions,
    _verify_declared_hashes,
    aggregate,
    benchmark_identity,
    bootstrap_reports,
    classify_failure,
    per_question_metrics,
    retrieval_input,
    subgroup_metrics,
)
from kingscode.benchmark_analysis import load_run


# ============================================================
# CONFIGURACION DE BUSQUEDA
# ============================================================

MAX_DEPTH = 180
SPLIT = "validation"

stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
RUN_DIR = OUT_ROOT / stamp
RUN_DIR.mkdir(parents=True, exist_ok=False)

(OUT_ROOT / "LATEST.txt").write_text(str(RUN_DIR), encoding="utf-8")

print("=" * 72, flush=True)
print("KINGSCODE SEARCH V2", flush=True)
print("VALIDATION ONLY - NO HOLDOUT", flush=True)
print("RUN:", RUN_DIR, flush=True)
print("=" * 72, flush=True)


# ============================================================
# PRE-FLIGHT
# ============================================================

_verify_declared_hashes(CORPUS)
_assert_clean_tree()

script_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

print("SCRIPT SHA256:", script_sha, flush=True)
print("CORPUS:", CORPUS, flush=True)

retriever = Retriever(
    CORPUS,
    mode="hybrid",
    rerank=False,
    candidate_k=MAX_DEPTH,
    graph_budget=0,
)

reranker = QwenReranker()

passages = retriever.passages

print("PASSAGES:", len(passages), flush=True)
print("GPU models loaded.", flush=True)


# ============================================================
# LOCATOR INDEX
# ============================================================

def article_norm(value):
    if value is None:
        return ""
    return (
        re.sub(r"\s+", "", str(value))
        .replace(",", ".")
        .lower()
        .strip()
    )


locator_index = defaultdict(list)
all_doc_ids = set()

for i, p in enumerate(passages):
    doc = canonical_document_id(p)
    all_doc_ids.add(doc)

    art = article_norm(p.get("article"))

    if art:
        locator_index[(doc, art)].append(i)


CODE_ALIASES = {
    "codigo general del proceso": "codigo_general_proceso",
    "codigo civil": "codigo_civil",
    "codigo de comercio": "codigo_comercio",
    "codigo comercio": "codigo_comercio",
    "codigo penal": "codigo_penal",
    "codigo sustantivo del trabajo": "codigo_sustantivo_trabajo",
    "estatuto tributario": "estatuto_tributario",
}


def query_document_ids(question, ref):
    docs = []

    # Ley / Decreto explícitos.
    for n in ref["norms"]:
        kind = "decreto" if n["kind"] == "decreto" else "ley"
        docs.append(
            f"{kind}:{str(n['number']).lstrip('0') or n['number']}:{n['year']}"
        )

    # Sentencias explícitas.
    for d in ref["decisions"]:
        decision_id = d["id"].replace("-", "").replace(" ", "").lower()

        m = re.match(r"([a-z]+)", decision_id)
        sala = m.group(1) if m else ""

        court = (
            "corte_constitucional"
            if sala in {"c", "t", "su"}
            else "corte_suprema"
        )

        docs.append(f"{court}:{decision_id}:{d['year']}")

    qn = normalize(question)

    # Alias de códigos cuando el corpus los representa como código canónico.
    for text, doc in CODE_ALIASES.items():
        if text in qn:
            docs.append(doc)

    # Constitución.
    if "constitucion politica" in qn or "constitucion de 1991" in qn:
        for doc in all_doc_ids:
            if doc.startswith("constitucion:"):
                docs.append(doc)

    return list(dict.fromkeys(docs))


def exact_locator_indices(question):
    ref = parse_reference(question)

    if not ref["articles"]:
        return []

    docs = query_document_ids(question, ref)

    if not docs:
        return []

    result = []

    for doc in docs:
        for article in ref["articles"]:
            result.extend(
                locator_index.get(
                    (doc, article_norm(article)),
                    []
                )
            )

    # Determinista y sin duplicar passage_id.
    result = sorted(
        set(result),
        key=lambda i: passages[i]["passage_id"]
    )

    return result


# ============================================================
# CANDIDATE GENERATION
# ============================================================

def weighted_hybrid(sparse, dense, depth, wb=1.0, wd=1.0):
    scores = defaultdict(float)

    for rank, idx in enumerate(sparse[:depth], 1):
        scores[idx] += wb / (60 + rank)

    for rank, idx in enumerate(dense[:depth], 1):
        scores[idx] += wd / (60 + rank)

    candidates = set(sparse[:depth]) | set(dense[:depth])

    return sorted(
        candidates,
        key=lambda i: (
            -scores[i],
            passages[i]["passage_id"],
        ),
    )[:depth]


# ============================================================
# VARIANT MATRIX
# ============================================================

variants = {}


def add(
    name,
    source,
    depth,
    wb=1.0,
    wd=1.0,
    metadata_scale=0.0,
    locator=False,
):
    variants[name] = {
        "source": source,
        "depth": depth,
        "bm25_weight": wb,
        "dense_weight": wd,
        "metadata_scale": metadata_scale,
        "locator_injection": locator,
    }


# ------------------------------------------------------------
# A. Profundidad pura
# ------------------------------------------------------------

for depth in (30, 60, 120, 180):
    add(f"HYB_{depth}", "hybrid", depth)
    add(f"BM25_{depth}", "bm25", depth)


# ------------------------------------------------------------
# B. BM25-heavy hybrid, mismo pool
# ------------------------------------------------------------

for weight in (2, 4, 8):
    add(
        f"HYB120_B{weight}D1",
        "hybrid",
        120,
        wb=float(weight),
        wd=1.0,
    )


# ------------------------------------------------------------
# C. Metadata sweep
# ------------------------------------------------------------

for alpha in (0.25, 0.50, 0.75, 1.00, 1.25):
    tag = str(alpha).replace(".", "p")

    add(
        f"HYB120_META_{tag}",
        "hybrid",
        120,
        metadata_scale=alpha,
    )

    add(
        f"BM25120_META_{tag}",
        "bm25",
        120,
        metadata_scale=alpha,
    )


# ------------------------------------------------------------
# D. Hybrid BM25-heavy + metadata
# ------------------------------------------------------------

for weight in (2, 4, 8):
    add(
        f"HYB120_B{weight}D1_META1",
        "hybrid",
        120,
        wb=float(weight),
        wd=1.0,
        metadata_scale=1.0,
    )


# ------------------------------------------------------------
# E. Locator injection
# ------------------------------------------------------------

for alpha in (0.0, 0.50, 1.00, 1.25):
    tag = str(alpha).replace(".", "p")

    add(
        f"HYB120_LOC_META_{tag}",
        "hybrid",
        120,
        metadata_scale=alpha,
        locator=True,
    )

    add(
        f"BM25120_LOC_META_{tag}",
        "bm25",
        120,
        metadata_scale=alpha,
        locator=True,
    )


# ------------------------------------------------------------
# F. BM25-heavy + locator + metadata
# ------------------------------------------------------------

for weight in (2, 4, 8):
    add(
        f"HYB120_B{weight}D1_LOC_META1",
        "hybrid",
        120,
        wb=float(weight),
        wd=1.0,
        metadata_scale=1.0,
        locator=True,
    )


# ------------------------------------------------------------
# G. Deep 180
# ------------------------------------------------------------

add(
    "HYB180_META1",
    "hybrid",
    180,
    metadata_scale=1.0,
)

add(
    "BM25180_META1",
    "bm25",
    180,
    metadata_scale=1.0,
)

add(
    "HYB180_LOC_META1",
    "hybrid",
    180,
    metadata_scale=1.0,
    locator=True,
)

add(
    "BM25180_LOC_META1",
    "bm25",
    180,
    metadata_scale=1.0,
    locator=True,
)


print("VARIANTS:", len(variants), flush=True)

for name, cfg in variants.items():
    print(name, cfg, flush=True)


# ============================================================
# RANKING PHASE
#
# IMPORTANTE:
# NO SE CARGA GOLD HASTA QUE TODAS LAS PREGUNTAS HAYAN SIDO
# RANKEADAS PARA TODAS LAS VARIANTES.
# ============================================================

questions = _safe_questions(SPLIT)

rankings = {
    name: []
    for name in variants
}

ranking_start = time.perf_counter()

for qnum, question in enumerate(questions, 1):

    text = retrieval_input(question)

    query_start = time.perf_counter()

    # Una sola consulta sparse+dense por pregunta.
    sparse, _ = retriever.bm25.ranking(
        text,
        MAX_DEPTH,
    )

    dense, _ = retriever.dense.ranking(
        text,
        MAX_DEPTH,
    )

    locators = exact_locator_indices(text)

    candidate_sets = {}

    # Construir todos los candidate sets primero.
    for name, cfg in variants.items():

        depth = cfg["depth"]

        if cfg["source"] == "bm25":
            base = list(sparse[:depth])

        else:
            base = weighted_hybrid(
                sparse,
                dense,
                depth,
                wb=cfg["bm25_weight"],
                wd=cfg["dense_weight"],
            )

        if cfg["locator_injection"]:
            base = list(dict.fromkeys(base + locators))

        candidate_sets[name] = base

    # Scorear por Qwen reranker CADA PASAJE SOLO UNA VEZ
    # aunque participe en muchas variantes.
    union = sorted(
        {
            idx
            for values in candidate_sets.values()
            for idx in values
        },
        key=lambda i: passages[i]["passage_id"],
    )

    docs = [
        passages[i]["text"]
        for i in union
    ]

    values = reranker.score(text, docs)

    rerank_score = dict(zip(union, values))

    ref = parse_reference(text)

    # Cache del boost porque varias variantes lo reutilizan.
    boost_cache = {}

    for idx in union:
        feats = metadata_features(
            text,
            passages[idx],
            ref,
        )
        boost_cache[idx] = locator_boost(feats)

    shared_ms = (
        time.perf_counter() - query_start
    ) * 1000.0

    for name, cfg in variants.items():

        alpha = cfg["metadata_scale"]

        candidate = candidate_sets[name]

        ordered = sorted(
            candidate,
            key=lambda i: (
                -(
                    rerank_score[i]
                    + alpha * boost_cache[i]
                ),
                passages[i]["passage_id"],
            ),
        )

        # Igual que el benchmark contractual:
        # 30 candidatos llegan a failure analysis,
        # top-10 se usa para métricas.
        rankings[name].append(
            {
                "question": question,
                "indices": ordered[:30],
                "shared_search_ms": shared_ms,
                "locator_candidates": len(locators),
                "union_candidates": len(union),
            }
        )

    if qnum % 5 == 0 or qnum == len(questions):
        elapsed = time.perf_counter() - ranking_start

        print(
            f"[{qnum:03d}/{len(questions)}] "
            f"elapsed={elapsed/60:.1f} min "
            f"union={len(union)} "
            f"locator={len(locators)}",
            flush=True,
        )


ranking_seconds = time.perf_counter() - ranking_start

print("=" * 72, flush=True)
print("ALL RANKINGS COMPLETE.", flush=True)
print("NOW loading gold.", flush=True)
print("=" * 72, flush=True)


# ============================================================
# SCORING PHASE
# ============================================================

gold_by_id = _gold_after_ranking(SPLIT)

reports = {}
rows_by_variant = {}

for name, cfg in variants.items():

    rows = []

    for item in rankings[name]:

        question = item["question"]
        gold = gold_by_id[question["id"]]

        candidate = [
            passages[i]
            for i in item["indices"]
        ]

        result = candidate[:10]

        metrics = per_question_metrics(
            result,
            gold,
        )

        matched_by_k = {
            str(k): sorted(
                _matches_at_k(
                    result,
                    gold,
                    k,
                )[0]
            )
            for k in (1, 3, 5, 8, 10)
        }

        rows.append(
            {
                "id": question["id"],
                "question": question,

                # Es latencia compartida por toda la búsqueda,
                # NO latencia deployable de esta variante.
                "latency_ms": item["shared_search_ms"],

                "metrics": metrics,
                "gold_direct_count": len(
                    _direct_gold(gold)
                ),
                "matched_direct_fragment_ids_by_k":
                    matched_by_k,

                "failure": classify_failure(
                    result,
                    candidate,
                    gold,
                    question["tags"],
                ),

                "exploration": {
                    "locator_candidates":
                        item["locator_candidates"],
                    "shared_union_candidates":
                        item["union_candidates"],
                },
            }
        )

    metrics = aggregate(rows)

    report = {
        "version": "kingscode-search-v2",
        "status": "passed",
        "variant": name,
        "split": SPLIT,
        "config": cfg,
        "metrics": metrics,
        "subgroups": subgroup_metrics(rows),
        "failure_taxonomy": dict(
            sorted(
                Counter(
                    row["failure"]
                    for row in rows
                ).items()
            )
        ),
        "questions": len(rows),
        "script_sha256": script_sha,
        "benchmark": benchmark_identity(),
        "ranking_seconds_shared": ranking_seconds,
        "label_boundary":
            "all variants and all questions ranked before gold was loaded",
        "latency_note":
            "latency_ms is shared search-v2 exploration cost; "
            "not standalone deployment latency",
    }

    variant_dir = RUN_DIR / name
    variant_dir.mkdir()

    write_jsonl(
        variant_dir / "per_question.jsonl",
        rows,
    )

    write_json(
        variant_dir / "report.json",
        report,
    )

    rows_by_variant[name] = rows
    reports[name] = report


# ============================================================
# ENCONTRAR R6 OFICIAL DEV PARA COMPARACION
# ============================================================

def latest_r6_dev():

    root = REPO / "reports" / "benchmark" / "r6"

    candidates = []

    if root.exists():

        for p in root.glob("*-dev"):

            report_file = p / "report.json"

            if not report_file.exists():
                continue

            try:
                data = json.loads(
                    report_file.read_text(
                        encoding="utf-8"
                    )
                )
            except Exception:
                continue

            if (
                data.get("status") == "passed"
                and data.get("variant") == "R6"
                and data.get("split") == "dev"
            ):
                candidates.append(p)

    if not candidates:
        return None

    return max(
        candidates,
        key=lambda p: p.stat().st_mtime,
    )


r6_dir = None

r6_report = None
r6_rows = None

if r6_dir:
    r6_report, r6_rows = load_run(r6_dir)

    print("REFERENCE R6:", r6_dir, flush=True)


# ============================================================
# RESUMEN POR PUNTO ESTIMADO
# ============================================================

summary = []

for name, report in reports.items():

    m = report["metrics"]
    failures = report["failure_taxonomy"]

    summary.append(
        {
            "variant": name,

            "EC8":
                m["Evidence Completeness@8"],

            "Recall10":
                m["Recall@10"],

            "MRR10":
                m["MRR@10"],

            "nDCG10":
                m["nDCG@10"],

            "correct_doc_wrong_passage":
                failures.get(
                    "correct_document_wrong_passage",
                    0,
                ),

            "ranking_failure":
                failures.get(
                    "ranking_failure",
                    0,
                ),

            "wrong_document":
                failures.get(
                    "wrong_document",
                    0,
                ),

            "config":
                variants[name],
        }
    )


summary.sort(
    key=lambda x: (
        x["EC8"],
        x["Recall10"],
        x["MRR10"],
        x["nDCG10"],
    ),
    reverse=True,
)


# ============================================================
# BOOTSTRAP SOLO TOP 8 VS R6
# ============================================================

if r6_rows is not None:

    for row in summary[:8]:

        comp = bootstrap_reports(
            r6_rows,
            rows_by_variant[row["variant"]],
        )

        row["vs_R6"] = comp


# ============================================================
# SANITY CHECK
#
# HYB_30 debe aproximar/reproducir R3.
# HYB120_META_1p0 debe aproximar/reproducir R6.
# ============================================================

sanity = {
    "HYB_30": reports["HYB_30"]["metrics"],
    "HYB120_META_1p0":
        reports["HYB120_META_1p0"]["metrics"],
}

if r6_report:
    sanity["official_R6"] = r6_report["metrics"]


# ============================================================
# SALVAR
# ============================================================

write_json(
    RUN_DIR / "SUMMARY.json",
    {
        "run": str(RUN_DIR),
        "ranking_seconds_shared":
            ranking_seconds,
        "variants":
            len(variants),
        "summary":
            summary,
        "sanity":
            sanity,
    },
)


csv_path = RUN_DIR / "SUMMARY.csv"

with csv_path.open(
    "w",
    newline="",
    encoding="utf-8-sig",
) as f:

    writer = csv.writer(f)

    writer.writerow(
        [
            "rank",
            "variant",
            "EC8",
            "Recall10",
            "MRR10",
            "nDCG10",
            "correct_document_wrong_passage",
            "ranking_failure",
            "wrong_document",
        ]
    )

    for rank, row in enumerate(summary, 1):

        writer.writerow(
            [
                rank,
                row["variant"],
                row["EC8"],
                row["Recall10"],
                row["MRR10"],
                row["nDCG10"],
                row["correct_doc_wrong_passage"],
                row["ranking_failure"],
                row["wrong_document"],
            ]
        )


# ============================================================
# TERMINAL SUMMARY
# ============================================================

print("", flush=True)
print("=" * 100, flush=True)
print("TOP 20", flush=True)
print("=" * 100, flush=True)

print(
    f"{'#':>2} "
    f"{'VARIANT':<32} "
    f"{'EC8':>8} "
    f"{'R10':>8} "
    f"{'MRR':>8} "
    f"{'nDCG':>8} "
    f"{'CDWP':>6} "
    f"{'RF':>4}",
    flush=True,
)

for rank, row in enumerate(summary[:20], 1):

    print(
        f"{rank:>2} "
        f"{row['variant']:<32} "
        f"{row['EC8']:>8.4f} "
        f"{row['Recall10']:>8.4f} "
        f"{row['MRR10']:>8.4f} "
        f"{row['nDCG10']:>8.4f} "
        f"{row['correct_doc_wrong_passage']:>6} "
        f"{row['ranking_failure']:>4}",
        flush=True,
    )


print("", flush=True)
print("=" * 100, flush=True)
print("SANITY", flush=True)
print("=" * 100, flush=True)

print(
    "HYB_30 EC8:",
    sanity["HYB_30"]["Evidence Completeness@8"],
    flush=True,
)

print(
    "HYB120_META_1p0 EC8:",
    sanity["HYB120_META_1p0"]["Evidence Completeness@8"],
    flush=True,
)

if r6_report:

    print(
        "OFFICIAL R6 EC8:",
        r6_report["metrics"]["Evidence Completeness@8"],
        flush=True,
    )


print("", flush=True)
print("=" * 100, flush=True)
print("TOP 8 BOOTSTRAP VS R6", flush=True)
print("=" * 100, flush=True)

for row in summary[:8]:

    print("", row["variant"], flush=True)

    comp = row.get("vs_R6")

    if not comp:
        print("  no R6 comparison", flush=True)
        continue

    for metric in (
        "Evidence Completeness@8",
        "Recall@10",
        "MRR@10",
    ):

        x = comp[metric]

        print(
            f"  {metric}: "
            f"delta={x['delta']:.6f} "
            f"CI95={x['ci_95']}",
            flush=True,
        )


best = summary[0]

(RUN_DIR / "BEST.txt").write_text(
    json.dumps(
        best,
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)


print("", flush=True)
print("=" * 100, flush=True)
print("SEARCH V2 FINISHED", flush=True)
print("BEST POINT ESTIMATE:", best["variant"], flush=True)
print("EC8:", best["EC8"], flush=True)
print("Recall10:", best["Recall10"], flush=True)
print("MRR10:", best["MRR10"], flush=True)
print("OUTPUT:", RUN_DIR, flush=True)
print("=" * 100, flush=True)


