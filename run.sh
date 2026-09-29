#!/usr/bin/env bash
# Comando único de reproducción sobre las 50 preguntas de muestra (enunciado
# 6.2 "reproducibilidad", 2 pts: "el repositorio se ejecuta desde cero
# mediante un único comando, en contenedor limpio, sobre las preguntas de
# muestra"). No descarga pesos ni requiere GPU: corre Gate 1B (BM25 + backend
# determinista) de punta a punta y emite el puntaje oficial.
#
# Uso:
#   ./run.sh                 # instala deps, exige corpus/ ya construido o publicado
#   ./run.sh --acquire       # además intenta construir corpus/ desde cero (red, lento, no determinista)
#   ./run.sh --skip-install  # reutiliza el entorno Python activo, no reinstala requirements
#   ./run.sh --fixture       # sin corpus: pasajes oficiales de tests/fixtures (verifica la mecánica, NO es un puntaje)
#
# El corpus (corpus/raw, corpus/clean, passages.jsonl, grafo, índice BM25) NO
# se versiona en git (ver .gitignore) por tamaño. Publicado en la nube según
# la sección "## Corpus e índice" del README; descárguelo y descomprímalo en
# ./corpus antes de correr sin --acquire, o pase --acquire para reconstruirlo
# desde las fuentes oficiales (requiere red; puede fallar por certificados o
# disponibilidad del sitio de origen, ver docs/MEMBER_A_RUNBOOK.md).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

ACQUIRE=0
SKIP_INSTALL=0
FIXTURE=0
for arg in "$@"; do
  case "$arg" in
    --acquire) ACQUIRE=1 ;;
    --skip-install) SKIP_INSTALL=1 ;;
    --fixture) FIXTURE=1 ;;
    *) echo "Argumento desconocido: $arg" >&2; exit 2 ;;
  esac
done

# Delivery command runs B's suites: some A tests need local, unversioned artifacts
# (tmp/ pools, corpus bytes) and would always fail in a clean container. The full
# suite is still run separately: python -m unittest discover -s tests -v
b_tests() {
  python -m unittest discover -s tests -p "test_reasoning.py"
  python -m unittest discover -s tests -p "test_member_b_v*.py"
}

PYTHON="${PYTHON:-python3}"
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python

if [ "$SKIP_INSTALL" -eq 0 ]; then
  if [ ! -d .venv ]; then
    "$PYTHON" -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate
  python -m pip install --upgrade pip
  python -m pip install -r requirements-knowledge.txt
fi

if [ "$FIXTURE" -eq 1 ]; then
  echo "== Modo fixture: tests de B + corrida por lotes de sample_50 con pasajes de fixtures (no es un puntaje competitivo) =="
  b_tests
  RUN_DIR="runs/fixture_$(date +%Y%m%d_%H%M%S)"
  python tools/member_b.py batch --fixture-evidence --input data/sample_50.jsonl --run-dir "$RUN_DIR" --fresh
  python scripts/evaluate.py --submission "$RUN_DIR/submissions.jsonl" --split sample
  echo "Reproducción con el corpus completo: PENDIENTE (requiere el snapshot congelado de A)."
  exit 0
fi

if [ ! -f corpus/manifest.json ]; then
  if [ "$ACQUIRE" -eq 1 ]; then
    echo "== Construyendo corpus desde fuentes oficiales (red, puede tardar) =="
    python tools/member_a.py acquire
    python tools/member_a.py reproduce
  else
    echo "No existe corpus/manifest.json." >&2
    echo "Descargue el corpus publicado (sección '## Corpus e índice' del README) en ./corpus," >&2
    echo "o vuelva a correr con --acquire para reconstruirlo desde las fuentes oficiales." >&2
    exit 1
  fi
fi

echo "== Tests de B =="
b_tests

echo "== Gate 1B: pipeline determinista (BM25 + backend dummy) sobre sample_50 =="
python tools/member_b.py smoke

RUN_DIR=$(python - <<'PY'
import json, pathlib
runs = sorted((pathlib.Path("reports/member_b")).iterdir(), key=lambda p: p.stat().st_mtime)
print(runs[-1])
PY
)
echo "== Puntaje oficial (sin --ragas; requiere OPENROUTER_API_KEY en scripts/.env para el juez de texto libre) =="
python scripts/evaluate.py --submission "$RUN_DIR/submissions.jsonl" --split sample
