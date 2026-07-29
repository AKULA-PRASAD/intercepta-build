#!/usr/bin/env python
"""
INTERCEPTA Layer 1 Overnight Job D: Per-Source-Study Deep Audit
Per charter v1.1: Layer 1 diagnostic for all 33 LuCA source studies.
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

LUCA_DIR = Path("/scratch/akula.pra/INTERCEPTA/data/nsclc/luca_salcher2022/data/12_input_adatas")
OUTPUT = Path("/scratch/akula.pra/INTERCEPTA/results/luca_per_study_deep_audit.json")

KAALCURA_GENES = {
    "prolif": ["MKI67","TOP2A","PCNA","CDK1","CCNB1","AURKA","BUB1","PLK1","MCM2","MCM6","FOXM1","BIRC5","NUSAP1","TPX2","CDC20","CENPF"],
    "emt_pos": ["VIM","CDH2","SNAI1","SNAI2","ZEB1","ZEB2","TWIST1","FN1"],
    "emt_neg": ["CDH1","CLDN1","TJP1"],
    "ddr": ["BRCA1","BRCA2","RAD51","ATM","ATR","CHEK1","CHEK2","PARP1","PARP2","XRCC1","MLH1","MSH2","FANCA","FANCD2","RPA1"],
}
ALL_KAALCURA = sorted(set(g for genes in KAALCURA_GENES.values() for g in genes))

NSCLC_SELECTIVITY = ["EGFR","KRAS","ERBB2","ALK","MET","BRAF","ROS1","RET","NTRK1","NTRK2","NTRK3","ERBB4","PIK3CA","AKT1","MTOR","TP53","RB1","STK11","KEAP1","NFE2L2","CDKN2A","MYC","VEGFA","KDR","FLT4","CD274","PDCD1","FGFR1","FGFR2","FGFR3","SOX2","BCL2","MCL1"]


def audit_one_study(h5ad_path):
    import scanpy as sc
    
    name = h5ad_path.stem
    print("=" * 70)
    print("Auditing: " + name)
    print("=" * 70)
    
    result = {
        "study_name": name,
        "file_path": str(h5ad_path),
        "file_size_bytes": h5ad_path.stat().st_size,
    }
    
    try:
        t0 = time.time()
        adata = sc.read_h5ad(h5ad_path, backed="r")
        result["load_time_sec"] = round(time.time() - t0, 2)
        result["shape"] = list(adata.shape)
        result["n_cells"] = int(adata.n_obs)
        result["n_genes"] = int(adata.n_vars)
        
        gene_set = set(adata.var_names)
        kaalcura_present = [g for g in ALL_KAALCURA if g in gene_set]
        kaalcura_absent = [g for g in ALL_KAALCURA if g not in gene_set]
        nsclc_present = [g for g in NSCLC_SELECTIVITY if g in gene_set]
        nsclc_absent = [g for g in NSCLC_SELECTIVITY if g not in gene_set]
        
        result["kaalcura_coverage"] = {
            "n_total": len(ALL_KAALCURA),
            "n_present": len(kaalcura_present),
            "coverage_pct": round(100.0 * len(kaalcura_present) / len(ALL_KAALCURA), 1),
            "absent_genes": kaalcura_absent,
        }
        result["nsclc_selectivity_coverage"] = {
            "n_total": len(NSCLC_SELECTIVITY),
            "n_present": len(nsclc_present),
            "coverage_pct": round(100.0 * len(nsclc_present) / len(NSCLC_SELECTIVITY), 1),
            "absent_genes": nsclc_absent,
        }
        
        result["kaalcura_by_signature"] = {}
        for sig, genes in KAALCURA_GENES.items():
            present = [g for g in genes if g in gene_set]
            result["kaalcura_by_signature"][sig] = {
                "n_total": len(genes),
                "n_present": len(present),
                "coverage_pct": round(100.0 * len(present) / len(genes), 1),
                "absent": [g for g in genes if g not in gene_set],
            }
        
        result["obs_columns"] = list(adata.obs.columns)
        result["n_obs_columns"] = len(adata.obs.columns)
        
        for key in ["sample", "patient", "donor", "Sample", "Patient", "PatientID"]:
            if key in adata.obs.columns:
                vals = adata.obs[key].astype(str)
                result[key + "_unique"] = int(vals.nunique())
                break
        
        for key in ["cell_type", "celltype", "CellType", "cell_type_coarse", "cell_type_major"]:
            if key in adata.obs.columns:
                vc = adata.obs[key].value_counts().head(10)
                result["cell_type_top10"] = {str(k): int(v) for k, v in vc.items()}
                result["cell_type_column_used"] = key
                break
        
        for key in ["condition", "Condition", "disease", "diagnosis", "tissue", "origin"]:
            if key in adata.obs.columns:
                vc = adata.obs[key].value_counts().head(10)
                result["condition_distribution"] = {str(k): int(v) for k, v in vc.items()}
                result["condition_column_used"] = key
                break
        
        result["var_columns"] = list(adata.var.columns)
        if "highly_variable" in adata.var.columns:
            result["n_hvg"] = int(adata.var["highly_variable"].sum())
        
        result["layers"] = list(adata.layers.keys()) if hasattr(adata, "layers") else []
        result["obsm_keys"] = list(adata.obsm.keys()) if hasattr(adata, "obsm") else []
        
        try:
            X = adata.X
            n_sample_cells = min(100, adata.n_obs)
            n_sample_genes = min(100, adata.n_vars)
            sample = X[:n_sample_cells, :n_sample_genes]
            if hasattr(sample, "toarray"):
                sample = sample.toarray()
            sample = np.array(sample)
            
            result["x_dtype"] = str(sample.dtype)
            result["x_min"] = float(sample.min())
            result["x_max"] = float(sample.max())
            result["x_mean"] = float(sample.mean())
            result["x_is_integer_like"] = bool(np.allclose(sample, np.round(sample)))
            if result["x_is_integer_like"] and result["x_max"] > 100:
                result["x_likely_normalization"] = "raw_counts"
            elif 0 <= result["x_min"] and result["x_max"] < 20:
                result["x_likely_normalization"] = "log1p"
            else:
                result["x_likely_normalization"] = "unknown"
        except Exception as e:
            result["x_inspection_error"] = str(e)
        
        result["status"] = "SUCCESS"
        print("  Cells: {:,}".format(result["n_cells"]))
        print("  Genes: {:,}".format(result["n_genes"]))
        print("  KAALCURA coverage: {}%".format(result["kaalcura_coverage"]["coverage_pct"]))
        print("  NSCLC coverage: {}%".format(result["nsclc_selectivity_coverage"]["coverage_pct"]))
        
    except Exception as e:
        result["status"] = "FAILED"
        result["error"] = str(e)
        print("  FAILED: " + str(e))
    
    return result


def main():
    print("=" * 70)
    print("INTERCEPTA Layer 1 Job D: Per-Source-Study Deep Audit")
    print("Started: " + datetime.now(timezone.utc).isoformat())
    print("Source dir: " + str(LUCA_DIR))
    print("=" * 70)
    
    h5ad_files = sorted(LUCA_DIR.glob("*.h5ad"))
    print("\nFound {} source-study h5ads".format(len(h5ad_files)))
    
    results = []
    for i, f in enumerate(h5ad_files, 1):
        print("\n[{}/{}] {}".format(i, len(h5ad_files), f.name))
        try:
            result = audit_one_study(f)
        except Exception as e:
            result = {"study_name": f.stem, "status": "EXCEPTION", "error": str(e)}
        results.append(result)
        
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        progress = {
            "started": datetime.now(timezone.utc).isoformat(),
            "n_total": len(h5ad_files),
            "n_completed": i,
            "studies": results,
        }
        with open(OUTPUT, "w") as out:
            json.dump(progress, out, indent=2, default=str)
    
    successful = [r for r in results if r.get("status") == "SUCCESS"]
    print("\n" + "=" * 70)
    print("COMPLETED: {}/{} successful audits".format(len(successful), len(results)))
    
    if successful:
        coverages = [r["kaalcura_coverage"]["coverage_pct"] for r in successful]
        print("KAALCURA coverage range: {:.1f}% - {:.1f}%".format(min(coverages), max(coverages)))
        print("KAALCURA coverage mean:  {:.1f}%".format(np.mean(coverages)))
        full_coverage = [r["study_name"] for r in successful if r["kaalcura_coverage"]["coverage_pct"] == 100.0]
        print("Studies with 100% KAALCURA coverage: {}".format(len(full_coverage)))
    
    final = {
        "started": datetime.now(timezone.utc).isoformat(),
        "completed": datetime.now(timezone.utc).isoformat(),
        "n_total": len(h5ad_files),
        "n_successful": len(successful),
        "studies": results,
    }
    with open(OUTPUT, "w") as out:
        json.dump(final, out, indent=2, default=str)
    
    print("\nReport written: " + str(OUTPUT))
    print("Finished: " + datetime.now(timezone.utc).isoformat())


if __name__ == "__main__":
    main()
