import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.benchmark_source_intake import INTAKE_RELATIVE, verify_pdf


class BenchmarkSourceIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "benchmarks/kingscode_ir_v2").mkdir(parents=True)
        (self.root / INTAKE_RELATIVE).mkdir(parents=True)
        self.pdf = self.root / INTAKE_RELATIVE / "candidate.pdf"
        self.pdf.write_bytes(b"%PDF-1.7\nfixture bytes\n")
        self.sha256 = hashlib.sha256(self.pdf.read_bytes()).hexdigest()
        self.source_rows = [{
            "source_id": "ICFES-GESTION-CONFLICTO-2026",
            "official_url": "https://www.icfes.gov.co/wp-content/uploads/example.pdf",
        }, {
            "source_id": "ICFES-COMUNICACION-JURIDICA-2026",
            "official_url": "https://www.icfes.gov.co/wp-content/uploads/current.pdf",
        }, {
            "source_id": "ICFES-GESTION-CONFLICTO-2018-EXTERNADO",
            "issuer": "ICFES",
            "canonical_year": 2018,
            "canonical_source_status": "OFFICIAL_ICFES_LISTING_VERIFIED",
            "official_listing_url": "https://www.icfes.gov.co/publicaciones-icfes/guias-de-orientacion/2018-2/",
            "retrieval_host": "Universidad Externado de Colombia",
            "retrieval_allowed_hostname": "www.uexternado.edu.co",
            "retrieval_url": "https://www.uexternado.edu.co/wp-content/uploads/2021/08/Cuadernillo-Gestion-del-conflicto-Saber-Pro-2021.pdf",
            "retrieval_status": "INSTITUTIONAL_MIRROR_BYTES_BLOCKED_HTTP_403",
            "identity_verification": "PENDING_LOCAL_DOCUMENT_METADATA_AND_BYTES",
        }]
        self.reader = patch("tools.benchmark_source_intake.read_jsonl", return_value=self.source_rows)
        self.reader.start()

    def tearDown(self):
        self.reader.stop()
        self.temp.cleanup()

    def test_hash_verified_source_is_ready_without_emitting_question_text(self):
        result = verify_pdf("ICFES-GESTION-CONFLICTO-2026", self.pdf, self.sha256, root=self.root)
        self.assertEqual(result["status"], "HASH_VERIFIED_READY_FOR_LOCAL_EXTRACTION")
        self.assertEqual(result["sha256"], self.sha256)
        self.assertFalse(result["question_text_emitted"])
        self.assertIn("authenticity", result["hash_scope"])

    def test_mirror_source_preserves_publisher_year_and_retrieval_host_separately(self):
        result = verify_pdf("ICFES-GESTION-CONFLICTO-2018-EXTERNADO", self.pdf, self.sha256, root=self.root)
        self.assertEqual(result["issuer"], "ICFES")
        self.assertEqual(result["canonical_year"], 2018)
        self.assertEqual(result["canonical_source_status"], "OFFICIAL_ICFES_LISTING_VERIFIED")
        self.assertEqual(result["retrieval_host"], "Universidad Externado de Colombia")
        self.assertIn("uexternado.edu.co", result["retrieval_url"])
        self.assertEqual(result["retrieval_status"], "INSTITUTIONAL_MIRROR_BYTES_BLOCKED_HTTP_403")
        self.assertEqual(result["identity_verification"], "PENDING_LOCAL_DOCUMENT_METADATA_AND_BYTES")

    def test_mirror_source_rejects_unlisted_retrieval_host(self):
        self.source_rows[2]["retrieval_url"] = "https://mirror.example/booklet.pdf"
        with self.assertRaisesRegex(ValueError, "allowlist"):
            verify_pdf("ICFES-GESTION-CONFLICTO-2018-EXTERNADO", self.pdf, self.sha256, root=self.root)

    def test_rejects_mismatched_hash(self):
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            verify_pdf("ICFES-GESTION-CONFLICTO-2026", self.pdf, "0" * 64, root=self.root)

    def test_rejects_input_outside_ignored_intake_directory(self):
        outside = self.root / "outside.pdf"
        outside.write_bytes(self.pdf.read_bytes())
        with self.assertRaisesRegex(ValueError, "inside tmp/official-source-intake"):
            verify_pdf("ICFES-GESTION-CONFLICTO-2026", outside, self.sha256, root=self.root)

    def test_rejects_non_pdf_bytes(self):
        self.pdf.write_bytes(b"not a PDF")
        with self.assertRaisesRegex(ValueError, "PDF header"):
            verify_pdf("ICFES-GESTION-CONFLICTO-2026", self.pdf, hashlib.sha256(self.pdf.read_bytes()).hexdigest(), root=self.root)

    def test_rejects_unknown_source_or_non_official_domain(self):
        with self.assertRaisesRegex(ValueError, "not enabled"):
            verify_pdf("CSJ-SIRNA-GUIDE-2026", self.pdf, self.sha256, root=self.root)
        current = verify_pdf("ICFES-COMUNICACION-JURIDICA-2026", self.pdf, self.sha256, root=self.root)
        self.assertEqual(current["official_url"], self.source_rows[1]["official_url"])
        self.source_rows[0]["official_url"] = "https://mirror.example/test.pdf"
        with self.assertRaisesRegex(ValueError, "official ICFES domain"):
            verify_pdf("ICFES-GESTION-CONFLICTO-2026", self.pdf, self.sha256, root=self.root)


if __name__ == "__main__":
    unittest.main()
