"""Generate the corpus report from measured artifacts, never from QA answers."""
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT, read_json


def main():
    m = read_json(ROOT / "corpus/manifest.json")
    b = read_json(ROOT / "reports/retrieval_bm25.json")
    if b["corpus_hashes"] != m["hashes"]:
        raise RuntimeError("Benchmark is stale; run benchmark before documenting")
    docs = m["documentos"]
    hosts = Counter(d["fuente"] for d in docs)
    areas = Counter(a for d in docs for a in d["areas"])
    lines = ["# CORPUS — KingsCode / Integrante A", "", f"Snapshot `{m['version']}`, parser `{m['parser_version']}`. Estado: baseline local previo a integración GPU y freeze competitivo.", "",
             "## Inventario medido", "",
             f"- {m['n_documentos']} documentos oficiales adquiridos y parseados; {len(m['failures'])} objetivos pendientes, registrados sin sustituir su identidad.",
             f"- {m['n_fragmentos']} pasajes conservados; {m['n_indexed']} elegibles para recuperación. Los demás son texto histórico explícito o numeraciones ambiguas.",
             f"- {m['n_nodes']} nodos y {m['n_edges']} relaciones con evidencia textual verificable.",
             "- Inventario original: 186 objetivos oficiales; configuración ampliada a 191 fuentes objetivo, sin indexar preguntas, respuestas ni etiquetas de evaluación.", "",
             "| Institución | Documentos |", "|---|---:|"]
    lines += [f"| {h} | {n} |" for h, n in sorted(hosts.items())]
    lines += ["", "| Área declarada en inventario | Documentos |", "|---|---:|"]
    lines += [f"| {a} | {n} |" for a, n in sorted(areas.items())]
    lines += ["", "Las áreas pueden solaparse; son metadatos de inventario y no juicios de relevancia de cada pasaje.", "",
              "## Procedencia y procesamiento", "",
              "Cada documento conserva URL solicitada/final, institución, instante UTC de consulta, HTTP 200, TLS verificado, bytes originales y SHA-256. El manifest registra raw, clean y sus hashes. Se conservan originales en `corpus/raw`, texto en `corpus/clean`, pasajes en `corpus/passages.jsonl` y grafo en `corpus/graph`.", "",
              "El parser extrae bloques del contenedor jurídico y conserva texto fuera de párrafos. El artículo es la unidad principal, con jerarquía y fragmentación por párrafo/oración cuando supera 3.600 caracteres. Los encabezados se incluyen como `text_prefix`; el resto corresponde exactamente a `[clean_start:clean_end]` en caracteres Unicode del clean. PDF: se registran páginas; Decisión CAN 486 omite la portada sin texto utilizable, pero conserva el documento original completo. Se revisaron visualmente páginas de ambos PDF.", "",
              "Las reformas citadas se mantienen bajo el artículo reformador cuando la estructura es inequívoca. Los grupos con números de artículo repetidos quedan conservados y excluidos de los índices: no se escoge automáticamente una versión ni se atribuye un anexo a la norma principal. `retrieval_eligible` e `index_exclusion_reasons` explican la exclusión. `is_current_text=null` significa vigencia no certificada. Se requiere revisar estas ambigüedades antes del freeze.", "",
              "El grafo representa norma/sentencia, sección, artículo, parágrafo y numeral. Genera `CONTIENE`, `CITA`, `REMITE_A` y patrones explícitos de `MODIFICA`/`DEROGA`. Los demás tipos y tags jurídicos quedan reservados; no se infieren relaciones jurídicas por similitud. Nodos externos sin texto no se recuperan como evidencia.", "",
              "## Retrieval y resultados de desarrollo", "",
              "BM25 usa k1=1,2 y b=0,75, normalización de acentos y desempate estable. La API pública es `retrieve(question, k=8, graph_mode=\"auto\")`. RRF, dense y reranker están implementados con Qwen3 abierto de 0,6B y commits fijos. La prueba neuronal usa pesos reales sobre dos pasajes oficiales; el índice denso completo y su benchmark quedan pendientes para la 4090.", "",
              f"De las 50 preguntas, {b['coverage']['evaluable_questions']} tienen referencias extraíbles y {b['coverage']['fully_covered_questions']} cuentan con todas sus referencias en el índice. Cobertura macro de referencias: {b['coverage']['macro_target_coverage']:.2%}. Las otras preguntas no cuentan como aciertos automáticos.", "",
              "| BM25 / grafo | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 |", "|---|---:|---:|---:|---:|---:|---:|"]
    for mode, r in b["runs"].items():
        lines.append(f"| {mode.upper()} | {r['Recall@1']:.4f} | {r['Recall@3']:.4f} | {r['Recall@5']:.4f} | {r['Recall@10']:.4f} | {r['MRR@10']:.4f} | {r['nDCG@10_unique_targets']:.4f} |")
    lines += ["", "La métrica compara identidad canónica de norma y artículo, no menciones a otra norma. `legal_basis` es un proxy ruidoso, no relevancia jurídica validada ni score oficial end-to-end. Se conservan etiquetas ambiguas originales (incluidos IDs 58 y 308) en la auditoría, separada del índice. Los desgloses por área/formato, latencias y predicciones están en `reports/retrieval_bm25*.json*`. AUTO no se activó en este sample: su igualdad con OFF no prueba beneficio del routing. ON es una ablation forzada, no la nueva política por defecto.", "",
              "## Reproducción y verificación", "",
              "Consultar [runbook](docs/MEMBER_A_RUNBOOK.md) para comandos, integración con B y pruebas. `tools/member_a.py reproduce` reconstruye desde el snapshot raw sin red. Volver a descargar puede producir versiones nuevas y requiere otro freeze. `tools/verify_member_a_second.py` reconstruye en otra carpeta, compara hashes byte a byte y recalcula métricas y rankings independientemente. Los reportes de verificación identifican el hash que comprobaron.", "",
              "Los 19 archivos oficiales se preservan. No se han generado submissions ni se afirma score del decoder. El equipo aún debe integrar B, ejecutar benchmark neuronal completo, revisar vigencia y exclusiones, escoger la licencia del procesamiento propio y publicar el paquete final. El acceso público a las fuentes no implica una licencia uniforme de redistribución. `enlace_nube=null`: corpus local, no publicado.", "",
              "## Hashes del snapshot", "", "| Artefacto | SHA-256 |", "|---|---|"]
    lines += [f"| `{name}` | `{value}` |" for name, value in m["hashes"].items()]
    lines += [f"| `index/bm25.json` | `{m['bm25_sha256']}` |", "", "## Fuentes completas", "", "Los hashes, fechas exactas, números, años, cuerpos canónicos y rutas están en [corpus_manifest.json](corpus_manifest.json).", "", "| Documento | Institución | Pasajes | Indexados | Fecha UTC | Fuente |", "|---|---|---:|---:|---|---|"]
    for d in docs:
        name = d["norm_name"].replace("|", "/")
        lines.append(f"| {name} | {d['fuente']} | {d['n_fragmentos']} | {d['n_indexed']} | {d['fecha_consulta']} | [Oficial]({d['source_url']}) |")
    lines += ["", "## Objetivos pendientes", "", "Los errores detallados se conservan en el manifest y en `corpus/acquisition.json`. Una coincidencia aproximada en año o número no se acepta como la misma norma.", ""]
    lines += [f"- `{d['doc_id']}` — {d['stage']}." for d in m["failures"]]
    lines += ["", "## Ambigüedades excluidas", "", "| Documento | Numeraciones repetidas | Pasajes afectados |", "|---|---:|---:|"]
    lines += [f"| `{d['doc_id']}` | {len(d['duplicate_headings'])} | {d['n_ambiguous_fragments']} |" for d in docs if d["duplicate_headings"]]
    (ROOT / "CORPUS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("CORPUS.md updated from matching manifest/benchmark")


if __name__ == "__main__":
    main()
