"""Nucleo de B: pregunta -> fila del esquema oficial.

answer_item() nunca lanza excepcion ni deja campos obligatorios vacios: si el
modelo falla, aplica un respaldo determinista y lo deja registrado."""
from __future__ import annotations

import json
import re
import time

from . import llm
from .config import Config
from .guard import build_refs, citation_guard
from .prompts import build_messages, json_schema_for
from .query import normalize_query
from .router import lookup_first, route_graph, rrf_merge

_WORD = re.compile(r"\w{4,}")


def parse_json(text: str) -> dict | None:
    t = re.sub(r"(?s)<think>.*?</think>", "", text or "").strip()
    t = re.sub(r"^```(?:json)?|```$", "", t, flags=re.M).strip()
    for cand in (t, t[t.find("{"): t.rfind("}") + 1] if "{" in t else ""):
        if not cand:
            continue
        try:
            d = json.loads(cand)
            if isinstance(d, dict):
                return d
        except json.JSONDecodeError:
            continue
    return None


def _lexical_choice(item: dict, passages: list[dict]) -> str:
    """Respaldo determinista para cerradas si el modelo no devolvio letra."""
    ev = set(w.lower() for p in passages for w in _WORD.findall(p.get("texto", "")))
    best, best_s = "A", -1.0
    for k, v in sorted((item.get("opciones") or {}).items()):
        ws = set(w.lower() for w in _WORD.findall(v))
        s = len(ws & ev) / (len(ws) or 1)
        if s > best_s:
            best, best_s = k, s
    return best


def _letter(v) -> str | None:
    m = re.match(r"\s*\(?([ABCD])\b", str(v or "").upper())
    return m.group(1) if m else None


def _clean_passage(p: dict) -> dict:
    out = {"doc_id": str(p.get("doc_id")), "texto": str(p.get("texto") or "").strip() or "(vacio)"}
    for f in ("inicio", "fin"):
        if isinstance(p.get(f), int) and p[f] >= 0:
            out[f] = p[f]
    if isinstance(p.get("score"), (int, float)):
        out["score"] = round(float(p["score"]), 4)
    return out


def _sentences(t: str, n: int) -> str:
    parts = re.split(r"(?<=[.!?])\s+", (t or "").strip())
    return " ".join(parts[:n]).strip()


def gather_passages(item: dict, cfg: Config, retrieve) -> tuple[list[dict], dict]:
    nq = normalize_query(item["pregunta"], item.get("tema"))
    main_q = nq.retrieval_query()
    lists = [retrieve(main_q, k=cfg.k_submit, graph_mode="off")]
    if item["formato"] == "multiple_choice" and cfg.mc_option_queries:
        for _, v in sorted((item.get("opciones") or {}).items()):
            lists.append(retrieve(f"{nq.clean} {v}", k=cfg.k_submit, graph_mode="off"))
    flat = rrf_merge(lists, k=cfg.k_submit * 2) if len(lists) > 1 else lists[0]
    mode = route_graph(nq, flat, cfg.graph_mode)
    if mode == "on":
        g = retrieve(main_q, k=cfg.k_submit, graph_mode="on")
        flat = rrf_merge([flat, g], k=cfg.k_submit * 2)
    flat = lookup_first(flat, nq)
    info = {"graph": mode, "queries": len(lists), "normas_pregunta": nq.cite_text, "signals": nq.signals}
    return flat[: cfg.k_submit], info


