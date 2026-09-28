# KingsCode — revisión de literatura para Legal RAG

**Fecha de corte:** 2026-09-27  
**Objetivo:** convertir la estrategia de la Hackathon 2026 en una arquitectura guiada por evidencia reciente, no solo por intuición.

## 1. Conclusión ejecutiva

La literatura reciente converge en una idea útil para este reto: **el techo de un Legal RAG lo pone primero la recuperación y la calidad de la evidencia, no el tamaño del generador**. Para KingsCode, esto refuerza una arquitectura de bajo riesgo y alto rendimiento:

1. **Corpus jurídico estructurado** por unidades normativas (norma → artículo → inciso/parágrafo/numeral cuando exista).
2. **Chunking consciente de estructura**, no cortes fijos arbitrarios.
3. **Recuperación híbrida**: BM25 + dense retrieval.
4. **Fusión** de rankings con RRF como baseline fuerte.
5. **Cross-encoder reranking** sobre un conjunto pequeño de candidatos.
6. **Contexto mínimo y preciso** al decoder, preservando metadatos y orden documental.
7. **Generación estrictamente grounded**: solo se puede citar evidencia recuperada.
8. **Auditoría post-generación** de referencias y citas.
9. **Fine-tuning del decoder solo si el retrieval ya es bueno y el generador sigue fallando**.
10. **Evaluación separada de retrieval y generation** para saber qué componente mejora o empeora.

## 2. Hallazgos de literatura y cómo se traducen al reto

### A. Retrieval es el principal cuello de botella en Legal RAG

**Legal RAG Bench (Butler & Butler, 2026)** evalúa embeddings y LLMs con un diseño factorial y concluye que la recuperación fue el principal impulsor del rendimiento legal end-to-end; varios errores atribuidos a “hallucination” empiezan realmente como fallos de retrieval.

**Implicación KingsCode:** no gastar los primeros ciclos en fine-tuning del decoder. Primero maximizar `Recall@k`, `MRR`, soporte de cita y recuperación de la norma correcta.

### B. En derecho conviene recuperar fragmentos pequeños y muy relevantes

**LegalBench-RAG (Pipitone & Alami, 2024)** argumenta a favor de fragmentos mínimos y muy relevantes, en vez de documentos enteros o chunks largos e imprecisos. Menos contexto irrelevante reduce latencia, olvido y alucinación, y facilita citar.

**Implicación KingsCode:** artículo o unidad normativa coherente como chunk preferido; no mandar grandes páginas completas al decoder por defecto.

### C. El chunking no debe ser “one size fits all”

**Legal Chunking (Ferraris et al., 2024)** muestra que la segmentación afecta fuertemente la recuperación legal y que las técnicas genéricas no producen relevancia alta de manera consistente.

**Adaptive Chunking (de Moura Júnior et al., 2026)** mejora el desempeño RAG sin cambiar modelos ni prompts usando chunking adaptado al documento y métricas de integridad/coherencia. Reporta 72% de answer correctness frente a 62–64% en sus baselines.

**Implicación KingsCode:** usar un splitter jurídico estructural, con reglas distintas para códigos/leyes, sentencias, decretos y documentos no estructurados. Preservar referencias, encabezados y jerarquía.

### D. Sparse + dense + reranking es una combinación recurrente en sistemas fuertes

**HyPA-RAG (Kalra et al., 2024)** usa recuperación híbrida y adaptación por complejidad de consulta para Legal/Policy RAG.

**Caraman et al. (SemEval 2026)** usa un pipeline de tres etapas: query rewriting, BM25+dense fusion mediante Reciprocal Rank Fusion y cross-encoder reranking; supera el baseline oficial en 10.7% nDCG@5. El trabajo también reporta que estrategias más complejas de expansión multi-query pueden degradar.

**Grounded in Law (Figueiredo et al., 2026)**, desplegado en portugués jurídico, combina lexical+dense+cross-encoder reranking y una auditoría de referencias.

**Qwen Goes Brrr (Bazdyrev et al., 2026)** muestra en una competencia de QA documental que el reranking llevó Recall@1 de 0.6957 a 0.7935 y el uso de los dos mejores pasajes rerankeados elevó accuracy de 0.9348 a 0.9674 en su split retenido.

**Implicación KingsCode:** baseline recomendado:

`BM25 + Qwen3-Embedding -> RRF -> Qwen3-Reranker -> top 6-8`.

No asumir que más pasos siempre ganan; todo módulo adicional debe justificar su latencia con ablation.

### E. Preservar estructura y orden puede ser más valioso que añadir complejidad

**Stronger Baselines for RAG (Laitenberger et al., 2025)** encuentra que una estrategia simple que preserva orden y estructura documental puede igualar o superar pipelines multietapa más complejos bajo presupuestos de contexto comparables.

**RDR2 (Xu et al., 2025)** refuerza la utilidad de incorporar estructura documental explícita en RAG.

