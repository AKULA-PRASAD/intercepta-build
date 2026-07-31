"""B59 — does the doubly-debiased VS residual differ by assay format? Confirmatory/post-hoc test on the committed B58
residuals: biochemical (cell-free isolated protein/enzyme) vs cell-based (functional + phenotypic), Mann-Whitney U +
rank-biserial effect size, with a descriptive look at the 2 phenotypic targets and a sensitivity excluding ambiguous
targets. Implements prereg/B59_assayclass_residual.md. Deterministic -> reproduce x2.
"""
import os, sys, json, time, hashlib
import numpy as np
import warnings; warnings.filterwarnings("ignore")
from scipy.stats import mannwhitneyu

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

# assay-format classification (by documented assay type, independent of residuals). amb = ambiguous.
BIOCHEM = {  # cell-free isolated protein/enzyme
    "FEN1": "flap endonuclease (biochemical)", "MAPK1": "ERK2 kinase (biochemical)",
    "ALDH1": "aldehyde dehydrogenase enzyme", "GBA": "glucocerebrosidase enzyme",
    "KAT2A": "histone acetyltransferase enzyme", "PKM2": "pyruvate kinase enzyme",
    "tyrosyl-dna_phosphodiesterase_butkiewicz": "TDP1 enzyme",
    "VDR": "nuclear-receptor binding (ambiguous)", "ESR1_ant": "nuclear-receptor binding (ambiguous)"}
CELL_FUNC = {  # cell-based functional, single target
    "m1_muscarinic_receptor_agonists_butkiewicz": "Ca2+ mobilization cell assay",
    "m1_muscarinic_receptor_antagonists_butkiewicz": "Ca2+ mobilization cell assay",
    "orexin1_receptor_butkiewicz": "GPCR cell fluorescence",
    "potassium_ion_channel_kir2.1_butkiewicz": "ion-channel functional (cell)",
    "kcnq2_potassium_channel_butkiewicz": "ion-channel functional (cell)",
    "cav3_t-type_calcium_channels_butkiewicz": "ion-channel functional (cell)",
    "choline_transporter_butkiewicz": "uptake cell assay",
    "serine_threonine_kinase_33_butkiewicz": "STK33 kinase/cell readout (ambiguous)"}
PHENOTYPIC = {"hiv": "viral replication (whole-cell)", "sarscov2_vitro_touret": "cytopathic antiviral (whole-cell)"}
AMBIGUOUS = {"VDR", "ESR1_ant", "serine_threonine_kinase_33_butkiewicz"}


def rank_biserial(a, b):
    """rank-biserial effect size from Mann-Whitney U (a vs b): r = 1 - 2U/(n1 n2); +ve => a>b stochastically."""
    U, _ = mannwhitneyu(a, b, alternative="two-sided")
    return round(1.0 - 2.0 * U / (len(a) * len(b)), 4)


def test_groups(bio, cell, label):
    if len(bio) < 3 or len(cell) < 3:
        return {"label": label, "note": "too few for a test"}
    U, p2 = mannwhitneyu(bio, cell, alternative="two-sided")
    _, p1 = mannwhitneyu(bio, cell, alternative="greater")  # H1: biochem > cell
    return {"label": label, "n_biochem": len(bio), "n_cell": len(cell),
            "median_biochem": round(float(np.median(bio)), 4), "median_cell": round(float(np.median(cell)), 4),
            "mean_biochem": round(float(np.mean(bio)), 4), "mean_cell": round(float(np.mean(cell)), 4),
            "mannwhitney_U": float(U), "p_two_sided": round(float(p2), 4), "p_one_sided_biochem_gt": round(float(p1), 4),
            "rank_biserial_effect": rank_biserial(bio, cell)}


