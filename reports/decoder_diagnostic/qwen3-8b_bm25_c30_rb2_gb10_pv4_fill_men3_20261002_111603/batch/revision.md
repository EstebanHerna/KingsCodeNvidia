# Revisión por pregunta

## 24 · semi_open

**Pregunta:** ¿Cuáles son los elementos esenciales de validez de un contrato?

**Medición:** cita=sin_ref_parseable · legal_basis=None

**Respuesta final:**
```json
{
  "respuesta": "Los elementos esenciales de validez de un contrato incluyen el consentimiento libre y espontáneo de los contrayentes, la capacidad de las partes y el cumplimiento de las formalidades legales. Estos elementos son fundamentales para que un contrato tenga efectos jurídicos, según lo establecido en la doctrina y aplicado en el derecho colombiano.",
  "palabras_clave": [
    "elementos esenciales",
    "validez",
    "contrato",
    "derecho colombiano"
  ],
  "referencia_legal": "Sentencia SU-214 de 2016; artículo 1045 del Código de Comercio; artículo 1 de la Ley 50 de 1990; artículo 1501 del Código Civil; artículo 23 del Código Sustantivo del Trabajo; Constitución Política; Sentencia C-577 de 2011; Sentencia C-397 de 2006"
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "respuesta": "Los elementos esenciales de validez de un contrato incluyen el consentimiento libre y espontáneo de los contrayentes, la capacidad de las partes y el cumplimiento de las formalidades legales. Estos elementos son fundamentales para que un contrato tenga efectos jurídicos, según lo establecido en la doctrina y aplicado en el derecho colombiano.",
  "palabras_clave": ["elementos esenciales", "validez", "contrato", "derecho colombiano"],
  "referencia_legal": "Sentencia SU-214 de 2016",
  "pasajes_usados": [
    "sentencia_su_214_de_2016:00248:1284d90b7401",
    "sentencia_su_214_de_2016:00240:6d3bf6eb0ccc"
  ]
}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 1 → después 12 · reparación {} · construidas ['Sentencia SU-214 de 2016', 'artículo 1045 del Código de Comercio', 'artículo 1 de la Ley 50 de 1990', 'artículo 1501 del Código Civil', 'artículo 23 del Código Sustantivo del Trabajo', 'Constitución Política', 'Sentencia C-577 de 2011', 'Sentencia C-397 de 2006']
**Pasajes declarados por el modelo:** ['sentencia_su_214_de_2016:00248:1284d90b7401', 'sentencia_su_214_de_2016:00240:6d3bf6eb0ccc']
**Evidencia:**
1. `sentencia_su_214_de_2016:00248:1284d90b7401` — Sentencia SU-214 de 2016 art. None
2. `codigo_comercio:01106:f65f7780a57d` — Código de Comercio (Decreto 410 de 1971) art. 1045
3. `sentencia_su_214_de_2016:00214:e6da86aa9dec` — Sentencia SU-214 de 2016 art. None
4. `ley_50_de_1990:00000:72aa613d77a5` — Ley 50 de 1990 art. 1
5. `sentencia_su_214_de_2016:00240:6d3bf6eb0ccc` — Sentencia SU-214 de 2016 art. None
6. `codigo_civil:01499:977520c226b2` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1501
7. `codigo_sustantivo_trabajo:00022:d44874b99a5a` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 23
8. `sentencia_c_134_de_2019:00015:f9b6a445d894` — Sentencia C-134 de 2019 art. None
*Tokens 6246→220 · generación 9861.703700007638 ms · retrieval 7.389799997326918 ms · grafo off*

## 51 · multiple_choice · ✔ correcta

**Pregunta:** ¿En cuál de los siguientes casos procede la acción judicial de grupo? 

- A: Cuando un grupo de personas busca proteger derechos fundamentales individuales de aplicación inmediata.
- B: Cuando un grupo de ciudadanos busca defender el interés colectivo ambiental o del espacio público.
- C: Cuando un conjunto de personas resulta afectado por un mismo hecho que les causa perjuicios individuales derivados de una causa común.
- D: Cuando se pretende declarar la inconstitucionalidad de una norma con fuerza de ley.

**Medición:** cita=cita_ok · legal_basis=Constitución Política, artículo 88; Ley 472 de 1998, artículos 3 y 46.

**Respuesta final:**
```json
{
  "respuesta_correcta": "C",
  "justificacion": "La acción de grupo se define como un mecanismo judicial que permite a un conjunto de personas afectadas por un mismo hecho, que les causa perjuicios individuales derivados de una causa común, presentar una demanda colectiva. Esto se fundamenta en la Sentencia SU-429 de 2024, donde se menciona que la acción de grupo se aplica en casos donde se persigue el reconocimiento y pago de un daño atribuible al Estado por su participación en un crimen de lesa humanidad. Además, se establece que la acción de grupo tiene como finalidad la reparación integral de las víctimas de desplazamiento forzado, lo cual implica que el daño afecta a un conjunto de personas con perjuicios individuales derivados de una causa común. Por lo tanto, la opción C se alinea con esta definición. Fundamento normativo: Sentencia SU-214 de 2016; Sentencia SU-455 de 2020; Sentencia C-259 de 2015; Constitución Política; Ley 472 de 1998; Ley 270 de 1996.",
  "descarte_opciones": {
    "A": "La opción A se refiere a la protección de derechos fundamentales individuales de aplicación inmediata, lo cual no se corresponde con la definición de la acción de grupo, que se enfoca en perjuicios colectivos.",
    "B": "La opción B menciona el interés colectivo ambiental o del espacio público, lo cual no se aborda en la evidencia proporcionada, que se centra en casos de desplazamiento forzado y reparación integral.",
    "D": "La opción D se refiere a la declaración de inconstitucionalidad de una norma con fuerza de ley, lo cual no es el enfoque de la acción de grupo, que se centra en la protección de derechos fundamentales de un grupo de personas afectadas por un mismo hecho."
  }
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "justificacion": "La acción de grupo se define como un mecanismo judicial que permite a un conjunto de personas afectadas por un mismo hecho, que les causa perjuicios individuales derivados de una causa común, presentar una demanda colectiva. Esto se fundamenta en la Sentencia SU-429 de 2024, donde se menciona que la acción de grupo se aplica en casos donde se persigue el reconocimiento y pago de un daño atribuible al Estado por su participación en un crimen de lesa humanidad. Además, se establece que la acción de grupo tiene como finalidad la reparación integral de las víctimas de desplazamiento forzado, lo cual implica que el daño afecta a un conjunto de personas con perjuicios individuales derivados de una causa común. Por lo tanto, la opción C se alinea con esta definición.",
  "respuesta_correcta": "C",
  "descarte_opciones": {
    "A": "La opción A se refiere a la protección de derechos fundamentales individuales de aplicación inmediata, lo cual no se corresponde con la definición de la acción de grupo, que se enfoca en perjuicios colectivos.",
    "B": "La opción B menciona el interés colectivo ambiental o del espacio público, lo cual no se aborda en la evidencia proporcionada, que se centra en casos de desplazamiento forzado y reparación integral.",
    "D": "La opción D se refiere a la declaración de inconstitucionalidad de una norma con fuerza de ley, lo cual no es el enfoque de la acción de grupo, que se centra en la protección de derechos fundamentales de un grupo de personas afectadas por un mismo hecho."
  },
  "pasajes_usados": [
    "sentencia_su_429_de_2024:00037:107e51e4d8bb",
    "sentencia_su_429_de_2024:00061:860f569e5e39",
    "sentencia_su_429_de_2024:00001:c6f8eb4a737f"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 1 → después 7 · reparación {} · construidas ['Sentencia SU-429 de 2024', 'Sentencia SU-214 de 2016', 'Sentencia SU-455 de 2020', 'Sentencia C-259 de 2015', 'Constitución Política', 'Ley 472 de 1998', 'Ley 270 de 1996']
**Pasajes declarados por el modelo:** ['sentencia_su_429_de_2024:00037:107e51e4d8bb', 'sentencia_su_429_de_2024:00061:860f569e5e39', 'sentencia_su_429_de_2024:00001:c6f8eb4a737f']
**Evidencia:**
1. `sentencia_su_214_de_2016:00237:d3bc4e76d291` — Sentencia SU-214 de 2016 art. None
2. `sentencia_su_429_de_2024:00022:7edfe1f0dc75` — Sentencia SU-429 de 2024 art. None
3. `sentencia_su_429_de_2024:00037:107e51e4d8bb` — Sentencia SU-429 de 2024 art. None
4. `sentencia_su_429_de_2024:00061:860f569e5e39` — Sentencia SU-429 de 2024 art. None
5. `sentencia_su_429_de_2024:00001:c6f8eb4a737f` — Sentencia SU-429 de 2024 art. None
6. `sentencia_su_455_de_2020:00015:26ded4ad04e0` — Sentencia SU-455 de 2020 art. None
7. `sentencia_c_259_de_2015:00009:1a0174281fcf` — Sentencia C-259 de 2015 art. None
8. `sentencia_su_429_de_2024:00011:94c8dade2af9` — Sentencia SU-429 de 2024 art. None
*Tokens 6835→514 · generación 22003.697599997395 ms · retrieval 83.43569999851752 ms · grafo off*

## 58 · multiple_choice · ✘ esperada A

**Pregunta:** ¿Qué normativa regula las actuaciones jurisdiccionales adelantadas ante la SIC?

- A: Ley 1564 de 2002
- B: Ley 270 de 1996
- C: Ley 472 de 1998
- D: Ley 906 de 2004

**Medición:** cita=cita_ok · legal_basis=Ley 1564 de 2002 (El Estatuto del Consumidor). 

**Respuesta final:**
```json
{
  "respuesta_correcta": "D",
  "justificacion": "La pregunta se refiere a la normativa que regula las actuaciones jurisdiccionales adelantadas ante la SIC. Además, se menciona que las superintendencias, incluida la SIC, ejercen funciones de vigilancia y control, y en algunos casos, funciones jurisdiccionales en determinados ámbitos definidos en la ley. Sin embargo, no se menciona directamente una norma específica que regule las actuaciones jurisdiccionales ante la SIC. Por lo tanto, no se puede determinar con base en la evidencia proporcionada. Fundamento normativo: Sentencia C-748 de 2011; artículo 1 del Código General del Proceso; Sentencia T-232 de 2025; artículo 153 del Código de la Infancia y la Adolescencia; Sentencia SU-429 de 2024; Sentencia C-1011 de 2008; Decreto 2153 de 1992; Constitución Política.",
  "descarte_opciones": {
    "A": "La no se menciona en la evidencia como normativa que regule las actuaciones jurisdiccionales ante la SIC.",
    "B": "La no se menciona en la evidencia como normativa que regule las actuaciones jurisdiccionales ante la SIC.",
    "C": "La no se menciona en la evidencia como normativa que regule las actuaciones jurisdiccionales ante la SIC."
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"La pregunta se refiere a la normativa que regula las actuaciones jurisdiccionales adelantadas ante la SIC. En la evidencia, se menciona que la SIC es un organismo de carácter técnico adscrito al Ministerio de Desarrollo Económico, según el artículo 1° del Decreto 2153 de 1992. Además, se menciona que las superintendencias, incluida la SIC, ejercen funciones de vigilancia y control, y en algunos casos, funciones jurisdiccionales en determinados ámbitos definidos en la ley. Sin embargo, no se menciona directamente una norma específica que regule las actuaciones jurisdiccionales ante la SIC. Por lo tanto, no se puede determinar con base en la evidencia proporcionada.","respuesta_correcta":"D","descarte_opciones":{"A":"La Ley 1564 de 2002 no se menciona en la evidencia como normativa que regule las actuaciones jurisdiccionales ante la SIC.","B":"La Ley 270 de 1996 no se menciona en la evidencia como normativa que regule las actuaciones jurisdiccionales ante la SIC.","C":"La Ley 472 de 1998 no se menciona en la evidencia como normativa que regule las actuaciones jurisdiccionales ante la SIC."},"pasajes_usados":["sentencia_c_748_de_2011:00226:c8d13ad22037"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 5 → después 10 · reparación {'suppressed_fragment': 3, 'suppressed_sentence': 4} · construidas ['Sentencia C-748 de 2011', 'artículo 1 del Código General del Proceso', 'Sentencia T-232 de 2025', 'artículo 153 del Código de la Infancia y la Adolescencia', 'Sentencia SU-429 de 2024', 'Sentencia C-1011 de 2008', 'Decreto 2153 de 1992', 'Constitución Política']
**Pasajes declarados por el modelo:** ['sentencia_c_748_de_2011:00226:c8d13ad22037']
**Evidencia:**
1. `codigo_general_proceso:00000:7e5b524b91ca` — Código General del Proceso (Ley 1564 de 2012) art. 1
2. `sentencia_t_232_de_2025:00013:9facb594dde9` — Sentencia T-232 de 2025 art. None
3. `sentencia_c_748_de_2011:00226:c8d13ad22037` — Sentencia C-748 de 2011 art. None
4. `codigo_infancia:00160:32878d3155d7` — Código de la Infancia y la Adolescencia (Ley 1098 de 2006) art. 153
5. `sentencia_su_429_de_2024:00050:11c63eee45e9` — Sentencia SU-429 de 2024 art. None
6. `codigo_general_proceso:00279:ce2c4c6e91fd` — Código General del Proceso (Ley 1564 de 2012) art. 275
7. `codigo_disciplinario:00154:59d343ebe57f` — Código General Disciplinario (Ley 1952 de 2019) art. 153
8. `codigo_procedimiento_penal:00023:01eff21653ac` — Código de Procedimiento Penal (Ley 906 de 2004) art. 24
*Tokens 4733→363 · generación 13986.12589998811 ms · retrieval 61.27320000086911 ms · grafo off*

## 60 · multiple_choice · ✔ correcta

**Pregunta:** ¿Cuál de las siguientes afirmaciones refleja correctamente el principio del juez natural en el proceso judicial colombiano?

- A: Nadie puede ser juzgado sino por un juez o tribunal competente, previamente establecido por la ley.
- B: El juez natural es aquel designado discrecionalmente por el Consejo Superior de la Judicatura.
- C: El principio del juez natural se refiere únicamente a la imparcialidad del funcionario, no a su competencia.
- D: Toda persona puede ser juzgada por cualquier autoridad que tenga competencia general sobre el asunto.

**Medición:** cita=cita_ok · legal_basis=Constitución Política de Colombia, artículo 29; Código General del Proceso (Ley 1564 de 2012), artículo 6.

**Respuesta final:**
```json
{
  "respuesta_correcta": "A",
  "justificacion": "Además, se menciona que la garantía del juez natural es un elemento constitutivo del derecho al debido proceso, y que el juez natural debe ser un humano, no una máquina. Por otro lado, la Sentencia SU-500 de 2015 afirma que el juez natural no puede ser desplazado por el juez constitucional, lo que reafirma la importancia de la competencia del juez natural. La opción A refleja correctamente esta idea, ya que establece que nadie puede ser juzgado sino por un juez o tribunal competente, previamente establecido por la ley. Las opciones B, C y D son incorrectas, ya que B contradice la idea de que el juez natural debe ser designado por la ley, C limita el principio del juez natural solo a la imparcialidad, y D contradice el principio de que el juez natural debe ser competente y previamente establecido. Fundamento normativo: Sentencia T-323 de 2024; Sentencia T-1001 de 2001; artículo 48 del Código General del Proceso; artículo 328 de la Ley 2452 de 2025; Constitución Política; Ley 270 de 1996; Sentencia C-543 de 1992.",
  "descarte_opciones": {
    "B": "Contradice la idea de que el juez natural debe ser designado por la ley.",
    "C": "Limita el principio del juez natural solo a la imparcialidad, ignorando la competencia.",
    "D": "Contradice el principio de que el juez natural debe ser competente y previamente establecido."
  }
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "justificacion": "La Sentencia T-323 de 2024 establece que el juez natural es aquel a quien la Constitución o la ley le ha atribuido el conocimiento de determinado asunto. Además, se menciona que la garantía del juez natural es un elemento constitutivo del derecho al debido proceso, y que el juez natural debe ser un humano, no una máquina. Por otro lado, la Sentencia SU-500 de 2015 afirma que el juez natural no puede ser desplazado por el juez constitucional, lo que reafirma la importancia de la competencia del juez natural. La opción A refleja correctamente esta idea, ya que establece que nadie puede ser juzgado sino por un juez o tribunal competente, previamente establecido por la ley. Las opciones B, C y D son incorrectas, ya que B contradice la idea de que el juez natural debe ser designado por la ley, C limita el principio del juez natural solo a la imparcialidad, y D contradice el principio de que el juez natural debe ser competente y previamente establecido.",
  "respuesta_correcta": "A",
  "descarte_opciones": {
    "B": "Contradice la idea de que el juez natural debe ser designado por la ley.",
    "C": "Limita el principio del juez natural solo a la imparcialidad, ignorando la competencia.",
    "D": "Contradice el principio de que el juez natural debe ser competente y previamente establecido."
  },
  "pasajes_usados": [
    "sentencia_t_323_de_2024:00054:ac1fc23534b8",
    "sentencia_t_323_de_2024:00055:b6b938c746e1",
    "sentencia_t_323_de_2024:00057:ed6ca92308cc",
    "sentencia_t_323_de_2024:00056:bb28fe8afde4",
    "sentencia_su_500_de_2015:00030:1a0700efdc3e"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 3 → después 10 · reparación {'suppressed_sentence': 1} · construidas ['Sentencia T-323 de 2024', 'Sentencia SU-500 de 2015', 'Sentencia T-1001 de 2001', 'artículo 48 del Código General del Proceso', 'artículo 328 de la Ley 2452 de 2025', 'Constitución Política', 'Ley 270 de 1996', 'Sentencia C-543 de 1992']
**Pasajes declarados por el modelo:** ['sentencia_t_323_de_2024:00054:ac1fc23534b8', 'sentencia_t_323_de_2024:00055:b6b938c746e1', 'sentencia_t_323_de_2024:00057:ed6ca92308cc', 'sentencia_t_323_de_2024:00056:bb28fe8afde4', 'sentencia_su_500_de_2015:00030:1a0700efdc3e']
**Evidencia:**
1. `sentencia_t_323_de_2024:00054:ac1fc23534b8` — Sentencia T-323 de 2024 art. None
2. `sentencia_t_323_de_2024:00055:b6b938c746e1` — Sentencia T-323 de 2024 art. None
3. `sentencia_t_323_de_2024:00057:ed6ca92308cc` — Sentencia T-323 de 2024 art. None
4. `sentencia_t_323_de_2024:00056:bb28fe8afde4` — Sentencia T-323 de 2024 art. None
5. `sentencia_t_1001_de_2001:00015:817e8826de55` — Sentencia T-1001 de 2001 art. None
6. `sentencia_su_500_de_2015:00030:1a0700efdc3e` — Sentencia SU-500 de 2015 art. None
7. `codigo_general_proceso:00050:94645e1b54fd` — Código General del Proceso (Ley 1564 de 2012) art. 48
8. `ley_2452_de_2025:00335:4f7ac5deff87` — Ley 2452 de 2025 art. 328
*Tokens 7370→541 · generación 23138.802700006636 ms · retrieval 76.73250000516418 ms · grafo off*

## 79 · semi_open

**Pregunta:** ¿Existe alguna norma en el ordenamiento jurídico colombiano que regule el acoso laboral?

**Medición:** cita=cita_ok · legal_basis=Ley 1010 de 2006 

**Respuesta final:**
```json
{
  "respuesta": "Sí, existe normativa en el ordenamiento jurídico colombiano que regula el acoso laboral. La Ley 1010 de 2006 establece medidas preventivas y correctivas para el acoso laboral, entre ellas, la creación de mecanismos internos de conciliación y la obligación de los empleadores de adoptar procedimientos confidenciales y efectivos para resolver las quejas. Además, la Sentencia T-262 de 2025 reafirma la importancia de estas normas en la protección del derecho al debido proceso de las víctimas de acoso laboral.",
  "palabras_clave": [
    "acoso laboral",
    "Ley 1010 de 2006",
    "derecho al debido proceso"
  ],
  "referencia_legal": "artículo 9 de la Ley 1010 de 2006; Sentencia T-262 de 2025; artículo 6 de la Ley 1010 de 2006; Sentencia T-317 de 2020; Sentencia C-960 de 2007; Código Sustantivo del Trabajo"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"Sí, existe normativa en el ordenamiento jurídico colombiano que regula el acoso laboral. La Ley 1010 de 2006 establece medidas preventivas y correctivas para el acoso laboral, entre ellas, la creación de mecanismos internos de conciliación y la obligación de los empleadores de adoptar procedimientos confidenciales y efectivos para resolver las quejas. Además, la Sentencia T-262 de 2025 reafirma la importancia de estas normas en la protección del derecho al debido proceso de las víctimas de acoso laboral.","palabras_clave":["acoso laboral","Ley 1010 de 2006","derecho al debido proceso"],"referencia_legal":"Ley 1010 de 2006, artículo 9; Sentencia T-262 de 2025","pasajes_usados":["ley_1010_de_2006:00008:9146ba17697d","sentencia_t_262_de_2025:00027:471c090a71fe"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 6 → después 11 · reparación {'rewritten_to_body': 1} · construidas ['artículo 9 de la Ley 1010 de 2006', 'Sentencia T-262 de 2025', 'artículo 6 de la Ley 1010 de 2006', 'Sentencia T-317 de 2020', 'Sentencia C-960 de 2007', 'Código Sustantivo del Trabajo']
**Pasajes declarados por el modelo:** ['ley_1010_de_2006:00008:9146ba17697d', 'sentencia_t_262_de_2025:00027:471c090a71fe']
**Evidencia:**
1. `sentencia_t_262_de_2025:00040:e09f9f29a4ca` — Sentencia T-262 de 2025 art. None
2. `sentencia_t_262_de_2025:00032:50ae27ba74c6` — Sentencia T-262 de 2025 art. None
3. `sentencia_t_262_de_2025:00027:471c090a71fe` — Sentencia T-262 de 2025 art. None
4. `ley_1010_de_2006:00008:9146ba17697d` — Ley 1010 de 2006 art. 9
5. `sentencia_t_262_de_2025:00024:716775f740fc` — Sentencia T-262 de 2025 art. None
6. `sentencia_t_262_de_2025:00000:1c33f1d0e919` — Sentencia T-262 de 2025 art. None
7. `ley_1010_de_2006:00005:68b3af1ab339` — Ley 1010 de 2006 art. 6
8. `sentencia_t_262_de_2025:00037:fb5768aca244` — Sentencia T-262 de 2025 art. None
*Tokens 6945→283 · generación 12607.211900001857 ms · retrieval 9.663399992859922 ms · grafo off*

## 128 · multiple_choice · ✘ esperada D

**Pregunta:** ¿Quiénes tienen la facultad de otorgar contratos de leasing financiero o arrendamiento financiero en Colombia? 

- A: Compañías de Financiamiento, los Bancos Comerciales, Fintech, Cooperativas, Fundaciones y Asociaciones
- B: Compañías de Financiamiento y Bancos Comerciales
- C: Cooperativas, Fundaciones y Asociaciones
- D: Compañías de Financiamiento, los Bancos Comerciales y las Fintech

**Medición:** cita=cita_ok · legal_basis=Decreto Ley 663 de 1993

**Respuesta final:**
```json
{
  "respuesta_correcta": "B",
  "justificacion": "La norma que establece quiénes pueden otorgar contratos de leasing financiero o arrendamiento financiero en Colombia se encuentra en el Decreto 663 de 1993, artículo 141. Según este artículo, las compañías de financiamiento comercial pueden realizar operaciones de leasing desde el 1 de julio de 1993, hasta el porcentaje máximo que señale el Gobierno Nacional. Además, el artículo 26 del mismo Decreto 663 de 1993 establece que las compañías de financiamiento comercial pueden recibir créditos para la adquisición de activos objeto de operaciones de leasing. Por lo tanto, las compañías de financiamiento comercial son las que tienen la facultad de otorgar contratos de leasing financiero o arrendamiento financiero en Colombia. Fundamento normativo: artículo 76 de la Ley 1819 de 2016; artículo 127-1 del Estatuto Tributario; Ley 510 de 1999; Constitución Política; Decreto 2816 de 1991.",
  "descarte_opciones": {
    "A": "No se menciona que las Fintech, Cooperativas, Fundaciones y Asociaciones tengan esta facultad en la norma.",
    "C": "No se menciona que las Cooperativas, Fundaciones y Asociaciones tengan esta facultad en la norma.",
    "D": "No se menciona que las Fintech tengan esta facultad en la norma."
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"La norma que establece quiénes pueden otorgar contratos de leasing financiero o arrendamiento financiero en Colombia se encuentra en el Decreto 663 de 1993, artículo 141. Según este artículo, las compañías de financiamiento comercial pueden realizar operaciones de leasing desde el 1 de julio de 1993, hasta el porcentaje máximo que señale el Gobierno Nacional. Además, el artículo 26 del mismo Decreto 663 de 1993 establece que las compañías de financiamiento comercial pueden recibir créditos para la adquisición de activos objeto de operaciones de leasing. Por lo tanto, las compañías de financiamiento comercial son las que tienen la facultad de otorgar contratos de leasing financiero o arrendamiento financiero en Colombia.","respuesta_correcta":"B","descarte_opciones":{"A":"No se menciona que las Fintech, Cooperativas, Fundaciones y Asociaciones tengan esta facultad en la norma.","C":"No se menciona que las Cooperativas, Fundaciones y Asociaciones tengan esta facultad en la norma.","D":"No se menciona que las Fintech tengan esta facultad en la norma."},"pasajes_usados":["decreto_663_de_1993:00204:4acf56878fce","decreto_663_de_1993:00035:8c6a5f6a33f5"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 4 → después 11 · reparación {} · construidas ['artículo 141 del Decreto 663 de 1993', 'artículo 26 del Decreto 663 de 1993', 'artículo 76 de la Ley 1819 de 2016', 'artículo 127-1 del Estatuto Tributario', 'artículo 142 del Decreto 663 de 1993', 'Ley 510 de 1999', 'Constitución Política', 'Decreto 2816 de 1991']
**Pasajes declarados por el modelo:** ['decreto_663_de_1993:00204:4acf56878fce', 'decreto_663_de_1993:00035:8c6a5f6a33f5']
**Evidencia:**
1. `ley_1819_de_2016:00088:f41467d4481e` — Ley 1819 de 2016 art. 76
2. `decreto_663_de_1993:00204:4acf56878fce` — Decreto 663 de 1993 art. 141
3. `estatuto_tributario:00224:0fea97482b61` — Estatuto Tributario (Decreto 624 de 1989) art. 127-1
4. `decreto_663_de_1993:00205:90c1f38b0893` — Decreto 663 de 1993 art. 142
5. `estatuto_tributario:00441:2506b7a4f0cb` — Estatuto Tributario (Decreto 624 de 1989) art. 267-1
6. `ley_1819_de_2016:00143:93d0590730a1` — Ley 1819 de 2016 art. 115
7. `decreto_663_de_1993:00035:8c6a5f6a33f5` — Decreto 663 de 1993 art. 26
8. `estatuto_tributario:00225:bf4fe5bcaf05` — Estatuto Tributario (Decreto 624 de 1989) art. 127-1
*Tokens 5532→353 · generación 14041.394700005185 ms · retrieval 30.48560000024736 ms · grafo off*

## 140 · semi_open

**Pregunta:** ¿Qué definió la Corte Constitucional en la Sentencia C 145 de 2018 frente a las potestades del acreedor garantizado que ejecuta la garantía mobiliaria fuera o dentro de un proceso concursal?

**Medición:** cita=cita_ok · legal_basis=Sentencia C 145 de 2018

**Respuesta final:**
```json
{
  "respuesta": "La Corte Constitucional definió en la Sentencia C-145 de 2018 que las potestades del acreedor garantizado para ejecutar la garantía mobiliaria fuera o dentro de un proceso concursal son exequibles condicionadas. Esto significa que solo proceden siempre que los demás bienes del deudor sean suficientes para asegurar el pago de las obligaciones alimentarias de los niños y las salariales y prestaciones derivadas del contrato de trabajo.",
  "palabras_clave": [
    "Corte Constitucional",
    "acreedor garantizado",
    "garantía mobiliaria",
    "derechos de los niños",
    "derechos de los trabajadores"
  ],
  "referencia_legal": "Sentencia C-145 de 2018; Ley 1676 de 2013; Código Civil; Constitución Política"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La Corte Constitucional definió en la Sentencia C-145 de 2018 que las potestades del acreedor garantizado para ejecutar la garantía mobiliaria fuera o dentro de un proceso concursal son exequibles condicionadas. Esto significa que solo proceden siempre que los demás bienes del deudor sean suficientes para asegurar el pago de las obligaciones alimentarias de los niños y las salariales y prestaciones derivadas del contrato de trabajo. La Corte reiteró que estas normas deben aplicarse bajo el marco del artículo 2498 del Código Civil, garantizando así la protección constitucional de los derechos de los niños y los trabajadores.","palabras_clave":["Corte Constitucional","acreedor garantizado","garantía mobiliaria","derechos de los niños","derechos de los trabajadores"],"referencia_legal":"Sentencia C-145 de 2018","pasajes_usados":["sentencia_c_145_de_2018:00035:4dfb7ce4e3b6","sentencia_c_145_de_2018:00034:544f29faa993"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 4 → después 5 · reparación {'suppressed_sentence': 1} · construidas ['Sentencia C-145 de 2018', 'Ley 1676 de 2013', 'Código Civil', 'Constitución Política']
**Pasajes declarados por el modelo:** ['sentencia_c_145_de_2018:00035:4dfb7ce4e3b6', 'sentencia_c_145_de_2018:00034:544f29faa993']
**Evidencia:**
1. `sentencia_c_145_de_2018:00022:4b9680b22d10` — Sentencia C-145 de 2018 art. None
2. `sentencia_c_145_de_2018:00035:4dfb7ce4e3b6` — Sentencia C-145 de 2018 art. None
3. `sentencia_c_145_de_2018:00032:dad2883033e1` — Sentencia C-145 de 2018 art. None
4. `sentencia_c_145_de_2018:00034:544f29faa993` — Sentencia C-145 de 2018 art. None
5. `sentencia_c_145_de_2018:00007:65b81292b813` — Sentencia C-145 de 2018 art. None
6. `sentencia_c_145_de_2018:00033:4db06e328a80` — Sentencia C-145 de 2018 art. None
7. `sentencia_c_145_de_2018:00014:1c8c5f56a51c` — Sentencia C-145 de 2018 art. None
8. `sentencia_c_145_de_2018:00015:00317177d1ef` — Sentencia C-145 de 2018 art. None
*Tokens 7002→287 · generación 12540.480200012098 ms · retrieval 21.33089999551885 ms · grafo off*

## 142 · semi_open

**Pregunta:** ¿Cuál es el precedente jurisprudencial en materia de deducibilidad de gastos en el impuesto sobre la renta?

**Medición:** cita=sin_ref_parseable · legal_basis=Sentencia de unificación 2020CE-SUJ-4-005 del 26 de noviembre de 2020 con expediente 21329.

**Respuesta final:**
```json
{
  "respuesta": "En el derecho colombiano, no existe un precedente jurisprudencial específico mencionado en la evidencia proporcionada sobre la deducibilidad de gastos en el impuesto sobre la renta. La normativa relevante se encuentra en el Estatuto Tributario (Decreto 624 de 1989) y en la Ley 1819 de 2016, que establecen reglas sobre la deducibilidad de ciertos gastos y la no deducibilidad de otros. Estas normas son las que regulan directamente el tema.",
  "palabras_clave": [
    "deducibilidad",
    "gastos",
    "impuesto sobre la renta",
    "Estatuto Tributario",
    "Ley 1819 de 2016"
  ],
  "referencia_legal": "artículo 85 del Estatuto Tributario; artículo 59 de la Ley 1819 de 2016; artículo 61 de la Ley 1819 de 2016; artículo 32 de la Ley 1819 de 2016; artículo 33 del Estatuto Tributario; Ley 863 de 2003; Ley 223 de 1995; Ley 2010 de 2019"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"En el derecho colombiano, no existe un precedente jurisprudencial específico mencionado en la evidencia proporcionada sobre la deducibilidad de gastos en el impuesto sobre la renta. La normativa relevante se encuentra en el Estatuto Tributario (Decreto 624 de 1989) y en la Ley 1819 de 2016, que establecen reglas sobre la deducibilidad de ciertos gastos y la no deducibilidad de otros. Estas normas son las que regulan directamente el tema.","palabras_clave":["deducibilidad","gastos","impuesto sobre la renta","Estatuto Tributario","Ley 1819 de 2016"],"referencia_legal":"Estatuto Tributario (Decreto 624 de 1989), artículo 85; Ley 1819 de 2016, artículo 59; Ley 1819 de 2016, artículo 61; Ley 1819 de 2016, artículo 32; Estatuto Tributario (Decreto 624 de 1989), artículo 33","pasajes_usados":["estatuto_tributario:00139:1d45173d5fa5","ley_1819_de_2016:00069:806b08149137","ley_1819_de_2016:00071:5a746eec5119","ley_1819_de_2016:00038:805bc33dc55b","estatuto_tributario:00059:df01934516fc"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 17 → después 18 · reparación {'renamed_to_evidence_name': 19, 'rewritten_to_body': 1, 'suppressed_fragment': 3} · construidas ['artículo 85 del Estatuto Tributario', 'artículo 59 de la Ley 1819 de 2016', 'artículo 61 de la Ley 1819 de 2016', 'artículo 32 de la Ley 1819 de 2016', 'artículo 33 del Estatuto Tributario', 'Ley 863 de 2003', 'Ley 223 de 1995', 'Ley 2010 de 2019']
**Pasajes declarados por el modelo:** ['estatuto_tributario:00139:1d45173d5fa5', 'ley_1819_de_2016:00069:806b08149137', 'ley_1819_de_2016:00071:5a746eec5119', 'ley_1819_de_2016:00038:805bc33dc55b', 'estatuto_tributario:00059:df01934516fc']
**Evidencia:**
1. `estatuto_tributario:00139:1d45173d5fa5` — Estatuto Tributario (Decreto 624 de 1989) art. 85
2. `estatuto_tributario:00500:44769a16f745` — Estatuto Tributario (Decreto 624 de 1989) art. 298-6
3. `estatuto_tributario:00497:ece7ffe5206b` — Estatuto Tributario (Decreto 624 de 1989) art. 298-3
4. `ley_1819_de_2016:00069:806b08149137` — Ley 1819 de 2016 art. 59
5. `estatuto_tributario:00172:4052251b1fae` — Estatuto Tributario (Decreto 624 de 1989) art. 105
6. `ley_1819_de_2016:00071:5a746eec5119` — Ley 1819 de 2016 art. 61
7. `ley_1819_de_2016:00038:805bc33dc55b` — Ley 1819 de 2016 art. 32
8. `estatuto_tributario:00059:df01934516fc` — Estatuto Tributario (Decreto 624 de 1989) art. 33
*Tokens 5640→431 · generación 17075.993300008122 ms · retrieval 7.108400008291937 ms · grafo off*

## 168 · semi_open

**Pregunta:** ¿Cuándo procede la declaración de lesión enorme en el contrato de compraventa  de bien inmueble ?

**Medición:** cita=sin_ref_parseable · legal_basis=Sentencia del 18 de julio de 2017, de la Sala Civil de la Corte Suprema de Justicia

**Respuesta final:**
```json
{
  "respuesta": "La declaración de lesión enorme en el contrato de compraventa de bien inmueble procede cuando el precio que recibe el vendedor es inferior a la mitad del justo precio de la cosa que vende, según el artículo 1947 del Código Civil. Además, la acción rescisoria por lesión enorme expira en cuatro años, contados desde la fecha de contrato, según el artículo 1954 del Código Civil.",
  "palabras_clave": [
    "lesión enorme",
    "contrato de compraventa",
    "justo precio",
    "acción rescisoria",
    "Código Civil"
  ],
  "referencia_legal": "artículo 1947 del Código Civil; artículo 1954 del Código Civil; artículo 1946 del Código Civil; artículo 1945 del Código Civil; artículo 1892 del Código Civil; Ley 57 de 1887; Ley 6 de 1992"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La declaración de lesión enorme en el contrato de compraventa de bien inmueble procede cuando el precio que recibe el vendedor es inferior a la mitad del justo precio de la cosa que vende, según el artículo 1947 del Código Civil. Además, la acción rescisoria por lesión enorme expira en cuatro años, contados desde la fecha de contrato, según el artículo 1954 del Código Civil.","palabras_clave":["lesión enorme","contrato de compraventa","justo precio","acción rescisoria","Código Civil"],"referencia_legal":"Código Civil (Ley 84 de 1873; Ley 57 de 1887), artículo 1947 y 1954.","pasajes_usados":["codigo_civil:01945:3a0cdba094a2","codigo_civil:01952:26a8515f0a6f"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 10 → después 17 · reparación {'suppressed_fragment': 2, 'suppressed_sentence': 1} · construidas ['artículo 1947 del Código Civil', 'artículo 1954 del Código Civil', 'artículo 1946 del Código Civil', 'artículo 1945 del Código Civil', 'artículo 1892 del Código Civil', 'Ley 57 de 1887', 'Ley 6 de 1992']
**Pasajes declarados por el modelo:** ['codigo_civil:01945:3a0cdba094a2', 'codigo_civil:01952:26a8515f0a6f']
**Evidencia:**
1. `codigo_civil:01944:9564975b1998` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1946
2. `codigo_civil:01945:3a0cdba094a2` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1947
3. `codigo_civil:01952:26a8515f0a6f` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1954
4. `codigo_civil:01943:6c2405b51940` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1945
5. `codigo_civil:01890:f506f1bb7cb4` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1892
6. `codigo_civil:01947:a4557853ed02` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1949
7. `estatuto_tributario:01089:360ecf4a0a47` — Estatuto Tributario (Decreto 624 de 1989) art. 671-1
8. `codigo_general_proceso:00385:1f78135e48e8` — Código General del Proceso (Ley 1564 de 2012) art. 375
*Tokens 3620→226 · generación 9496.006100001978 ms · retrieval 6.737500007147901 ms · grafo off*

## 190 · semi_open

**Pregunta:**  ¿Cuales son los principales antecedentes fácticos que se nombran en la sentencia T-256 de 2025? 

**Medición:** cita=sin_ref_parseable · legal_basis=sentencia t-256

**Respuesta final:**
```json
{
  "respuesta": "Estas sentencias definen la salud como un derecho complejo y establecen que los servicios y tecnologías de salud deben ser suministrados de manera completa para prevenir, paliar o curar la enfermedad.",
  "palabras_clave": [
    "derecho a la salud",
    "jurisprudencia constitucional"
  ],
  "referencia_legal": "Sentencia T-323 de 2024; Sentencia T-350 de 2025; artículo 4 de la Ley 256 de 1996; Sentencia T-26 de 2025; Sentencia T-760 de 2008; Sentencia T-539 de 2013; Sentencia T-499 de 2014; Sentencia T-745 de 2014"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La sentencia T-256 de 2025 no menciona específicamente los antecedentes fácticos del caso. Sin embargo, se refiere a la jurisprudencia constitucional sobre el derecho a la salud, incluyendo sentencias como T-760 de 2008, T-539 de 2013, T-499 de 2014, T-745 de 2014, C-313 de 2014, T-094 de 2016, T-014 de 2017 y T-005 de 2023. Estas sentencias definen la salud como un derecho complejo y establecen que los servicios y tecnologías de salud deben ser suministrados de manera completa para prevenir, paliar o curar la enfermedad.","palabras_clave":["derecho a la salud","jurisprudencia constitucional","sentencia T-256 de 2025"],"referencia_legal":"Sentencia T-256 de 2025, [256] y [257]","pasajes_usados":["sentencia_t_323_de_2024:00133:e060ca18b6a2"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 11 → después 9 · reparación {'emptied': 1, 'suppressed_fragment': 2, 'suppressed_sentence': 4} · construidas ['Sentencia T-323 de 2024', 'Sentencia T-350 de 2025', 'artículo 4 de la Ley 256 de 1996', 'Sentencia T-26 de 2025', 'Sentencia T-760 de 2008', 'Sentencia T-539 de 2013', 'Sentencia T-499 de 2014', 'Sentencia T-745 de 2014']
**Pasajes declarados por el modelo:** ['sentencia_t_323_de_2024:00133:e060ca18b6a2']
**Evidencia:**
1. `sentencia_t_350_de_2025:00046:3b099b6b10dd` — Sentencia T-350 de 2025 art. None
2. `ley_256_de_1996:00003:4b7dbebf3370` — Ley 256 de 1996 art. 4
3. `sentencia_t_26_de_2025:00017:93a40ff223cc` — Sentencia T-26 de 2025 art. None
4. `sentencia_t_323_de_2024:00133:e060ca18b6a2` — Sentencia T-323 de 2024 art. None
5. `sentencia_t_760_de_2008:00006:23f4f0c3c60b` — Sentencia T-760 de 2008 art. None
6. `sentencia_su_214_de_2016:00039:cd1edc47ad3e` — Sentencia SU-214 de 2016 art. None
7. `codigo_civil:01222:59e8af3991e0` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1224
8. `sentencia_c_39_de_2025:00002:662e2c65adb7` — Sentencia C-39 de 2025 art. None
*Tokens 5709→312 · generación 13648.997500000405 ms · retrieval 23.230599996168166 ms · grafo auto*

## 218 · semi_open · ABSTENCIÓN (citation_repair)

**Pregunta:** Cómo se resuelve el conflicto normativo entre la potestad del artículo 32 de la Ley 2294 de 2023 para que el Ministerio de Agricultura y Desarrollo Rural pueda expedir resoluciones donde fija el uso del suelo de los Municipios, con el artículo 313 #7 de la Constitución Política

**Medición:** cita=ref_en_evidencia_no_citada · legal_basis=Artículo 311 y 313 de la Constitución Política

**Respuesta final:**
```json
{
  "respuesta": "",
  "palabras_clave": [],
  "referencia_legal": ""
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El conflicto normativo entre la potestad del artículo 32 de la Ley 2294 de 2023 y el artículo 313 numeral 7 de la Constitución Política no se resuelve directamente en los pasajes proporcionados. La Ley 2294 de 2023 modifica el artículo 31 de la Ley 160 de 1994, permitiendo la adjudicación de tierras a juventudes rurales, mientras que el artículo 313 numeral 7 de la Constitución Política establece que la fijación del hecho gravable corresponde a la ley. Sin embargo, los pasajes no mencionan cómo se resuelve este conflicto normativo.","palabras_clave":["Ley 2294 de 2023","artículo 32","artículo 313 numeral 7","Constitución Política"],"referencia_legal":"Ley 2294 de 2023, artículo 31; Ley 160 de 1994, artículo 31; Constitución Política, artículo 313 numeral 7","pasajes_usados":["ley_2466_de_2025:00033:f119134a9e42","ley_160_de_1994:00032:4b242108cf15"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 23 → después 0 · reparación {'suppressed_fragment': 10, 'suppressed_sentence': 7} · construidas ['artículo 31 de la Ley 2466 de 2025', 'artículo 31 de la Ley 160 de 1994', 'artículo 4 de la Ley 160 de 1994', 'Sentencia C-413 de 1996', 'artículo 230 del Decreto 663 de 1993', 'Ley 1151 de 2007', 'Decreto 2363 de 2015', 'Ley 2294 de 2023']
**Pasajes declarados por el modelo:** ['ley_2466_de_2025:00033:f119134a9e42', 'ley_160_de_1994:00032:4b242108cf15']
**Evidencia:**
1. `ley_160_de_1994:00004:a84aa92e1029` — Ley 160 de 1994 art. 4
2. `ley_160_de_1994:00032:4b242108cf15` — Ley 160 de 1994 art. 31
3. `sentencia_c_413_de_1996:00001:00c586b7e483` — Sentencia C-413 de 1996 art. None
4. `decreto_663_de_1993:00325:c3b4a25e0709` — Decreto 663 de 1993 art. 230
5. `ley_1151_de_2007:00021:6cae4979a2b2` — Ley 1151 de 2007 art. 6
6. `ley_1151_de_2007:00071:5af27b6ed23e` — Ley 1151 de 2007 art. 20
7. `decreto_663_de_1993:00322:f02525f5fdb8` — Decreto 663 de 1993 art. 227
8. `ley_2466_de_2025:00033:f119134a9e42` — Ley 2466 de 2025 art. 31
*Tokens 6710→329 · generación 14526.978499998222 ms · retrieval 71.4668000000529 ms · grafo auto*

## 239 · semi_open

**Pregunta:** ¿A qué subregla jurídica llega la Corte Suprema de Justicia en relación con la renuncia a la cesantía comercial por parte del agente, en la sentencia de William Namen Vargas del 19 de octubre de 2011?

**Medición:** cita=ref_fuera_de_evidencia · legal_basis=Artículos 1324 y 1325 del Código de Comercio. Así como en los principios de autonomía de la voluntad privada (Artículos 16, 822 y 871).

**Respuesta final:**
```json
{
  "respuesta": "Estos principios son fundamentales para garantizar la igualdad de trato jurídico y la seguridad jurídica. La Sala Laboral de la Corte Suprema de Justicia tiene el deber de fijar el sentido y alcance de las normas convencionales para asegurar una aplicación uniforme.",
  "palabras_clave": [
    "interpretación sistemática",
    "principio de favorabilidad",
    "seguridad jurídica"
  ],
  "referencia_legal": "Sentencia SU-27 de 2021; Sentencia SU-315 de 2025; Sentencia SU-455 de 2020; Sentencia SU-149 de 2021; Sentencia SU-396 de 2024; Constitución Política; Sentencia SU-267 de 2019; Sentencia SU-241 de 2015"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La Corte Suprema de Justicia en la sentencia del 19 de octubre de 2011, resalta la importancia de la interpretación sistemática entre la ley y la Constitución, así como el principio de favorabilidad en sentido amplio. Estos principios son fundamentales para garantizar la igualdad de trato jurídico y la seguridad jurídica. La Sala Laboral de la Corte Suprema de Justicia tiene el deber de fijar el sentido y alcance de las normas convencionales para asegurar una aplicación uniforme.","palabras_clave":["interpretación sistemática","principio de favorabilidad","seguridad jurídica"],"referencia_legal":"Corte Suprema de Justicia, Sala de Casación Civil. Sentencia del 19 de octubre de 2011, rad. 52835-3103-001-2000-00005-01. M.P. William Namen Vargas.","pasajes_usados":["sentencia_su_27_de_2021:00039:2fa49a0a5c5a"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 3 → después 8 · reparación {'suppressed_sentence': 2} · construidas ['Sentencia SU-27 de 2021', 'Sentencia SU-315 de 2025', 'Sentencia SU-455 de 2020', 'Sentencia SU-149 de 2021', 'Sentencia SU-396 de 2024', 'Constitución Política', 'Sentencia SU-267 de 2019', 'Sentencia SU-241 de 2015']
**Pasajes declarados por el modelo:** ['sentencia_su_27_de_2021:00039:2fa49a0a5c5a']
**Evidencia:**
1. `sentencia_su_315_de_2025:00081:fd5dc0faec40` — Sentencia SU-315 de 2025 art. None
2. `sentencia_su_315_de_2025:00078:611a4fb04ffe` — Sentencia SU-315 de 2025 art. None
3. `sentencia_su_315_de_2025:00086:0f49de4eb27e` — Sentencia SU-315 de 2025 art. None
4. `sentencia_su_455_de_2020:00049:8d99f6702a23` — Sentencia SU-455 de 2020 art. None
5. `sentencia_su_27_de_2021:00039:2fa49a0a5c5a` — Sentencia SU-27 de 2021 art. None
6. `sentencia_su_149_de_2021:00057:244b602ae835` — Sentencia SU-149 de 2021 art. None
7. `sentencia_su_396_de_2024:00091:0cd6e7a617e2` — Sentencia SU-396 de 2024 art. None
8. `sentencia_su_315_de_2025:00085:7102c19939f2` — Sentencia SU-315 de 2025 art. None
*Tokens 6868→266 · generación 11538.545000003069 ms · retrieval 24.5036000123946 ms · grafo off*

## 247 · open_ended

**Pregunta:** La alcadia de bogotá a través de la secretaria de movilidad expide una resolución con el fin de ampliar la avenida 68 con sustento normativo en el articulo 2 de la constitucipon politica  el cual menciona como "fines del estado, servir a la comunidad y promover la prosperidad general y garantizar la efectividad de los principios". Lo anterior, lo afecta a usted y a la comunidad pues dicha intervención afectarpia el parque Simon Bolivar y generaria una desaparición parcial de este; además esta ampliación afecta a quienes sacan a su perro a pasear contantemente allí, las personas que se ejercitan y lo mas importante los animales que viven allí. De acuerdo a lo anterior, que acción procede ante dicha situación.

**Medición:** cita=ref_fuera_de_evidencia · legal_basis=ley 472 de 1998 

**Respuesta final:**
```json
{
  "marco_normativo": "Constitución Política de Colombia de 1991, artículo 2, que establece que uno de los fines esenciales del Estado es garantizar la efectividad de los principios, derechos y deberes consagrados en la Constitución, así como promover la prosperidad general y servir a la comunidad. Además, la Constitución menciona que las autoridades están instituidas para proteger a todas las personas residentes en Colombia, en su vida, honra, bienes, creencias, y demás derechos y libertades.",
  "analisis": "La alcadia de Bogotá, a través de la secretaria de movilidad, expide una resolución con el fin de ampliar la avenida 68, basándose en el artículo 2 de la Constitución Política de Colombia de 1991, que menciona como fines del Estado servir a la comunidad, promover la prosperidad general y garantizar la efectividad de los principios, derechos y deberes consagrados en la Constitución. Sin embargo, dicha ampliación afecta al parque Simón Bolívar, generando la desaparición parcial de este espacio y afectando a quienes utilizan el parque para pasear a sus perros, ejercitarse y a los animales que viven allí. De acuerdo con el marco normativo, las autoridades están instituidas para proteger a todas las personas residentes en Colombia, en su vida, honra, bienes, creencias, y demás derechos y libertades. Por lo tanto, la acción que procede ante dicha situación es la tutela judicial efectiva, ya que se vulneran los derechos de la comunidad y los animales que viven en el parque Simón Bolívar.",
  "jurisprudencia": "La Corte Constitucional ha establecido que el acceso a la administración de justicia es un derecho medular, de contenido múltiple o complejo, cuyo marco jurídico de aplicación compromete, en un orden lógico, el derecho de acción o de promoción de la actividad jurisdiccional, el derecho a que la promoción de la actividad jurisdiccional concluya con una decisión de fondo, el derecho a que existan procedimientos adecuados, idóneos y efectivos para la definición de las pretensiones y excepciones debatidas, el derecho a que los procesos se desarrollen en un término razonable, sin dilaciones injustificadas y con observancia de las garantías propias del debido proceso, y el derecho a que subsistan en el orden jurídico una gama amplia y suficiente de mecanismos judiciales -acciones y recursos- para la efectiva resolución de los conflictos.",
  "conclusion": "La acción que procede ante la situación descrita es la tutela judicial efectiva, ya que se vulneran los derechos de la comunidad y los animales que viven en el parque Simón Bolívar, según el marco normativo establecido en la Constitución Política de Colombia de 1991 y la jurisprudencia constitucional."
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "marco_normativo": "Constitución Política de Colombia de 1991, artículo 2, que establece que uno de los fines esenciales del Estado es garantizar la efectividad de los principios, derechos y deberes consagrados en la Constitución, así como promover la prosperidad general y servir a la comunidad. Además, la Constitución menciona que las autoridades están instituidas para proteger a todas las personas residentes en Colombia, en su vida, honra, bienes, creencias, y demás derechos y libertades.",
  "analisis": "La alcadia de Bogotá, a través de la secretaria de movilidad, expide una resolución con el fin de ampliar la avenida 68, basándose en el artículo 2 de la Constitución Política de Colombia de 1991, que menciona como fines del Estado servir a la comunidad, promover la prosperidad general y garantizar la efectividad de los principios, derechos y deberes consagrados en la Constitución. Sin embargo, dicha ampliación afecta al parque Simón Bolívar, generando la desaparición parcial de este espacio y afectando a quienes utilizan el parque para pasear a sus perros, ejercitarse y a los animales que viven allí. De acuerdo con el marco normativo, las autoridades están instituidas para proteger a todas las personas residentes en Colombia, en su vida, honra, bienes, creencias, y demás derechos y libertades. Por lo tanto, la acción que procede ante dicha situación es la tutela judicial efectiva, ya que se vulneran los derechos de la comunidad y los animales que viven en el parque Simón Bolívar.",
  "jurisprudencia": "La Corte Constitucional ha establecido que el acceso a la administración de justicia es un derecho medular, de contenido múltiple o complejo, cuyo marco jurídico de aplicación compromete, en un orden lógico, el derecho de acción o de promoción de la actividad jurisdiccional, el derecho a que la promoción de la actividad jurisdiccional concluya con una decisión de fondo, el derecho a que existan procedimientos adecuados, idóneos y efectivos para la definición de las pretensiones y excepciones debatidas, el derecho a que los procesos se desarrollen en un término razonable, sin dilaciones injustificadas y con observancia de las garantías propias del debido proceso, y el derecho a que subsistan en el orden jurídico una gama amplia y suficiente de mecanismos judiciales -acciones y recursos- para la efectiva resolución de los conflictos.",
  "conclusion": "La acción que procede ante la situación descrita es la tutela judicial efectiva, ya que se vulneran los derechos de la comunidad y los animales que viven en el parque Simón Bolívar, según el marco normativo establecido en la Constitución Política de Colombia de 1991 y la jurisprudencia constitucional.",
  "pasajes_usados": [
    "constitucion:00001:2c8ef8b34c21",
    "sentencia_su_11_de_2020:00052:fd0b6b197421",
    "sentencia_c_345_de_2017:00041:4e84eac67f5b"
  ]
}
```
**Parser:** none · correcciones [] · avisos ['open_ended_analysis_sentences_4_outside_5_8']
**Citas:** antes 8 → después 8 · reparación {} · construidas ['artículo 2 de la Constitución Política', 'Sentencia SU-11 de 2020', 'Sentencia C-345 de 2017']
**Pasajes declarados por el modelo:** ['constitucion:00001:2c8ef8b34c21', 'sentencia_su_11_de_2020:00052:fd0b6b197421', 'sentencia_c_345_de_2017:00041:4e84eac67f5b']
**Evidencia:**
1. `constitucion:00001:2c8ef8b34c21` — Constitución Política de Colombia de 1991 art. 2
2. `sentencia_su_11_de_2020:00052:fd0b6b197421` — Sentencia SU-11 de 2020 art. None
3. `sentencia_c_535_de_2002:00006:cb0433f9fac7` — Sentencia C-535 de 2002 art. None
4. `sentencia_su_425_de_2025:00037:64c51e08adfe` — Sentencia SU-425 de 2025 art. None
5. `sentencia_c_345_de_2017:00041:4e84eac67f5b` — Sentencia C-345 de 2017 art. None
6. `sentencia_c_332_de_2025:00005:2a0d826325d7` — Sentencia C-332 de 2025 art. None
7. `codigo_nacional_policia:00136:428a543fa8be` — Código Nacional de Seguridad y Convivencia Ciudadana (Ley 1801 de 2016) art. 124
8. `sentencia_c_332_de_2025:00007:ce255159abb2` — Sentencia C-332 de 2025 art. None
*Tokens 6391→803 · generación 32674.059600001783 ms · retrieval 82.235199995921 ms · grafo auto*

## 253 · open_ended

**Pregunta:** El 28 de noviembre el trabajador Rodolfo Gómez se movilizaba en bus a su lugar de trabajo como cocinero. A mitad de recorrido, dado a fuertes lluvias se generó un deslizamiento que provocó que un árbol cayera encima de la parte trasera del bus en donde se encontraba el señor Gómez. Debido a esto, lo tuvieron que trasladar en ambulancia al centro médico más cercano para remitirlo a urgencias y consecuentemente se le realizaran los procedimientos necesarios.  
Ante esta situación: ¿Los accidentes ocurridos en el traslado de los trabajadores a su lugar de trabajo se reconocen como accidentes laborales? ¿Quién responde por las prestaciones económicas y asistenciales que generan de un hecho de fuerza mayor o caso fortuito? 

**Medición:** cita=cita_ok · legal_basis=Sentencia SL3385-2022.
Ley 1562 de 2012.  
artículo 56 y 57 del CST.  

**Respuesta final:**
```json
{
  "marco_normativo": "Ley 1562 de 2012, Ley 50 de 1990, Código Sustantivo del Trabajo (Decreto 2663 de 1950), Sentencia SL-3385 de 2022, Sentencia SU-396 de 2024",
  "analisis": "Según la Ley 1562 de 2012, se considera accidente de trabajo el que se produce durante el traslado de los trabajadores o contratistas desde su residencia a los lugares de trabajo o viceversa, cuando el transporte lo suministre el empleador. En el caso de Rodolfo Gómez, el traslado no fue realizado por el empleador, por lo que no se considera un accidente de trabajo. La Ley 50 de 1990 establece que el contrato de trabajo se suspende por fuerza mayor o caso fortuito que temporalmente impida su ejecución. En este caso, las fuertes lluvias y el deslizamiento que provocaron el accidente se consideran caso fortuito. La Sentencia SL-3385 de 2022 afirma que el accidente no se considera de origen laboral si no se produce en cumplimiento de tareas o en desarrollo de una situación excepcional creada por el empleador. Por lo tanto, el accidente no se considera laboral. La Ley 1562 de 2012 también establece que el empleador y/o contratista son responsables de los gastos incurridos por la Entidad Administradora de Riesgos Laborales por causa de las prestaciones asistenciales otorgadas, así como del pago de los aportes en mora con sus respectivos intereses y el pago de las prestaciones económicas a que hubiere lugar. En este caso, el empleador debe responder por las prestaciones económicas y asistenciales generadas por el hecho de fuerza mayor o caso fortuito.",
  "jurisprudencia": "La Sentencia SL-3385 de 2022 establece que el accidente no se considera de origen laboral si no se produce en cumplimiento de tareas o en desarrollo de una situación excepcional creada por el empleador. La Sentencia SU-396 de 2024 afirma que los trabajadores que han sufrido accidentes de trabajo tienen derecho a prestaciones asistenciales y económicas de por vida.",
  "conclusion": "Los accidentes ocurridos en el traslado de los trabajadores a su lugar de trabajo no se reconocen como accidentes laborales si el transporte no es suministrado por el empleador. Quien responde por las prestaciones económicas y asistenciales generadas por un hecho de fuerza mayor o caso fortuito es el empleador."
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "marco_normativo": "Ley 1562 de 2012, Ley 50 de 1990, Código Sustantivo del Trabajo (Decreto 2663 de 1950), Sentencia SL-3385 de 2022, Sentencia SU-396 de 2024",
  "analisis": "Según la Ley 1562 de 2012, se considera accidente de trabajo el que se produce durante el traslado de los trabajadores o contratistas desde su residencia a los lugares de trabajo o viceversa, cuando el transporte lo suministre el empleador. En el caso de Rodolfo Gómez, el traslado no fue realizado por el empleador, por lo que no se considera un accidente de trabajo. La Ley 50 de 1990 establece que el contrato de trabajo se suspende por fuerza mayor o caso fortuito que temporalmente impida su ejecución. En este caso, las fuertes lluvias y el deslizamiento que provocaron el accidente se consideran caso fortuito. La Sentencia SL-3385 de 2022 afirma que el accidente no se considera de origen laboral si no se produce en cumplimiento de tareas o en desarrollo de una situación excepcional creada por el empleador. Por lo tanto, el accidente no se considera laboral. La Ley 1562 de 2012 también establece que el empleador y/o contratista son responsables de los gastos incurridos por la Entidad Administradora de Riesgos Laborales por causa de las prestaciones asistenciales otorgadas, así como del pago de los aportes en mora con sus respectivos intereses y el pago de las prestaciones económicas a que hubiere lugar. En este caso, el empleador debe responder por las prestaciones económicas y asistenciales generadas por el hecho de fuerza mayor o caso fortuito.",
  "jurisprudencia": "La Sentencia SL-3385 de 2022 establece que el accidente no se considera de origen laboral si no se produce en cumplimiento de tareas o en desarrollo de una situación excepcional creada por el empleador. La Sentencia SU-396 de 2024 afirma que los trabajadores que han sufrido accidentes de trabajo tienen derecho a prestaciones asistenciales y económicas de por vida.",
  "conclusion": "Los accidentes ocurridos en el traslado de los trabajadores a su lugar de trabajo no se reconocen como accidentes laborales si el transporte no es suministrado por el empleador. Quien responde por las prestaciones económicas y asistenciales generadas por un hecho de fuerza mayor o caso fortuito es el empleador.",
  "pasajes_usados": [
    "ley_1562_de_2012:00007:d3a8db714767",
    "ley_1562_de_2012:00005:84741522d889",
    "ley_50_de_1990:00003:f774eec2cd32",
    "sentencia_sl_3385_de_2022:00008:c03c7a4a507c",
    "sentencia_su_396_de_2024:00073:3dbf45821206"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 12 → después 12 · reparación {} · construidas ['Ley 1562 de 2012', 'artículo 4 de la Ley 50 de 1990', 'Sentencia SL-3385 de 2022']
**Pasajes declarados por el modelo:** ['ley_1562_de_2012:00007:d3a8db714767', 'ley_1562_de_2012:00005:84741522d889', 'ley_50_de_1990:00003:f774eec2cd32', 'sentencia_sl_3385_de_2022:00008:c03c7a4a507c', 'sentencia_su_396_de_2024:00073:3dbf45821206']
**Evidencia:**
1. `ley_1562_de_2012:00007:d3a8db714767` — Ley 1562 de 2012 art. 7
2. `sentencia_sl_3385_de_2022:00008:c03c7a4a507c` — Sentencia SL-3385 de 2022 art. None
3. `ley_1562_de_2012:00005:84741522d889` — Ley 1562 de 2012 art. 5
4. `ley_50_de_1990:00003:f774eec2cd32` — Ley 50 de 1990 art. 4
5. `sentencia_su_396_de_2024:00073:3dbf45821206` — Sentencia SU-396 de 2024 art. None
6. `ley_50_de_1990:00025:f81f055ba802` — Ley 50 de 1990 art. 26
7. `codigo_sustantivo_trabajo:00049:b00881778b49` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 51
8. `sentencia_sl_3385_de_2022:00004:d921a6a9b7b4` — Sentencia SL-3385 de 2022 art. None
*Tokens 6466→827 · generación 34413.086200002 ms · retrieval 49.627100001089275 ms · grafo on*

## 272 · open_ended

**Pregunta:** Debe una Fiduciaria proceder con la entrega de recursos existentes en un patrimonio autónomo de garantía, administración y fuente de pago a la sociedad fideicomitente inmersa en un proceso de reorganización ley 1116 de 2006 o al beneficiario del contrato, cuando el juez de la SuperSociedades ha dicho que el contrato no es garantía y únicamente funciona como fuente de pago? Que parte tiene derecho sobre esos recursos ?

**Medición:** cita=cita_ok · legal_basis=Ley 1116 de 2006 y jurisprudencia de la superintendencia de sociedades en especial el auto auto No. 2025-01-730337

**Respuesta final:**
```json
{
  "marco_normativo": "Decreto 1082 de 2015, Ley 1116 de 2006, Ley 1258 de 2008, Decreto 663 de 1993, Sentencia C-207 de 2019",
  "analisis": "Según el Decreto 1082 de 2015, la sociedad fiduciaria debe cumplir con requisitos específicos al crear un patrimonio autónomo como garantía, incluyendo la obligación de realizar valoraciones periódicas y notificar la insuficiencia del patrimonio autónomo. La Ley 1116 de 2006 establece que en caso de no presentación o falta de confirmación del acuerdo de reorganización, los contratos de fiducia mercantil celebrados por el deudor se terminan, y la fiduciaria debe entregar los bienes al promotor. La Ley 1258 de 2008 menciona que las acciones pueden estar radicadas en una fiducia mercantil, y los derechos y obligaciones del fideicomitente son ejercidos por la sociedad fiduciaria. El Decreto 663 de 1993 indica que los recursos del fideicomiso forman un patrimonio autónomo distinto del de la Nación y del Banco de Comercio Exterior. La Sentencia C-207 de 2019 menciona que el patrimonio autónomo debe ser administrado por el contratista y la fiduciaria debe reportar información a la UIAF. En este contexto, si el juez de la SuperSociedades determina que el contrato no es garantía y únicamente funciona como fuente de pago, la fiduciaria debe entregar los recursos al beneficiario del contrato, ya que el patrimonio autónomo es administrado por el contratista y la fiduciaria debe cumplir con las instrucciones del contratista.",
  "jurisprudencia": "La Sentencia C-207 de 2019 menciona que el patrimonio autónomo debe ser administrado por el contratista y la fiduciaria debe reportar información a la UIAF. No se aportó jurisprudencia adicional.",
  "conclusion": "La fiduciaria debe entregar los recursos existentes en el patrimonio autónomo al beneficiario del contrato, ya que el patrimonio autónomo es administrado por el contratista y la fiduciaria debe cumplir con las instrucciones del contratista. La parte que tiene derecho sobre esos recursos es el beneficiario del contrato."
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "marco_normativo": "Decreto 1082 de 2015, Ley 1116 de 2006, Ley 1258 de 2008, Decreto 663 de 1993, Decreto 1510 de 2013, Sentencia C-207 de 2019, Ley 80 de 1993, Ley 1508 de 2012",
  "analisis": "Según el Decreto 1082 de 2015, la sociedad fiduciaria debe cumplir con requisitos específicos al crear un patrimonio autónomo como garantía, incluyendo la obligación de realizar valoraciones periódicas y notificar la insuficiencia del patrimonio autónomo. La Ley 1116 de 2006 establece que en caso de no presentación o falta de confirmación del acuerdo de reorganización, los contratos de fiducia mercantil celebrados por el deudor se terminan, y la fiduciaria debe entregar los bienes al promotor. La Ley 1258 de 2008 menciona que las acciones pueden estar radicadas en una fiducia mercantil, y los derechos y obligaciones del fideicomitente son ejercidos por la sociedad fiduciaria. El Decreto 663 de 1993 indica que los recursos del fideicomiso forman un patrimonio autónomo distinto del de la Nación y del Banco de Comercio Exterior. La Sentencia C-207 de 2019 menciona que el patrimonio autónomo debe ser administrado por el contratista y la fiduciaria debe reportar información a la UIAF. La Ley 1508 de 2012 establece que los recursos públicos deben ser administrados a través de un patrimonio autónomo constituido por el contratista. En este contexto, si el juez de la SuperSociedades determina que el contrato no es garantía y únicamente funciona como fuente de pago, la fiduciaria debe entregar los recursos al beneficiario del contrato, ya que el patrimonio autónomo es administrado por el contratista y la fiduciaria debe cumplir con las instrucciones del contratista.",
  "jurisprudencia": "La Sentencia C-207 de 2019 menciona que el patrimonio autónomo debe ser administrado por el contratista y la fiduciaria debe reportar información a la UIAF. No se aportó jurisprudencia adicional.",
  "conclusion": "La fiduciaria debe entregar los recursos existentes en el patrimonio autónomo al beneficiario del contrato, ya que el patrimonio autónomo es administrado por el contratista y la fiduciaria debe cumplir con las instrucciones del contratista. La parte que tiene derecho sobre esos recursos es el beneficiario del contrato.",
  "pasajes_usados": [
    "decreto_1082_de_2015:00182:ef633ec18771",
    "ley_1116_de_2006:00039:3405fdcac51b",
    "ley_1258_de_2008:00011:56f7de68841e",
    "decreto_663_de_1993:00420:33cc13e9205c",
    "sentencia_c_207_de_2019:00146:caa02b6f88e6"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 15 → después 11 · reparación {'suppressed_fragment': 3, 'suppressed_sentence': 2} · construidas ['artículo 2.2.1.2.3.3.1 del Decreto 1082 de 2015', 'artículo 38 de la Ley 1116 de 2006', 'artículo 12 de la Ley 1258 de 2008']
**Pasajes declarados por el modelo:** ['decreto_1082_de_2015:00182:ef633ec18771', 'ley_1116_de_2006:00039:3405fdcac51b', 'ley_1258_de_2008:00011:56f7de68841e', 'decreto_663_de_1993:00420:33cc13e9205c', 'sentencia_c_207_de_2019:00146:caa02b6f88e6']
**Evidencia:**
1. `decreto_1082_de_2015:00182:ef633ec18771` — Decreto 1082 de 2015 art. 2.2.1.2.3.3.1
2. `ley_1116_de_2006:00039:3405fdcac51b` — Ley 1116 de 2006 art. 38
3. `ley_1258_de_2008:00011:56f7de68841e` — Ley 1258 de 2008 art. 12
4. `ley_1116_de_2006:00052:e8ecfb330b7f` — Ley 1116 de 2006 art. 50
5. `decreto_663_de_1993:00420:33cc13e9205c` — Decreto 663 de 1993 art. 283
6. `decreto_1082_de_2015:00055:b42d9d844b35` — Decreto 1082 de 2015 art. 2.2.1.1.2.4.1
7. `sentencia_c_207_de_2019:00146:caa02b6f88e6` — Sentencia C-207 de 2019 art. None
8. `ley_1116_de_2006:00014:4867114693bc` — Ley 1116 de 2006 art. 15
*Tokens 6430→864 · generación 35248.955200004275 ms · retrieval 37.445399997523054 ms · grafo off*

## 280 · semi_open

**Pregunta:** ¿Cuál es el artículo del código penal colombiano que define los requisitos que un juez debe tomar en cuenta para conceder la libertad condicional?

**Medición:** cita=cita_ok · legal_basis=Artículo 64 del código penal colombiano

**Respuesta final:**
```json
{
  "respuesta": "El artículo 64 del Código Penal (Ley 599 de 2000) define los requisitos que un juez debe tomar en cuenta para conceder la libertad condicional. Estos incluyen que la persona haya cumplido las tres quintas partes de la pena, demuestre adecuado desempeño y comportamiento durante el tratamiento penitenciario, y muestre arraigo familiar y social. Además, la concesión está supeditada a la reparación a la víctima o al aseguramiento del pago de la indemnización.",
  "palabras_clave": [
    "libertad condicional",
    "Código Penal"
  ],
  "referencia_legal": "artículo 64 del Código Penal; artículo 471 del Código de Procedimiento Penal; artículo 479 de la Ley 600 de 2000; artículo 63 del Código Penal; artículo 474 del Código de Procedimiento Penal; Ley 2098 de 2021; Ley 890 de 2004; Ley 1709 de 2014"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El artículo 64 del Código Penal (Ley 599 de 2000) define los requisitos que un juez debe tomar en cuenta para conceder la libertad condicional. Estos incluyen que la persona haya cumplido las tres quintas partes de la pena, demuestre adecuado desempeño y comportamiento durante el tratamiento penitenciario, y muestre arraigo familiar y social. Además, la concesión está supeditada a la reparación a la víctima o al aseguramiento del pago de la indemnización.","palabras_clave":["artículo 64","libertad condicional","Código Penal"],"referencia_legal":"codigo_penal:00083:d667540b7f50","pasajes_usados":["codigo_penal:00083:d667540b7f50"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 5 → después 17 · reparación {'suppressed_fragment': 1, 'suppressed_sentence': 1} · construidas ['artículo 64 del Código Penal', 'artículo 471 del Código de Procedimiento Penal', 'artículo 479 de la Ley 600 de 2000', 'artículo 63 del Código Penal', 'artículo 474 del Código de Procedimiento Penal', 'Ley 2098 de 2021', 'Ley 890 de 2004', 'Ley 1709 de 2014']
**Pasajes declarados por el modelo:** ['codigo_penal:00083:d667540b7f50']
**Evidencia:**
1. `codigo_penal:00083:d667540b7f50` — Código Penal (Ley 599 de 2000) art. 64
2. `codigo_procedimiento_penal:00498:99920ea4b636` — Código de Procedimiento Penal (Ley 906 de 2004) art. 471
3. `ley_600_de_2000:00431:3b486270f6e9` — Ley 600 de 2000 art. 479
4. `codigo_penal:00082:72457621d34f` — Código Penal (Ley 599 de 2000) art. 63
5. `codigo_procedimiento_penal:00501:653e23d7f798` — Código de Procedimiento Penal (Ley 906 de 2004) art. 474
6. `ley_600_de_2000:00434:4e42c5fde7da` — Ley 600 de 2000 art. 483
7. `codigo_procedimiento_penal:00506:a3b9cfb10c76` — Código de Procedimiento Penal (Ley 906 de 2004) art. 479
8. `codigo_procedimiento_penal:00499:4c75c332783a` — Código de Procedimiento Penal (Ley 906 de 2004) art. 472
*Tokens 3338→207 · generación 7315.994000004139 ms · retrieval 28.53049999976065 ms · grafo off*

## 290 · multiple_choice · ✔ correcta

**Pregunta:** En caso de no pactar un plazo para la liquidación bilateral de un contrato Estatal sometido al Estatuto de contratación, ¿cuál sería el plazo supletorio de este?

- A: 2 años 
- B: 8 meses 
- C: 4 meses 
- D: 2 meses 

**Medición:** cita=cita_ok · legal_basis=Artículo 11 ley 1150 de 2007

**Respuesta final:**
```json
{
  "respuesta_correcta": "C",
  "justificacion": "La pregunta se refiere al plazo supletorio para la liquidación bilateral de un contrato Estatal cuando no se pacta un plazo en los pliegos de condiciones. De acuerdo con el artículo 11 de la Ley 1150 de 2007, si no existe un término fijado en los pliegos de condiciones o sus equivalentes, la liquidación se realizará dentro de los cuatro (4) meses siguientes a la expiración del término previsto para la ejecución del contrato o a la expedición del acto administrativo que ordene la terminación, o a la fecha del acuerdo que la disponga. Por lo tanto, el plazo supletorio es de 4 meses. Fundamento normativo: artículo 2.2.1.1.2.1.2 del Decreto 1082 de 2015; artículo 2.2.1.2.3.1.3 del Decreto 1082 de 2015; artículo 2.2.1.2.3.1.18 del Decreto 1082 de 2015; artículo 2.2.2.1.5.11 del Decreto 1082 de 2015; Decreto 1510 de 2013; Ley 1508 de 2012; Decreto 438 de 2021.",
  "descarte_opciones": {
    "A": "No se menciona en la norma",
    "B": "No se menciona en la norma",
    "D": "No se menciona en la norma"
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"La pregunta se refiere al plazo supletorio para la liquidación bilateral de un contrato Estatal cuando no se pacta un plazo en los pliegos de condiciones. De acuerdo con el artículo 11 de la Ley 1150 de 2007, si no existe un término fijado en los pliegos de condiciones o sus equivalentes, la liquidación se realizará dentro de los cuatro (4) meses siguientes a la expiración del término previsto para la ejecución del contrato o a la expedición del acto administrativo que ordene la terminación, o a la fecha del acuerdo que la disponga. Por lo tanto, el plazo supletorio es de 4 meses.","respuesta_correcta":"C","descarte_opciones":{"A":"No se menciona en la norma","B":"No se menciona en la norma","D":"No se menciona en la norma"},"pasajes_usados":["ley_1150_de_2007:00020:a442ace14a36"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 2 → después 13 · reparación {} · construidas ['artículo 11 de la Ley 1150 de 2007', 'artículo 2.2.1.1.2.1.2 del Decreto 1082 de 2015', 'artículo 2.2.1.2.3.1.3 del Decreto 1082 de 2015', 'artículo 2.2.1.2.3.1.18 del Decreto 1082 de 2015', 'artículo 2.2.2.1.5.11 del Decreto 1082 de 2015', 'Decreto 1510 de 2013', 'Ley 1508 de 2012', 'Decreto 438 de 2021']
**Pasajes declarados por el modelo:** ['ley_1150_de_2007:00020:a442ace14a36']
**Evidencia:**
1. `decreto_1082_de_2015:00040:ae5297bce595` — Decreto 1082 de 2015 art. 2.2.1.1.2.1.2
2. `decreto_1082_de_2015:00154:24b44755c8b5` — Decreto 1082 de 2015 art. 2.2.1.2.3.1.3
3. `ley_1150_de_2007:00020:a442ace14a36` — Ley 1150 de 2007 art. 11
4. `decreto_1082_de_2015:00169:de0e0b06e4cf` — Decreto 1082 de 2015 art. 2.2.1.2.3.1.18
5. `decreto_1082_de_2015:00286:3139d30e8aaa` — Decreto 1082 de 2015 art. 2.2.2.1.5.11
6. `sentencia_c_207_de_2019:00034:dfe3789e0c02` — Sentencia C-207 de 2019 art. None
7. `decreto_1082_de_2015:00301:8dd4330675f0` — Decreto 1082 de 2015 art. 2.2.2.1.8.3
8. `decreto_1082_de_2015:00031:ebe4765c5d2d` — Decreto 1082 de 2015 art. 2.2.1.1.1.6.4
*Tokens 5564→244 · generación 10644.238699998823 ms · retrieval 69.61240000964608 ms · grafo off*

## 308 · multiple_choice · ✔ correcta

**Pregunta:** ¿Cuál es el plazo de liquidación del contrato de manera unilateral?


- A: 2 meses
- B: No hay plazo
- C: Dos años
- D: 4 meses

**Medición:** cita=sin_ref_parseable · legal_basis=Art 44 ley 1150 

**Respuesta final:**
```json
{
  "respuesta_correcta": "A",
  "justificacion": "C. A. Por lo tanto, el plazo de liquidación del contrato de manera unilateral es de 2 meses. Fundamento normativo: artículo 11 de la Ley 1150 de 2007; artículo 5 de la Ley 50 de 1990; artículo 16 de la Ley 80 de 1993; artículo 61 del Código Sustantivo del Trabajo; Sentencia C-207 de 2019; Decreto 2351 de 1965; Sentencia C-16 de 1998; Sentencia C-1507 de 2000.",
  "descarte_opciones": {
    "B": "No hay plazo: Esto es incorrecto, ya que el artículo 11 de la Ley 1150 de 2007 establece un plazo de 2 meses para la liquidación unilateral.",
    "C": "C. A.",
    "D": "4 meses: Esto es incorrecto, ya que el plazo de 4 meses se refiere a la liquidación dentro de los cuatro (4) meses siguientes a la expiración del término previsto para la ejecución del contrato o a la expedición del acto administrativo que ordene la terminación, o a la fecha del acuerdo que la disponga."
  }
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "justificacion": "De acuerdo con el artículo 11 de la Ley 1150 de 2007, si el contratista no se presenta a la liquidación previa notificación o convocatoria que le haga la entidad, o las partes no lleguen a un acuerdo sobre su contenido, la entidad tendrá la facultad de liquidar en forma unilateral dentro de los dos (2) meses siguientes, de conformidad con lo dispuesto en el artículo 136 del C. C. A. Por lo tanto, el plazo de liquidación del contrato de manera unilateral es de 2 meses.",
  "respuesta_correcta": "A",
  "descarte_opciones": {
    "B": "No hay plazo: Esto es incorrecto, ya que el artículo 11 de la Ley 1150 de 2007 establece un plazo de 2 meses para la liquidación unilateral.",
    "C": "Dos años: Esto es incorrecto, ya que el plazo de dos años se refiere a la liquidación en cualquier tiempo dentro de los dos años siguientes al vencimiento del término a que se refieren los incisos anteriores, de mutuo acuerdo o unilateralmente, sin perjuicio de lo previsto en el artículo 136 del C. C. A.",
    "D": "4 meses: Esto es incorrecto, ya que el plazo de 4 meses se refiere a la liquidación dentro de los cuatro (4) meses siguientes a la expiración del término previsto para la ejecución del contrato o a la expedición del acto administrativo que ordene la terminación, o a la fecha del acuerdo que la disponga."
  },
  "pasajes_usados": [
    "ley_1150_de_2007:00020:a442ace14a36"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 6 → después 14 · reparación {'suppressed_sentence': 2} · construidas ['artículo 11 de la Ley 1150 de 2007', 'artículo 5 de la Ley 50 de 1990', 'artículo 16 de la Ley 80 de 1993', 'artículo 61 del Código Sustantivo del Trabajo', 'Sentencia C-207 de 2019', 'Decreto 2351 de 1965', 'Sentencia C-16 de 1998', 'Sentencia C-1507 de 2000']
**Pasajes declarados por el modelo:** ['ley_1150_de_2007:00020:a442ace14a36']
**Evidencia:**
1. `ley_1150_de_2007:00020:a442ace14a36` — Ley 1150 de 2007 art. 11
2. `ley_50_de_1990:00004:d1a5e529e3e6` — Ley 50 de 1990 art. 5
3. `ley_80_de_1993:00021:e5d787cb298e` — Ley 80 de 1993 art. 16
4. `codigo_sustantivo_trabajo:00060:7142bbd6ef28` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 61
5. `sentencia_c_207_de_2019:00079:6babc1b45b07` — Sentencia C-207 de 2019 art. None
6. `cpaca:00179:7b13bd2bf137` — Código de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) art. 164
7. `sentencia_c_207_de_2019:00101:675156a88518` — Sentencia C-207 de 2019 art. None
8. `sentencia_c_207_de_2019:00027:99881ee5b5f7` — Sentencia C-207 de 2019 art. None
*Tokens 6364→421 · generación 17609.91159999685 ms · retrieval 43.278299999656156 ms · grafo off*

## 352 · multiple_choice · ✔ correcta

**Pregunta:** La Corte Constitucional de Colombia puede decretar la nulidad de los procesos que tramita cuando:

- A: Exista desacuerdo sobre la ponencia debatida
- B: Se acredite una violación del debido proceso
- C: No haya quórum para discutir la ponencia bajo revisión
- D: Así lo solicite cualquier ciudadano

**Medición:** cita=cita_ok · legal_basis=Decreto 2067 de 1991, art. 49 (nulidad por violación del debido proceso).

**Respuesta final:**
```json
{
  "respuesta_correcta": "B",
  "justificacion": "La Sentencia C-239 de 1997 establece que la nulidad de los procesos ante la Corte Constitucional solo podrá ser alegada antes de proferido el fallo y que las irregularidades que impliquen violación del debido proceso podrán servir de base para que el Pleno de la Corte anule el proceso. Por lo tanto, la nulidad solo puede ser solicitada cuando se acredite una violación del debido proceso. Esto se refleja en el artículo 49 del Decreto 2067 de 1991, que establece que contra las sentencias de la Corte Constitucional no procede recurso alguno y que la nulidad solo puede ser alegada antes del fallo. La opción B es la correcta porque se alinea con esta normativa. Fundamento normativo: Sentencia C-355 de 2006; artículo 1914 del Código de Comercio; Sentencia SU-214 de 2016; Constitución Política; Sentencia C-1299 de 2005; Sentencia C-1300 de 2005.",
  "descarte_opciones": {
    "A": "No se menciona desacuerdo sobre la ponencia como causa para la nulidad.",
    "C": "No se menciona quórum como causa para la nulidad.",
    "D": "No se menciona que cualquier ciudadano pueda solicitar la nulidad sin cumplir con requisitos."
  }
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "justificacion": "La Sentencia C-239 de 1997 establece que la nulidad de los procesos ante la Corte Constitucional solo podrá ser alegada antes de proferido el fallo y que las irregularidades que impliquen violación del debido proceso podrán servir de base para que el Pleno de la Corte anule el proceso. Por lo tanto, la nulidad solo puede ser solicitada cuando se acredite una violación del debido proceso. Esto se refleja en el artículo 49 del Decreto 2067 de 1991, que establece que contra las sentencias de la Corte Constitucional no procede recurso alguno y que la nulidad solo puede ser alegada antes del fallo. La opción B es la correcta porque se alinea con esta normativa.",
  "respuesta_correcta": "B",
  "descarte_opciones": {
    "A": "No se menciona desacuerdo sobre la ponencia como causa para la nulidad.",
    "C": "No se menciona quórum como causa para la nulidad.",
    "D": "No se menciona que cualquier ciudadano pueda solicitar la nulidad sin cumplir con requisitos."
  },
  "pasajes_usados": [
    "sentencia_c_239_de_1997:00085:bff064fc20f4",
    "sentencia_c_239_de_1997:00084:9b3f9fad0f54",
    "sentencia_c_239_de_1997:00097:492283098fdb",
    "decreto_2067_de_1991:00048:2a53e2667adc"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 3 → después 10 · reparación {} · construidas ['Sentencia C-239 de 1997', 'artículo 49 del Decreto 2067 de 1991', 'Sentencia C-355 de 2006', 'artículo 1914 del Código de Comercio', 'Sentencia SU-214 de 2016', 'Constitución Política', 'Sentencia C-1299 de 2005', 'Sentencia C-1300 de 2005']
**Pasajes declarados por el modelo:** ['sentencia_c_239_de_1997:00085:bff064fc20f4', 'sentencia_c_239_de_1997:00084:9b3f9fad0f54', 'sentencia_c_239_de_1997:00097:492283098fdb', 'decreto_2067_de_1991:00048:2a53e2667adc']
**Evidencia:**
1. `sentencia_c_239_de_1997:00085:bff064fc20f4` — Sentencia C-239 de 1997 art. None
2. `sentencia_c_239_de_1997:00084:9b3f9fad0f54` — Sentencia C-239 de 1997 art. None
3. `sentencia_c_239_de_1997:00097:492283098fdb` — Sentencia C-239 de 1997 art. None
4. `sentencia_c_355_de_2006:00256:2c38f21835ef` — Sentencia C-355 de 2006 art. None
5. `decreto_2067_de_1991:00048:2a53e2667adc` — Decreto 2067 de 1991 art. 49
6. `codigo_comercio:01989:5e28bef5c68b` — Código de Comercio (Decreto 410 de 1971) art. 1914
7. `sentencia_c_239_de_1997:00102:7f429cd67b33` — Sentencia C-239 de 1997 art. None
8. `sentencia_su_214_de_2016:00217:89ed0ec89393` — Sentencia SU-214 de 2016 art. None
*Tokens 7029→436 · generación 18528.737699991325 ms · retrieval 58.54820000240579 ms · grafo off*

## 358 · multiple_choice · ✘ esperada D

**Pregunta:** Conforme a la tradición civilista (civil law), ¿qué mecanismo procesal se encuentra previsto para reclamar la restitución derivada de una usurpación o transferencia ilegal de bienes?

- A: Ninguna de las anteriores.
- B: Acción posesoria.
- C: Acción resolutoria.
- D: Acción reivindicatoria.

**Medición:** cita=cita_ok · legal_basis=c) Acción reivindicatoria, disponible únicamente para los dueños legales del bien, de acuerdo con el artículo 946 del C.C.


**Respuesta final:**
```json
{
  "respuesta_correcta": "A",
  "justificacion": "La Sentencia SU-214 de 2016 menciona que en los países de tradición civilista, como Colombia, las Cortes tienen el poder constitucional para invalidar la discriminación legal. Esto implica que en el sistema jurídico colombiano, se permite a las Cortes Constitucionales actuar para corregir situaciones de ilegalidad o discriminación, incluyendo la usurpación o transferencia ilegal de bienes. Sin embargo, el mecanismo procesal específico para reclamar la restitución derivada de una usurpación o transferencia ilegal de bienes no se menciona directamente en los pasajes proporcionados. La Sentencia T-77 de 2025 no aborda este tema. Por lo tanto, la opción correcta es la que indica que no hay mecanismo procesal previsto para reclamar la restitución derivada de una usurpación o transferencia ilegal de bienes, ya que no se menciona directamente en los pasajes proporcionados. Fundamento normativo: artículo 571 del Código General del Proceso; artículo 33 de la Ley 160 de 1994; artículo 384 del Código General del Proceso; Código Civil; Ley 1116 de 2006; Decreto 508 de 1974.",
  "descarte_opciones": {
    "B": "La acción posesoria se refiere a la recuperación de un bien por prescripción, lo cual no se menciona directamente en los pasajes proporcionados.",
    "C": "La acción resolutoria se refiere a la anulación de un acto jurídico, lo cual no se menciona directamente en los pasajes proporcionados.",
    "D": "La acción reivindicatoria se refiere a la recuperación de un bien por el derecho de propiedad, lo cual no se menciona directamente en los pasajes proporcionados."
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"La Sentencia SU-214 de 2016 menciona que en los países de tradición civilista, como Colombia, las Cortes tienen el poder constitucional para invalidar la discriminación legal. Esto implica que en el sistema jurídico colombiano, se permite a las Cortes Constitucionales actuar para corregir situaciones de ilegalidad o discriminación, incluyendo la usurpación o transferencia ilegal de bienes. Por otro lado, el Código General del Proceso (Ley 1564 de 2012) en su artículo 571 establece los efectos de la adjudicación, lo cual se relaciona con la restitución de bienes. Sin embargo, el mecanismo procesal específico para reclamar la restitución derivada de una usurpación o transferencia ilegal de bienes no se menciona directamente en los pasajes proporcionados. La Sentencia T-77 de 2025 no aborda este tema. Por lo tanto, la opción correcta es la que indica que no hay mecanismo procesal previsto para reclamar la restitución derivada de una usurpación o transferencia ilegal de bienes, ya que no se menciona directamente en los pasajes proporcionados.","respuesta_correcta":"A","descarte_opciones":{"B":"La acción posesoria se refiere a la recuperación de un bien por prescripción, lo cual no se menciona directamente en los pasajes proporcionados.","C":"La acción resolutoria se refiere a la anulación de un acto jurídico, lo cual no se menciona directamente en los pasajes proporcionados.","D":"La acción reivindicatoria se refiere a la recuperación de un bien por el derecho de propiedad, lo cual no se menciona directamente en los pasajes proporcionados."},"pasajes_usados":["sentencia_su_214_de_2016:00184:fcaf8421c912","codigo_general_proceso:00593:c1edf5972d50"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 5 → después 11 · reparación {'suppressed_sentence': 1} · construidas ['Sentencia SU-214 de 2016', 'artículo 571 del Código General del Proceso', 'artículo 33 de la Ley 160 de 1994', 'Sentencia T-77 de 2025', 'artículo 384 del Código General del Proceso', 'Código Civil', 'Ley 1116 de 2006', 'Decreto 508 de 1974']
**Pasajes declarados por el modelo:** ['sentencia_su_214_de_2016:00184:fcaf8421c912', 'codigo_general_proceso:00593:c1edf5972d50']
**Evidencia:**
1. `sentencia_su_214_de_2016:00184:fcaf8421c912` — Sentencia SU-214 de 2016 art. None
2. `ley_160_de_1994:00040:137fbbf11276` — Ley 160 de 1994 art. 33
3. `sentencia_t_77_de_2025:00026:131cfcc7f11e` — Sentencia T-77 de 2025 art. None
4. `codigo_general_proceso:00396:a7ec72cd2300` — Código General del Proceso (Ley 1564 de 2012) art. 384
5. `codigo_comercio:01763:9fce23dd9450` — Código de Comercio (Decreto 410 de 1971) art. 1687
6. `codigo_procedimiento_penal:00075:34b0feb2b224` — Código de Procedimiento Penal (Ley 906 de 2004) art. 74
7. `codigo_general_proceso:00593:c1edf5972d50` — Código General del Proceso (Ley 1564 de 2012) art. 571
8. `codigo_civil:00971:8f1814731196` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 973
*Tokens 7091→476 · generación 20229.91799999727 ms · retrieval 54.26370000350289 ms · grafo off*

## 442 · semi_open

**Pregunta:** Cité un fragmento de el artículo 60 del código sustantivo del trabajo que menciona la prohibición al trabajador de disminuir el ritmo de trabajo.

**Medición:** cita=cita_ok · legal_basis=El Código sustantivo del trabajo 

**Respuesta final:**
```json
{
  "respuesta": "El artículo 60 del Código Sustantivo del Trabajo (Decreto 2663 de 1950) prohíbe al trabajador disminuir intencionalmente el ritmo de ejecución del trabajo, suspender labores, promover suspensiones intempestivas del trabajo o excitar a su declaración o mantenimiento, sea que participe o no en ellas.",
  "palabras_clave": [
    "Código Sustantivo del Trabajo",
    "prohibición",
    "ritmo de trabajo"
  ],
  "referencia_legal": "artículo 60 del Código Sustantivo del Trabajo; artículo 343 del Código Sustantivo del Trabajo; artículo 65 del Código Sustantivo del Trabajo; artículo 136 del Código Sustantivo del Trabajo; Ley 2141 de 2021; Sentencia C-781 de 2003; Sentencia C-892 de 2009; Ley 789 de 2002"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El artículo 60 del Código Sustantivo del Trabajo (Decreto 2663 de 1950) prohíbe al trabajador disminuir intencionalmente el ritmo de ejecución del trabajo, suspender labores, promover suspensiones intempestivas del trabajo o excitar a su declaración o mantenimiento, sea que participe o no en ellas.","palabras_clave":["artículo 60","Código Sustantivo del Trabajo","prohibición","ritmo de trabajo"],"referencia_legal":"codigo_sustantivo_trabajo:00059:fa8d3365aa21","pasajes_usados":["codigo_sustantivo_trabajo:00059:fa8d3365aa21"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_1_outside_3_5']
**Citas:** antes 5 → después 16 · reparación {'suppressed_fragment': 1, 'suppressed_sentence': 1} · construidas ['artículo 60 del Código Sustantivo del Trabajo', 'artículo 343 del Código Sustantivo del Trabajo', 'artículo 65 del Código Sustantivo del Trabajo', 'artículo 136 del Código Sustantivo del Trabajo', 'Ley 2141 de 2021', 'Sentencia C-781 de 2003', 'Sentencia C-892 de 2009', 'Ley 789 de 2002']
**Pasajes declarados por el modelo:** ['codigo_sustantivo_trabajo:00059:fa8d3365aa21']
**Evidencia:**
1. `codigo_sustantivo_trabajo:00059:fa8d3365aa21` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 60
2. `codigo_sustantivo_trabajo:00355:38750db83bb3` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 343
3. `codigo_sustantivo_trabajo:00065:3a1c4bd7813c` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 65
4. `codigo_sustantivo_trabajo:00137:ade6fe19a20d` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 136
5. `ley_2141_de_2021:00000:c6a5d7ead9bb` — Ley 2141 de 2021 art. 1
6. `ley_2466_de_2025:00051:0ff973653e2d` — Ley 2466 de 2025 art. 48
7. `codigo_sustantivo_trabajo:00150:b09b99550711` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 149
8. `ley_50_de_1990:00036:059f731c17e6` — Ley 50 de 1990 art. 37
*Tokens 4885→185 · generación 7301.321200007806 ms · retrieval 27.706300010322593 ms · grafo off*

## 453 · semi_open

**Pregunta:** ¿Cuál es el principal precedente jurisprudencial en Colombia sobre el reconocimiento de los animales como seres sintientes? 

**Medición:** cita=cita_ok · legal_basis=Sentencia C-468 de 2024, sentencia C-332 de 2025 y SU-016 de 2020

**Respuesta final:**
```json
{
  "respuesta": "En esta sentencia, la Corte Constitucional estableció que los animales deben ser considerados como seres sintientes, lo que implica que tienen un interés en no sentir dolor ni ser dañados.",
  "palabras_clave": [
    "reconocimiento",
    "seres sintientes",
    "jurisprudencia",
    "Corte Constitucional"
  ],
  "referencia_legal": "Sentencia C-332 de 2025; Sentencia C-55 de 2022; Ley 84 de 1989; Constitución Política; Sentencia C-666 de 2010"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El principal precedente jurisprudencial en Colombia sobre el reconocimiento de los animales como seres sintientes es la Sentencia C-467 de 2016. En esta sentencia, la Corte Constitucional estableció que los animales deben ser considerados como seres sintientes, lo que implica que tienen un interés en no sentir dolor ni ser dañados. Este reconocimiento se basa en la Constitución y en la jurisprudencia constante de la Corporación.","palabras_clave":["reconocimiento","seres sintientes","jurisprudencia","Corte Constitucional","Sentencia C-467 de 2016"],"referencia_legal":"Sentencia C-467 de 2016","pasajes_usados":["sentencia_c_332_de_2025:00032:fc4390247b97","sentencia_c_332_de_2025:00033:7a9e6dc83297"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 4 → después 5 · reparación {'suppressed_fragment': 2, 'suppressed_sentence': 4} · construidas ['Sentencia C-332 de 2025', 'Sentencia C-55 de 2022', 'Ley 84 de 1989', 'Constitución Política', 'Sentencia C-666 de 2010']
**Pasajes declarados por el modelo:** ['sentencia_c_332_de_2025:00032:fc4390247b97', 'sentencia_c_332_de_2025:00033:7a9e6dc83297']
**Evidencia:**
1. `sentencia_c_332_de_2025:00032:fc4390247b97` — Sentencia C-332 de 2025 art. None
2. `sentencia_c_55_de_2022:00330:a814c9c40c7c` — Sentencia C-55 de 2022 art. None
3. `sentencia_c_332_de_2025:00048:0d30a5834964` — Sentencia C-332 de 2025 art. None
4. `sentencia_c_332_de_2025:00022:d131f2f00f88` — Sentencia C-332 de 2025 art. None
5. `sentencia_c_332_de_2025:00008:06600d24b379` — Sentencia C-332 de 2025 art. None
6. `sentencia_c_332_de_2025:00033:7a9e6dc83297` — Sentencia C-332 de 2025 art. None
7. `sentencia_c_332_de_2025:00020:12d64e4f047c` — Sentencia C-332 de 2025 art. None
8. `sentencia_c_332_de_2025:00009:d94c1f92c37a` — Sentencia C-332 de 2025 art. None
*Tokens 6834→246 · generación 11133.694799995283 ms · retrieval 14.230400003725663 ms · grafo off*

## 472 · semi_open

**Pregunta:** Cuales son los requisitos que exige la ley para el control de integraciones empresariales? 

**Medición:** cita=cita_ok · legal_basis=Ley 1340 de 2009

**Respuesta final:**
```json
{
  "respuesta": "La ley establece que las empresas que se dediquen a la misma actividad económica o participen en la misma cadena de valor, y que cumplan con ciertas condiciones, estarán obligadas a informar sobre operaciones de integración empresarial. Estas condiciones incluyen tener ingresos operacionales o activos totales superiores a un monto determinado por la Superintendencia de Industria y Comercio. Además, en algunos casos, se requiere la notificación previa a la Superintendencia de Industria y Comercio.",
  "palabras_clave": [
    "control de integraciones empresariales",
    "ingresos operacionales",
    "activos totales",
    "Superintendencia de Industria y Comercio"
  ],
  "referencia_legal": "artículo 9 de la Ley 1340 de 2009; artículo 33 de la Ley 1340 de 2009; artículo 46 del Decreto 2153 de 1992; artículo 2 de la Ley 1340 de 2009; artículo 8 de la Ley 1340 de 2009; Ley 155 de 1959; Ley 222 de 1995; Código Civil"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La ley establece que las empresas que se dediquen a la misma actividad económica o participen en la misma cadena de valor, y que cumplan con ciertas condiciones, estarán obligadas a informar sobre operaciones de integración empresarial. Estas condiciones incluyen tener ingresos operacionales o activos totales superiores a un monto determinado por la Superintendencia de Industria y Comercio. Además, en algunos casos, se requiere la notificación previa a la Superintendencia de Industria y Comercio.","palabras_clave":["control de integraciones empresariales","ingresos operacionales","activos totales","Superintendencia de Industria y Comercio"],"referencia_legal":"ley_1340_de_2009:00008:d7e885341c50","pasajes_usados":["ley_1340_de_2009:00008:d7e885341c50"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 0 → después 13 · reparación {} · construidas ['artículo 9 de la Ley 1340 de 2009', 'artículo 33 de la Ley 1340 de 2009', 'artículo 46 del Decreto 2153 de 1992', 'artículo 2 de la Ley 1340 de 2009', 'artículo 8 de la Ley 1340 de 2009', 'Ley 155 de 1959', 'Ley 222 de 1995', 'Código Civil']
**Pasajes declarados por el modelo:** ['ley_1340_de_2009:00008:d7e885341c50']
**Evidencia:**
1. `ley_1340_de_2009:00033:43459ffa1f51` — Ley 1340 de 2009 art. 33
2. `decreto_2153_de_1992:00049:7821acf23781` — Decreto 2153 de 1992 art. 46
3. `ley_1340_de_2009:00001:8f7ee6104e47` — Ley 1340 de 2009 art. 2
4. `ley_1340_de_2009:00007:d5ae8eeb6058` — Ley 1340 de 2009 art. 8
5. `ley_1340_de_2009:00008:d7e885341c50` — Ley 1340 de 2009 art. 9
6. `codigo_comercio:00484:fe9b95b24867` — Código de Comercio (Decreto 410 de 1971) art. 476
7. `estatuto_tributario:00956:16afc95d6550` — Estatuto Tributario (Decreto 624 de 1989) art. 587-1
8. `ley_1116_de_2006:00001:b0804ab86185` — Ley 1116 de 2006 art. 2
*Tokens 4155→235 · generación 9533.312400002615 ms · retrieval 18.587099999422207 ms · grafo off*

## 487 · multiple_choice · ✔ correcta

**Pregunta:** ¿Qué es la disolución de la sociedad conyugal?

- A: La declaración de que la sociedad conyugal ha terminado. 
- B: Un requisito para la liquidación. 
- C: Una forma más rápida para divorciarse. 
- D: La liquidación de la sociedad conyugal. 

**Medición:** cita=cita_ok · legal_basis=1820 del Código Civil. 

**Respuesta final:**
```json
{
  "respuesta_correcta": "A",
  "justificacion": "La disolución de la sociedad conyugal se refiere a la terminación de la relación jurídica entre los cónyuges. Según el artículo 1820 del Código Civil, la sociedad conyugal se disuelve por diversos motivos, entre ellos la disolución del matrimonio, la separación judicial de cuerpos, la sentencia de separación de bienes, la declaración de nulidad del matrimonio y el mutuo acuerdo de los cónyuges. Por lo tanto, la disolución de la sociedad conyugal es la terminación de esta relación, lo que se refleja en la opción A. Las otras opciones no definen correctamente la disolución de la sociedad conyugal, ya que una liquidación es un proceso posterior a la disolución, un requisito no es la definición de la disolución, y una forma más rápida para divorciarse no se menciona en la evidencia. Fundamento normativo: artículo 523 del Código General del Proceso; artículo 69 de la Ley 2220 de 2022; artículo 22 del Código General del Proceso; artículo 23 del Código General del Proceso; Ley 57 de 1887; Ley 1996 de 2019; Ley 2447 de 2025.",
  "descarte_opciones": {
    "B": "Un requisito para la liquidación no define la disolución de la sociedad conyugal.",
    "C": "Una forma más rápida para divorciarse no se menciona en la evidencia.",
    "D": "La liquidación de la sociedad conyugal es un proceso posterior a la disolución."
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"La disolución de la sociedad conyugal se refiere a la terminación de la relación jurídica entre los cónyuges. Según el artículo 1820 del Código Civil, la sociedad conyugal se disuelve por diversos motivos, entre ellos la disolución del matrimonio, la separación judicial de cuerpos, la sentencia de separación de bienes, la declaración de nulidad del matrimonio y el mutuo acuerdo de los cónyuges. Por lo tanto, la disolución de la sociedad conyugal es la terminación de esta relación, lo que se refleja en la opción A. Las otras opciones no definen correctamente la disolución de la sociedad conyugal, ya que una liquidación es un proceso posterior a la disolución, un requisito no es la definición de la disolución, y una forma más rápida para divorciarse no se menciona en la evidencia.","respuesta_correcta":"A","descarte_opciones":{"B":"Un requisito para la liquidación no define la disolución de la sociedad conyugal.","C":"Una forma más rápida para divorciarse no se menciona en la evidencia.","D":"La liquidación de la sociedad conyugal es un proceso posterior a la disolución."},"pasajes_usados":["codigo_civil:01818:faa724d12b7e"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 2 → después 13 · reparación {} · construidas ['artículo 1820 del Código Civil', 'artículo 523 del Código General del Proceso', 'artículo 69 de la Ley 2220 de 2022', 'artículo 22 del Código General del Proceso', 'artículo 23 del Código General del Proceso', 'Ley 57 de 1887', 'Ley 1996 de 2019', 'Ley 2447 de 2025']
**Pasajes declarados por el modelo:** ['codigo_civil:01818:faa724d12b7e']
**Evidencia:**
1. `codigo_civil:01818:faa724d12b7e` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1820
2. `codigo_general_proceso:00543:e619df7325af` — Código General del Proceso (Ley 1564 de 2012) art. 523
3. `ley_2220_de_2022:00071:8788a8bab59a` — Ley 2220 de 2022 art. 69
4. `codigo_general_proceso:00021:52321c1b4f18` — Código General del Proceso (Ley 1564 de 2012) art. 22
5. `codigo_general_proceso:00022:6044d07399d7` — Código General del Proceso (Ley 1564 de 2012) art. 23
6. `codigo_civil:01793:78aa9859c8cb` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1795
7. `ley_640_de_2001:00039:3ed05ab97955` — Ley 640 de 2001 art. 40
8. `ley_979_de_2005:00003:e88f9f2136f2` — Ley 979 de 2005 art. 4
*Tokens 5469→307 · generación 12304.97299999115 ms · retrieval 15.387000006739981 ms · grafo off*

## 490 · semi_open

**Pregunta:** ¿Qué comprende los pasivos de la sociedad conyugal?

**Medición:** cita=cita_ok · legal_basis=1796 del Código Civil. 

**Respuesta final:**
```json
{
  "respuesta": "Los pasivos de la sociedad conyugal comprenden las obligaciones que consten en título que preste mérito ejecutivo, siempre que en la audiencia no se objeten, y las que a pesar de no tener dicha calidad se acepten expresamente en ella por todos los herederos o por estos y por el cónyuge o compañero permanente, cuando conciernan a la sociedad conyugal o patrimonial. También se incluyen los créditos de los acreedores que concurran a la audiencia.",
  "palabras_clave": [
    "sociedad conyugal",
    "pasivos",
    "obligaciones",
    "acreedores",
    "audiencia"
  ],
  "referencia_legal": "artículo 501 del Código General del Proceso; artículo 523 del Código General del Proceso; artículo 1820 del Código Civil; artículo 1774 del Código Civil; artículo 1804 del Código Civil; Ley 28 de 1932; Ley 57 de 1887; Constitución Política"
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "respuesta": "Los pasivos de la sociedad conyugal comprenden las obligaciones que consten en título que preste mérito ejecutivo, siempre que en la audiencia no se objeten, y las que a pesar de no tener dicha calidad se acepten expresamente en ella por todos los herederos o por estos y por el cónyuge o compañero permanente, cuando conciernan a la sociedad conyugal o patrimonial. También se incluyen los créditos de los acreedores que concurran a la audiencia.",
  "palabras_clave": ["sociedad conyugal", "pasivos", "obligaciones", "acreedores", "audiencia"],
  "referencia_legal": "Código General del Proceso (Ley 1564 de 2012), Artículo 501",
  "pasajes_usados": ["codigo_general_proceso:00520:e40d313ec22c"]
}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 3 → después 13 · reparación {'suppressed_fragment': 1, 'suppressed_sentence': 1} · construidas ['artículo 501 del Código General del Proceso', 'artículo 523 del Código General del Proceso', 'artículo 1820 del Código Civil', 'artículo 1774 del Código Civil', 'artículo 1804 del Código Civil', 'Ley 28 de 1932', 'Ley 57 de 1887', 'Constitución Política']
**Pasajes declarados por el modelo:** ['codigo_general_proceso:00520:e40d313ec22c']
**Evidencia:**
1. `codigo_general_proceso:00543:e619df7325af` — Código General del Proceso (Ley 1564 de 2012) art. 523
2. `codigo_general_proceso:00520:e40d313ec22c` — Código General del Proceso (Ley 1564 de 2012) art. 501
3. `codigo_civil:01818:faa724d12b7e` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1820
4. `codigo_civil:01772:f917f7612f99` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1774
5. `codigo_civil:01802:77320bb0024b` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1804
6. `codigo_civil:00867:8c171df1ee08` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 869
7. `codigo_civil:01236:e294f9a6ae57` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1238
8. `codigo_general_proceso:00022:6044d07399d7` — Código General del Proceso (Ley 1564 de 2012) art. 23
*Tokens 4708→225 · generación 9211.21989999665 ms · retrieval 3.5719000006793067 ms · grafo off*

## 513 · open_ended

**Pregunta:** ¿Cómo debería actuar una empresa si esta decide ingresar de manera legal su producto a un país para generar una venta y el consumidor final decide revender dicho producto? ¿ Es posible que la empresa prohíba la venta por segunda vez? 

**Medición:** cita=sin_ref_parseable · legal_basis=https://www.wipo.int/edocs/mdocs/mdocs/en/wipo_ip_bog_12/wipo_ip_bog_12_ref_u14b_aleman.pdf 

**Respuesta final:**
```json
{
  "marco_normativo": "Estatuto del Consumidor (Ley 1480 de 2011) y otros marcos normativos aplicables.",
  "analisis": "El Estatuto del Consumidor (Ley 1480 de 2011) establece que el consumidor tiene derechos sobre los productos que adquiere, incluyendo la posibilidad de resolver el contrato si el producto no se entrega en el plazo acordado o no corresponde a lo solicitado. Sin embargo, no se menciona explícitamente la prohibición de revender un producto adquirido. La prohibición de revender un producto depende de los términos del contrato entre la empresa y el consumidor, así como de las condiciones de venta establecidas por la empresa. Si la empresa incluye en su política o en el contrato una prohibición de revender el producto, esta podría ser válida siempre que no viole derechos fundamentales del consumidor. En caso de que la empresa prohíba la venta por segunda vez, debe hacerlo de manera clara y transparente, y sin afectar los derechos del consumidor, como el derecho a la libertad de elección y a la propiedad.",
  "jurisprudencia": "No se aportó jurisprudencia.",
  "conclusion": "La empresa puede establecer condiciones de venta que prohíban la revendición del producto, siempre que estas condiciones no violean los derechos del consumidor. La prohibición debe ser clara y transparente, y no debe afectar los derechos fundamentales del consumidor."
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "marco_normativo": "Estatuto del Consumidor (Ley 1480 de 2011) y otros marcos normativos aplicables.",
  "analisis": "El Estatuto del Consumidor (Ley 1480 de 2011) establece que el consumidor tiene derechos sobre los productos que adquiere, incluyendo la posibilidad de resolver el contrato si el producto no se entrega en el plazo acordado o no corresponde a lo solicitado. Sin embargo, no se menciona explícitamente la prohibición de revender un producto adquirido. La prohibición de revender un producto depende de los términos del contrato entre la empresa y el consumidor, así como de las condiciones de venta establecidas por la empresa. Si la empresa incluye en su política o en el contrato una prohibición de revender el producto, esta podría ser válida siempre que no viole derechos fundamentales del consumidor. En caso de que la empresa prohíba la venta por segunda vez, debe hacerlo de manera clara y transparente, y sin afectar los derechos del consumidor, como el derecho a la libertad de elección y a la propiedad.",
  "jurisprudencia": "No se aportó jurisprudencia.",
  "conclusion": "La empresa puede establecer condiciones de venta que prohíban la revendición del producto, siempre que estas condiciones no violean los derechos del consumidor. La prohibición debe ser clara y transparente, y no debe afectar los derechos fundamentales del consumidor.",
  "pasajes_usados": [
    "estatuto_consumidor:00052:f6244361ed61",
    "estatuto_consumidor:00004:6a0a811ea60f"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 4 → después 4 · reparación {} · construidas ['artículo 50 del Estatuto del Consumidor', 'artículo 5 del Estatuto del Consumidor']
**Pasajes declarados por el modelo:** ['estatuto_consumidor:00052:f6244361ed61', 'estatuto_consumidor:00004:6a0a811ea60f']
**Evidencia:**
1. `estatuto_consumidor:00052:f6244361ed61` — Estatuto del Consumidor (Ley 1480 de 2011) art. 50
2. `estatuto_consumidor:00017:24bfce463ddf` — Estatuto del Consumidor (Ley 1480 de 2011) art. 17
3. `estatuto_consumidor:00004:6a0a811ea60f` — Estatuto del Consumidor (Ley 1480 de 2011) art. 5
4. `estatuto_consumidor:00053:8152c33f16bd` — Estatuto del Consumidor (Ley 1480 de 2011) art. 51
5. `estatuto_tributario:00728:ecbc37ca3e4d` — Estatuto Tributario (Decreto 624 de 1989) art. 444
6. `ley_1819_de_2016:00240:0137b371b9b2` — Ley 1819 de 2016 art. 181
7. `decision_andina_486:00115:207e44d18083` — Decisión Andina 486 de 2000 art. 116
8. `decision_andina_486:00019:151ae0f5ead2` — Decisión Andina 486 de 2000 art. 20
*Tokens 5517→422 · generación 17194.456199998967 ms · retrieval 19.42630000121426 ms · grafo off*

## 528 · multiple_choice · ✔ correcta

**Pregunta:** Si un proceso declarativo tiene pretensiones por un monto de 30.000.000 COP ¿a qué tipo de cuantía corresponde? 

- A: Alta cuantía 
- B: Menor cuantía 
- C: Mínima cuantía 
- D: Mayor cuantía 

**Medición:** cita=cita_ok · legal_basis=Código General del Proceso. Art. 25.

**Respuesta final:**
```json
{
  "respuesta_correcta": "C",
  "justificacion": "Según el artículo 25 del Código General del Proceso (Ley 1564 de 2012), los procesos son de mínima cuantía cuando versan sobre pretensiones patrimoniales que no excedan el equivalente a cuarenta salarios mínimos legales mensuales vigentes (40 smlmv). Sin embargo, en el caso de un monto de 30.000.000 COP, se debe considerar el valor del salario mínimo legal mensual vigente al momento de la presentación de la demanda. Si el salario mínimo legal mensual vigente es de 1.000.000 COP, entonces 30.000.000 COP equivale a 30 smlmv, lo cual se encuentra dentro del rango de mínima cuantía. Por lo tanto, el proceso corresponde a mínima cuantía. Fundamento normativo: artículo 13 de la Ley 2452 de 2025; artículo 2 de la Ley 1150 de 2007; Sentencia C-149 de 1993; Sentencia C-507 de 2014; Ley 100 de 1993; Ley 1122 de 2007.",
  "descarte_opciones": {
    "A": "Alta cuantía: El monto de 30.000.000 COP no alcanza el umbral de alta cuantía, que es superior a 150 smlmv.",
    "B": "Menor cuantía: El monto de 30.000.000 COP no alcanza el umbral de menor cuantía, que es superior a 40 smlmv pero inferior a 150 smlmv.",
    "D": "Mayor cuantía: El monto de 30.000.000 COP no alcanza el umbral de mayor cuantía, que es superior a 150 smlmv."
  }
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "justificacion": "Según el artículo 25 del Código General del Proceso (Ley 1564 de 2012), los procesos son de mínima cuantía cuando versan sobre pretensiones patrimoniales que no excedan el equivalente a cuarenta salarios mínimos legales mensuales vigentes (40 smlmv). Sin embargo, en el caso de un monto de 30.000.000 COP, se debe considerar el valor del salario mínimo legal mensual vigente al momento de la presentación de la demanda. Si el salario mínimo legal mensual vigente es de 1.000.000 COP, entonces 30.000.000 COP equivale a 30 smlmv, lo cual se encuentra dentro del rango de mínima cuantía. Por lo tanto, el proceso corresponde a mínima cuantía.",
  "respuesta_correcta": "C",
  "descarte_opciones": {
    "A": "Alta cuantía: El monto de 30.000.000 COP no alcanza el umbral de alta cuantía, que es superior a 150 smlmv.",
    "B": "Menor cuantía: El monto de 30.000.000 COP no alcanza el umbral de menor cuantía, que es superior a 40 smlmv pero inferior a 150 smlmv.",
    "D": "Mayor cuantía: El monto de 30.000.000 COP no alcanza el umbral de mayor cuantía, que es superior a 150 smlmv."
  },
  "pasajes_usados": [
    "codigo_general_proceso:00026:fb5f7951641e"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 3 → después 11 · reparación {} · construidas ['artículo 25 del Código General del Proceso', 'artículo 13 de la Ley 2452 de 2025', 'artículo 338 del Código General del Proceso', 'artículo 2 de la Ley 1150 de 2007', 'Sentencia C-149 de 1993', 'Sentencia C-507 de 2014', 'Ley 100 de 1993', 'Ley 1122 de 2007']
**Pasajes declarados por el modelo:** ['codigo_general_proceso:00026:fb5f7951641e']
**Evidencia:**
1. `ley_2452_de_2025:00012:019e8d54a4c5` — Ley 2452 de 2025 art. 13
2. `codigo_general_proceso:00026:fb5f7951641e` — Código General del Proceso (Ley 1564 de 2012) art. 25
3. `codigo_general_proceso:00346:073b4e15ff1e` — Código General del Proceso (Ley 1564 de 2012) art. 338
4. `ley_1150_de_2007:00001:aa81ca5905a2` — Ley 1150 de 2007 art. 2
5. `sentencia_c_149_de_1993:00011:ec831350d28e` — Sentencia C-149 de 1993 art. None
6. `sentencia_c_149_de_1993:00002:86e420305252` — Sentencia C-149 de 1993 art. None
7. `sentencia_c_55_de_2022:00084:da9791621e96` — Sentencia C-55 de 2022 art. None
8. `sentencia_c_117_de_2018:00048:c99ffeef81ee` — Sentencia C-117 de 2018 art. None
*Tokens 7195→436 · generación 18675.454700001865 ms · retrieval 44.87310000695288 ms · grafo off*

## 563 · semi_open

**Pregunta:** ¿Cuál es la jerarquía normativa de los autos de seguimiento proferidos por la Sala Especial de Seguimiento a la Sentencia T-760 de 2008 de la Corte Contitucional?

**Medición:** cita=ref_fuera_de_evidencia · legal_basis=Sentencia SU-277/25

**Respuesta final:**
```json
{
  "respuesta": "Estos autos son considerados como parte del sistema jurídico nacional y tienen valor normativo dentro del marco constitucional.",
  "palabras_clave": [
    "Corte Constitucional",
    "Sentencia T-760 de 2008",
    "Autos de seguimiento",
    "Jerarquía normativa"
  ],
  "referencia_legal": "Sentencia T-760 de 2008; Sentencia T-1096 de 2008; Sentencia SU-429 de 2024; Constitución Política; Decreto 2591 de 1991; Código General del Proceso"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La jerarquía normativa de los autos de seguimiento proferidos por la Sala Especial de Seguimiento a la Sentencia T-760 de 2008 de la Corte Constitucional se basa en la Constitución Política de Colombia y en los artículos 86 y 241, numeral 9°, que otorgan competencia a la Corte para revisar casos de tutela. Estos autos son considerados como parte del sistema jurídico nacional y tienen valor normativo dentro del marco constitucional.","palabras_clave":["Corte Constitucional","Sentencia T-760 de 2008","Autos de seguimiento","Jerarquía normativa"],"referencia_legal":"Sentencia T-760 de 2008, II. Consideraciones y fundamentos, 1. Competencia.","pasajes_usados":["sentencia_t_760_de_2008:00007:924ba2e0c63d"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 7 → después 7 · reparación {'suppressed_sentence': 1} · construidas ['Sentencia T-760 de 2008', 'Sentencia T-1096 de 2008', 'Sentencia SU-429 de 2024', 'Constitución Política', 'Decreto 2591 de 1991', 'Código General del Proceso']
**Pasajes declarados por el modelo:** ['sentencia_t_760_de_2008:00007:924ba2e0c63d']
**Evidencia:**
1. `sentencia_t_760_de_2008:00309:783cdfa1ef24` — Sentencia T-760 de 2008 art. None
2. `sentencia_t_760_de_2008:00307:9b4ae0e26c22` — Sentencia T-760 de 2008 art. None
3. `sentencia_t_1096_de_2008:00001:49f82cd0465e` — Sentencia T-1096 de 2008 art. None
4. `sentencia_t_760_de_2008:00007:924ba2e0c63d` — Sentencia T-760 de 2008 art. None
5. `sentencia_t_760_de_2008:00308:b9d74d95aff3` — Sentencia T-760 de 2008 art. None
6. `sentencia_su_429_de_2024:00015:42852007effd` — Sentencia SU-429 de 2024 art. None
7. `sentencia_t_760_de_2008:00460:82471dcc712e` — Sentencia T-760 de 2008 art. None
8. `sentencia_su_429_de_2024:00039:0a73ebc9109d` — Sentencia SU-429 de 2024 art. None
*Tokens 7673→237 · generación 10747.049500001594 ms · retrieval 24.126599993905984 ms · grafo on*

## 589 · semi_open

**Pregunta:** ¿Cómo se define el litisconsorcio facultativo?

**Medición:** cita=cita_ok · legal_basis=Artículo 60 del Código General del Proceso. 

**Respuesta final:**
```json
{
  "respuesta": "El litisconsorcio facultativo se define como aquel en el cual la participación de una parte no es indispensable para el desarrollo del proceso, y por lo tanto, los efectos de la notificación se surtirán para cada uno separadamente, salvo norma sustancial o procesal en contrario.",
  "palabras_clave": [
    "litisconsorcio facultativo",
    "notificación",
    "efectos",
    "Código General del Proceso"
  ],
  "referencia_legal": "artículo 94 del Código General del Proceso; artículo 318 de la Ley 2452 de 2025; artículo 372 del Código General del Proceso; artículo 224 del Código de Procedimiento Administrativo y de lo Contencioso Administrativo; artículo 93 de la Ley 2220 de 2022; Constitución Política; Ley 1551 de 2012"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El litisconsorcio facultativo se define como aquel en el cual la participación de una parte no es indispensable para el desarrollo del proceso, y por lo tanto, los efectos de la notificación se surtirán para cada uno separadamente, salvo norma sustancial o procesal en contrario. Este concepto se menciona en el Código General del Proceso (Ley 1564 de 2012) en el artículo 94.","palabras_clave":["litisconsorcio facultativo","notificación","efectos","Código General del Proceso"],"referencia_legal":"Código General del Proceso (Ley 1564 de 2012), artículo 94","pasajes_usados":["codigo_general_proceso:00097:2f910a754e80"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 7 → después 13 · reparación {'suppressed_fragment': 1, 'suppressed_sentence': 2} · construidas ['artículo 94 del Código General del Proceso', 'artículo 318 de la Ley 2452 de 2025', 'artículo 372 del Código General del Proceso', 'artículo 224 del Código de Procedimiento Administrativo y de lo Contencioso Administrativo', 'artículo 93 de la Ley 2220 de 2022', 'Constitución Política', 'Ley 1551 de 2012']
**Pasajes declarados por el modelo:** ['codigo_general_proceso:00097:2f910a754e80']
**Evidencia:**
1. `codigo_general_proceso:00097:2f910a754e80` — Código General del Proceso (Ley 1564 de 2012) art. 94
2. `ley_2452_de_2025:00325:9cc925220bcd` — Ley 2452 de 2025 art. 318
3. `codigo_general_proceso:00381:3549022bad26` — Código General del Proceso (Ley 1564 de 2012) art. 372
4. `cpaca:00247:ed501c1f0dfd` — Código de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) art. 224
5. `ley_2220_de_2022:00096:08c844c517df` — Ley 2220 de 2022 art. 93
6. `ley_2452_de_2025:00139:1520185b2fa5` — Ley 2452 de 2025 art. 137
7. `codigo_general_proceso:00196:5838ca848714` — Código General del Proceso (Ley 1564 de 2012) art. 192
8. `ley_1581_de_2012:00011:45b0acfd60be` — Ley 1581 de 2012 art. 12
*Tokens 4562→195 · generación 7557.618999999249 ms · retrieval 10.783400008222088 ms · grafo off*

## 600 · multiple_choice · ✔ correcta

**Pregunta:** ¿Cuándo se consuma el tipo penal de hurto calificado según el artículo 241 del Código Penal?

- A: Cuando se toma la cosa por un momento sin el consentimiento de la persona que es propietaria. 
- B: Cuando se vende la cosa sin el consentimiento del propietario. 
- C: Cuando se aprendhe el objeto, se extrae de la esfera personal de dominio y se dispone de la cosa al menos por un momento 
- D:  Cuando el agente oculta o sustrae la cosa del lugar donde se encontraba, sin que sea necesario disponer de ella.

**Medición:** cita=cita_ok · legal_basis=Artículo 241 del Código Penal. 

**Respuesta final:**
```json
{
  "respuesta_correcta": "C",
  "justificacion": "Según el Código Penal, el hurto calificado se define como la acción de tomar posesión de una cosa ajena, sin el consentimiento del propietario, con la intención de apropiársela. La opción C menciona que el hurto calificado ocurre cuando se aprehende el objeto, se extrae de la esfera personal de dominio y se dispone de la cosa al menos por un momento, lo cual coincide con la definición del hurto calificado según el Código Penal. Las otras opciones no se alinean con la definición del hurto calificado según el Código Penal. Fundamento normativo: artículo 314 del Código de Procedimiento Penal; artículo 534 del Código de Procedimiento Penal; Sentencia C-80 de 2025; Sentencia C-15 de 2018; Ley 813 de 2003; Ley 1142 de 2007; Ley 1944 de 2018.",
  "descarte_opciones": {
    "A": "La opción A describe una situación que no se alinea con la definición del hurto calificado según el Código Penal.",
    "B": "La opción B no se alinea con la definición del hurto calificado según el Código Penal.",
    "D": "La opción D no se alinea con la definición del hurto calificado según el Código Penal."
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"Según el artículo 241 del Código Penal, el hurto calificado se define como la acción de tomar posesión de una cosa ajena, sin el consentimiento del propietario, con la intención de apropiársela. La opción C menciona que el hurto calificado ocurre cuando se aprehende el objeto, se extrae de la esfera personal de dominio y se dispone de la cosa al menos por un momento, lo cual coincide con la definición del hurto calificado según el artículo 241 del Código Penal. Las otras opciones no se alinean con la definición del hurto calificado según el artículo 241 del Código Penal.","respuesta_correcta":"C","descarte_opciones":{"A":"La opción A describe una situación que no se alinea con la definición del hurto calificado según el artículo 241 del Código Penal.","B":"La opción B no se alinea con la definición del hurto calificado según el artículo 241 del Código Penal.","D":"La opción D no se alinea con la definición del hurto calificado según el artículo 241 del Código Penal."},"pasajes_usados":["codigo_penal:00300:4bd46d5c5cc2"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 12 → después 15 · reparación {'renamed_to_evidence_name': 120, 'suppressed_fragment': 6} · construidas ['artículo 240 del Código Penal', 'artículo 314 del Código de Procedimiento Penal', 'artículo 534 del Código de Procedimiento Penal', 'Sentencia C-80 de 2025', 'Sentencia C-15 de 2018', 'Ley 813 de 2003', 'Ley 1142 de 2007', 'Ley 1944 de 2018']
**Pasajes declarados por el modelo:** ['codigo_penal:00300:4bd46d5c5cc2']
**Evidencia:**
1. `codigo_procedimiento_penal:00338:a93b56b56848` — Código de Procedimiento Penal (Ley 906 de 2004) art. 314
2. `codigo_penal:00300:4bd46d5c5cc2` — Código Penal (Ley 599 de 2000) art. 240
3. `codigo_procedimiento_penal:00564:000bffb3e316` — Código de Procedimiento Penal (Ley 906 de 2004) art. 534
4. `sentencia_c_80_de_2025:00049:667857727b57` — Sentencia C-80 de 2025 art. None
5. `sentencia_c_15_de_2018:00034:28b3e688422d` — Sentencia C-15 de 2018 art. None
6. `sentencia_c_15_de_2018:00028:bdd00881d1c7` — Sentencia C-15 de 2018 art. None
7. `sentencia_c_239_de_1997:00013:a5942dc4f56a` — Sentencia C-239 de 1997 art. None
8. `codigo_civil:01423:9ed957a4a06b` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1425
*Tokens 6997→290 · generación 12621.136599991587 ms · retrieval 247.90189998748247 ms · grafo auto*

## 617 · multiple_choice · ABSTENCIÓN (pipeline_error)

**Pregunta:** ¿Qué clases de fueros sindicales existen dentro del ordenamiento jurídico colombiano?

- A: Fuero convencional, circunstanciales, comisión de reclamos, directivos, fundadores y adherentes.
- B: Fuero de fundadores, adherentes, directivos, comisión de reclamos, circunstancial y convencional. 
- C: Fuero de Comisión de Reclamos, adherentes, fundadores y asalariados.
- D: Fuero de fundadores, cooperativos, convencional, comisión de juntas, directivos y adherentes. 

**Error:** INVALID_MODEL_OUTPUT: Output must be exactly one JSON object, without prose around it

**Medición:** cita=ref_fuera_de_evidencia · legal_basis=Código Sustantivo del Trabajo. 

**Respuesta final:**
```json
{
  "respuesta_correcta": "A",
  "justificacion": "Abstención automática (pipeline_error). A es un marcador formal exigido por el schema; no representa una elección de respuesta.",
  "descarte_opciones": {}
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"La norma que establece las clases de fueros sindicales es el artículo 406 del Código Sustantivo del Trabajo, modificado por el artículo 57 de la Ley 50 de 1990. Según este artículo, los trabajadores amparados por el fuero sindical incluyen: los fundadores de un sindicato, los trabajadores que ingresen al sindicato antes de su inscripción, los miembros de la junta directiva y subdirectivas, los miembros de los comités seccionales, y dos de los miembros de la comisión estatutaria de reclamos. Estos son los tipos de fueros mencionados en la norma. La opción B menciona los mismos elementos: fuero de fundadores, adherentes, directivos, comisión de reclamos, circunstancial y convencional. Sin embargo, el término 'circunstancial' y 'convencional' no están explícitamente mencionados en el artículo 406. Por lo tanto, la opción B no es correcta. La opción A menciona 'fuero convencional, circunstanciales, comisión de reclamos, directivos, fundadores y adherentes', lo cual incluye términos que no están explícitamente mencionados en el artículo 406. La opción C menciona 'fuero de Comisión de Reclamos, adherentes, fundadores y asalariados', lo cual tampoco está explícitamente mencionado en el artículo 406. La opción D menciona 'fuero de fundadores, cooperativos, convencional, comisión de juntas, directivos y adherentes', lo cual tampoco está explícitamente mencionado en el artículo 406. Por lo tanto, la opción correcta es la que menciona los tipos de fueros que están explícitamente mencionados en el artículo 406, que son: fundadores, adherentes, directivos, comisión de reclamos, y los términos 'circunstancial' y 'convencional' no están explícitamente mencionados en el artículo 406. Por lo tanto, la opción correcta es la que menciona los tipos de fueros que están explícitamente mencionados en el artículo 406, que son: fundadores, adherentes, directivos, comisión de reclamos, y los términos 'circunstancial' y 'convencional' no están explícitamente mencionados en el artículo 406. Por lo tanto, la opción correcta es la que menciona los tipos de fueros que están explícitamente mencionados en el artículo 406, que son: fundadores, adherentes, directivos, comisión de reclamos, y los términos 'circunstancial' y 'convencional' no están explícitamente mencionados en el artículo 406. Por lo tanto, la opción correcta es la que menciona los tipos de fueros que están explícitamente mencionados en el artículo 406, que son: fundadores, adherentes, directivos, comisión de reclamos, y los términos 'circunstancial' y 'convencional' no están explícitamente mencionados en el artículo 406. Por lo tanto, la opción correcta es la que menciona los tipos
```
**Parser:** None · correcciones None · avisos None
**Citas:** antes None → después None · reparación None · construidas None
**Pasajes declarados por el modelo:** None
**Evidencia:**
*Tokens None→None · generación None ms · retrieval None ms · grafo None*

## 647 · multiple_choice · ✔ correcta

**Pregunta:** La Ayuda como efecto personal del matrimonio es:

- A: (a) y (b) 
- B:  El apoyo intelectual, moral yafectivo en forma recíproca 
- C: Ninguna de las anteriores. 
- D: Un deber de asistencia 

**Medición:** cita=cita_ok · legal_basis=Código civil.

**Respuesta final:**
```json
{
  "respuesta_correcta": "B",
  "justificacion": "La sentencia SU-214 de 2016 establece que la ayuda mutua, el afecto, la solidaridad y el apoyo recíproco son elementos esenciales de la convivencia entre parejas, independientemente de su orientación sexual. En el texto de la sentencia, se menciona que la unión marital de hecho, como la unión entre parejas homosexuales, comporta una entrega personal orientada a conformar una comunidad de vida y amor, lo cual incluye el apoyo mutuo. Por lo tanto, la ayuda como efecto personal del matrimonio se refiere al apoyo intelectual, moral y afectivo en forma recíproca. La opción B se alinea con esta interpretación. Fundamento normativo: Sentencia C-164 de 2022; Sentencia C-985 de 2010; Sentencia C-131 de 2018; Sentencia C-507 de 2004; Sentencia C-577 de 2011; Código Civil; Constitución Política.",
  "descarte_opciones": {
    "A": "La opción A menciona (a) y (b), pero no se especifica qué son (a) y (b), por lo que no se puede confirmar su contenido.",
    "C": "La opción C es incorrecta porque la evidencia muestra que la ayuda mutua es un efecto personal del matrimonio.",
    "D": "La opción D menciona un deber de asistencia, lo cual no se menciona explícitamente en la evidencia."
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"La sentencia SU-214 de 2016 establece que la ayuda mutua, el afecto, la solidaridad y el apoyo recíproco son elementos esenciales de la convivencia entre parejas, independientemente de su orientación sexual. En el texto de la sentencia, se menciona que la unión marital de hecho, como la unión entre parejas homosexuales, comporta una entrega personal orientada a conformar una comunidad de vida y amor, lo cual incluye el apoyo mutuo. Por lo tanto, la ayuda como efecto personal del matrimonio se refiere al apoyo intelectual, moral y afectivo en forma recíproca. La opción B se alinea con esta interpretación.","respuesta_correcta":"B","descarte_opciones":{"A":"La opción A menciona (a) y (b), pero no se especifica qué son (a) y (b), por lo que no se puede confirmar su contenido.","C":"La opción C es incorrecta porque la evidencia muestra que la ayuda mutua es un efecto personal del matrimonio.","D":"La opción D menciona un deber de asistencia, lo cual no se menciona explícitamente en la evidencia."},"pasajes_usados":["sentencia_su_214_de_2016:00098:8ab5aa1c6f94","sentencia_su_214_de_2016:00166:f0e80dd25c48"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 1 → después 8 · reparación {} · construidas ['Sentencia SU-214 de 2016', 'Sentencia C-164 de 2022', 'Sentencia C-985 de 2010', 'Sentencia C-131 de 2018', 'Sentencia C-507 de 2004', 'Sentencia C-577 de 2011', 'Código Civil', 'Constitución Política']
**Pasajes declarados por el modelo:** ['sentencia_su_214_de_2016:00098:8ab5aa1c6f94', 'sentencia_su_214_de_2016:00166:f0e80dd25c48']
**Evidencia:**
1. `sentencia_c_164_de_2022:00060:8e9b44809c88` — Sentencia C-164 de 2022 art. None
2. `sentencia_su_214_de_2016:00098:8ab5aa1c6f94` — Sentencia SU-214 de 2016 art. None
3. `sentencia_c_985_de_2010:00013:f29e6280a016` — Sentencia C-985 de 2010 art. None
4. `sentencia_su_214_de_2016:00216:6f2ec1c15b2c` — Sentencia SU-214 de 2016 art. None
5. `sentencia_c_131_de_2018:00017:28d6bf245b5b` — Sentencia C-131 de 2018 art. None
6. `sentencia_su_214_de_2016:00166:f0e80dd25c48` — Sentencia SU-214 de 2016 art. None
7. `sentencia_su_214_de_2016:00058:c1e814d0863e` — Sentencia SU-214 de 2016 art. None
8. `sentencia_c_507_de_2004:00070:4ba606b72e29` — Sentencia C-507 de 2004 art. None
*Tokens 7033→347 · generación 14926.195899999584 ms · retrieval 56.51460000080988 ms · grafo off*

## 661 · semi_open

**Pregunta:** ¿En qué consiste el principio de legalidad en materia tributaria? 

**Medición:** cita=cita_ok · legal_basis=Artículos 29 y 338 de la Constitución Política, sentencia C-89112 de la Corte Constitucional. 

**Respuesta final:**
```json
{
  "respuesta": "El principio de legalidad en materia tributaria establece que el Legislador tiene la facultad para crear, modificar y eliminar contribuciones fiscales, así como definir sus elementos estructurales esenciales. Este principio se fundamenta en el aforismo \"nullum tributum sine lege\", que exige un acto del legislador para la creación de gravámenes. Además, se deriva de la máxima \"no taxation without representation\", que establece que la creación de impuestos está condicionada a una representación democrática suficiente y plural. Este principio es una característica fundamental del Estado constitucional moderno.",
  "palabras_clave": [
    "principio de legalidad",
    "tributaria",
    "legislador",
    "nullum tributum sine lege"
  ],
  "referencia_legal": "Sentencia C-389 de 2023; Sentencia C-891 de 2012; Sentencia C-94 de 2021; Estatuto Tributario; Ley 2277 de 2022; Constitución Política"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El principio de legalidad en materia tributaria establece que el Legislador tiene la facultad para crear, modificar y eliminar contribuciones fiscales, así como definir sus elementos estructurales esenciales. Este principio se fundamenta en el aforismo \"nullum tributum sine lege\", que exige un acto del legislador para la creación de gravámenes. Además, se deriva de la máxima \"no taxation without representation\", que establece que la creación de impuestos está condicionada a una representación democrática suficiente y plural. Este principio es una característica fundamental del Estado constitucional moderno.","palabras_clave":["principio de legalidad","tributaria","legislador","nullum tributum sine lege"],"referencia_legal":"artículo 338 y 150.12 CP","pasajes_usados":["sentencia_c_389_de_2023:00020:c1cd1f99f3bd","sentencia_c_891_de_2012:00011:74adba4692b6"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 2 → después 6 · reparación {'emptied': 1, 'suppressed_fragment': 1, 'suppressed_sentence': 1} · construidas ['Sentencia C-389 de 2023', 'Sentencia C-891 de 2012', 'Sentencia C-94 de 2021', 'Estatuto Tributario', 'Ley 2277 de 2022', 'Constitución Política']
**Pasajes declarados por el modelo:** ['sentencia_c_389_de_2023:00020:c1cd1f99f3bd', 'sentencia_c_891_de_2012:00011:74adba4692b6']
**Evidencia:**
1. `sentencia_c_94_de_2021:00000:c4b0cabe571c` — Sentencia C-94 de 2021 art. None
2. `sentencia_c_891_de_2012:00000:993ba336d7dc` — Sentencia C-891 de 2012 art. None
3. `sentencia_c_389_de_2023:00000:a616826527b7` — Sentencia C-389 de 2023 art. None
4. `sentencia_c_891_de_2012:00014:09e5897da0c0` — Sentencia C-891 de 2012 art. None
5. `sentencia_c_389_de_2023:00021:333d6af4a487` — Sentencia C-389 de 2023 art. None
6. `sentencia_c_389_de_2023:00020:c1cd1f99f3bd` — Sentencia C-389 de 2023 art. None
7. `sentencia_c_891_de_2012:00011:74adba4692b6` — Sentencia C-891 de 2012 art. None
8. `sentencia_c_891_de_2012:00012:ce5633677c29` — Sentencia C-891 de 2012 art. None
*Tokens 7471→262 · generación 11673.62570000114 ms · retrieval 9.249900002032518 ms · grafo off*

## 671 · multiple_choice · ✘ esperada C

**Pregunta:** Las "reglas de desempate" solucionan el/los conflicto/s: 

- A: Conflicto de residencia-fuente. 
- B: Todas las anteriores. 
- C: Conflicto residencia-residencia. 
- D: Conflicto fuente-fuente. 

**Medición:** cita=sin_ref_parseable · legal_basis=Doctrina. 

**Respuesta final:**
```json
{
  "respuesta_correcta": "A",
  "justificacion": "Estos factores incluyen la preferencia por bienes o servicios nacionales, la preferencia por la mujer cabeza de familia, y la protección de la información sensible relacionada con ciertos grupos vulnerables. Estas reglas de desempate se aplican para resolver conflictos en la adjudicación de contratos, específicamente en el caso de empates. Por lo tanto, las reglas de desempate solucionan el conflicto de residencia-fuente, ya que se refiere a la preferencia por bienes o servicios nacionales, lo cual implica una consideración de la residencia y la fuente de los bienes o servicios. Las otras opciones no se mencionan directamente en el texto proporcionado. Fundamento normativo: artículo 2.2.1.2.4.2.17 del Decreto 1082 de 2015; Sentencia SU-500 de 2015; artículo 2.2.1.1.2.2.9 del Decreto 1082 de 2015; artículo 2.2.1.2.4.2.7 del Decreto 1082 de 2015; artículo 9 del Estatuto Tributario; Ley 1712 de 2014; Ley 1581 de 2012; Decreto 1860 de 2021.",
  "descarte_opciones": {
    "B": "No se mencionan todas las anteriores en el texto proporcionado.",
    "C": "No se menciona un conflicto de residencia-residencia en el texto proporcionado.",
    "D": "No se menciona un conflicto de fuente-fuente en el texto proporcionado."
  }
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "justificacion": "El Decreto 1082 de 2015 establece en el artículo 2.2.1.2.4.2.17 los factores de desempate que deben aplicarse en los procesos de contratación cuando se presenta un empate entre ofertas. Estos factores incluyen la preferencia por bienes o servicios nacionales, la preferencia por la mujer cabeza de familia, y la protección de la información sensible relacionada con ciertos grupos vulnerables. Estas reglas de desempate se aplican para resolver conflictos en la adjudicación de contratos, específicamente en el caso de empates. Por lo tanto, las reglas de desempate solucionan el conflicto de residencia-fuente, ya que se refiere a la preferencia por bienes o servicios nacionales, lo cual implica una consideración de la residencia y la fuente de los bienes o servicios. Las otras opciones no se mencionan directamente en el texto proporcionado.",
  "respuesta_correcta": "A",
  "descarte_opciones": {
    "B": "No se mencionan todas las anteriores en el texto proporcionado.",
    "C": "No se menciona un conflicto de residencia-residencia en el texto proporcionado.",
    "D": "No se menciona un conflicto de fuente-fuente en el texto proporcionado."
  },
  "pasajes_usados": [
    "decreto_1082_de_2015:00230:502754fc8001",
    "decreto_1082_de_2015:00223:67e8a38974cb"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 2 → después 12 · reparación {'suppressed_sentence': 1} · construidas ['artículo 2.2.1.2.4.2.17 del Decreto 1082 de 2015', 'Sentencia SU-500 de 2015', 'artículo 2.2.1.1.2.2.9 del Decreto 1082 de 2015', 'artículo 2.2.1.2.4.2.7 del Decreto 1082 de 2015', 'artículo 9 del Estatuto Tributario', 'Ley 1712 de 2014', 'Ley 1581 de 2012', 'Decreto 1860 de 2021']
**Pasajes declarados por el modelo:** ['decreto_1082_de_2015:00230:502754fc8001', 'decreto_1082_de_2015:00223:67e8a38974cb']
**Evidencia:**
1. `decreto_1082_de_2015:00230:502754fc8001` — Decreto 1082 de 2015 art. 2.2.1.2.4.2.17
2. `decreto_1082_de_2015:00223:67e8a38974cb` — Decreto 1082 de 2015 art. 2.2.1.2.4.2.17
3. `sentencia_su_500_de_2015:00090:b332f7641588` — Sentencia SU-500 de 2015 art. None
4. `decreto_1082_de_2015:00053:6d7a3c4ebcf5` — Decreto 1082 de 2015 art. 2.2.1.1.2.2.9
5. `sentencia_su_500_de_2015:00089:22af01a51fec` — Sentencia SU-500 de 2015 art. None
6. `decreto_1082_de_2015:00200:c6243c60eddf` — Decreto 1082 de 2015 art. 2.2.1.2.4.2.7
7. `estatuto_tributario:00009:6fcfd20552aa` — Estatuto Tributario (Decreto 624 de 1989) art. 9
8. `estatuto_tributario:00537:19dca5883f45` — Estatuto Tributario (Decreto 624 de 1989) art. 319-6
*Tokens 7343→404 · generación 17632.36770000367 ms · retrieval 17.27160000882577 ms · grafo off*

## 674 · semi_open

**Pregunta:** Identifique en el siguiente enunciado si existe o no una cláusula abusiva: “El Usuario manifiesta con la aceptación de los Términos y Condiciones que, para el perfeccionamiento de la relación contractual, solicitará a LUKIAO que en su nombre adquiera un seguro contra riesgos en caso de muerte y otros siniestros probables que puedan repercutir en el impago de la deuda [...]. La solicitud de la adquisición del seguro se realizará de forma automática con la aceptación de los Términos y Condiciones, de forma tal que, al efectuarse la aceptación de este clausulado, LUKIAO entenderá que se encuentra obligado a adquirir el respectivo seguro en favor del Usuario para el pago de la deuda que solicitó en caso de la ocurrencia de los respectivos siniestros. El Usuario manifiesta que la solicitud para la adquisición del seguro se efectúa con la finalidad de prever una garantía de su obligación en pro de los intereses de sus familiares y de su propio patrimonio”.


**Medición:** cita=cita_ok · legal_basis=Artículos 3, 23 y 24 del Estatuto del Consumidor

**Respuesta final:**
```json
{
  "respuesta": "La cláusula mencionada no se considera abusiva según el Estatuto del Consumidor, ya que no se observan características de desequilibrio significativo entre las partes ni de restricción injusta de derechos del consumidor. La cláusula establece una obligación contractual que se pacta entre las partes, sin imponer condiciones que limiten el derecho del consumidor a decidir sobre su protección financiera.",
  "palabras_clave": [
    "cláusula abusiva",
    "Estatuto del Consumidor",
    "contrato de adhesión"
  ],
  "referencia_legal": "artículo 5 del Estatuto del Consumidor; artículo 127 del Decreto 663 de 1993; artículo 149 del Decreto 663 de 1993; artículo 102 del Estatuto Tributario; Sentencia T-760 de 2008; Decreto 1026 de 1990; Ley 3 de 1991; Ley 9 de 1989"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La cláusula mencionada no se considera abusiva según el Estatuto del Consumidor, ya que no se observan características de desequilibrio significativo entre las partes ni de restricción injusta de derechos del consumidor. La cláusula establece una obligación contractual que se pacta entre las partes, sin imponer condiciones que limiten el derecho del consumidor a decidir sobre su protección financiera.","palabras_clave":["cláusula abusiva","Estatuto del Consumidor","contrato de adhesión"],"referencia_legal":"Estatuto del Consumidor (Ley 1480 de 2011)","pasajes_usados":["estatuto_consumidor:00004:6a0a811ea60f"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 4 → después 14 · reparación {} · construidas ['artículo 5 del Estatuto del Consumidor', 'artículo 127 del Decreto 663 de 1993', 'artículo 149 del Decreto 663 de 1993', 'artículo 102 del Estatuto Tributario', 'Sentencia T-760 de 2008', 'Decreto 1026 de 1990', 'Ley 3 de 1991', 'Ley 9 de 1989']
**Pasajes declarados por el modelo:** ['estatuto_consumidor:00004:6a0a811ea60f']
**Evidencia:**
1. `estatuto_consumidor:00004:6a0a811ea60f` — Estatuto del Consumidor (Ley 1480 de 2011) art. 5
2. `decreto_663_de_1993:00188:68e5e29c7af4` — Decreto 663 de 1993 art. 127
3. `decreto_663_de_1993:00212:16be4ac9b072` — Decreto 663 de 1993 art. 149
4. `estatuto_tributario:00164:f8f3e919ccad` — Estatuto Tributario (Decreto 624 de 1989) art. 102
5. `sentencia_t_760_de_2008:00386:3daa572568c8` — Sentencia T-760 de 2008 art. None
6. `ley_769_de_2002:00184:e990ce146469` — Ley 769 de 2002 art. 161
7. `decreto_663_de_1993:00232:a68d5351d1e0` — Decreto 663 de 1993 art. 165
8. `decreto_780_de_2016:00648:fdc001984f3a` — Decreto 780 de 2016 art. 2.5.2.5.4
*Tokens 6656→186 · generación 8264.768399996683 ms · retrieval 27.24820000003092 ms · grafo off*

## 679 · open_ended

**Pregunta:** Sara López, de 38 años, fue diagnosticada con esclerosis múltiple en marzo de 2024 por la neuróloga de la EPS SALUD Y VIDA S.A.S. Su tratamiento requiere el medicamento Interferón, cuya patente de invención pertenece a la empresa estadounidense BIG PHARMA INC. Este medicamento presenta recurrentes problemas de desabastecimiento y precios elevados en Colombia, lo que ha impedido a Sara y a otros pacientes con el mismo diagnóstico acceder de forma continua y oportuna al tratamiento prescrito.

Ante esta situación, el Gobierno colombiano estudia medidas regulatorias para garantizar el acceso al interferón. En ese marco, la Superintendencia de Industria y Comercio (SIC) recibe una solicitud del Ministerio de Salud para conceptuar sobre la posibilidad de acceder a la base de datos del sistema de salud que contiene los registros clínicos de pacientes colombianos diagnosticados con esclerosis múltiple. El propósito declarado es cuantificar la demanda real del medicamento, justificar técnicamente una eventual declaratoria de interés público y viabilizar la producción nacional del interferón.

Problema jurídico: La SIC, le solicita conceptuar sobre si puede acceder a los datos en salud de la población colombiana con diagnóstico de esclerosis múltiple a fin de producir el medicamento en Colombia y garantizar los derechos de los pacientes. Tome en consideración derechos constitucionales y derechos humanos.




**Medición:** cita=ref_fuera_de_evidencia · legal_basis= Ley 1581 de 2012

**Respuesta final:**
```json
{
  "marco_normativo": "La Sentencia T-67 de 2025 establece que los derechos de propiedad industrial no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'. Además, se menciona que los derechos de propiedad intelectual no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'. La Sentencia T-760 de 2008 establece que el derecho a la salud es un derecho fundamental y que el Estado debe garantizar su acceso efectivo, incluso cuando se requiere de medicamentos no incluidos en el Plan Obligatorio de Salud (POS).",
  "analisis": "La Sentencia T-760 de 2008 establece que el Estado debe garantizar el acceso efectivo a los servicios de salud, incluso cuando se requiere de medicamentos no incluidos en el POS. Por otro lado, la Sentencia T-67 de 2025 indica que los derechos de propiedad industrial no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'. En este contexto, la SIC debe analizar si el acceso a los datos clínicos es necesario para garantizar el acceso al medicamento Interferón, considerando el derecho a la salud y la necesidad de garantizar el acceso a los servicios de salud. La SIC debe asegurar que el acceso a los datos no viole los derechos de propiedad intelectual, pero debe priorizar el derecho a la salud de los pacientes. La SIC debe evaluar si el acceso a los datos clínicos es compatible con los derechos de propiedad intelectual y si es necesario para garantizar el acceso al medicamento Interferón. La SIC debe considerar que el acceso a los datos clínicos es necesario para garantizar el acceso al medicamento Interferón, pero debe asegurar que no viole los derechos de propiedad intelectual. La SIC debe evaluar si el acceso a los datos clínicos es compatible con los derechos de propiedad intelectual y si es necesario para garantizar el acceso al medicamento Interferón.",
  "jurisprudencia": "La Sentencia T-760 de 2008 establece que el derecho a la salud es un derecho fundamental y que el Estado debe garantizar su acceso efectivo, incluso cuando se requiere de medicamentos no incluidos en el Plan Obligatorio de Salud (POS). La Sentencia T-67 de 2025 establece que los derechos de propiedad industrial no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'.",
  "conclusion": "La SIC debe considerar el derecho a la salud como un derecho fundamental y garantizar el acceso efectivo a los servicios de salud, incluso cuando se requiere de medicamentos no incluidos en el Plan Obligatorio de Salud (POS). La SIC debe evaluar si el acceso a los datos clínicos es compatible con los derechos de propiedad intelectual y si es necesario para garantizar el acceso al medicamento Interferón. La SIC debe asegurar que el acceso a los datos clínicos no viole los derechos de propiedad intelectual, pero debe priorizar el derecho a la salud de los pacientes."
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "marco_normativo": "La Sentencia T-67 de 2025 establece que los derechos de propiedad industrial no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'. Además, se menciona que los derechos de propiedad intelectual no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'. La Sentencia T-760 de 2008 establece que el derecho a la salud es un derecho fundamental y que el Estado debe garantizar su acceso efectivo, incluso cuando se requiere de medicamentos no incluidos en el Plan Obligatorio de Salud (POS).",
  "analisis": "La SIC, al solicitar acceder a los datos de salud de pacientes con esclerosis múltiple, debe considerar el derecho a la salud como un derecho fundamental garantizado por la Constitución. La Sentencia T-760 de 2008 establece que el Estado debe garantizar el acceso efectivo a los servicios de salud, incluso cuando se requiere de medicamentos no incluidos en el POS. Por otro lado, la Sentencia T-67 de 2025 indica que los derechos de propiedad industrial no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'. En este contexto, la SIC debe analizar si el acceso a los datos clínicos es necesario para garantizar el acceso al medicamento Interferón, considerando el derecho a la salud y la necesidad de garantizar el acceso a los servicios de salud. La SIC debe asegurar que el acceso a los datos no viole los derechos de propiedad intelectual, pero debe priorizar el derecho a la salud de los pacientes. La SIC debe evaluar si el acceso a los datos clínicos es compatible con los derechos de propiedad intelectual y si es necesario para garantizar el acceso al medicamento Interferón. La SIC debe considerar que el acceso a los datos clínicos es necesario para garantizar el acceso al medicamento Interferón, pero debe asegurar que no viole los derechos de propiedad intelectual. La SIC debe evaluar si el acceso a los datos clínicos es compatible con los derechos de propiedad intelectual y si es necesario para garantizar el acceso al medicamento Interferón.",
  "jurisprudencia": "La Sentencia T-760 de 2008 establece que el derecho a la salud es un derecho fundamental y que el Estado debe garantizar su acceso efectivo, incluso cuando se requiere de medicamentos no incluidos en el Plan Obligatorio de Salud (POS). La Sentencia T-67 de 2025 establece que los derechos de propiedad industrial no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'.",
  "conclusion": "La SIC debe considerar el derecho a la salud como un derecho fundamental y garantizar el acceso efectivo a los servicios de salud, incluso cuando se requiere de medicamentos no incluidos en el Plan Obligatorio de Salud (POS). La SIC debe evaluar si el acceso a los datos clínicos es compatible con los derechos de propiedad intelectual y si es necesario para garantizar el acceso al medicamento Interferón. La SIC debe asegurar que el acceso a los datos clínicos no viole los derechos de propiedad intelectual, pero debe priorizar el derecho a la salud de los pacientes.",
  "pasajes_usados": [
    "sentencia_t_67_de_2025:00068:9162819aaf31",
    "sentencia_t_760_de_2008:00016:8c42cc32daaa",
    "sentencia_t_760_de_2008:00149:eeae2d1fcd2d"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 7 → después 6 · reparación {'suppressed_sentence': 1} · construidas ['Sentencia T-67 de 2025', 'Sentencia T-760 de 2008']
**Pasajes declarados por el modelo:** ['sentencia_t_67_de_2025:00068:9162819aaf31', 'sentencia_t_760_de_2008:00016:8c42cc32daaa', 'sentencia_t_760_de_2008:00149:eeae2d1fcd2d']
**Evidencia:**
1. `sentencia_c_145_de_2020:00071:61e12298a848` — Sentencia C-145 de 2020 art. None
2. `sentencia_t_67_de_2025:00068:9162819aaf31` — Sentencia T-67 de 2025 art. None
3. `sentencia_c_145_de_2020:00005:abcdf7cf7a0b` — Sentencia C-145 de 2020 art. None
4. `sentencia_t_760_de_2008:00016:8c42cc32daaa` — Sentencia T-760 de 2008 art. None
5. `sentencia_t_760_de_2008:00149:eeae2d1fcd2d` — Sentencia T-760 de 2008 art. None
6. `sentencia_c_145_de_2020:00058:7dc4c676bbb0` — Sentencia C-145 de 2020 art. None
7. `decreto_780_de_2016:02219:ad3517b8ca8a` — Decreto 780 de 2016 art. 2.11.2.4.1
8. `sentencia_t_760_de_2008:00047:b41fd1aa6412` — Sentencia T-760 de 2008 art. None
*Tokens 6650→939 · generación 39269.83970000583 ms · retrieval 39.44459999911487 ms · grafo off*

## 697 · semi_open

**Pregunta:** Explique en qué consiste la teoría del Grupo de Compañías e indique cuál es el caso que la doctrina cita como exponente de dicha teoría.

**Medición:** cita=sin_ref_parseable · legal_basis=caso francés de Dow Chemical

**Respuesta final:**
```json
{
  "respuesta": "La teoría del Grupo de Compañías se refiere a la idea de que una empresa puede influir psíquicamente en la conducta de otra empresa, lo cual puede generar responsabilidad penal. Esta teoría se menciona en la Sentencia SP-1167 de 2022, donde se explica que el inductor debe tener una influencia psíquica sobre el autor material para que pueda ser considerado responsable penalmente. No se menciona específicamente un caso que sirva como exponente de esta teoría en el pasaje proporcionado.",
  "palabras_clave": [
    "teoría del Grupo de Compañías",
    "influencia psíquica",
    "responsabilidad penal"
  ],
  "referencia_legal": "Sentencia SP-1167 de 2022; artículo 2.2.4.5.2 del Decreto 1082 de 2015; Sentencia C-259 de 2015; Sentencia C-345 de 2017; Sentencia C-96 de 2024; Decreto 1073 de 2012; Código de Procedimiento Administrativo y de lo Contencioso Administrativo; Sentencia C-426 de 2002"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La teoría del Grupo de Compañías se refiere a la idea de que una empresa puede influir psíquicamente en la conducta de otra empresa, lo cual puede generar responsabilidad penal. Esta teoría se menciona en la Sentencia SP-1167 de 2022, donde se explica que el inductor debe tener una influencia psíquica sobre el autor material para que pueda ser considerado responsable penalmente. No se menciona específicamente un caso que sirva como exponente de esta teoría en el pasaje proporcionado.","palabras_clave":["teoría del Grupo de Compañías","influencia psíquica","responsabilidad penal"],"referencia_legal":"Sentencia SP-1167 de 2022","pasajes_usados":["sentencia_sp_1167_de_2022:00010:0589dc5daeb8"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 2 → después 10 · reparación {} · construidas ['Sentencia SP-1167 de 2022', 'artículo 2.2.4.5.2 del Decreto 1082 de 2015', 'Sentencia C-259 de 2015', 'Sentencia C-345 de 2017', 'Sentencia C-96 de 2024', 'Decreto 1073 de 2012', 'Código de Procedimiento Administrativo y de lo Contencioso Administrativo', 'Sentencia C-426 de 2002']
**Pasajes declarados por el modelo:** ['sentencia_sp_1167_de_2022:00010:0589dc5daeb8']
**Evidencia:**
1. `sentencia_sp_1167_de_2022:00010:0589dc5daeb8` — Sentencia SP-1167 de 2022 art. None
2. `decreto_1082_de_2015:00606:2d4affa55017` — Decreto 1082 de 2015 art. 2.2.4.5.2
3. `sentencia_c_259_de_2015:00012:b72e3cb10756` — Sentencia C-259 de 2015 art. None
4. `sentencia_c_259_de_2015:00035:905fd7d5ecaa` — Sentencia C-259 de 2015 art. None
5. `sentencia_c_345_de_2017:00051:82b167484315` — Sentencia C-345 de 2017 art. None
6. `sentencia_c_259_de_2015:00002:6efd7841d730` — Sentencia C-259 de 2015 art. None
7. `sentencia_c_96_de_2024:00063:131111f0e9b3` — Sentencia C-96 de 2024 art. None
8. `sentencia_su_149_de_2021:00050:01b6cd0168a2` — Sentencia SU-149 de 2021 art. None
*Tokens 6705→216 · generación 9606.719499992323 ms · retrieval 17.409999985829927 ms · grafo off*

## 748 · multiple_choice · ✘ esperada A

**Pregunta:** Habiendo hecho la lectura previa de la Resolución No. 368 de 2014 expedida por el Ministerio de Ambiente y Desarrollo Sostenible, lea con atención cada pregunta y responda la siguiente pregunta. 

Pregunta jurídica: No tener en cuenta en el acto administrativo que permite la operación de un relleno sanitario, lo presentado por los pueblos indígenas en la consulta previa puede configurar el vicio: 

- A: Falsa motivación
- B: Usurpación de funciones
- C: Desviación de poder
- D: No estar basado en las normas necesarias para la emisión del acto

**Medición:** cita=ref_fuera_de_evidencia · legal_basis=CPACA 

**Respuesta final:**
```json
{
  "respuesta_correcta": "C",
  "justificacion": "La norma que establece los vicios que pueden afectar a un acto administrativo es la Ley 678 de 2001, artículo 5º, que menciona que se presume dolo del agente público por las siguientes causas: 1. Que el acto administrativo haya sido declarado nulo por desviación de poder, indebida motivación, o falta de motivación, y por falsa motivación. La opción C, \"Desviación de poder\", se menciona explícitamente como una causa que puede configurar dolo. Por lo tanto, la opción correcta es C. Fundamento normativo: artículo 111 de la Ley 1151 de 2007; artículo 2.5.2.4.2.4 del Decreto 780 de 2016; artículo 2.5.3.8.3.2.9 del Decreto 780 de 2016; artículo 6 de la Ley 1151 de 2007; Ley 2195 de 2022; Ley 344 de 1996; Ley 388 de 1997.",
  "descarte_opciones": {
    "A": "Falsa motivación no es la causa específica mencionada en el contexto de la consulta previa en el acto administrativo.",
    "B": "Usurpación de funciones no se menciona como una causa específica en la norma.",
    "D": "No estar basado en las normas necesarias no se menciona como una causa específica en la norma."
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"La norma que establece los vicios que pueden afectar a un acto administrativo es la Ley 678 de 2001, artículo 5º, que menciona que se presume dolo del agente público por las siguientes causas: 1. Que el acto administrativo haya sido declarado nulo por desviación de poder, indebida motivación, o falta de motivación, y por falsa motivación. La opción C, \"Desviación de poder\", se menciona explícitamente como una causa que puede configurar dolo. Por lo tanto, la opción correcta es C.","respuesta_correcta":"C","descarte_opciones":{"A":"Falsa motivación no es la causa específica mencionada en el contexto de la consulta previa en el acto administrativo.","B":"Usurpación de funciones no se menciona como una causa específica en la norma.","D":"No estar basado en las normas necesarias no se menciona como una causa específica en la norma."},"pasajes_usados":["ley_678_de_2001:00004:80c69cb8e6ef"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 1 → después 12 · reparación {} · construidas ['Ley 678 de 2001', 'artículo 111 de la Ley 1151 de 2007', 'artículo 2.5.2.4.2.4 del Decreto 780 de 2016', 'artículo 2.5.3.8.3.2.9 del Decreto 780 de 2016', 'artículo 6 de la Ley 1151 de 2007', 'Ley 2195 de 2022', 'Ley 344 de 1996', 'Ley 388 de 1997']
**Pasajes declarados por el modelo:** ['ley_678_de_2001:00004:80c69cb8e6ef']
**Evidencia:**
1. `ley_1151_de_2007:00162:746fa756804f` — Ley 1151 de 2007 art. 111
2. `decreto_780_de_2016:00626:78a5460adca5` — Decreto 780 de 2016 art. 2.5.2.4.2.4
3. `decreto_780_de_2016:00843:cdd0cf7308ff` — Decreto 780 de 2016 art. 2.5.3.8.3.2.9
4. `ley_1151_de_2007:00040:8c4a77cfe21d` — Ley 1151 de 2007 art. 6
5. `ley_160_de_1994:00002:6c8dd3966bf6` — Ley 160 de 1994 art. 2
6. `decreto_780_de_2016:00636:c545c14bb183` — Decreto 780 de 2016 art. 2.5.2.4.2.12
7. `ley_1819_de_2016:00234:04d6f671410c` — Ley 1819 de 2016 art. 175
8. `ley_678_de_2001:00004:80c69cb8e6ef` — Ley 678 de 2001 art. 5
*Tokens 5042→268 · generación 11059.771999993245 ms · retrieval 184.60519998916425 ms · grafo auto*

## 857 · semi_open

**Pregunta:** ¿Cuáles son las principales diferencias entre la función ejecutiva y judicial del Estado? 

**Medición:** cita=sin_ref_parseable · legal_basis=Doctrina. 

**Respuesta final:**
```json
{
  "respuesta": "La función ejecutiva y judicial del Estado tienen roles distintos en el sistema de gobierno. La función ejecutiva se encarga de la aplicación y cumplimiento de las leyes, mientras que la función judicial se encarga de interpretar y aplicar las leyes en casos concretos. Estas funciones son separadas para garantizar el equilibrio de poderes.",
  "palabras_clave": [
    "función ejecutiva",
    "función judicial",
    "equilibrio de poderes"
  ],
  "referencia_legal": "Sentencia SU-431 de 2015; Sentencia SU-296 de 2023; Sentencia C-748 de 2011; Sentencia C-683 de 2015; artículo 362 de la Ley 1819 de 2016; Constitución Política; Ley 1743 de 2014; Ley 42 de 1993"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La función ejecutiva y judicial del Estado tienen roles distintos en el sistema de gobierno. La función ejecutiva se encarga de la aplicación y cumplimiento de las leyes, mientras que la función judicial se encarga de interpretar y aplicar las leyes en casos concretos. Estas funciones son separadas para garantizar el equilibrio de poderes.","palabras_clave":["función ejecutiva","función judicial","equilibrio de poderes"],"referencia_legal":"Sentencia SU-431 de 2015","pasajes_usados":["sentencia_su_431_de_2015:00039:caedbd4fc1e4"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 1 → después 9 · reparación {} · construidas ['Sentencia SU-431 de 2015', 'Sentencia SU-296 de 2023', 'Sentencia C-748 de 2011', 'Sentencia C-683 de 2015', 'artículo 362 de la Ley 1819 de 2016', 'Constitución Política', 'Ley 1743 de 2014', 'Ley 42 de 1993']
**Pasajes declarados por el modelo:** ['sentencia_su_431_de_2015:00039:caedbd4fc1e4']
**Evidencia:**
1. `sentencia_su_296_de_2023:00067:97cf0ebfa045` — Sentencia SU-296 de 2023 art. None
2. `sentencia_c_748_de_2011:00228:176a9e8eb430` — Sentencia C-748 de 2011 art. None
3. `sentencia_c_683_de_2015:00148:d9d76c35210b` — Sentencia C-683 de 2015 art. None
4. `sentencia_su_431_de_2015:00039:caedbd4fc1e4` — Sentencia SU-431 de 2015 art. None
5. `sentencia_su_296_de_2023:00007:eb97a429c94a` — Sentencia SU-296 de 2023 art. None
6. `ley_1819_de_2016:00444:28b573b502ed` — Ley 1819 de 2016 art. 362
7. `sentencia_su_296_de_2023:00049:db5c81637419` — Sentencia SU-296 de 2023 art. None
8. `sentencia_su_431_de_2015:00026:52dbe3fbbdd1` — Sentencia SU-431 de 2015 art. None
*Tokens 6762→162 · generación 7433.409799996298 ms · retrieval 11.42759999493137 ms · grafo off*

## 865 · semi_open

**Pregunta:** ¿Qué dice el artículo 113 del Código Civil en relación al matrimonio? 

**Medición:** cita=cita_ok · legal_basis=artículo 113 del Código Civil

**Respuesta final:**
```json
{
  "respuesta": "El establece que el matrimonio es un contrato solemne por el cual un hombre y una mujer se unen con el fin de vivir juntos, de procrear y de auxiliarse mutuamente. Esta definición fue declarada exequible por la, la cual sostuvo que el matrimonio está reservado constitucional y legalmente para parejas heterosexuales. Por lo tanto, el no reconoce el matrimonio entre personas del mismo sexo.",
  "palabras_clave": [
    "matrimonio",
    "parejas heterosexuales"
  ],
  "referencia_legal": "Sentencia SU-214 de 2016; Sentencia C-394 de 2017; Código Civil; Sentencia C-577 de 2011; Ley 57 de 1887"
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "respuesta": "El artículo 113 del Código Civil establece que el matrimonio es un contrato solemne por el cual un hombre y una mujer se unen con el fin de vivir juntos, de procrear y de auxiliarse mutuamente. Esta definición fue declarada exequible por la Sentencia C-577 de 2011, la cual sostuvo que el matrimonio está reservado constitucional y legalmente para parejas heterosexuales. Por lo tanto, el artículo 113 del Código Civil no reconoce el matrimonio entre personas del mismo sexo.",
  "palabras_clave": ["artículo 113", "Código Civil", "matrimonio", "parejas heterosexuales", "Sentencia C-577 de 2011"],
  "referencia_legal": "artículo 113 del Código Civil",
  "pasajes_usados": [
    "sentencia_su_214_de_2016:00251:f5c257e6e810",
    "sentencia_su_214_de_2016:00249:12d1ef8dd253",
    "sentencia_su_214_de_2016:00158:eaf37ec105c5",
    "sentencia_su_214_de_2016:00019:8265c935ab57",
    "sentencia_su_214_de_2016:00210:7801afbcc855"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 10 → después 5 · reparación {'suppressed_fragment': 10, 'suppressed_sentence': 7} · construidas ['Sentencia SU-214 de 2016', 'Sentencia C-394 de 2017', 'Código Civil', 'Sentencia C-577 de 2011', 'Ley 57 de 1887']
**Pasajes declarados por el modelo:** ['sentencia_su_214_de_2016:00251:f5c257e6e810', 'sentencia_su_214_de_2016:00249:12d1ef8dd253', 'sentencia_su_214_de_2016:00158:eaf37ec105c5', 'sentencia_su_214_de_2016:00019:8265c935ab57', 'sentencia_su_214_de_2016:00210:7801afbcc855']
**Evidencia:**
1. `sentencia_su_214_de_2016:00251:f5c257e6e810` — Sentencia SU-214 de 2016 art. None
2. `sentencia_su_214_de_2016:00249:12d1ef8dd253` — Sentencia SU-214 de 2016 art. None
3. `sentencia_su_214_de_2016:00158:eaf37ec105c5` — Sentencia SU-214 de 2016 art. None
4. `sentencia_su_214_de_2016:00019:8265c935ab57` — Sentencia SU-214 de 2016 art. None
5. `sentencia_c_394_de_2017:00078:4654b291fd4c` — Sentencia C-394 de 2017 art. None
6. `sentencia_su_214_de_2016:00187:d196cb78dfd6` — Sentencia SU-214 de 2016 art. None
7. `sentencia_su_214_de_2016:00210:7801afbcc855` — Sentencia SU-214 de 2016 art. None
8. `sentencia_su_214_de_2016:00169:44e77baf9e02` — Sentencia SU-214 de 2016 art. None
*Tokens 7500→382 · generación 16612.90540000482 ms · retrieval 56.694500002777204 ms · grafo auto*

## 879 · semi_open

**Pregunta:** Si CLAUDIA inicia un proceso para cobrar y obtener el pago de la suma de 1 millón de pesos contra CARLOS, encontrándose sometida dicha obligación a un plazo no vencido, el demandante: 

**Medición:** cita=cita_ok · legal_basis=Código General del Proceso. 

**Respuesta final:**
```json
{
  "respuesta": "Si Claudia inicia un proceso para cobrar y obtener el pago de la suma de 1 millón de pesos contra Carlos, encontrándose sometida dicha obligación a un plazo no vencido, el demandante deberá solicitar al juez que ordene a los signatarios que depositen, a disposición del juzgado, el importe del título. Si los obligados se negaren a realizar el pago, quien obtuvo la cancelación podrá legitimarse con la copia de la sentencia, para exigir las prestaciones derivadas del título. El depósito del importe del título hecho por uno de los signatarios libera a los otros de la obligación de hacerlo.",
  "palabras_clave": [
    "proceso ejecutivo",
    "pago",
    "obligación",
    "demandante",
    "título"
  ],
  "referencia_legal": "artículo 398 del Código General del Proceso; artículo 308 del Estatuto Tributario; artículo 381 del Código General del Proceso; artículo 432 del Código General del Proceso; artículo 70 de la Ley 1116 de 2006; Ley 1607 de 2012; Código Civil; Ley 1676 de 2013"
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "respuesta": "Si Claudia inicia un proceso para cobrar y obtener el pago de la suma de 1 millón de pesos contra Carlos, encontrándose sometida dicha obligación a un plazo no vencido, el demandante deberá solicitar al juez que ordene a los signatarios que depositen, a disposición del juzgado, el importe del título. Si los obligados se negaren a realizar el pago, quien obtuvo la cancelación podrá legitimarse con la copia de la sentencia, para exigir las prestaciones derivadas del título. El depósito del importe del título hecho por uno de los signatarios libera a los otros de la obligación de hacerlo.",
  "palabras_clave": ["proceso ejecutivo", "pago", "obligación", "demandante", "título"],
  "referencia_legal": "Código General del Proceso (Ley 1564 de 2012), Artículo 398",
  "pasajes_usados": ["codigo_general_proceso:00413:39dd7a83bb23"]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 3 → después 13 · reparación {'suppressed_fragment': 1, 'suppressed_sentence': 1} · construidas ['artículo 398 del Código General del Proceso', 'artículo 308 del Estatuto Tributario', 'artículo 381 del Código General del Proceso', 'artículo 432 del Código General del Proceso', 'artículo 70 de la Ley 1116 de 2006', 'Ley 1607 de 2012', 'Código Civil', 'Ley 1676 de 2013']
**Pasajes declarados por el modelo:** ['codigo_general_proceso:00413:39dd7a83bb23']
**Evidencia:**
1. `estatuto_tributario:00515:a897e821e1f5` — Estatuto Tributario (Decreto 624 de 1989) art. 308
2. `codigo_general_proceso:00392:781c808a0f18` — Código General del Proceso (Ley 1564 de 2012) art. 381
3. `codigo_general_proceso:00448:a32c64614277` — Código General del Proceso (Ley 1564 de 2012) art. 432
4. `ley_1116_de_2006:00073:7cf93506a426` — Ley 1116 de 2006 art. 70
5. `codigo_general_proceso:00413:39dd7a83bb23` — Código General del Proceso (Ley 1564 de 2012) art. 398
6. `codigo_comercio:01286:c5a5aaeef1d0` — Código de Comercio (Decreto 410 de 1971) art. 1213
7. `ley_2452_de_2025:00295:3c6e5b8d777e` — Ley 2452 de 2025 art. 288
8. `codigo_civil:02392:2e8db054764f` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 2394
*Tokens 4489→259 · generación 9768.734500001301 ms · retrieval 18.71559998835437 ms · grafo off*

## 919 · semi_open

**Pregunta:** ¿Cuál es el problema jurídico abordado en la sentencia SU-455 de 2020 de la Corte Constitucional? 

**Medición:** cita=cita_ok · legal_basis=Sentencia SU-455 de 2020 de la Corte Constitucional. 

**Respuesta final:**
```json
{
  "respuesta": "El problema jurídico abordado en la sentencia SU-455 de 2020 de la Corte Constitucional es la revisión de la decisión de la Sala de Casación Civil de la Corte Suprema de Justicia, que negó el amparo solicitado por la Arrocera Potrerito S.A.S. en un proceso de responsabilidad civil extracontractual.",
  "palabras_clave": [
    "Corte Constitucional",
    "Sentencia SU-455 de 2020",
    "procedimiento judicial",
    "derecho constitucional"
  ],
  "referencia_legal": "sentencia_su_455_de_2020:00028:4997242600f8"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El problema jurídico abordado en la sentencia SU-455 de 2020 de la Corte Constitucional es la revisión de la decisión de la Sala de Casación Civil de la Corte Suprema de Justicia, que negó el amparo solicitado por la Arrocera Potrerito S.A.S. en un proceso de responsabilidad civil extracontractual. La Corte Constitucional determinó que la sentencia acusada incurrió en un defecto procedimental por exceso ritual manifiesto, un defecto fáctico por indebida valoración probatoria y en violación directa de la Constitución.","palabras_clave":["Corte Constitucional","Sentencia SU-455 de 2020","procedimiento judicial","derecho constitucional"],"referencia_legal":"sentencia_su_455_de_2020:00028:4997242600f8"}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 3 → después 2 · reparación {'suppressed_sentence': 1} · construidas []
**Pasajes declarados por el modelo:** []
**Evidencia:**
1. `sentencia_su_455_de_2020:00042:7edc066fb9bb` — Sentencia SU-455 de 2020 art. None
2. `sentencia_c_55_de_2022:00275:71dec94ba057` — Sentencia C-55 de 2022 art. None
3. `sentencia_c_233_de_2021:00044:2618b7bf6c8e` — Sentencia C-233 de 2021 art. None
4. `sentencia_su_455_de_2020:00014:6e0d8ebf6032` — Sentencia SU-455 de 2020 art. None
5. `sentencia_su_429_de_2024:00114:b5b9b9053928` — Sentencia SU-429 de 2024 art. None
6. `sentencia_su_455_de_2020:00028:4997242600f8` — Sentencia SU-455 de 2020 art. None
7. `sentencia_su_455_de_2020:00013:ac1c4eb073c5` — Sentencia SU-455 de 2020 art. None
8. `sentencia_c_15_de_2018:00011:10a7e8462645` — Sentencia C-15 de 2018 art. None
*Tokens 7288→225 · generación 10296.218699993915 ms · retrieval 16.168100002687424 ms · grafo off*

## 946 · semi_open

**Pregunta:** ¿Cuál es el problema jurídico abordado en la sentencia C-039 de 2025 de la Corte Constitucional? 

**Medición:** cita=cita_ok · legal_basis= Sentencia C-039 de 2025 de la Corte Constitucional

**Respuesta final:**
```json
{
  "respuesta": "El problema jurídico abordado en la sentencia C-039 de 2025 de la Corte Constitucional es la inconstitucionalidad de las normas que reconocen efectos jurídicos a los matrimonios y a las uniones maritales de hecho con o entre personas menores de 18 años, así como la exequibilidad condicionada de algunas disposiciones relacionadas con esta materia.",
  "palabras_clave": [
    "inconstitucionalidad",
    "matrimonios",
    "uniones maritales",
    "CEDAW",
    "derechos de los niños"
  ],
  "referencia_legal": "Sentencia C-39 de 2025; Sentencia C-55 de 2022; Sentencia C-183 de 2025; Sentencia C-15 de 2018; Sentencia C-233 de 2021; Código Civil; Ley 1306 de 2009; Ley 1098 de 2006"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El problema jurídico abordado en la sentencia C-039 de 2025 de la Corte Constitucional es la inconstitucionalidad de las normas que reconocen efectos jurídicos a los matrimonios y a las uniones maritales de hecho con o entre personas menores de 18 años, así como la exequibilidad condicionada de algunas disposiciones relacionadas con esta materia. La Corte determinó que estas normas desconocían el artículo 16.2 de la Convención sobre la Eliminación de todas las Formas de Discriminación contra la Mujer (CEDAW) y el estándar de mayor protección aplicable a los derechos de los niños y las niñas.","palabras_clave":["inconstitucionalidad","matrimonios","uniones maritales","CEDAW","derechos de los niños"],"referencia_legal":"Sentencia C-39 de 2025","pasajes_usados":["sentencia_c_39_de_2025:00060:cb905c5b4bcf","sentencia_c_39_de_2025:00063:5e8c4e2ffad4"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 3 → después 9 · reparación {'suppressed_sentence': 1} · construidas ['Sentencia C-39 de 2025', 'Sentencia C-55 de 2022', 'Sentencia C-183 de 2025', 'Sentencia C-15 de 2018', 'Sentencia C-233 de 2021', 'Código Civil', 'Ley 1306 de 2009', 'Ley 1098 de 2006']
**Pasajes declarados por el modelo:** ['sentencia_c_39_de_2025:00060:cb905c5b4bcf', 'sentencia_c_39_de_2025:00063:5e8c4e2ffad4']
**Evidencia:**
1. `sentencia_c_39_de_2025:00060:cb905c5b4bcf` — Sentencia C-39 de 2025 art. None
2. `sentencia_c_39_de_2025:00063:5e8c4e2ffad4` — Sentencia C-39 de 2025 art. None
3. `sentencia_c_55_de_2022:00275:71dec94ba057` — Sentencia C-55 de 2022 art. None
4. `sentencia_c_183_de_2025:00011:b145e10d3c7d` — Sentencia C-183 de 2025 art. None
5. `sentencia_c_15_de_2018:00011:10a7e8462645` — Sentencia C-15 de 2018 art. None
6. `sentencia_c_233_de_2021:00044:2618b7bf6c8e` — Sentencia C-233 de 2021 art. None
7. `sentencia_c_80_de_2025:00013:684ca03f17cf` — Sentencia C-80 de 2025 art. None
8. `sentencia_c_39_de_2025:00062:ac722a62c0e6` — Sentencia C-39 de 2025 art. None
*Tokens 7408→284 · generación 12742.187299998477 ms · retrieval 16.725299996323884 ms · grafo off*

## 960 · semi_open

**Pregunta:** En el derecho de la protección de la competencia, ¿qué es una "posición dominante"?

**Medición:** cita=cita_ok · legal_basis=Artículo 45 del Decreto 2153 de 1992

**Respuesta final:**
```json
{
  "respuesta": "En el derecho de la protección de la competencia, una \"posición dominante\" se refiere a la capacidad que tiene una empresa o persona de determinar, directa o indirectamente, las condiciones en su respectivo mercado. Esto se establece en el Decreto 780 de 2016, artículo 2.5.6.8. Cuando una empresa ocupa una posición dominante, su comportamiento puede ser regulado para evitar abusos que afecten la libre competencia.",
  "palabras_clave": [
    "posición dominante",
    "derecho de la competencia",
    "Decreto 780 de 2016",
    "abuso de posición dominante"
  ],
  "referencia_legal": "artículo 2.5.6.8 del Decreto 780 de 2016; artículo 2.5.6.9 del Decreto 780 de 2016; artículo 44 del Decreto 2153 de 1992; artículo 66 de la Decisión Andina 486 de 2000; artículo 50 del Decreto 2153 de 1992; Decreto 1663 de 1994; Ley 155 de 1959; Ley 590 de 2000"
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "respuesta": "En el derecho de la protección de la competencia, una \"posición dominante\" se refiere a la capacidad que tiene una empresa o persona de determinar, directa o indirectamente, las condiciones en su respectivo mercado. Esto se establece en el Decreto 780 de 2016, artículo 2.5.6.8. Cuando una empresa ocupa una posición dominante, su comportamiento puede ser regulado para evitar abusos que afecten la libre competencia.",
  "palabras_clave": ["posición dominante", "derecho de la competencia", "Decreto 780 de 2016", "abuso de posición dominante"],
  "referencia_legal": "Decreto 780 de 2016, artículo 2.5.6.8",
  "pasajes_usados": [
    "decreto_780_de_2016:01078:099f831ca574",
    "decreto_780_de_2016:01079:ef5746dc55ab"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 5 → después 16 · reparación {} · construidas ['artículo 2.5.6.8 del Decreto 780 de 2016', 'artículo 2.5.6.9 del Decreto 780 de 2016', 'artículo 44 del Decreto 2153 de 1992', 'artículo 66 de la Decisión Andina 486 de 2000', 'artículo 50 del Decreto 2153 de 1992', 'Decreto 1663 de 1994', 'Ley 155 de 1959', 'Ley 590 de 2000']
**Pasajes declarados por el modelo:** ['decreto_780_de_2016:01078:099f831ca574', 'decreto_780_de_2016:01079:ef5746dc55ab']
**Evidencia:**
1. `decreto_2153_de_1992:00047:66be588e84a7` — Decreto 2153 de 1992 art. 44
2. `decreto_780_de_2016:01079:ef5746dc55ab` — Decreto 780 de 2016 art. 2.5.6.9
3. `decreto_780_de_2016:01078:099f831ca574` — Decreto 780 de 2016 art. 2.5.6.8
4. `decision_andina_486:00065:9e7002ffb5ab` — Decisión Andina 486 de 2000 art. 66
5. `decreto_2153_de_1992:00053:8d78a0ceebf1` — Decreto 2153 de 1992 art. 50
6. `sentencia_c_345_de_2017:00033:8fab44d81ed2` — Sentencia C-345 de 2017 art. None
7. `sentencia_c_345_de_2017:00057:c2f7a8dbad06` — Sentencia C-345 de 2017 art. None
8. `sentencia_sl_648_de_2018:00009:902c784b8318` — Sentencia SL-648 de 2018 art. None
*Tokens 5070→270 · generación 11066.109100007452 ms · retrieval 11.970699997618794 ms · grafo off*

## 991 · semi_open

**Pregunta:** ¿Cuál fue el fundamento jurídico central de la sentencia C-891 del 2012 de la Corte Constitucional? 

**Medición:** cita=cita_ok · legal_basis=Sentencia C-891 del 2012 de la Corte Constitucional

**Respuesta final:**
```json
{
  "respuesta": "La sentencia C-891 de 2012 de la Corte Constitucional se basó en el principio de legalidad tributaria, el cual establece que los tributos deben ser creados por el legislador y no por otros organismos.",
  "palabras_clave": [
    "principio de legalidad tributaria",
    "autonomía de las entidades territoriales"
  ],
  "referencia_legal": "Sentencia C-891 de 2012; Sentencia C-683 de 2015; Sentencia C-164 de 2022; Sentencia C-80 de 2025; Sentencia C-259 de 2015; Constitución Política; Sentencia C-71 de 2015; Sentencia C-931 de 2008"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La sentencia C-891 de 2012 de la Corte Constitucional se basó en el principio de legalidad tributaria, el cual establece que los tributos deben ser creados por el legislador y no por otros organismos. La Corte determinó que la norma demandada vulneraba la autonomía de las entidades territoriales y el artículo 287 de la Constitución Política.","palabras_clave":["principio de legalidad tributaria","autonomía de las entidades territoriales","artículo 287"],"referencia_legal":"Sentencia C-891 de 2012","pasajes_usados":["sentencia_c_891_de_2012:00023:1009f425ace1","sentencia_c_891_de_2012:00000:993ba336d7dc"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 5 → después 9 · reparación {'suppressed_fragment': 1, 'suppressed_sentence': 2} · construidas ['Sentencia C-891 de 2012', 'Sentencia C-683 de 2015', 'Sentencia C-164 de 2022', 'Sentencia C-80 de 2025', 'Sentencia C-259 de 2015', 'Constitución Política', 'Sentencia C-71 de 2015', 'Sentencia C-931 de 2008']
**Pasajes declarados por el modelo:** ['sentencia_c_891_de_2012:00023:1009f425ace1', 'sentencia_c_891_de_2012:00000:993ba336d7dc']
**Evidencia:**
1. `sentencia_c_891_de_2012:00023:1009f425ace1` — Sentencia C-891 de 2012 art. None
2. `sentencia_c_683_de_2015:00164:24bf024c7ba4` — Sentencia C-683 de 2015 art. None
3. `sentencia_c_164_de_2022:00074:dc2ac3b7a018` — Sentencia C-164 de 2022 art. None
4. `sentencia_c_80_de_2025:00060:a7e3ffd20beb` — Sentencia C-80 de 2025 art. None
5. `sentencia_c_891_de_2012:00000:993ba336d7dc` — Sentencia C-891 de 2012 art. None
6. `sentencia_c_259_de_2015:00017:34e9972342a9` — Sentencia C-259 de 2015 art. None
7. `sentencia_c_80_de_2025:00061:ee220a032bb7` — Sentencia C-80 de 2025 art. None
8. `sentencia_su_566_de_2015:00085:6b415202ae46` — Sentencia SU-566 de 2015 art. None
*Tokens 6848→218 · generación 9645.538199998555 ms · retrieval 17.155699999420904 ms · grafo off*

## 1005 · semi_open

**Pregunta:** Con base a la siguiente afirmación, establezca si es falsa o verdadera: 

El Congreso tiene la facultad de efectuar, mediante ley, traslados o adiciones presupuestales, fruto de las cuales se amplíe o cambie la destinación de las apropiaciones de gastos inicialmente autorizados. 

**Medición:** cita=cita_ok · legal_basis=Constitución Política. 

**Respuesta final:**
```json
{
  "respuesta": "La afirmación es verdadera. El Congreso tiene la facultad de efectuar, mediante ley, traslados o adiciones presupuestales, fruto de las cuales se amplíe o cambie la destinación de las apropiaciones de gastos inicialmente autorizados. Esto se refleja en el artículo 347 de la Constitución Política de Colombia de 1991, que establece que el proyecto de ley de apropiaciones debe contener la totalidad de los gastos que el Estado pretende realizar durante la vigencia fiscal respectiva.",
  "palabras_clave": [
    "Congreso",
    "facultad",
    "traslados presupuestales",
    "apropiaciones de gastos",
    "Constitución Política de Colombia de 1991"
  ],
  "referencia_legal": "artículo 347 de la Constitución Política de Colombia de 1991; artículo 57 del Código General Disciplinario; artículo 115 de la Ley 50 de 1990; artículo 42 de la Ley 80 de 1993; Sentencia SU-11 de 2020; Sentencia C-614 de 2002; Acto Legislativo 1 de 2001; Ley 5 de 1992"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La afirmación es verdadera. El Congreso tiene la facultad de efectuar, mediante ley, traslados o adiciones presupuestales, fruto de las cuales se amplíe o cambie la destinación de las apropiaciones de gastos inicialmente autorizados. Esto se refleja en el artículo 347 de la Constitución Política de Colombia de 1991, que establece que el proyecto de ley de apropiaciones debe contener la totalidad de los gastos que el Estado pretende realizar durante la vigencia fiscal respectiva.","palabras_clave":["Congreso","facultad","traslados presupuestales","apropiaciones de gastos","Constitución Política"],"referencia_legal":"Constitución Política de Colombia de 1991, artículo 347","pasajes_usados":["constitucion:00457:fb686f25ce55"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 5 → después 15 · reparación {'renamed_to_evidence_name': 1} · construidas ['artículo 347 de la Constitución Política de Colombia de 1991', 'artículo 57 del Código General Disciplinario', 'artículo 115 de la Ley 50 de 1990', 'artículo 42 de la Ley 80 de 1993', 'Sentencia SU-11 de 2020', 'Sentencia C-614 de 2002', 'Acto Legislativo 1 de 2001', 'Ley 5 de 1992']
**Pasajes declarados por el modelo:** ['constitucion:00457:fb686f25ce55']
**Evidencia:**
1. `codigo_disciplinario:00059:190cb268e29a` — Código General Disciplinario (Ley 1952 de 2019) art. 57
2. `ley_50_de_1990:00115:a1899933a91d` — Ley 50 de 1990 art. 115
3. `ley_80_de_1993:00057:15a0c99b9119` — Ley 80 de 1993 art. 42
4. `sentencia_su_11_de_2020:00006:a3d1eabc2812` — Sentencia SU-11 de 2020 art. None
5. `sentencia_su_11_de_2020:00027:67764100bd55` — Sentencia SU-11 de 2020 art. None
6. `sentencia_su_11_de_2020:00004:9b02d13dc549` — Sentencia SU-11 de 2020 art. None
7. `constitucion:00457:fb686f25ce55` — Constitución Política de Colombia de 1991 art. 347
8. `ley_1819_de_2016:00283:dca86ada5072` — Ley 1819 de 2016 art. 218
*Tokens 6399→210 · generación 9027.656499994919 ms · retrieval 43.008199994801544 ms · grafo on*

## 1015 · semi_open

**Pregunta:** ¿Qué se requiere para que un aborto sea no punible bajo las causales de la Sentencia C-355 de 2006?

**Medición:** cita=cita_ok · legal_basis=Sentencia C-355 de 2006

**Respuesta final:**
```json
{
  "respuesta": "Para que un aborto sea no punible bajo las causales de la Sentencia C-355 de 2006, se requiere que se cumplan alguna de las tres circunstancias establecidas: (i) que la continuación del embarazo constituya peligro para la vida o la salud de la mujer, certificada por un médico; (ii) que exista grave malformación del feto que haga inviable su vida, certificada por un médico; y, (iii) que el embarazo sea el resultado de una conducta, debidamente denunciada, constitutiva de acceso carnal o acto sexual sin consentimiento, abusivo o de inseminación artificial o transferencia de óvulo fecundado no consentidas, o de incesto. Estas causales se establecen en la Sentencia C-355 de 2006.",
  "palabras_clave": [
    "aborto",
    "causales",
    "Sentencia C-355 de 2006",
    "no punible"
  ],
  "referencia_legal": "Sentencia C-55 de 2022; artículo 9 del Código Penal; Sentencia C-355 de 2006; Ley 1257 de 2008; Constitución Política; Código Civil"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"Para que un aborto sea no punible bajo las causales de la Sentencia C-355 de 2006, se requiere que se cumplan alguna de las tres circunstancias establecidas: (i) que la continuación del embarazo constituya peligro para la vida o la salud de la mujer, certificada por un médico; (ii) que exista grave malformación del feto que haga inviable su vida, certificada por un médico; y, (iii) que el embarazo sea el resultado de una conducta, debidamente denunciada, constitutiva de acceso carnal o acto sexual sin consentimiento, abusivo o de inseminación artificial o transferencia de óvulo fecundado no consentidas, o de incesto. Estas causales se establecen en la Sentencia C-355 de 2006.","palabras_clave":["aborto","causales","Sentencia C-355 de 2006","no punible"],"referencia_legal":"Sentencia C-55 de 2022","pasajes_usados":["sentencia_c_55_de_2022:00286:b747a94cdda9"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 4 → después 10 · reparación {} · construidas ['Sentencia C-55 de 2022', 'artículo 9 del Código Penal', 'Sentencia C-355 de 2006', 'Ley 1257 de 2008', 'Constitución Política', 'Código Civil']
**Pasajes declarados por el modelo:** ['sentencia_c_55_de_2022:00286:b747a94cdda9']
**Evidencia:**
1. `sentencia_c_55_de_2022:00312:fb8d22a3b6e4` — Sentencia C-55 de 2022 art. None
2. `codigo_penal:00008:3c39173b1f70` — Código Penal (Ley 599 de 2000) art. 9
3. `sentencia_c_55_de_2022:00025:1b75b530231a` — Sentencia C-55 de 2022 art. None
4. `sentencia_c_355_de_2006:00482:bcee5459959f` — Sentencia C-355 de 2006 art. None
5. `sentencia_c_55_de_2022:00265:c06834bfa2de` — Sentencia C-55 de 2022 art. None
6. `sentencia_c_55_de_2022:00286:b747a94cdda9` — Sentencia C-55 de 2022 art. None
7. `sentencia_c_55_de_2022:00034:eb680fe5efb7` — Sentencia C-55 de 2022 art. None
8. `sentencia_c_55_de_2022:00276:09abf2fa61d8` — Sentencia C-55 de 2022 art. None
*Tokens 7063→289 · generación 12579.593899994507 ms · retrieval 18.732399999862537 ms · grafo off*

## 1065 · semi_open

**Pregunta:** Una ministra a quien le fue aceptada la renuncia continúa celebrando contratos estatales durante dos semanas adicionales. ¿Puede ser sujeto activo de peculado u otros delitos contra la administración pública?

**Medición:** cita=cita_ok · legal_basis=Artículo 20 del Código Penal. 

**Respuesta final:**
```json
{
  "respuesta": "La ministra que renunció y continuó celebrando contratos estatales puede ser sujeto activo de peculado u otros delitos contra la administración pública. Según el artículo 38G del Código Penal, el peculado se refiere a la apropiación de bienes o recursos públicos. Además, el artículo 396C del Código Penal establece que la omisión de información sobre aportes a campañas electorales puede constituir un delito. Sin embargo, la renuncia no impide la responsabilidad penal si se comete un delito durante el periodo de transición.",
  "palabras_clave": [
    "peculado",
    "delitos contra la administración pública",
    "renuncia",
    "Código Penal"
  ],
  "referencia_legal": "artículo 396c del Código Penal; artículo 38g del Código Penal; Sentencia C-15 de 2018; Sentencia C-80 de 2025; artículo 75 del Código de Procedimiento Penal; Ley 1864 de 2017; Ley 1709 de 2014; Ley 1150 de 2007"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La ministra que renunció y continuó celebrando contratos estatales puede ser sujeto activo de peculado u otros delitos contra la administración pública. Según el artículo 38G del Código Penal, el peculado se refiere a la apropiación de bienes o recursos públicos. Además, el artículo 396C del Código Penal establece que la omisión de información sobre aportes a campañas electorales puede constituir un delito. Sin embargo, la renuncia no impide la responsabilidad penal si se comete un delito durante el periodo de transición.","palabras_clave":["peculado","delitos contra la administración pública","renuncia","Código Penal"],"referencia_legal":"Código Penal (Ley 599 de 2000), artículo 38G y 396C","pasajes_usados":["codigo_penal:00511:720189458a3b","codigo_penal:00046:2dd15d07605f"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 9 → después 16 · reparación {'suppressed_fragment': 1, 'suppressed_sentence': 1} · construidas ['artículo 396c del Código Penal', 'artículo 38g del Código Penal', 'Sentencia C-15 de 2018', 'Sentencia C-80 de 2025', 'artículo 75 del Código de Procedimiento Penal', 'Ley 1864 de 2017', 'Ley 1709 de 2014', 'Ley 1150 de 2007']
**Pasajes declarados por el modelo:** ['codigo_penal:00511:720189458a3b', 'codigo_penal:00046:2dd15d07605f']
**Evidencia:**
1. `codigo_penal:00511:720189458a3b` — Código Penal (Ley 599 de 2000) art. 396c
2. `sentencia_c_15_de_2018:00038:309304789c09` — Sentencia C-15 de 2018 art. None
3. `codigo_penal:00046:2dd15d07605f` — Código Penal (Ley 599 de 2000) art. 38g
4. `sentencia_c_80_de_2025:00029:f3ba02e0475b` — Sentencia C-80 de 2025 art. None
5. `sentencia_c_15_de_2018:00028:bdd00881d1c7` — Sentencia C-15 de 2018 art. None
6. `sentencia_c_80_de_2025:00034:361ef33ad92d` — Sentencia C-80 de 2025 art. None
7. `codigo_procedimiento_penal:00076:503238c7847a` — Código de Procedimiento Penal (Ley 906 de 2004) art. 75
8. `constitucion:00251:4d6f09faa73a` — Constitución Política de Colombia de 1991 art. 194
*Tokens 6521→248 · generación 10817.030000005616 ms · retrieval 35.889699996914715 ms · grafo on*

## 1073 · semi_open

**Pregunta:** Una empresa contrata a una persona mediante una Cooperativa de Trabajo Asociado para que preste servicios de asesoría jurídica exclusivamente para ella, en horario fijo de lunes a viernes de 8:00 a.m. a 5:00 p.m., bajo instrucciones directas del gerente. ¿Existe una relación laboral?

**Medición:** cita=cita_ok · legal_basis=Artículo 53 de la Constitución Política. 
Artículos 23 y 34 del Código Sustantivo del Trabajo. 

**Respuesta final:**
```json
{
  "respuesta": "La relación laboral se define por la subordinación jurídica, que implica la capacidad del empleador para impartir órdenes y exigir su cumplimiento. En este caso, la persona presta servicios bajo instrucciones directas del gerente, lo que sugiere una relación de subordinación. Por lo tanto, existe una relación laboral.",
  "palabras_clave": [
    "relación laboral",
    "subordinación jurídica",
    "contrato de trabajo",
    "Código Sustantivo del Trabajo",
    "Cooperativa de Trabajo Asociado"
  ],
  "referencia_legal": "Sentencia T-243 de 2018; artículo 2 de la Ley 50 de 1990; Sentencia C-201 de 2002; artículo 2.5.3.10.1.2 del Decreto 780 de 2016; artículo 160 del Código Sustantivo del Trabajo; Sentencia C-934 de 2004; Sentencia T-290 de 1993; Sentencia T-611 de 2001"
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "respuesta": "La relación laboral se define por la subordinación jurídica, que implica la capacidad del empleador para impartir órdenes y exigir su cumplimiento. En este caso, la persona presta servicios bajo instrucciones directas del gerente, lo que sugiere una relación de subordinación. Según el artículo 2 del Código Sustantivo del Trabajo, se presume que toda relación de trabajo personal está regida por un contrato de trabajo, siempre que se demuestre la subordinación jurídica. Por lo tanto, existe una relación laboral.",
  "palabras_clave": ["relación laboral", "subordinación jurídica", "contrato de trabajo", "Código Sustantivo del Trabajo", "Cooperativa de Trabajo Asociado"],
  "referencia_legal": "Artículo 2 del Código Sustantivo del Trabajo (Decreto 2663 de 1950) y Sentencia T-243 de 2018.",
  "pasajes_usados": ["sentencia_t_243_de_2018:00030:dee4682368d7", "ley_50_de_1990:00001:433e2caf2f79"]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 7 → después 12 · reparación {'renamed_to_evidence_name': 40, 'suppressed_fragment': 1} · construidas ['Sentencia T-243 de 2018', 'artículo 2 de la Ley 50 de 1990', 'Sentencia C-201 de 2002', 'artículo 2.5.3.10.1.2 del Decreto 780 de 2016', 'artículo 160 del Código Sustantivo del Trabajo', 'Sentencia C-934 de 2004', 'Sentencia T-290 de 1993', 'Sentencia T-611 de 2001']
**Pasajes declarados por el modelo:** ['sentencia_t_243_de_2018:00030:dee4682368d7', 'ley_50_de_1990:00001:433e2caf2f79']
**Evidencia:**
1. `sentencia_t_243_de_2018:00030:dee4682368d7` — Sentencia T-243 de 2018 art. None
2. `sentencia_c_201_de_2002:00049:95d87ae21c32` — Sentencia C-201 de 2002 art. None
3. `ley_50_de_1990:00001:433e2caf2f79` — Ley 50 de 1990 art. 2
4. `decreto_780_de_2016:00998:fa304fd5e2ae` — Decreto 780 de 2016 art. 2.5.3.10.1.2
5. `codigo_sustantivo_trabajo:00161:3e3de9cca1c2` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 160
6. `codigo_sustantivo_trabajo:00178:a8c88eacee80` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 177
7. `codigo_sustantivo_trabajo:00184:586aca7657aa` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 183
8. `ley_1819_de_2016:00426:0873e973d570` — Ley 1819 de 2016 art. 345
*Tokens 4590→306 · generación 12242.103099997621 ms · retrieval 19.673200004035607 ms · grafo off*

## 1089 · semi_open

**Pregunta:** En el trámite de una apelación ante el Consejo de Estado, el magistrado ponente profiere un auto rechazando la demanda de reconvención. La parte afectada quiere impugnar ese auto. ¿Qué recurso procede, quién lo resuelve y en qué término debe interponerse?

**Medición:** cita=cita_ok · legal_basis=Artículo 246 del CPACA. 

**Respuesta final:**
```json
{
  "respuesta": "En el trámite de una apelación ante el Consejo de Estado, si el magistrado ponente rechaza la demanda de reconvención, la parte afectada puede interponer recurso de súplica contra ese auto. Este recurso se resuelve por los demás integrantes de la sala, sección o subsección de la que haga parte quien profirió el auto. Debe interponerse dentro de los tres (3) días siguientes a la notificación del auto, mediante escrito dirigido al magistrado sustanciador.",
  "palabras_clave": [
    "recurso de súplica",
    "auto rechazando demanda de reconvención",
    "Consejo de Estado",
    "término de interposición"
  ],
  "referencia_legal": "artículo 246 del Código de Procedimiento Administrativo y de lo Contencioso Administrativo; artículo 331 del Código General del Proceso; artículo 244 del Código de Procedimiento Administrativo y de lo Contencioso Administrativo; artículo 318 del Código General del Proceso; artículo 247 de la Ley 2452 de 2025; Ley 2080 de 2021"
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "respuesta": "En el trámite de una apelación ante el Consejo de Estado, si el magistrado ponente rechaza la demanda de reconvención, la parte afectada puede interponer recurso de súplica contra ese auto. Este recurso se resuelve por los demás integrantes de la sala, sección o subsección de la que haga parte quien profirió el auto. Debe interponerse dentro de los tres (3) días siguientes a la notificación del auto, mediante escrito dirigido al magistrado sustanciador.",
  "palabras_clave": ["recurso de súplica", "auto rechazando demanda de reconvención", "Consejo de Estado", "término de interposición"],
  "referencia_legal": "Código de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011), artículo 246",
  "pasajes_usados": ["cpaca:00270:f59e2b0321fb", "codigo_general_proceso:00339:6f19ebe3ffd7"]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 3 → después 11 · reparación {'suppressed_fragment': 1, 'suppressed_sentence': 1} · construidas ['artículo 246 del Código de Procedimiento Administrativo y de lo Contencioso Administrativo', 'artículo 331 del Código General del Proceso', 'artículo 244 del Código de Procedimiento Administrativo y de lo Contencioso Administrativo', 'artículo 318 del Código General del Proceso', 'artículo 247 de la Ley 2452 de 2025', 'Ley 2080 de 2021']
**Pasajes declarados por el modelo:** ['cpaca:00270:f59e2b0321fb', 'codigo_general_proceso:00339:6f19ebe3ffd7']
**Evidencia:**
1. `cpaca:00270:f59e2b0321fb` — Código de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) art. 246
2. `cpaca:00268:bf7aa1e240d7` — Código de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) art. 244
3. `codigo_general_proceso:00339:6f19ebe3ffd7` — Código General del Proceso (Ley 1564 de 2012) art. 331
4. `codigo_general_proceso:00325:c5cdd108a5ab` — Código General del Proceso (Ley 1564 de 2012) art. 318
5. `ley_2452_de_2025:00251:923ae69c11c7` — Ley 2452 de 2025 art. 247
6. `cpaca:00207:2f14d638d576` — Código de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) art. 185a
7. `cpaca:00310:28d46cec0f2e` — Código de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) art. 282
8. `cpaca:00197:67fe2ecd6cba` — Código de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) art. 180
*Tokens 6061→278 · generación 11477.62689999945 ms · retrieval 19.875099998898804 ms · grafo off*
