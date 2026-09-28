# Contenedor limpio para la verificación de reproducibilidad (enunciado 6.2,
# 2 pts): construye el entorno e intenta correr Gate 1B (BM25 + backend
# determinista, sin GPU) sobre data/sample_50.jsonl con un único comando.
#
#   docker build -t kingscode .
#   docker run --rm -v "$(pwd)/corpus:/app/corpus:ro" kingscode
#
# El corpus no viaja en la imagen (no está en git, ver .gitignore): móntelo
# desde el snapshot publicado en la nube (sección "## Corpus e índice" del
# README), o pase ACQUIRE=1 para que el contenedor intente construirlo desde
# las fuentes oficiales (requiere red saliente desde el contenedor).
FROM python:3.12-slim

WORKDIR /app

COPY requirements-knowledge.txt ./
RUN pip install --no-cache-dir -r requirements-knowledge.txt

COPY . .
RUN chmod +x run.sh

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ACQUIRE=0

ENTRYPOINT ["sh", "-c", "if [ \"$ACQUIRE\" = \"1\" ]; then ./run.sh --skip-install --acquire; else ./run.sh --skip-install; fi"]
