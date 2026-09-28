"""Run the prepared smoke on a real CUDA GPU. Stops with CUDA_NOT_AVAILABLE otherwise."""
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="qwen3-8b")
    parser.add_argument("--output-root", type=Path, default=ROOT / "reports/gpu_smoke")
    parser.add_argument("--precision", choices=["bf16", "int8", "int4"], default="bf16")
    parser.add_argument("--oom-record", type=Path)
    args = parser.parse_args(argv)
    from kingscode.generation.gpu_smoke import run_gpu_smoke
    result = run_gpu_smoke(args.model, output_root=args.output_root, precision=args.precision, oom_record=args.oom_record)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(result["status"] != "passed")


if __name__ == "__main__":
    raise SystemExit(main())
