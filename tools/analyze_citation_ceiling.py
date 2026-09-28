"""Analisis de desarrollo (NO forma parte del pipeline competitivo).

Mide, sobre una corrida existente de B, cuanto puntaje de citacion y abstencion
se puede obtener solo con la evidencia que ya recupero A, variando la forma de
construir las referencias. Sirve para decidir la estrategia de citas antes de
tener decoder.

Lee `legal_basis` del sample UNICAMENTE aqui y en evaluate.py, para medir.
Nada de este script entra al indice, al prompt ni al decoder.

Uso:
    python tools/analyze_citation_ceiling.py                      # ultima corrida en reports/member_b
    python tools/analyze_citation_ceiling.py --run reports/member_b/<carpeta>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import citations  # noqa: E402  (oficial)

CODE_NAMES = {
    "constitucion": "Constitución Política", "codigo_civil": "Código Civil", "codigo_penal": "Código Penal",
    "codigo_procedimiento_penal": "Código de Procedimiento Penal", "codigo_comercio": "Código de Comercio",
    "codigo_sustantivo_trabajo": "Código Sustantivo del Trabajo", "codigo_procesal_trabajo": "Código Procesal del Trabajo",
    "codigo_general_proceso": "Código General del Proceso",
    "cpaca": "Código de Procedimiento Administrativo y de lo Contencioso Administrativo",
    "estatuto_tributario": "Estatuto Tributario", "codigo_infancia": "Código de la Infancia y la Adolescencia",
    "codigo_nacional_policia": "Código Nacional de Seguridad y Convivencia Ciudadana",
    "codigo_disciplinario": "Código General Disciplinario", "estatuto_consumidor": "Estatuto del Consumidor",
    "decision_andina_486": "Decisión 486 de la Comisión de la Comunidad Andina",
}
KIND = {"ley": "Ley", "decreto": "Decreto", "acto_legislativo": "Acto Legislativo",
        "resolucion": "Resolución", "circular": "Circular", "acuerdo": "Acuerdo"}


def render(b: tuple) -> str:
    if b[0] in CODE_NAMES:
        return CODE_NAMES[b[0]]
    if b[0] == "jurisprudencia":
        return f"Sentencia {b[1]} de {b[2]}"
    return f"{KIND.get(b[0], b[0])} {b[1]} de {b[2]}"


def header_bodies(p: dict) -> list:
    return sorted(citations.bodies(citations.extract(p["texto"][:200])), key=str)


def top_headers(n: int):
    def f(ps):
        out = []
        for p in ps[:n]:
            for b in header_bodies(p)[:1]:
                if b not in out:
                    out.append(b)
        return out
    return f


def all_in_evidence(ps):
    s = set()
    for p in ps[:10]:
        s |= citations.bodies(citations.extract(p["texto"]))
    return sorted(s, key=str)


STRATEGIES = {"ninguna": lambda ps: [], "encabezado_top1": top_headers(1), "encabezado_top3": top_headers(3),
              "encabezado_top8": top_headers(8), "todas_en_evidencia": all_in_evidence}


def latest_run() -> Path:
    runs = sorted(p for p in (ROOT / "reports/member_b").iterdir() if (p / "submissions.jsonl").exists())
    return runs[-1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", type=Path, default=None)
    a = ap.parse_args()
    run = a.run or latest_run()
    subs = [json.loads(l) for l in (run / "submissions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    sample = {r["id"]: r for r in map(json.loads, (ROOT / "data/sample_50.jsonl").read_text(encoding="utf-8").splitlines())}

    # 1) techo de respaldo: cuerpos de legal_basis presentes en la evidencia recuperada
    tot = hit = items = items_hit = 0
    for s in subs:
        ref = citations.bodies(citations.extract(sample[s["id"]].get("legal_basis") or ""))
        if not ref:
            continue
        sup = set()
        for p in s["pasajes_recuperados"][:10]:
            sup |= citations.bodies(citations.extract(p["texto"]))
        items += 1
        tot += len(ref)
        hit += len(ref & sup)
        items_hit += bool(ref & sup)
    print(f"corrida: {run.name}")
    print(f"techo de respaldo (nivel cuerpo, como el evaluador): {hit}/{tot} = {hit / max(1, tot):.2f}; "
          f"items con >=1 norma correcta en evidencia: {items_hit}/{items}")

    # 2) puntaje de citas/abstencion por estrategia, con el evaluador oficial
    for name, fn in STRATEGIES.items():
        rows = []
        for s in subs:
            ps = [{"doc_id": p["doc_id"], "texto": p["texto"]} for p in s["pasajes_recuperados"]]
            ref = "; ".join(render(b) for b in fn(ps)) or "Evidencia recuperada."
            r = {"id": s["id"], "formato": s["formato"], "abstencion": False, "pasajes_recuperados": ps}
            if s["formato"] == "multiple_choice":
                r.update(respuesta_correcta="A", justificacion=f"Fundamento: {ref}.",
                         descarte_opciones={"B": "-", "C": "-", "D": "-"})
            elif s["formato"] == "semi_open":
                r.update(respuesta="-", palabras_clave=["-"], referencia_legal=ref)
            else:
                r.update(marco_normativo=ref, analisis="-", jurisprudencia="-", conclusion="-")
            rows.append(r)
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
            fh.write("\n".join(json.dumps(r, ensure_ascii=False) for r in rows))
        out = subprocess.run([sys.executable, str(ROOT / "scripts/evaluate.py"), "--submission", fh.name,
                              "--split", "sample"], capture_output=True, text=True, check=True).stdout
        rep = json.loads(out)
        c, ab = rep["citas"], rep["abstencion"]
        print(f"{name:20s} citas {c['puntos']:5.2f}/20  recall {c['recall_citas_ponderado']:.2f}  "
              f"sin_respaldo {c['tasa_sin_respaldo']:.2f}  citas/item {c['n_citadas'] / max(1, c['items_evaluados']):4.1f}  "
              f"| abstencion {ab['puntos']:4.2f}/10")
    print("Nota: cerradas fijas en 'A' y sin texto real: RAGAS y exactitud no se miden aqui.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
