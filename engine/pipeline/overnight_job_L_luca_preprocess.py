#!/usr/bin/env python
"""
INTERCEPTA Layer 1 Job L: LuCA Top-3 Source Study Preprocessing
================================================================
Pre-processes 3 best LuCA source studies for FM hands-on testing tomorrow.
Per Job D results: 28/30 studies have 100% KAALCURA coverage.

Selects 3 studies based on:
- 100% KAALCURA coverage
- Diverse cell counts (small, medium, large)
- Different originating studies (avoid Leader/Merad redundancy)

Conservative scope: load h5ad, verify integrity, save metadata report.
Does NOT do format conversion (each FM has different requirements).
Does NOT modify source data (read-only).

Per charter: Layer 1 diagnostic, NOT Layer 2-4 implementation.
"""
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

LUCA_DIR = Path("/scratch/akula.pra/INTERCEPTA/data/nsclc/luca_salcher2022/data/12_input_adatas")
OUTPUT_DIR = Path("/scratch/akula.pra/INTERCEPTA/results/luca_top3_preprocessed")
REPORT = Path("/scratch/akula.pra/INTERCEPTA/results/luca_top3_preprocessing_report.json")

# Selected based on Job D results (100% coverage):
# - Small/diverse: Travaglini_Krasnow_2020_Lung_SS2 (9,409 cells, SmartSeq2)
# - Medium: Maynard 2020 (21,409 cells, distinctive cohort)
# - Large NSCLC-specific: Kim_Lee_2020_LUAD (208,506 cells, full LUAD cohort, 29,634 genes)
TARGET_STUDIES = [
    "Travaglini_Krasnow_2020_Lung_SS2",
    "maynard2020",
    "Kim_Lee_2020_LUAD",
]


