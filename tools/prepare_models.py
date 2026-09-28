"""List, download or verify exact locked snapshots. Never loads model weights."""
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT, read_json
from kingscode.model_assets import DECODERS, RETRIEVAL, prepare_snapshot, resolve_model, verify_snapshot


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--list", action="store_true")
    action.add_argument("--verify", nargs="?", const="all", metavar="MODEL")
    action.add_argument("--download", metavar="MODEL")
    action.add_argument("--download-retrieval", action="store_true")
    action.add_argument("--download-decoders", action="store_true")
    parser.add_argument("--include-optional", action="store_true")
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "models")
    args = parser.parse_args(argv)
    config = read_json(ROOT / "config/decoder_bakeoff.json")
    decoders = [v["repo_id"] for v in config["candidates"].values() if v["enabled"] or args.include_optional]
    if args.list:
        print(json.dumps([resolve_model(n) for n in RETRIEVAL + DECODERS], ensure_ascii=False, indent=2))
        return 0
    names = ([args.download] if args.download else list(RETRIEVAL) if args.download_retrieval else decoders
             if args.download_decoders else list(RETRIEVAL) + decoders if args.verify == "all" else [args.verify])
    results = []
    for name in names:
        try:
            entry = resolve_model(name)
            result = verify_snapshot(entry, args.cache_dir) if args.verify else prepare_snapshot(entry, args.cache_dir)
            results.append({"status": "verified", **result})
        except Exception as exc:
            # Do not print Hub request objects, headers or authentication tokens.
            results.append({"model": name, "status": "failed", "error_type": type(exc).__name__,
                            "action": "Check pinned revision, local integrity and gated-model access; no substitution performed."})
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return int(any(r["status"] == "failed" for r in results))


if __name__ == "__main__":
    raise SystemExit(main())
