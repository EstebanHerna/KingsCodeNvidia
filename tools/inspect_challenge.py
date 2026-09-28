#!/usr/bin/env python3
"""Resumen reproducible y priorización del material oficial de Hackathon 2026."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = [json.loads(x) for x in (ROOT / 'data/sample_50.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
seed = json.loads((ROOT / 'data/seed_targets.json').read_text(encoding='utf-8'))

print('MUESTRA')
print('  total:', len(rows))
print('  formatos:', dict(Counter(r['formato'] for r in rows)))
print('  areas:')
for area, n in Counter(r['area'] for r in rows).most_common():
    print(f'    {n:>2} | {area}')
print('  complejidad:', dict(Counter(str(r.get('complejidad')) for r in rows)))
print('  subtareas:')
for st, n in Counter(str(r.get('sub_tarea')) for r in rows).most_common():
    print(f'    {n:>2} | {st}')

print('\nSEED TARGETS')
docs = sorted(seed.get('documentos', []), key=lambda x: x.get('items_del_banco', 0), reverse=True)
print('  seed:', seed.get('seed'))
print('  documentos:', len(docs))
print('  suma items_del_banco:', sum(d.get('items_del_banco', 0) for d in docs))
print('\nTOP 20 por items_del_banco')
for i, d in enumerate(docs[:20], 1):
    print(f"  {i:>2}. {d.get('items_del_banco',0):>3} | {d.get('norma')}")
print('\nCOBERTURA ACUMULADA (conteo seed, no preguntas únicas)')
for k in (5, 10, 20, 50):
    print(f"  top-{k}: {sum(d.get('items_del_banco',0) for d in docs[:k])}")