def main():
    b58 = json.load(open(os.path.join(ROOT, "experiments/B58_residual_rogi_repowered/results/B58_metrics.json")))
    per = b58["per_target"]
    resid = {t: v["residual_A1B1"] for t, v in per.items() if "residual_A1B1" in v}

    groups = {}
    for t, r in resid.items():
        if t in BIOCHEM: groups[t] = ("biochemical", r)
        elif t in CELL_FUNC: groups[t] = ("cell_functional", r)
        elif t in PHENOTYPIC: groups[t] = ("phenotypic", r)
        else: groups[t] = ("unclassified", r)

    bio = [r for t, (g, r) in groups.items() if g == "biochemical"]
    cellf = [r for t, (g, r) in groups.items() if g == "cell_functional"]
    pheno = [r for t, (g, r) in groups.items() if g == "phenotypic"]
    cell_all = cellf + pheno

    print("classification & residuals:")
    for g in ("biochemical", "cell_functional", "phenotypic", "unclassified"):
        ts = sorted([(t, r) for t, (gg, r) in groups.items() if gg == g], key=lambda x: -x[1])
        if ts: print(f"  [{g}] " + ", ".join(f"{t[:16]}={r:.3f}" for t, r in ts))

    main_test = test_groups(bio, cell_all, "biochemical_vs_cellbased(functional+phenotypic)")
    # sensitivity: drop ambiguous (VDR, ESR1, STK33)
    bio_s = [r for t, (g, r) in groups.items() if g == "biochemical" and t not in AMBIGUOUS]
    cell_s = [r for t, (g, r) in groups.items() if g in ("cell_functional", "phenotypic") and t not in AMBIGUOUS]
    sens_test = test_groups(bio_s, cell_s, "sensitivity_excluding_ambiguous(VDR,ESR1,STK33)")

    h1 = bool("p_one_sided_biochem_gt" in main_test and main_test["p_one_sided_biochem_gt"] < 0.05
              and abs(main_test["rank_biserial_effect"]) >= 0.3)

    summary = {"n_targets": len(resid), "main_test": main_test, "sensitivity_test": sens_test,
               "phenotypic_descriptive": {"n": len(pheno), "residuals": sorted(pheno),
                                          "mean": round(float(np.mean(pheno)), 4) if pheno else None,
                                          "vs_rest_mean": round(float(np.mean(bio + cellf)), 4)},
               "H1_biochem_gt_cellbased": h1,
               "verdict": (
                   f"ASSAY FORMAT MATTERS: biochemical (isolated-protein) targets have HIGHER residual than cell-based "
                   f"(median {main_test['median_biochem']} vs {main_test['median_cell']}, one-sided p="
                   f"{main_test['p_one_sided_biochem_gt']}, rank-biserial {main_test['rank_biserial_effect']}). "
                   f"Isolated binding is more structure-learnable than cellular/phenotypic activity. Confirmatory/"
                   f"post-hoc, n={len(resid)}; not wet-lab."
                   if h1 else
                   f"NULL — ASSAY FORMAT DOES NOT EXPLAIN THE RESIDUAL (bounds B58's suggestive signal): biochemical vs "
                   f"cell-based residual medians {main_test['median_biochem']} vs {main_test['median_cell']} "
                   f"(one-sided p={main_test['p_one_sided_biochem_gt']}, two-sided {main_test['p_two_sided']}, "
                   f"rank-biserial {main_test['rank_biserial_effect']}) — NOT significant. B58's assay-type signal "
                   f"(Spearman -0.44) was driven by the 2 phenotypic antiviral points (residuals {sorted(pheno)}), NOT "
                   f"a general biochemical/cell-based effect; the powerable dichotomy shows no difference (sensitivity "
                   f"excluding ambiguous: p={sens_test.get('p_one_sided_biochem_gt')}). The PURE phenotypic test is "
                   f"infeasible (only {len(pheno)} datasets). So the phenotypic 'mechanism' is NOT supported at power; "
                   f"the residual's target-dependence stays unexplained (consistent with B57/B58). First-class null; "
                   f"confirmatory/post-hoc, n={len(resid)}; not wet-lab."),
               }
    print("\nMAIN:", main_test)
    print("SENSITIVITY:", sens_test)
    print("VERDICT:", summary["verdict"])

    prov = {"experiment": "B59_assayclass_residual", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "residual_source": "B58_metrics.json cells A1B1",
            "classification": {"biochemical": list(BIOCHEM), "cell_functional": list(CELL_FUNC),
                               "phenotypic": list(PHENOTYPIC), "ambiguous": list(AMBIGUOUS)},
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = {"provenance": prov, "summary": summary,
           "per_target": {t: {"group": g, "residual": r} for t, (g, r) in groups.items()}}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "B59_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary, "per_target": out["per_target"]}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B59_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B59_metrics.json")


def _libvers():
    import numpy, scipy
    return {"numpy": numpy.__version__, "scipy": scipy.__version__}


if __name__ == "__main__":
    main()
