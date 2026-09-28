"""Run Gate 1B end to end on sample_50 without network, GPU or a real decoder."""
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT
from kingscode.reasoning.experiments import run_experiment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["smoke"])
    parser.add_argument("--config", type=Path, default=ROOT / "config/reasoning.json")
    parser.add_argument("--output-root", type=Path, default=ROOT / "reports/member_b")
    args = parser.parse_args()
    result = run_experiment(config_path=args.config, output_root=args.output_root)
    print(json.dumps({"status": result["status"], "fingerprint": result["fingerprint"], "paths": result["paths"],
                      "submission_sha256": result["submission_sha256"], "metrics": result["metrics"],
                      "official_total": result["official_evaluation"]["total_automatico"],
                      "neural_modules_loaded": result["neural_modules_loaded"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
