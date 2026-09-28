# Member A seed audit

- Seed targets: **186**.
- Textos jurídicos completos dentro del ZIP oficial: **0**.
- Preguntas de desarrollo: **50**; `legal_basis` presente en **49/50**.
- `seed_targets.json` es inventario de qué/dónde buscar, no el corpus.

## Top seed targets por `items_del_banco`

| # | Norma | items_del_banco | menciones sample* | dónde buscar |
|---:|---|---:|---:|---|
| 1 | Constitucion | 90 | 6 | http://www.secretariasenado.gov.co/senado/basedoc/constitucion_politica_1991.html?q=Constitucion |
| 2 | Codigo general proceso | 65 | 4 | http://www.secretariasenado.gov.co/senado/basedoc/?q=Codigo%20general%20proceso |
| 3 | Codigo sustantivo trabajo | 37 | 4 | http://www.secretariasenado.gov.co/senado/basedoc/?q=Codigo%20sustantivo%20trabajo |
| 4 | Estatuto tributario | 35 | 0 | http://www.secretariasenado.gov.co/senado/basedoc/?q=Estatuto%20tributario |
| 5 | Decision andina 486 | 23 | 0 | http://www.secretariasenado.gov.co/senado/basedoc/?q=Decision%20andina%20486 |
| 6 | Estatuto consumidor | 13 | 2 | http://www.secretariasenado.gov.co/senado/basedoc/?q=Estatuto%20consumidor |
| 7 | Ley 80 de 1993 | 12 | 0 | https://www.suin-juriscol.gov.co/legislacion/?q=Ley%2080%20de%201993 |
| 8 | Ley 2220 de 2022 | 11 | 0 | https://www.suin-juriscol.gov.co/legislacion/?q=Ley%202220%20de%202022 |
| 9 | Decreto 2153 de 1992 | 10 | 1 | https://www.suin-juriscol.gov.co/legislacion/?q=Decreto%202153%20de%201992 |
| 10 | Sentencia C-355 de 2006 | 7 | 1 | https://www.corteconstitucional.gov.co/relatoria/?q=Sentencia%20C-355%20de%202006 |
| 11 | Ley 1116 de 2006 | 7 | 1 | https://www.suin-juriscol.gov.co/legislacion/?q=Ley%201116%20de%202006 |
| 12 | Ley 1581 de 2012 | 6 | 1 | https://www.suin-juriscol.gov.co/legislacion/?q=Ley%201581%20de%202012 |
| 13 | Codigo infancia | 5 | 0 | http://www.secretariasenado.gov.co/senado/basedoc/?q=Codigo%20infancia |
| 14 | Sentencia C-207 de 2019 | 4 | 0 | https://www.corteconstitucional.gov.co/relatoria/?q=Sentencia%20C-207%20de%202019 |
| 15 | Sentencia SL-3385 de 2022 | 4 | 0 | https://www.corteconstitucional.gov.co/relatoria/?q=Sentencia%20SL-3385%20de%202022 |
| 16 | Sentencia T-323 de 2024 | 4 | 0 | https://www.corteconstitucional.gov.co/relatoria/?q=Sentencia%20T-323%20de%202024 |
| 17 | Ley 1258 de 2008 | 4 | 0 | https://www.suin-juriscol.gov.co/legislacion/?q=Ley%201258%20de%202008 |
| 18 | Ley 1010 de 2006 | 3 | 1 | https://www.suin-juriscol.gov.co/legislacion/?q=Ley%201010%20de%202006 |
| 19 | Ley 1150 de 2007 | 3 | 1 | https://www.suin-juriscol.gov.co/legislacion/?q=Ley%201150%20de%202007 |
| 20 | Ley 1340 de 2009 | 3 | 1 | https://www.suin-juriscol.gov.co/legislacion/?q=Ley%201340%20de%202009 |
| 21 | Sentencia C-394 de 2017 | 3 | 0 | https://www.corteconstitucional.gov.co/relatoria/?q=Sentencia%20C-394%20de%202017 |
| 22 | Sentencia C-55 de 2022 | 3 | 0 | https://www.corteconstitucional.gov.co/relatoria/?q=Sentencia%20C-55%20de%202022 |
| 23 | Sentencia SU-315 de 2025 | 3 | 0 | https://www.corteconstitucional.gov.co/relatoria/?q=Sentencia%20SU-315%20de%202025 |
| 24 | Sentencia T-243 de 2018 | 3 | 0 | https://www.corteconstitucional.gov.co/relatoria/?q=Sentencia%20T-243%20de%202018 |
| 25 | Sentencia T-760 de 2008 | 3 | 0 | https://www.corteconstitucional.gov.co/relatoria/?q=Sentencia%20T-760%20de%202008 |
| 26 | Ley 153 de 1887 | 3 | 0 | https://www.suin-juriscol.gov.co/legislacion/?q=Ley%20153%20de%201887 |
| 27 | Ley 2437 de 2024 | 3 | 0 | https://www.suin-juriscol.gov.co/legislacion/?q=Ley%202437%20de%202024 |
| 28 | Ley 54 de 1990 | 3 | 0 | https://www.suin-juriscol.gov.co/legislacion/?q=Ley%2054%20de%201990 |
| 29 | Ley 979 de 2005 | 3 | 0 | https://www.suin-juriscol.gov.co/legislacion/?q=Ley%20979%20de%202005 |
| 30 | Decreto 1563 de 2012 | 2 | 0 | https://www.suin-juriscol.gov.co/legislacion/?q=Decreto%201563%20de%202012 |

\* Conteo auxiliar por coincidencia de nombre/alias en `legal_basis`; no sustituye revisión jurídica.

## Hallazgo operativo

El ZIP no trae una carpeta de normas ni PDFs/HTML jurídicos. El trabajo real del Integrante A empieza descargando los textos oficiales, preservando URL, versión/fecha, hash y estructura.

## Ruido del sample

`legal_basis` sirve para cobertura/evaluación, pero no debe tratarse automáticamente como dato canónico. Hay entradas incompletas como `Doctrina.` y referencias que requieren verificación. El corpus debe basarse en las fuentes jurídicas oficiales.