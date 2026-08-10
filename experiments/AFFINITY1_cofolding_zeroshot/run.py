#!/usr/bin/env python3
"""AFFINITY1 - zero-shot deep co-folding (Boltz-2) for novel-target binding-affinity ranking.

Frontier 2 (OPEN-PROBLEM). Head-to-head vs HIT2 docking on thrombin (CHEMBL204).

Modes:
  prep   - build per-compound Boltz-2 YAMLs (thrombin seq + ligand SMILES + affinity head)
           for a pre-registered stratified subsample; writes compounds_manifest.csv
  score  - read cached Boltz-2 affinity outputs, join labels + HIT2 docking,
           compute Spearman/AUROC (overall + novelty split), head-to-head vs docking,
           write results/AFFINITY1_metrics.json (sorted keys) + payload.sha256

Determinism: scoring is pure-deterministic (no RNG). Boltz inference uses --seed 42 but
neural inference may be non-byte-identical; raw affinity JSONs are CACHED and the DOWNSTREAM
scoring is what we reproduce x2 byte-identical (payload sha). See SUMMARY.md.
"""
import os, sys, json, hashlib, glob
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
# Portable paths (HPC-ready; no hard-coded machine paths). Small INPUT fixtures ship in the repo;
# WORK/output data goes to $INTERCEPTA_DATA (scratch on HPC) or a local _work/ fallback.
FIXTURES = os.path.join(HERE, "benchmark_data")
WORK = os.path.join(os.environ.get("INTERCEPTA_DATA", os.path.join(HERE, "_work")), "affinity1")
os.makedirs(WORK, exist_ok=True)
DATA = WORK            # outputs: yamls/, compounds_manifest.csv, scored.csv, out/
HIT2 = FIXTURES        # thrombin_vina.tsv (committed fixture)
MACE = os.path.join(FIXTURES, "CHEMBL204_Ki.csv")  # public MoleculeACE source (provenance; unused at runtime)

# thrombin 1OYT chains (SEQRES): L light chain, H heavy/catalytic chain
THROMBIN_L = "TFGSGEADCGLRPLFEKKSLEDKTERELLESYIDGR"
THROMBIN_H = ("IVEGSDAEIGMSPWQVMLFRKSPQELLCGASLISDRWVLTAAHCLLYPPWDKNFTENDLLVRIGKHSRTRYERNIEK"
              "ISMLEKIYIHPRYNWRENLDRDIALMKLKKPVAFSDYIHPVCLPDRETAASLLQAGYKGRVTGWGNLKETWTANVGK"
              "GQPSVLQVVNLPIVERPVCKDSTRIRITDNMFCAGYKPDEGKRGDACEGDSGGPFVMKSPFNNRWYQMGIVSWGEGC"
              "DRDGKYGFYTHVFRLKKWIQKVIDQFGE")
ACT_CUT = 6.5
SEED = 42

def load_test():
    nov = pd.read_csv(os.path.join(FIXTURES, "test_novelty.csv"))
    v = pd.read_csv(os.path.join(FIXTURES, "thrombin_vina.tsv"), sep="\t")
    # join on idx (both derive from the same MoleculeACE test order)
    df = nov.merge(v[["idx", "vina"]], on="idx", how="left")
    return df

def prep(budget_n):
    df = load_test()
    rng = np.random.default_rng(SEED)
    # pre-registered stratified subsample: ALL novel actives + balanced random draw
    novel_act = df[(df.active == 1) & (df.novelty == "novel")]
    rest = df.drop(novel_act.index)
    remaining = max(0, budget_n - len(novel_act))
    # balance actives / inactives in the remaining draw
    act = rest[rest.active == 1]
    ina = rest[rest.active == 0]
    n_each = remaining // 2
    pick_act = act.sample(min(n_each, len(act)), random_state=SEED)
    pick_ina = ina.sample(min(remaining - len(pick_act), len(ina)), random_state=SEED)
    sub = pd.concat([novel_act, pick_act, pick_ina]).sort_values("idx").reset_index(drop=True)
    ydir = os.path.join(DATA, "yamls"); os.makedirs(ydir, exist_ok=True)
    for _, r in sub.iterrows():
        name = f"cmpd_{int(r.idx):04d}"
        smi = r.smiles.replace("'", "")
        with open(os.path.join(ydir, name + ".yaml"), "w") as f:
            f.write("version: 1\nsequences:\n"
                    f"  - protein:\n      id: A\n      sequence: {THROMBIN_L}\n"
                    f"  - protein:\n      id: B\n      sequence: {THROMBIN_H}\n"
                    f"  - ligand:\n      id: L\n      smiles: '{smi}'\n"
                    "properties:\n  - affinity:\n      binder: L\n")
    sub.to_csv(os.path.join(DATA, "compounds_manifest.csv"), index=False)
    print(f"prep: wrote {len(sub)} YAMLs (novel_act={len(novel_act)}, "
          f"act={len(pick_act)}, ina={len(pick_ina)}) to {ydir}")

