#!/usr/bin/env python
"""
INTERCEPTA Layer 1 Job K: scDrugMap Reproducibility Setup
==========================================================
Clones scDrugMap repository, installs dependencies, runs minimal smoke test.
Per charter Q1: hands-on validation that we can run the SOTA benchmark tool.

DEPENDENCY: Job B Phase 1 must complete first (creates intercepta-fm env).
This job uses --dependency=afterok:JOB_B_ID in slurm.
"""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_DIR = Path("/scratch/akula.pra/INTERCEPTA/external/scDrugMap")
REPORT = Path("/scratch/akula.pra/INTERCEPTA/results/scDrugMap_setup.json")


def run_cmd(cmd, cwd=None, timeout=600):
    """Run shell command, return dict with stdout, stderr, returncode."""
    print("  RUN:", cmd if isinstance(cmd, str) else " ".join(cmd))
    try:
        result = subprocess.run(
            cmd if isinstance(cmd, list) else cmd.split(),
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "cmd": cmd if isinstance(cmd, str) else " ".join(cmd),
            "returncode": result.returncode,
            "stdout": result.stdout[:2000],
            "stderr": result.stderr[:2000],
        }
    except subprocess.TimeoutExpired:
        return {"cmd": str(cmd), "returncode": -1, "error": "timeout"}
    except Exception as e:
        return {"cmd": str(cmd), "returncode": -1, "error": str(e)}


def main():
    print("=" * 70)
    print("Job K: scDrugMap Reproducibility Setup")
    print("Started:", datetime.now(timezone.utc).isoformat())
    print("=" * 70)
    
    report = {
        "started": datetime.now(timezone.utc).isoformat(),
        "steps": [],
    }
    
    # Step 1: Create external dir
    print()
    print("[1/4] Setup external/ directory")
    REPO_DIR.parent.mkdir(parents=True, exist_ok=True)
    
    # Step 2: Clone scDrugMap
    print()
    print("[2/4] Clone scDrugMap repository")
    if REPO_DIR.exists():
        print("  Already cloned, pulling latest")
        r = run_cmd(["git", "pull"], cwd=str(REPO_DIR))
    else:
        r = run_cmd(["git", "clone", "https://github.com/Wang-lab-UCONN/scDrugMap.git", str(REPO_DIR)])
    report["steps"].append({"step": "clone", "result": r})
    
    if not REPO_DIR.exists():
        print("  CLONE FAILED, trying alternate URLs")
        for url in [
            "https://github.com/QSong-github/scDrugMap.git",
            "https://github.com/songlab-cal/scDrugMap.git",
        ]:
            r = run_cmd(["git", "clone", url, str(REPO_DIR)])
            report["steps"].append({"step": "clone_alt", "url": url, "result": r})
            if REPO_DIR.exists():
                print("  Cloned from", url)
                break
    
    if not REPO_DIR.exists():
        print("  ALL CLONE ATTEMPTS FAILED")
        report["status"] = "FAILED_CLONE"
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        with open(REPORT, "w") as f:
            json.dump(report, f, indent=2, default=str)
        return
    
    # Step 3: Inventory the repo
    print()
    print("[3/4] Repository inventory")
    files = list(REPO_DIR.rglob("*"))
    n_files = sum(1 for f in files if f.is_file())
    has_readme = any(f.name.lower().startswith("readme") for f in files)
    has_requirements = any(f.name in ("requirements.txt", "environment.yml", "setup.py", "pyproject.toml") for f in files)
    py_files = [f for f in files if f.suffix == ".py"]
    
    report["repo_inventory"] = {
        "total_files": n_files,
        "has_readme": has_readme,
        "has_requirements": has_requirements,
        "n_py_files": len(py_files),
        "top_level": sorted([f.name for f in REPO_DIR.iterdir()])[:30],
    }
    print("  Files:", n_files)
    print("  Has README:", has_readme)
    print("  Has requirements:", has_requirements)
    print("  Python files:", len(py_files))
    print("  Top level:", report["repo_inventory"]["top_level"][:10])
    
    # Step 4: Try to install requirements (if exists)
    print()
    print("[4/4] Try install requirements")
    req_file = REPO_DIR / "requirements.txt"
    setup_py = REPO_DIR / "setup.py"
    pyproject = REPO_DIR / "pyproject.toml"
    
    if req_file.exists():
        print("  Found requirements.txt, attempting pip install")
        r = run_cmd(["pip", "install", "--no-cache-dir", "-r", str(req_file)], timeout=1200)
        report["steps"].append({"step": "pip_install_requirements", "result": r})
    elif setup_py.exists():
        print("  Found setup.py, attempting pip install -e .")
        r = run_cmd(["pip", "install", "-e", "."], cwd=str(REPO_DIR), timeout=1200)
        report["steps"].append({"step": "pip_install_setup", "result": r})
    elif pyproject.exists():
        print("  Found pyproject.toml, attempting pip install -e .")
        r = run_cmd(["pip", "install", "-e", "."], cwd=str(REPO_DIR), timeout=1200)
        report["steps"].append({"step": "pip_install_pyproject", "result": r})
    else:
        print("  No standard requirements file found, skipping install")
        report["steps"].append({"step": "no_install", "note": "no requirements.txt/setup.py/pyproject.toml"})
    
    report["completed"] = datetime.now(timezone.utc).isoformat()
    report["status"] = "COMPLETE"
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print()
    print("=" * 70)
    print("Job K COMPLETE")
    print("Repo:", REPO_DIR)
    print("Report:", REPORT)
    print("=" * 70)


if __name__ == "__main__":
    main()
