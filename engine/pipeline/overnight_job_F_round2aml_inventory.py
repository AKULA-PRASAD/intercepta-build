#!/usr/bin/env python
"""
INTERCEPTA Layer 1 Job F: round2_aml/ Inventory
Read-only inventory of round2_aml/ folder.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

ROUND2 = Path.home() / "INTERCEPTA" / "round2_aml"
REPORT = Path.home() / "Downloads" / "INTERCEPTA_overnight_2026-05-09" / "reports" / "round2_aml_inventory.json"


def main():
    print("=" * 70)
    print("Job F: round2_aml/ Inventory")
    print("Started:", datetime.now(timezone.utc).isoformat())
    print("=" * 70)
    
    if not ROUND2.exists():
        print("FOLDER NOT FOUND:", ROUND2)
        return
    
    total_size = 0
    total_files = 0
    by_extension = defaultdict(lambda: {"count": 0, "size": 0})
    by_subfolder = defaultdict(lambda: {"count": 0, "size": 0})
    largest_files = []
    
    for f in ROUND2.rglob("*"):
        if f.is_file():
            try:
                size = f.stat().st_size
                total_size += size
                total_files += 1
                
                ext = f.suffix.lower() or "no_ext"
                by_extension[ext]["count"] += 1
                by_extension[ext]["size"] += size
                
                relative = f.relative_to(ROUND2)
                if len(relative.parts) > 1:
                    sub = relative.parts[0]
                    by_subfolder[sub]["count"] += 1
                    by_subfolder[sub]["size"] += size
                else:
                    by_subfolder["_root"]["count"] += 1
                    by_subfolder["_root"]["size"] += size
                
                largest_files.append((str(relative), size))
            except OSError:
                pass
    
    largest_files.sort(key=lambda x: x[1], reverse=True)
    largest_files = largest_files[:20]
    
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "folder": str(ROUND2),
        "total_files": total_files,
        "total_size_bytes": total_size,
        "total_size_gb": round(total_size / 1e9, 3),
        "by_extension": dict(sorted(by_extension.items(), key=lambda x: -x[1]["size"])),
        "by_subfolder": dict(sorted(by_subfolder.items(), key=lambda x: -x[1]["size"])),
        "largest_20_files": [{"path": p, "size_bytes": s, "size_mb": round(s / 1e6, 1)} for p, s in largest_files],
    }
    
    data_extensions = [".h5ad", ".h5", ".pkl", ".rds", ".csv.gz", ".tsv.gz", ".loom"]
    likely_data = sum(report["by_extension"].get(ext, {"size": 0})["size"] for ext in data_extensions)
    code_extensions = [".py", ".R", ".sh", ".ipynb", ".md", ".txt", ".yaml", ".yml"]
    likely_code = sum(report["by_extension"].get(ext, {"size": 0})["size"] for ext in code_extensions)
    
    report["categorized"] = {
        "likely_data_size_gb": round(likely_data / 1e9, 3),
        "likely_code_size_gb": round(likely_code / 1e9, 3),
        "should_move_to_data_dir": likely_data > 100e6,
        "recommendation": "move large data files to data/ and add to .gitignore" if likely_data > 100e6 else "keep in place",
    }
    
    print()
    print("Total files:", total_files)
    print("Total size:", report["total_size_gb"], "GB")
    print()
    print("By extension (top 10):")
    for ext, info in list(report["by_extension"].items())[:10]:
        size_mb = info["size"] / 1e6
        print("  {:10s}: {:5d} files, {:8.1f} MB".format(ext, info["count"], size_mb))
    print()
    print("By subfolder (top 10):")
    for sub, info in list(report["by_subfolder"].items())[:10]:
        size_mb = info["size"] / 1e6
        print("  {:25s}: {:5d} files, {:8.1f} MB".format(sub, info["count"], size_mb))
    print()
    print("Top 5 largest files:")
    for p, s in largest_files[:5]:
        print("  {:6.1f} MB  {}".format(s / 1e6, p))
    print()
    print("CATEGORIZED:")
    print("  Likely data files:", report["categorized"]["likely_data_size_gb"], "GB")
    print("  Likely code files:", report["categorized"]["likely_code_size_gb"], "GB")
    print("  Recommendation:", report["categorized"]["recommendation"])
    
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print()
    print("Report:", REPORT)


if __name__ == "__main__":
    main()
