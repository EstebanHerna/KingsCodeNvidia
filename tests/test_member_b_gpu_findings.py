"""Regressions from the first real Qwen3-8B run on the RTX 4090 (2026-10-01)."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from kingscode.common import ROOT, read_json
from kingscode.generation.prompts import length_warnings, parse_response, parse_response_v3, sentence_count
from kingscode.reasoning import Pipeline, Question
from kingscode.reasoning.official import official_bodies

FIXTURES = read_json(ROOT / "tests/fixtures/member_b_official_passages.json")
# Literal raw_response of gpu_smoke.py --model qwen3-8b (BF16, temperature 0) on the 4090.
QWEN_4090_RAW = (
    "{\"abstencion\":false,\"respuesta\":\"El objeto del artículo 1 de la Ley 1010 de 2006 es definir, prevenir, corregir y "
    "sancionar las diversas formas de agresión, maltrato, vejámenes, trato desconsiderado y ofensivo, así como todo ultraje "
    "a la dignidad humana que se ejercen sobre quienes realizan sus actividades económicas en el contexto de una relación "
    "laboral privada o pública. Este artículo protege bienes jurídicos como el trabajo en condiciones dignas y justas, la "
    "libertad, la intimidad, la honra y la salud mental de los trabajadores, empleados, la armonía entre quienes comparten "
    "un mismo ambiente laboral y el buen ambiente en la empresa.\",\"palabras_clave\":[\"Ley 1010 de 2006\",\"artículo 1\","
    "\"objeto de la ley\",\"bienes jurídicos\"],\"referencia_legal\":\"ley_1010_de_2006:00000:3a5f84542db4\","
    "\"pasajes_usados\":[\"ley_1010_de_2006:00000:3a5f84542db4\"]}")
Q = Question(1,"¿Cuál es el objeto del artículo 1 de la Ley 1010 de 2006?", "semi_open")


class ReplayDecoder:
    """Returns the recorded 4090 output through the real v3 parser, like HFDecoder."""
    name, version = "qwen3-8b-replay", "b968826"

    def __init__(self):
        self.last_usage = {}

    def generate(self, question, passages, prompt, generation):
        row, meta = parse_response_v3(QWEN_4090_RAW, question, passages)
        self.last_usage = {"model": "qwen3-8b", "prompt_version": "grounded-formats-v3", **meta}
        return row


class QwenSmokeRegressionTests(unittest.TestCase):
    def test_two_sentence_grounded_answer_is_kept_with_a_warning(self):
        row, meta = parse_response_v3(QWEN_4090_RAW, Q, [deepcopy(FIXTURES[1])])
        self.assertFalse(row["abstencion"])
        self.assertEqual(meta["format_warnings"], ["semi_open_sentences_2_outside_3_5"])
        self.assertEqual(meta["attribution"]["status"], "explicit")

    def test_legacy_v1_v2_contract_still_rejects_length(self):
        value = json.loads(QWEN_4090_RAW)
        value.pop("pasajes_usados")
        with self.assertRaises(ValueError):
            parse_response(json.dumps(value, ensure_ascii=False), Q, [deepcopy(FIXTURES[1])])

    def test_pipeline_replaces_passage_id_with_canonical_citation(self):
        pipeline = Pipeline(lambda *a, **k: [deepcopy(FIXTURES[1]), deepcopy(FIXTURES[0])], decoder=ReplayDecoder(),
                            graph_policy="off", retrieval_mode="base")
        row, trace = pipeline.run(Q)
        self.assertFalse(row["abstencion"])
        self.assertNotIn(":", row["referencia_legal"])
        self.assertIn(("ley", "1010", "2006"), {tuple(b) for b in official_bodies(row["referencia_legal"])})
        self.assertEqual(trace["diagnostics"]["format_warnings"], ["semi_open_sentences_2_outside_3_5"])

    def test_deterministic_decoder_failure_is_not_retried(self):
        from kingscode.generation.hf_decoder import DecoderFailure
        from kingscode.reasoning.batch import BatchRunner
        calls = []

        class Failing:
            def run(self, question):
                calls.append(question.id)
                raise DecoderFailure("INVALID_MODEL_OUTPUT", {})

        with tempfile.TemporaryDirectory() as tmp:
            report = BatchRunner(Failing(), Path(tmp), retries=2).run([Q])
        self.assertEqual(calls, [Q.id])
        self.assertEqual(report["counts"]["fallback"], 1)

    def test_long_evidence_drops_lowest_ranked_passages_from_prompt_only(self):
        from unittest.mock import patch
        from kingscode.generation.hf_decoder import ATTN_IMPLEMENTATION, HFDecoder
        from kingscode.reasoning.decoder import GENERATION_CONFIG, PromptSpec
        from test_gpu_preparation import FakeInputs, FakeTokenizer, fake_torch, fake_transformers

        class LengthTokenizer(FakeTokenizer):
            """3000 tokens per passage in the prompt: 8 passages never fit 8192."""
            def __call__(self, text, **kwargs):
                user = json.loads(json.loads(text[0])[1]["content"])
                return FakeInputs(500 + 3000 * len(user["evidencia"]))

        evidence = [dict(deepcopy(FIXTURES[i % 5]), passage_id=f"p{i}") for i in range(8)]
        transformers, model = fake_transformers(LengthTokenizer())
        decoder = HFDecoder("qwen3-8b", torch_module=fake_torch(), transformers_module=transformers)
        with patch("kingscode.generation.hf_decoder.verify_snapshot", return_value={}):
            row = decoder.generate(Q, evidence, PromptSpec("semi_open"), dict(GENERATION_CONFIG))
        self.assertEqual(decoder.last_usage["evidence_in_prompt"], 2)        # 500 + 2*3000 + 512 <= 8192
        self.assertEqual(decoder.last_usage["evidence_dropped_for_context"], [f"p{i}" for i in range(2, 8)])
        self.assertEqual(len(row["pasajes_recuperados"]), 8)                  # the official row keeps all
        self.assertEqual(transformers.AutoModelForCausalLM.from_pretrained.call_args.kwargs["attn_implementation"], "sdpa")
        self.assertEqual(ATTN_IMPLEMENTATION, "sdpa")
        model.generate.assert_called_once()

    def test_missing_abstencion_on_complete_answer_is_an_answer(self):
        value = json.loads(QWEN_4090_RAW)
        value.pop("abstencion")
        row, meta = parse_response_v3(json.dumps(value, ensure_ascii=False), Q, [deepcopy(FIXTURES[1])])
        self.assertFalse(row["abstencion"])
        self.assertIn("inferred_abstencion_false_from_complete_answer", meta["field_coercions"])
        value["abstencion"] = "false"
        row, meta = parse_response_v3(json.dumps(value, ensure_ascii=False), Q, [deepcopy(FIXTURES[1])])
        self.assertEqual(meta["field_coercions"][0], "coerced_string:abstencion")

    def test_incomplete_or_reserved_objects_are_still_rejected(self):
        value = json.loads(QWEN_4090_RAW)
        value.pop("abstencion"); value.pop("palabras_clave")       # incomplete: never inferred
        with self.assertRaises(ValueError):
            parse_response_v3(json.dumps(value, ensure_ascii=False), Q, [deepcopy(FIXTURES[1])])
        value = json.loads(QWEN_4090_RAW); value["pasajes_recuperados"] = []
        with self.assertRaises(ValueError):
            parse_response_v3(json.dumps(value, ensure_ascii=False), Q, [deepcopy(FIXTURES[1])])

    def test_multiple_choice_shape_is_normalized_without_new_content(self):
        q = Question(2, "¿Qué regula la Ley 1010 de 2006?", "multiple_choice", {"A": "Acoso laboral", "B": "Pensiones", "C": "Salud"})
        raw = json.dumps({"respuesta_correcta": "A) Acoso laboral", "justificacion": ["Artículo 1 de la Ley 1010 de 2006.", "Define el acoso."],
                          "descarte_opciones": {"A": "correcta", "B)": "No trata pensiones.", "C": 3, "E": "no existe"},
                          "comentario": "extra"}, ensure_ascii=False)
        row, meta = parse_response_v3(raw, q, [deepcopy(FIXTURES[1])])
        self.assertEqual(row["respuesta_correcta"], "A")
        self.assertEqual(row["descarte_opciones"], {"B": "No trata pensiones.", "C": "3"})
        self.assertEqual(row["justificacion"], "Artículo 1 de la Ley 1010 de 2006. Define el acoso.")
        self.assertNotIn("comentario", row)
        self.assertIn("dropped_extra_key:comentario", meta["field_coercions"])

    def test_over_limit_text_is_cut_at_sentence_boundaries(self):
        long = " ".join(f"Oración número {i} sobre la Ley 1010 de 2006." for i in range(1, 9))
        value = json.loads(QWEN_4090_RAW); value["respuesta"] = long
        row, meta = parse_response_v3(json.dumps(value, ensure_ascii=False), Q, [deepcopy(FIXTURES[1])])
        self.assertEqual(sentence_count(row["respuesta"]), 5)
        self.assertTrue(row["respuesta"].endswith("Oración número 5 sobre la Ley 1010 de 2006."))
        self.assertIn("truncated_to_limit:respuesta", meta["field_coercions"])
        self.assertEqual(meta["format_warnings"], [])

    def test_length_warnings_cover_words_and_open_ended(self):
        self.assertEqual(length_warnings({"formato": "semi_open", "respuesta": "Uno. Dos. " + "x " * 160 + "."}),
                         ["semi_open_words_163_over_150"])
        self.assertEqual(length_warnings({"formato": "open_ended", "analisis": "Una. Dos."}),
                         ["open_ended_analysis_sentences_2_outside_5_8"])
        self.assertEqual(length_warnings({"formato": "multiple_choice"}), [])


if __name__ == "__main__":
    unittest.main()
