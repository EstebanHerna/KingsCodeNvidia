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