def spearman(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    m = ~(np.isnan(a) | np.isnan(b))
    a, b = a[m], b[m]
    if len(a) < 3: return None
    ra = pd.Series(a).rank().values; rb = pd.Series(b).rank().values
    return float(np.corrcoef(ra, rb)[0, 1])

def auroc(scores, labels):
    s = np.asarray(scores, float); y = np.asarray(labels, int)
    m = ~np.isnan(s); s, y = s[m], y[m]
    npos = int(y.sum()); nneg = int(len(y) - npos)
    if npos == 0 or nneg == 0: return None
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s)); ranks[order] = np.arange(1, len(s) + 1)
    # average ties
    df = pd.DataFrame({"s": s, "r": ranks})
    df["r"] = df.groupby("s")["r"].transform("mean")
    ranks = df["r"].values
    return float((ranks[y == 1].sum() - npos * (npos + 1) / 2.0) / (npos * nneg))

def build_affinity_index():
    """ONE pass over <DATA>/out -> {cmpd_name: json_path}. Replaces the old per-compound recursive
    glob (553 x '**' walks over an NFS tree of 10^4-10^5 files) that was pathologically slow and got
    `score` SIGKILLed by the login-node resource policy. Prefers chunk_* outputs over any leftover
    smoke tree, so duplicated compounds resolve DETERMINISTICALLY to the chunk run."""
    index = {}
    for root, _dirs, files in os.walk(os.path.join(DATA, "out")):
        is_chunk = (os.sep + "chunk_") in root
        for fn in files:
            if fn.startswith("affinity_cmpd_") and fn.endswith(".json"):
                name = fn[len("affinity_"):-len(".json")]
                if name not in index or is_chunk:
                    index[name] = os.path.join(root, fn)
    return index

def read_affinity(name, index):
    p = index.get(name)
    if not p: return None
    with open(p) as f:
        return json.load(f)

