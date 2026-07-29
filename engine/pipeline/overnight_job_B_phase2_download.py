#!/usr/bin/env python
"""
INTERCEPTA Layer 1 Job B Phase 2: Foundation Model Downloads
============================================================
Downloads scFoundation, scGPT, UCE model weights from HuggingFace
Per Job G result: requires intercepta-fm env with transformers + huggingface_hub.
Per scDrugMap benchmark: these 3 models are SOTA for single-cell drug response.
"""
import os
import sys
import json
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

MODELS_DIR = Path("/scratch/akula.pra/INTERCEPTA/models")
RESULTS = Path("/scratch/akula.pra/INTERCEPTA/results/foundation_model_downloads.json")

# Models to download.
# These HuggingFace repo IDs are based on scDrugMap paper references and public availability.
# Format: (model_name, hf_repo_id, allow_patterns)
MODELS = [
    ("scFoundation", "biomap-research/scFoundation", None),
    ("scGPT", "wanglab/scGPT", None),
    ("Geneformer", "ctheodoris/Geneformer", None),
]


def download_one(name, repo_id, allow_patterns):
    print("=" * 70)
    print(f"Downloading: {name} ({repo_id})")
    print("=" * 70)
    
    target_dir = MODELS_DIR / name
    target_dir.mkdir(parents=True, exist_ok=True)
    
    result = {
        "name": name,
        "repo_id": repo_id,
        "target_dir": str(target_dir),
        "started": datetime.now(timezone.utc).isoformat(),
    }
    
    try:
        from huggingface_hub import snapshot_download
        
        t0 = time.time()
        path = snapshot_download(
            repo_id=repo_id,
            local_dir=str(target_dir),
            allow_patterns=allow_patterns,
            local_dir_use_symlinks=False,
            resume_download=True,
        )
        elapsed = time.time() - t0
        
        # Tally downloaded size
        total_size = 0
        n_files = 0
        for f in target_dir.rglob("*"):
            if f.is_file():
                total_size += f.stat().st_size
                n_files += 1
        
        result["status"] = "SUCCESS"
        result["elapsed_sec"] = round(elapsed, 1)
        result["total_size_bytes"] = total_size
        result["total_size_gb"] = round(total_size / 1e9, 3)
        result["n_files"] = n_files
        result["downloaded_path"] = str(path)
        
        print(f"\n  SUCCESS: {n_files} files, {result['total_size_gb']} GB in {elapsed:.0f}s")
        
    except Exception as e:
        result["status"] = "FAILED"
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()
        print(f"\n  FAILED: {e}")
        print(traceback.format_exc())
    
    result["completed"] = datetime.now(timezone.utc).isoformat()
    return result


def main():
    print("=" * 70)
    print("INTERCEPTA Layer 1 Job B Phase 2: Foundation Model Downloads")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print(f"Target: {MODELS_DIR}")
    print(f"Models to download: {len(MODELS)}")
    print("=" * 70)
    
    # Verify deps
    try:
        from huggingface_hub import snapshot_download
        import huggingface_hub
        print(f"\nhuggingface_hub: {huggingface_hub.__version__}")
    except ImportError as e:
        print(f"FATAL: huggingface_hub not installed: {e}")
        print("Phase 1 env setup must run first.")
        sys.exit(1)
    
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Download each, save progress incrementally
    results = []
    for name, repo, patterns in MODELS:
        result = download_one(name, repo, patterns)
        results.append(result)
        
        # Save progress after each (so partial progress survives crashes)
        report = {
            "started": datetime.now(timezone.utc).isoformat(),
            "n_total": len(MODELS),
            "n_completed": len(results),
            "downloads": results,
        }
        RESULTS.parent.mkdir(parents=True, exist_ok=True)
        with open(RESULTS, "w") as f:
            json.dump(report, f, indent=2, default=str)
    
    # Summary
    print("\n" + "=" * 70)
    print("DOWNLOAD SUMMARY")
    print("=" * 70)
    succeeded = [r for r in results if r["status"] == "SUCCESS"]
    failed = [r for r in results if r["status"] == "FAILED"]
    print(f"  Succeeded: {len(succeeded)}/{len(MODELS)}")
    for r in succeeded:
        print(f"    {r['name']:15s}: {r['total_size_gb']} GB, {r['elapsed_sec']}s")
    if failed:
        print(f"  Failed: {len(failed)}")
        for r in failed:
            print(f"    {r['name']:15s}: {r['error'][:100]}")
    
    # Final report
    final = {
        "started": datetime.now(timezone.utc).isoformat(),
        "completed": datetime.now(timezone.utc).isoformat(),
        "n_total": len(MODELS),
        "n_succeeded": len(succeeded),
        "n_failed": len(failed),
        "downloads": results,
    }
    with open(RESULTS, "w") as f:
        json.dump(final, f, indent=2, default=str)
    
    print(f"\nReport: {RESULTS}")
    print(f"Models: {MODELS_DIR}")


if __name__ == "__main__":
    main()
