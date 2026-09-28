"""Diagnose or emit a plan. Never runs pip or installs CUDA/PyTorch."""
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT, read_json, write_json
from kingscode.gpu_environment import diagnose, environment_plan, require_cuda


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--diagnose", action="store_true")
    action.add_argument("--plan", action="store_true")
    action.add_argument("--configure-retrieval", action="store_true", help="Explicitly switch A's config to GPU after a real CUDA check")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/gpu_diagnostic.json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--torch-version")
    parser.add_argument("--cuda-tag")
    args = parser.parse_args(argv)
    if args.diagnose:
        result = diagnose()
    elif args.plan:
        result = environment_plan(read_json(args.report), torch_version=args.torch_version, cuda_tag=args.cuda_tag)
    else:
        import torch
        require_cuda(torch)
        path = ROOT / "config/neural.json"
        config = read_json(path)
        config.update(device="cuda:0", dtype="bfloat16", batch_size=2, local_files_only=True)
        write_json(path, config)
        result = {"status": "configured_not_benchmarked", "config": config,
                  "note": "Existing dense indices with a different config must be rebuilt. No project completion state was changed."}
    if args.output:
        write_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