def score():
    man = pd.read_csv(os.path.join(DATA, "compounds_manifest.csv"))
    index = build_affinity_index()          # single NFS walk (was 553x recursive glob -> SIGKILL)
    print("indexed %d affinity JSONs under %s/out" % (len(index), DATA))
    rows = []
    for _, r in man.iterrows():
        name = f"cmpd_{int(r.idx):04d}"
        aff = read_affinity(name, index)
        if aff is None:
            pred_val = np.nan; pbin = np.nan
        else:
            pred_val = float(aff.get("affinity_pred_value", np.nan))
            pbin = float(aff.get("affinity_probability_binary", np.nan))
        rows.append(dict(idx=int(r.idx), pact=float(r.pact), active=int(r.active),
                         novelty=r.novelty, vina=float(r.vina) if pd.notna(r.vina) else np.nan,
                         aff_pred_value=pred_val, aff_prob_binary=pbin))
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(DATA, "scored.csv"), index=False)
    done = d[~d.aff_pred_value.isna()]
    n_done = len(done)

    # Orientation: Boltz affinity_pred_value = predicted log(IC50) (lower = stronger binder).
    # For "higher score = more active", proxy = -aff_pred_value and aff_prob_binary.
    def block(sub):
        return {
            "n": int(len(sub)),
            "n_active": int(sub.active.sum()),
            "spearman_affval_vs_pact": spearman(-sub.aff_pred_value, sub.pact),
            "spearman_probbin_vs_pact": spearman(sub.aff_prob_binary, sub.pact),
            "auroc_affval": auroc(-sub.aff_pred_value, sub.active),
            "auroc_probbin": auroc(sub.aff_prob_binary, sub.active),
            "auroc_docking": auroc(-sub.vina, sub.active),  # HIT2 baseline on same compounds
        }

    overall = block(done)
    # novelty split: actives-of-that-class vs inactives (matches HIT1/HIT2 novel_vs_inactive)
    ina = done[done.active == 0]
    analog_act = done[(done.active == 1) & (done.novelty == "analog")]
    novel_act = done[(done.active == 1) & (done.novelty == "novel")]
    def cls_auroc(act_sub, score_col, sign=1.0):
        s = pd.concat([act_sub, ina])
        return auroc(sign * s[score_col].values, s["active"].values)
    novelty = {
        "analog_vs_inactive_affval": cls_auroc(analog_act, "aff_pred_value", -1.0),
        "analog_vs_inactive_probbin": cls_auroc(analog_act, "aff_prob_binary", 1.0),
        "novel_vs_inactive_affval": cls_auroc(novel_act, "aff_pred_value", -1.0),
        "novel_vs_inactive_probbin": cls_auroc(novel_act, "aff_prob_binary", 1.0),
        "n_analog_active": int(len(analog_act)),
        "n_novel_active": int(len(novel_act)),
    }

    # pre-registered gate
    best_overall = max([x for x in [overall["auroc_affval"], overall["auroc_probbin"]] if x is not None], default=None)
    best_novel = max([x for x in [novelty["novel_vs_inactive_affval"], novelty["novel_vs_inactive_probbin"]] if x is not None], default=None)
    DOCK_BASE = 0.4285  # HIT2 full-set docking overall AUROC
    gate_overall = (best_overall is not None and best_overall >= 0.60 and best_overall > DOCK_BASE)
    gate_novel = (best_novel is not None and best_novel >= 0.60)
    verdict = "PASS" if (gate_overall and gate_novel) else "BOUNDED-NEGATIVE"

    payload = {
        "target": "thrombin (CHEMBL204), receptor 1OYT (same as HIT2)",
        "method": "Boltz-2 co-folding affinity head (affinity_pred_value=predicted log(IC50), lower=stronger; affinity_probability_binary=P(binder))",
        "act_cut": ACT_CUT, "seed": SEED,
        "n_scored": int(n_done),
        "overall": overall,
        "novelty_split": novelty,
        "docking_baseline_fullset": {"auroc_overall": DOCK_BASE, "source": "HIT2_metrics.json"},
        "gate": {"gate_overall_ge_0.60_and_gt_docking": bool(gate_overall),
                 "gate_novel_ge_0.60": bool(gate_novel),
                 "best_overall_auroc": best_overall, "best_novel_auroc": best_novel,
                 "verdict": verdict},
    }
    _full = n_done >= 500
    payload["run_note"] = ((("FULL GPU head-to-head (n_scored=%d, n_novel_active=%d): the definitive "
                             "co-folding-affinity-vs-docking benchmark per GPU_BENCHMARK_SPEC.md.") if _full else
                            ("UNDERPOWERED subsample (n_scored=%d, n_novel_active=%d): NOT definitive; "
                             "no overclaim from small n.")) % (n_done, novelty["n_novel_active"]))
    payload["n_manifest"] = int(len(man))
    payload = json.loads(json.dumps(payload, sort_keys=True))
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    sha = hashlib.sha256(blob).hexdigest()
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "AFFINITY_PILOT_metrics.json"), "w") as f:
        json.dump({"payload": payload, "payload_sha256": sha,
                   "provenance": {"git_sha": os.popen("git -C %s rev-parse HEAD" % HERE).read().strip(),
                                  "boltz_version": "2.2.1", "python": "3.11.15",
                                  "hardware": os.environ.get("INTERCEPTA_HW", "see SLURM log (nvidia-smi)"),
                                  "n_scored": int(n_done), "n_manifest": int(len(man))}},
                  f, sort_keys=True, indent=2)
    with open(os.path.join(RESULTS, "pilot_payload.sha256"), "w") as f:
        f.write(sha + "\n")
    print("score_pilot: n_scored=%d verdict=%s sha=%s" % (n_done, verdict, sha))
    print(json.dumps(payload, indent=2))