def answer_item(item: dict, cfg: Config, retrieve) -> tuple[dict, dict]:
    t0 = time.time()
    f = item["formato"]
    log: dict = {"id": item["id"], "formato": f, "fallbacks": []}
    try:
        passages, info = gather_passages(item, cfg, retrieve)
    except Exception as e:
        passages, info = [], {"error_retrieval": repr(e)}
    log.update(info)
    submit = [_clean_passage(p) for p in passages]
    row: dict = {"id": item["id"], "formato": f, "abstencion": False, "pasajes_recuperados": submit}

    top = max([p.get("score") or 0.0 for p in passages], default=0.0)
    abstain = (not passages and cfg.abstain_if_no_passages) or \
              (cfg.abstain_min_score is not None and f != "multiple_choice" and top < cfg.abstain_min_score)
    if abstain:
        row["abstencion"] = True
        if f == "multiple_choice":
            row.update(respuesta_correcta=None, justificacion="", descarte_opciones={})
        elif f == "semi_open":
            row.update(respuesta="", palabras_clave=[], referencia_legal="")
        else:
            row.update(marco_normativo="", analisis="", jurisprudencia="", conclusion="")
        log["abstencion"] = True
        log["latencia_ms"] = int((time.time() - t0) * 1000)
        row["latencia_ms"] = log["latencia_ms"]
        return row, log

    llm_passages = passages[: cfg.k]
    msgs = build_messages(item, llm_passages, cfg.max_passage_chars)
    out, usage = None, {}
    try:
        raw, usage = llm.chat(cfg, msgs, json_schema_for(f) if cfg.json_mode == "schema" else None)
        out = parse_json(raw)
        if out is None:
            log["fallbacks"].append("json_invalido")
            log["raw"] = raw[:500]
    except llm.LLMError as e:
        log["fallbacks"].append(f"llm_error:{e}")
    out = out or {}
    used = [int(x) for x in (out.get("pasajes_usados") or []) if str(x).isdigit()]
    refs = build_refs(passages, used, cfg.max_cites) if cfg.cite_from != "none" else []
    ref_txt = "; ".join(refs)

    if f == "multiple_choice":
        letter = _letter(out.get("respuesta"))
        if not letter:
            letter = _lexical_choice(item, passages)
            log["fallbacks"].append("letra_lexica")
        just = (out.get("justificacion") or "").strip() or "La opción elegida es la que concuerda con la evidencia recuperada."
        if ref_txt:
            just = f"{just} Fundamento normativo: {ref_txt}."
        an = out.get("analisis_opciones") or {}
        desc = {k: (str(an.get(k) or "").strip() or "No concuerda con la evidencia recuperada.")
                for k in sorted(item.get("opciones") or {"A": 0, "B": 0, "C": 0, "D": 0}) if k != letter}
        row.update(respuesta_correcta=letter, justificacion=just, descarte_opciones=desc)
        log["respuesta"] = letter
    elif f == "semi_open":
        resp = (out.get("respuesta") or "").strip()
        if not resp:
            resp = _sentences(passages[0]["texto"], 3) if passages else "Sin respuesta."
            log["fallbacks"].append("respuesta_extractiva")
        kws = [str(k).strip() for k in (out.get("palabras_clave") or []) if str(k).strip()][:6]
        row.update(respuesta=resp, palabras_clave=kws or ["derecho colombiano"],
                   referencia_legal=ref_txt or "Evidencia recuperada del corpus.")
    else:
        def g(k, default):
            v = (out.get(k) or "").strip()
            if not v:
                log["fallbacks"].append(f"{k}_vacio")
            return v or default
        marco = g("marco_normativo", ref_txt or "Normas de la evidencia recuperada.")
        if ref_txt and ref_txt.split(";")[0].strip()[:20].lower() not in marco.lower():
            marco = f"{marco} Normas aplicables: {ref_txt}."
        row.update(marco_normativo=marco,
                   analisis=g("analisis", _sentences(passages[0]["texto"], 5) if passages else "Sin análisis."),
                   jurisprudencia=g("jurisprudencia", "No se identificó jurisprudencia específica en la evidencia recuperada."),
                   conclusion=g("conclusion", "Ver análisis."))

    log["guard"] = citation_guard(row, passages)
    # la guarda puede vaciar un campo: reponer texto neutro para no invalidar la fila
    req = {"multiple_choice": ["justificacion"], "semi_open": ["respuesta", "referencia_legal"],
           "open_ended": ["marco_normativo", "analisis", "jurisprudencia", "conclusion"]}[f]
    for k in req:
        if not row.get(k):
            row[k] = "Según la evidencia recuperada del corpus."
            log["fallbacks"].append(f"{k}_vaciado_por_guarda")
    row["latencia_ms"] = int((time.time() - t0) * 1000)
    log["latencia_ms"] = row["latencia_ms"]
    log["tokens"] = usage
    log["top_score"] = top
    return row, log