def preprocess_one(study_name):
    print("=" * 70)
    print(f"Preprocessing: {study_name}")
    print("=" * 70)
    
    h5ad_path = LUCA_DIR / f"{study_name}.h5ad"
    if not h5ad_path.exists():
        return {"study_name": study_name, "status": "FILE_NOT_FOUND", "path": str(h5ad_path)}
    
    result = {
        "study_name": study_name,
        "input_path": str(h5ad_path),
        "input_size_bytes": h5ad_path.stat().st_size,
    }
    
    try:
        import scanpy as sc
        import numpy as np
        
        t0 = time.time()
        adata = sc.read_h5ad(h5ad_path, backed="r")
        result["load_time_sec"] = round(time.time() - t0, 2)
        result["shape"] = list(adata.shape)
        result["n_cells"] = int(adata.n_obs)
        result["n_genes"] = int(adata.n_vars)
        result["obs_columns"] = list(adata.obs.columns)
        result["var_columns"] = list(adata.var.columns)
        
        # Sample first 10 obs for inspection
        result["obs_sample_first10"] = {}
        for col in adata.obs.columns[:20]:
            try:
                vals = adata.obs[col].head(10).astype(str).tolist()
                result["obs_sample_first10"][col] = vals
            except Exception:
                pass
        
        # Sample first 20 var (gene) entries
        result["var_sample_first20"] = list(adata.var_names[:20])
        
        # X matrix inspection
        try:
            X = adata.X
            n_sample_cells = min(50, adata.n_obs)
            n_sample_genes = min(50, adata.n_vars)
            sample = X[:n_sample_cells, :n_sample_genes]
            if hasattr(sample, "toarray"):
                sample = sample.toarray()
            sample_arr = np.array(sample)
            
            result["x_inspection"] = {
                "dtype": str(sample_arr.dtype),
                "min": float(sample_arr.min()),
                "max": float(sample_arr.max()),
                "mean": float(sample_arr.mean()),
                "median": float(np.median(sample_arr)),
                "n_zeros": int((sample_arr == 0).sum()),
                "n_total": int(sample_arr.size),
                "sparsity_pct": round(100.0 * (sample_arr == 0).sum() / sample_arr.size, 1),
                "is_integer_like": bool(np.allclose(sample_arr, np.round(sample_arr))),
            }
            
            # Determine likely normalization status
            if result["x_inspection"]["is_integer_like"] and result["x_inspection"]["max"] > 100:
                result["x_inspection"]["likely_normalization"] = "raw_counts"
            elif 0 <= result["x_inspection"]["min"] and result["x_inspection"]["max"] < 20:
                result["x_inspection"]["likely_normalization"] = "log1p_normalized"
            else:
                result["x_inspection"]["likely_normalization"] = "unknown"
        except Exception as e:
            result["x_inspection_error"] = str(e)
        
        # Cell type column
        for key in ["cell_type", "cell_type_major", "cell_type_coarse", "celltype", "CellType"]:
            if key in adata.obs.columns:
                vc = adata.obs[key].value_counts().head(15)
                result["cell_type_distribution"] = {str(k): int(v) for k, v in vc.items()}
                result["cell_type_column"] = key
                break
        
        # Sample/donor column
        for key in ["sample", "patient", "donor", "Sample", "Patient"]:
            if key in adata.obs.columns:
                result[f"{key}_n_unique"] = int(adata.obs[key].nunique())
                break
        
        # Layers (if available)
        if hasattr(adata, "layers"):
            result["layers_available"] = list(adata.layers.keys())
        
        # obsm (embeddings if precomputed)
        if hasattr(adata, "obsm"):
            result["obsm_keys"] = list(adata.obsm.keys())
        
        # Suitability assessment for FM testing
        result["fm_suitability"] = {
            "has_raw_counts": result.get("x_inspection", {}).get("likely_normalization") == "raw_counts",
            "has_layers": bool(result.get("layers_available")),
            "has_cell_type": "cell_type_column" in result,
            "has_donors": any(k.endswith("_n_unique") for k in result.keys()),
            "n_cells_adequate_for_fm": result["n_cells"] >= 1000,
            "n_genes_adequate_for_fm": result["n_genes"] >= 5000,
        }
        ready_count = sum(1 for v in result["fm_suitability"].values() if v)
        result["fm_suitability"]["ready_score"] = f"{ready_count}/6"
        
        result["status"] = "SUCCESS"
        print(f"  Cells: {result['n_cells']:,}, Genes: {result['n_genes']:,}")
        print(f"  Likely normalization: {result.get('x_inspection', {}).get('likely_normalization', 'unknown')}")
        print(f"  FM suitability: {result['fm_suitability']['ready_score']}")
        
    except Exception as e:
        print(f"  FAILED: {e}")
        result["status"] = "FAILED"
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()[:2000]
    
    return result


def main():
    print("=" * 70)
    print("INTERCEPTA Layer 1 Job L: LuCA Top-3 Source Study Preprocessing")
    print("Started:", datetime.now(timezone.utc).isoformat())
    print("=" * 70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    results = []
    for study in TARGET_STUDIES:
        result = preprocess_one(study)
        results.append(result)
        
        # Save progress incrementally
        progress = {
            "started": datetime.now(timezone.utc).isoformat(),
            "n_total": len(TARGET_STUDIES),
            "n_completed": len(results),
            "studies": results,
        }
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        with open(REPORT, "w") as f:
            json.dump(progress, f, indent=2, default=str)
    
    # Summary
    print()
    print("=" * 70)
    print("PREPROCESSING SUMMARY")
    print("=" * 70)
    successful = [r for r in results if r.get("status") == "SUCCESS"]
    print(f"Successful: {len(successful)}/{len(results)}")
    for r in results:
        ready = r.get("fm_suitability", {}).get("ready_score", "n/a")
        print(f"  {r['study_name']:40s}: {r.get('status')}  FM-ready: {ready}")
    
    # Final
    final = {
        "started": datetime.now(timezone.utc).isoformat(),
        "completed": datetime.now(timezone.utc).isoformat(),
        "n_total": len(TARGET_STUDIES),
        "n_successful": len(successful),
        "studies": results,
    }
    with open(REPORT, "w") as f:
        json.dump(final, f, indent=2, default=str)
    
    print()
    print("Report:", REPORT)


if __name__ == "__main__":
    main()