def finalize_infeasible():
    """Deterministic bookkeeping writer for the pre-registered CPU-INFEASIBLE outcome.
    No dependence on RNG or on any boltz output -> reproducible byte-identical x2.
    Records the ACTUAL observed G1/G2 evidence, the carried-over docking baseline + gate,
    and pointers to GPU_BENCHMARK_SPEC.md."""
    DOCK_BASE = 0.4285  # HIT2 full-set docking overall AUROC (baseline to beat)
    payload = {
        "target": "thrombin (CHEMBL204), receptor 1OYT (same target/receptor/compounds as HIT2)",
        "problem": "Frontier 2 (OPEN-PROBLEM): zero-shot binding-affinity RANKING for a target with zero activity data",
        "method_under_test": "Boltz-2 (v2.2.1) co-folding + affinity head (affinity_pred_value, affinity_probability_binary)",
        "verdict": "CPU_INFEASIBLE",
        "verdict_long": ("The co-folding invention is COMPUTE-GATED on this CPU-only Apple-Silicon machine, "
                         "not refuted. G1 install PASSED; a single-complex CPU inference did NOT complete in "
                         "the observation window and, decisively, the throughput required for the 553-compound "
                         "head-to-head (and even the pre-registered subsample) exceeds the feasible in-session "
                         "CPU budget. The definitive head-to-head is delivered as a ready-to-run GPU spec."),
        "feasibility_gate": {
            "G1_install": {
                "pass": True,
                "evidence": ("pip install boltz -> boltz-2.2.1 installed cleanly into a fresh venv on "
                             "Python 3.11.14 (arm64). Python 3.13 first FAILED: it forced scipy to build "
                             "from source (no wheel) and needs a Fortran compiler (flang/gfortran) absent "
                             "here; downgrading the venv to 3.11 resolved it. torch 2.13.0 CPU, rdkit 2026.3.5."),
            },
            "G2_single_complex": {
                "pass": False,
                "cap_minutes": 20,
                "oom": False,
                "evidence": ("Actually launched `boltz predict` on ONE thrombin(L+H)+ligand complex, "
                             "--accelerator cpu --use_msa_server --seed 42. One-time weight download 3.6 GB "
                             "(boltz2_conf.ckpt 2.3 GB + boltz2_aff.ckpt 1.3 GB) + CCD mols. MSA retrieved from "
                             "the colabfold mmseqs2 server. Structure diffusion ran at 500-550% CPU. Peak RSS "
                             "~2.6 GB (NO OOM; well under the ~15 GB cap). Process ran 10 min 38 s total "
                             "wall-clock (download+MSA+~7 min pure inference) and had NOT produced the "
                             "affinity_*.json when it was terminated (SIGTERM) to finalize the run. "
                             "So G2 is recorded as NOT-completed-in-window (not a clean pass); no OOM."),
            },
        },
        "throughput_infeasibility": {
            "n_compounds_full_headtohead": 553,
            "n_novel_actives": 5, "n_actives": 292,
            "note": ("Even at an optimistic ~7-15 min/complex (pure inference, no OOM), 553 complexes ~ 64-138 "
                     "CPU-hours; the pre-registered <=24h subsample (~40 complexes) was also not completed "
                     "in-session. Full/subsample head-to-head is therefore compute-gated -> GPU spec."),
        },
        "docking_baseline_to_beat": {"auroc_overall": DOCK_BASE, "source": "HIT2 (thrombin, AutoDock Vina)",
                                     "random": 0.5},
        "preregistered_gate_carried_to_gpu": {
            "PASS": "overall AUROC >= 0.60 AND > 0.4285 (docking) AND novel-vs-inactive AUROC >= 0.60",
            "FAIL": "otherwise -> first-class BOUNDED-NEGATIVE",
        },
        "deliverable_pointers": {
            "gpu_spec": "GPU_BENCHMARK_SPEC.md",
            "prereg": "PREREG.md", "feasibility": "FEASIBILITY.md", "runner": "run.py",
            "novelty_split_cached": "$INTERCEPTA_DATA/affinity1/test_novelty.csv",
        },
        "scope": ("in-silico; one target (thrombin, docking's most favourable case); CPU-only arm64, NO GPU/CUDA; "
                  "a confidence/affinity PROXY not measured affinity; enrichment != proven activity; not wet-lab; "
                  "no SOTA claim; the co-folding method is UNtested here (compute-gated), not refuted."),
    }
    payload = json.loads(json.dumps(payload, sort_keys=True))
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    sha = hashlib.sha256(blob).hexdigest()
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "AFFINITY1_metrics.json"), "w") as f:
        json.dump({"payload": payload, "payload_sha256": sha,
                   "provenance": {"git_sha": os.popen("git -C %s rev-parse HEAD" % HERE).read().strip(),
                                  "boltz_version": "2.2.1", "python": "3.11.14",
                                  "hardware": "Apple M4, 10 core, 16 GB RAM, arm64, macOS, NO GPU/CUDA"}},
                  f, sort_keys=True, indent=2)
    with open(os.path.join(RESULTS, "payload.sha256"), "w") as f:
        f.write(sha + "\n")
    print("finalize_infeasible: verdict=CPU_INFEASIBLE payload_sha256=%s" % sha)
    return sha

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "score"
    if mode == "prep":
        prep(int(sys.argv[2]) if len(sys.argv) > 2 else 40)
    elif mode == "score":
        score()
    elif mode == "finalize_infeasible":
        finalize_infeasible()
