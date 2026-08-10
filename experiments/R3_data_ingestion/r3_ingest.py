#!/usr/bin/env python3
"""R3 — public-data ingestion + auto-re-test engine (roadmap R3).

Harmonizes a diverse public bioactivity dataset into R2's format with a POWERED scaffold-leave-out split
(whole Murcko scaffolds held out -> test actives are genuinely off-manifold, unlike thrombin's n=5), runs
the R2 OOD testbed on each target, and appends a growing frontier log. This operationalizes "the vision is
data-asymptotic": each new public dataset gets auto-tested for whether the extrapolation wall breaks.

First source: LIT-PCBA (property-matched inactives; cached in $INTERCEPTA_DATA/lit_pcba). Drop-in more
sources by adding a harmonize_*() adapter. External method scores plug into R2's `external` slot.
Usage: python r3_ingest.py [TARGET ...]   (default: a diverse LIT-PCBA panel)
"""
import os, sys, json, subprocess, hashlib
import numpy as np, pandas as pd
from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
R2 = os.path.abspath(os.path.join(HERE, "..", "R2_ood_testbed", "ood_testbed.py"))
SEED, MAX_ACT, MAX_INACT_RATIO, MAX_INACT, TEST_FRAC10 = 42, 2000, 30, 6000, 3   # ~30% of scaffolds -> test

def read_smi(p):
    return [ln.split()[0] for ln in open(p) if ln.split()]

def scaffold(smi):
    m = Chem.MolFromSmiles(smi)
    if m is None: return None
    try: return MurckoScaffold.MurckoScaffoldSmiles(mol=m)
    except Exception: return None

def harmonize_litpcba(target):
    d = os.path.join(DATA, "lit_pcba", target)
    acts, inacts = read_smi(os.path.join(d, "actives.smi")), read_smi(os.path.join(d, "inactives.smi"))
    rng = np.random.default_rng(SEED)
    if len(acts) > MAX_ACT: acts = [acts[i] for i in rng.choice(len(acts), MAX_ACT, replace=False)]
    cap = min(len(inacts), max(MAX_INACT_RATIO * len(acts), 1000), MAX_INACT)
    if len(inacts) > cap: inacts = [inacts[i] for i in rng.choice(len(inacts), cap, replace=False)]
    df = pd.DataFrame([(s, 1) for s in acts] + [(s, 0) for s in inacts], columns=["smiles", "active"])
    df = df.assign(scaf=[scaffold(s) for s in df.smiles])
    def bucket(sc):
        sc = sc or "__none__"
        return "test" if (int(hashlib.md5(sc.encode()).hexdigest(), 16) % 10) < TEST_FRAC10 else "train"
    df = df.assign(split=[bucket(s) for s in df.scaf])
    df["y [pEC50/pKi]"] = np.where(df.active == 1, 7.0, 4.0)
    return df[["smiles", "y [pEC50/pKi]", "split", "active"]]

def run_target(target):
    df = harmonize_litpcba(target)
    tr, te = df[df.split == "train"], df[df.split == "test"]
    guard = {"train_act": int(tr.active.sum()), "test_act": int(te.active.sum()),
             "train_inact": int((tr.active == 0).sum()), "test_inact": int((te.active == 0).sum())}
    if guard["train_act"] < 5 or guard["test_act"] < 5 or guard["test_inact"] < 5:
        return {"target": target, "error": "split too small for a powered test", **guard}
    outdir = os.path.join(RES, target); os.makedirs(outdir, exist_ok=True)
    csv = os.path.join(outdir, "r2input.csv"); df[["smiles", "y [pEC50/pKi]", "split"]].to_csv(csv, index=False)
    env = dict(os.environ, R2_OUT=outdir)
    r = subprocess.run([sys.executable, R2, csv, "smiles", "y [pEC50/pKi]", "split"], env=env, capture_output=True, text=True)
    mfile = os.path.join(outdir, "R2_metrics.json")
    if not os.path.exists(mfile):
        return {"target": target, "error": (r.stderr or r.stdout)[-500:], **guard}
    p = json.load(open(mfile))["payload"]; rf = p["results"]["qsar_rf"]
    return {"target": target, "verdict": p["verdict"], "n_test_novel_active": p["counts"]["test_novel_active"],
            "qsar_rf_SEEN_auroc": rf["SEEN_analog"]["auroc"], "qsar_rf_NOVEL_auroc": rf["NOVEL"]["auroc"],
            "qsar_rf_NOVEL_ci": rf["NOVEL"]["ci95"], "qsar_rf_NOVEL_npos": rf["NOVEL"]["n_pos"],
            "alarm": p["alarm_per_method"]["qsar_rf"], "leakage_median_maxTanimoto": p["leakage_audit_test_to_train_maxTanimoto"]["median"]}

def main():
    targets = sys.argv[1:] or ["FEN1", "MAPK1", "PKM2", "KAT2A", "GBA", "ESR1_ant", "ALDH1"]
    log = []
    for t in targets:
        print(f"=== R3 ingest+run: {t} ===")
        try: res = run_target(t)
        except Exception as e: res = {"target": t, "error": str(e)[:300]}
        log.append(res)
        print("  " + json.dumps({k: res.get(k) for k in ["verdict", "n_test_novel_active", "qsar_rf_SEEN_auroc",
              "qsar_rf_NOVEL_auroc", "qsar_rf_NOVEL_ci", "qsar_rf_NOVEL_npos", "alarm", "error"] if k in res}))
    frontier = {"instrument": "R3 ingestion -> R2 OOD testbed", "source": "LIT-PCBA (property-matched)",
                "config": {"seed": SEED, "max_act": MAX_ACT, "max_inact_ratio": MAX_INACT_RATIO, "test_scaffold_frac": TEST_FRAC10 / 10.0},
                "targets": log, "any_wall_breaking": any(x.get("verdict") == "WALL_BREAKING" for x in log),
                "n_targets_powered": sum(1 for x in log if (x.get("qsar_rf_NOVEL_npos") or 0) >= 10)}
    json.dump(frontier, open(os.path.join(RES, "frontier_log.json"), "w"), sort_keys=True, indent=2)
    print("\nFRONTIER: any_wall_breaking =", frontier["any_wall_breaking"], "| powered targets (>=10 novel actives) =", frontier["n_targets_powered"])

if __name__ == "__main__":
    main()