**Implicación KingsCode:** después del reranking, no destruir la jerarquía legal. Mantener `doc_id`, norma, artículo, parágrafo/inciso y posición; para evidencia del mismo documento, considerar ordenar por estructura original antes de armar el prompt.

### F. En español jurídico, terminología controlada y sinónimos pueden mejorar retrieval

**Terminology Enhanced RAG for Spanish Legal Corpora (Martín Chozas et al., 2025)** reporta mejoras al combinar enfoques neuronales con terminología controlada y expansión por sinónimos.

**Implicación KingsCode:** agregar un módulo ligero de normalización/expansión jurídica controlada, no una expansión libre generativa. Ejemplos: abreviaturas legales, nombres canónicos de códigos, variantes de “acción de tutela”, “CGP”, “Código General del Proceso”, etc.

### G. Grafo jurídico desde Corpus v0, pero expansión selectiva

**Retrieval-Augmented Generation and Knowledge Graphs in Portuguese-Language Legal Documents (Oliveira et al., 2026)** modela artículos, párrafos e ítems como grafo y reporta beneficios de retrieval estructural.

**MiniRAG (Fan et al., 2026)** muestra que estructuras de grafo pueden compensar limitaciones de SLMs. La revisión posterior del equipo añadió además evidencia de enfoques legales jerárquicos y de graph/tag retrieval eficiente.

**Implicación KingsCode revisada en v0.4/v0.5:** el corpus debe nacer con jerarquía y relaciones del grafo desde la ingesta. Sin embargo, el grafo no se recorre obligatoriamente para cada consulta: BM25+dense+RRF es el fast path y `graph_router` activa expansión selectiva cuando hay remisiones, temporalidad, modificación/derogación/reglamentación, jerarquía u otra necesidad relacional. La decisión se valida con Graph OFF vs AUTO.

### H. La auditoría de citas es un componente de producción, no un adorno

**Grounded in Law (Figueiredo et al., 2026)** valida referencias contra fuentes autoritativas y reporta que su verificación de fidelidad corrigió 6.5% de las respuestas revisadas antes de entregarlas.

**ClaimRAG-LAW (2026)** insiste en evaluar retrieval, generación y claims por separado porque Legal RAG sigue alucinando aun estando grounded.

**Implicación KingsCode:** añadir un `citation_guard` determinista que:
- extraiga referencias legales producidas;
- normalice nombre de norma/artículo;
- compruebe que cada cita aparece en `pasajes_recuperados`;
- suprima o fuerce abstención cuando el soporte sea insuficiente.

### I. Fine-tuning: primero retrieval; el decoder es la última palanca

**Fine Tuning vs RAG for Less Popular Knowledge (Soudani et al., 2024)** encuentra que RAG supera ampliamente a fine-tuning en conocimiento factual poco frecuente.

**Lawton et al. (2025)** muestra que varias estrategias de fine-tuning RAG obtienen mejoras parecidas con costes distintos, y que la estrategia depende de tener labels de contexto.

**Nguyen et al. (2024)** encuentra en FinanceBench que el fine-tuning del embedding aportó más ganancia relativa que el fine-tuning del LLM.

**LegalDrill (Li et al., 2026)** demuestra que SFT + DPO sobre trayectorias de razonamiento legales cuidadosamente sintetizadas puede mejorar SLMs, pero requiere un proceso de datos y teacher más complejo.

**Implicación KingsCode:**
1. sin decoder fine-tuning inicialmente;
2. si `Recall@10` es insuficiente, ajustar retrieval/reranker;
3. si retrieval es alto y generation bajo, entonces probar QLoRA/SFT del decoder;
4. no usar las 50 preguntas como un simple dataset de memorización.

## 3. Cambio importante en candidatos de decoder

La investigación añadió un candidato que no estaba en v0.2:

### `SINAI/ALIA-es-legal-administrative-7B-Instruct`

Modelo 7B, Apache-2.0, especializado en español jurídico/administrativo, derivado de Salamandra-7B mediante continual pre-training en corpus legal-administrativo e instruction tuning. No es colombiano y puede traer priors del derecho español, así que **no se adopta sin benchmark**, pero merece estar en el bakeoff.

Orden de prueba recomendado, no de “verdad absoluta”:
1. Qwen3-8B — baseline principal generalista fuerte.
2. ALIA-es-legal-administrative-7B-Instruct — candidato especializado en español jurídico.
3. Salamandra-7b-fc-2607 — candidato hispanohablante general/instruction.
4. Llama-3.1-8B-Instruct — control adicional si hay tiempo.

## 4. Arquitectura v0.3 guiada por literatura

```text
PREGUNTA
   |
   +--> normalización jurídica / expansión controlada
   |
   +------------------------------+
   |                              |
  BM25                      dense retriever
                             Qwen3-Embedding
   |                              |
   +------------- RRF ------------+
                  |
               top 30
                  |
            cross-encoder
           Qwen3-Reranker
                  |
               top 6-8
                  |
     estructura + orden documental
                  |
             DECODER <=8B
                  |
        JSON / respuesta grounded
                  |
          citation_guard
          /            \
       soporte        sin soporte
         |               |
      entregar       corregir / abstener
```

