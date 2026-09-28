---
description: Medir el estado actual de B en la muestra (tests, smoke, techo de citas)
---
Sin editar código:
1. `python -m unittest discover -s tests -v` y resume fallos.
2. `python tools/member_b.py smoke` y extrae del reporte: cerradas, citas, abstención, total, errores de validación, abstenciones por razón, latencia p50.
3. `python tools/analyze_citation_ceiling.py` sobre esa corrida.
4. Compara con la corrida anterior en reports/member_b/ y con la línea base 5,00/50.
Entrega una tabla y tres observaciones concretas. No uses --ragas.
