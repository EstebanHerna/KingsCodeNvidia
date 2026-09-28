"""Pin/download only the two approved open retrieval models (no inference API)."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT, read_json, write_json
from kingscode.neural import ALLOWED


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--download", action="store_true")
    args = p.parse_args()
    from huggingface_hub import HfApi, snapshot_download
    path = ROOT / "config/models.lock.json"
    lock = read_json(path) if path.exists() else {}
    for name in sorted(ALLOWED):
        if name not in lock:
            info = HfApi().model_info(name)
            lock[name] = {"revision": info.sha, "repo_id": name, "model_card": f"https://huggingface.co/{name}",
                          "license": "apache-2.0"}
        if args.download:
            snapshot_download(name, revision=lock[name]["revision"], cache_dir=str(ROOT / "models"),
                              allow_patterns=["*.json", "*.safetensors", "*.txt", "*.model", "README.md"])
    write_json(path, lock)
    print("Pinned revisions saved to config/models.lock.json; weights " + ("downloaded" if args.download else "not requested"))


if __name__ == "__main__":
    main()
