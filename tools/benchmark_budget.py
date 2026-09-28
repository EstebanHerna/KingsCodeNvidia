#!/usr/bin/env python3
"""Proyecta si la latencia medida cumple el presupuesto de 992 preguntas / 6 horas."""
import argparse

p = argparse.ArgumentParser()
p.add_argument("--seconds-per-question", type=float, required=True)
p.add_argument("--questions", type=int, default=992)
p.add_argument("--hours", type=float, default=6.0)
a = p.parse_args()

total_seconds = a.seconds_per_question * a.questions
budget_seconds = a.hours * 3600
print(f"Latencia media: {a.seconds_per_question:.3f} s/pregunta")
print(f"Tiempo proyectado: {total_seconds/3600:.2f} h para {a.questions} preguntas")
print(f"Presupuesto: {a.hours:.2f} h")
print(f"Margen: {(budget_seconds-total_seconds)/3600:.2f} h")
print("OK" if total_seconds <= budget_seconds else "NO CUMPLE")
