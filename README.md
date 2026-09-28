# KingsCode Nvidia

KingsCode v0.5: sistema de recuperación jurídica para el Hackathon AI Week 2026. La capa del Integrante A incluye adquisición de fuentes oficiales, parsing estructural, grafo, BM25 y adaptadores abiertos de embeddings/RRF/reranking.

## Empezar

- [Guía del proyecto](START_HERE.md)
- [Estado y arquitectura](docs/KINGSCODE_MASTER_KNOWLEDGE.md)
- [Corpus y resultados medidos](CORPUS.md)
- [Instalación, ejecución e integración con B](docs/MEMBER_A_RUNBOOK.md)
- [Verificaciones realizadas](docs/VERIFICATION.md)
- [Harness de B sin GPU](docs/MEMBER_B_RUNBOOK.md)
- [Preparación y comandos para la 4090](docs/GPU_DAY_RUNBOOK.md)
- [Revisiones, licencias y acceso de modelos](docs/MODEL_LOCKS_GATE2.md)
- [Contexto para Claude Code](CLAUDE.md), [hallazgos de B](docs/B_FINDINGS_2026-09-28.md) y [plan de extensión](docs/B_EXTENSION_PLAN.md)

## Interfaz gráfica

`interfaz/app.py` (Streamlit) consulta el pipeline real de extremo a extremo (`kingscode.reasoning.Pipeline` + `kingscode.Retriever`), con la identidad visual de Software Colombia. Requiere `corpus/` construido:

```powershell
.venv/Scripts/python.exe -m pip install -r requirements-ui.txt
.venv/Scripts/python.exe -m streamlit run interfaz/app.py
```

## Comando único de reproducción (sample_50)

```bash
./run.sh                 # requiere corpus/ ya presente (ver "Corpus e índice")
./run.sh --acquire       # además intenta construir corpus/ desde las fuentes oficiales (red)
```

Instala dependencias, corre la suite de tests, ejecuta Gate 1B (BM25 + backend determinista, sin GPU) sobre `data/sample_50.jsonl` y publica el puntaje oficial con `scripts/evaluate.py`. En contenedor limpio:

```bash
docker build -t kingscode .
docker run --rm -v "$(pwd)/corpus:/app/corpus:ro" kingscode
```

No requiere GPU ni descarga pesos: es el piso reproducible y determinista (decoder real/bakeoff se corren aparte en la 4090, ver `docs/GPU_DAY_RUNBOOK.md`).

## Corpus e índice

Pendiente: publicar el corpus enriquecido y el índice vectorial serializado bajo licencia abierta en un enlace de descarga directa (Google Drive/OneDrive/Zenodo) y declarar aquí el enlace, conforme a la sección 9.3 del enunciado. Mientras tanto, `./run.sh --acquire` reconstruye `corpus/` desde las fuentes oficiales listadas en `data/seed_targets.json` y `CORPUS.md`.

## Después de clonar

El repositorio incluye código, configuración, inventario de fuentes, manifest y reportes. `corpus/`, `models/`, `.venv/` y `tmp/` permanecen fuera de Git.

En Windows, desde la raíz del proyecto:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-knowledge.txt
.venv/Scripts/python.exe tools/member_a.py acquire
.venv/Scripts/python.exe tools/member_a.py reproduce
.venv/Scripts/python.exe -m unittest discover -s tests -v
```

La adquisición requiere red y `curl` con verificación TLS. Una descarga nueva puede reflejar cambios en las fuentes; para reproducir exactamente los hashes publicados debe usarse el snapshot raw conservado por el equipo. El runbook explica cómo preparar los pesos y ejecutar el benchmark neuronal completo en la GPU objetivo.

Los archivos oficiales se conservan byte a byte. Gate 1B está implementado con dummy y se ejecuta con `.venv/Scripts/python.exe tools/member_b.py smoke` después de disponer del corpus. Decoder real, benchmark neuronal completo, resolución de fuentes pendientes y freeze competitivo siguen pendientes.

Gate 2-Prep añade la infraestructura de ejecución real y comparación de modelos, **sin ejecutar pruebas ni smokes por instrucción del usuario**. No hay resultados nuevos de GPU. Para llegar a la 4090 con el mismo corpus, seguir el runbook GPU y transferir el snapshot conservado, en lugar de volver a adquirir fuentes.