## 5. Experimentos obligatorios antes de sofisticar

### Retrieval
- BM25 solo
- dense solo
- BM25+dense con RRF
- híbrido + reranker
- híbrido + reranker + expansión jurídica controlada
- dos estrategias de chunking: artículo-estructural vs adaptativo

Métricas:
- Recall@1/3/5/10
- MRR
- nDCG@10 si es posible
- % de `legal_basis` encontrado en top-10
- Document-Level Retrieval Mismatch

### Generation
Con retrieval congelado:
- Qwen3-8B
- ALIA Legal 7B
- Salamandra 7B
- Llama 8B (opcional)

Métricas:
- score oficial
- exactitud cerradas
- RAGAS/answer correctness
- cita respaldada
- abstención
- JSON válido
- segundos/pregunta
- VRAM pico

## 6. Fine-tuning decision tree

```text
¿Recall@10 bajo?
  sí -> NO tocar decoder
        mejorar chunking / corpus / retriever / reranker

¿Recall@10 alto y respuesta mala?
  sí -> prompt + constrained output
        luego evaluar QLoRA/SFT decoder

¿Reranker falla en hard negatives?
  sí -> fine-tuning del reranker con pares positivos/hard negatives

¿Todo funciona y el score es competitivo?
  sí -> no entrenar por entrenar; congelar baseline reproducible
```

## 7. Referencias prioritarias

1. Butler, A.-R. & Butler, U. (2026). **Legal RAG Bench: an end-to-end benchmark for legal RAG.** arXiv:2603.01710.
2. Pipitone, N. & Alami, G. H. (2024). **LegalBench-RAG: A Benchmark for Retrieval-Augmented Generation in the Legal Domain.** arXiv:2408.10343.
3. Zheng, L. et al. (2025). **A Reasoning-Focused Legal Retrieval Benchmark.** arXiv:2505.03970.
4. Kalra, R. et al. (2024). **HyPA-RAG: A Hybrid Parameter Adaptive RAG System for AI Legal and Policy Applications.** ACL CustomNLP4U. DOI:10.18653/v1/2024.customnlp4u-1.18.
5. Reuter, M. et al. (2025). **Towards Reliable Retrieval in RAG Systems for Large Legal Datasets.** NLLP 2025.
6. Ferraris, A. F. et al. (2024). **Legal Chunking: Evaluating Methods for Effective Legal Text Retrieval.** JURIX 2024. DOI:10.3233/FAIA241255.
7. de Moura Júnior, P. R. et al. (2026). **Adaptive Chunking: Optimizing Chunking-Method Selection for RAG.** LREC 2026. DOI:10.63317/3n8eu2phsvmc.
8. Figueiredo, A. et al. (2026). **Grounded in Law: A Multi-Stage Anti-Hallucination Pipeline for Legal RAG Systems in Brazilian Portuguese.** PROPOR 2026.
9. Martín Chozas, P. et al. (2025). **Terminology Enhanced Retrieval Augmented Generation for Spanish Legal Corpora.** LDK 2025.
10. Bazdyrev, A. et al. (2026). **Qwen Goes Brrr: Off-the-Shelf RAG for Ukrainian Multi-Domain Document Understanding.** UNLP 2026.
11. Lawton, N. G. et al. (2025). **A Comparison of Independent and Joint Fine-tuning Strategies for RAG.** Findings EMNLP 2025. DOI:10.18653/v1/2025.findings-emnlp.1247.
12. Li, T. et al. (2026). **LegalDrill: Diagnosis-Driven Synthesis for Legal Reasoning in Small Language Models.** ACL 2026. DOI:10.18653/v1/2026.acl-industry.120.
13. Zhang, Y. et al. (2025). **Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models.** arXiv:2506.05176.
14. Oliveira, V. T. et al. (2026). **Retrieval-Augmented Generation and Knowledge Graphs in Portuguese-Language Legal Documents.** PROPOR 2026.
15. Fan, T. et al. (2026). **MiniRAG: A Lightweight RAG system with Small Language Models.** ACL 2026. DOI:10.18653/v1/2026.acl-long.1721.
16. Laitenberger, A. et al. (2025). **Stronger Baselines for Retrieval-Augmented Generation.** EMNLP 2025.
17. SINAI Research Group (2026). **ALIA Spanish Legal and Administrative 7B Instruct Model.** Hugging Face model card.

## 8. Regla de lectura de esta revisión

Esta revisión **no demuestra que una combinación concreta vaya a ganar la Hackathon**. Los papers usan dominios, idiomas, bancos y LLMs diferentes. Se usa como evidencia para priorizar experimentos. La decisión final siempre se toma con ablations sobre las 50 preguntas oficiales y el evaluador del reto.
