"""Generate submission figures for the INTERCEPTA engine manuscript, entirely from committed, reproduced-x2
metrics JSONs (experiments/*/results/). No hand-entered numbers. Run from repo root:
    python papers/intercepta_engine/figures/make_figures.py
Outputs Fig1/2/3 as PDF + PNG (300 dpi) alongside this script.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RES = os.path.join(ROOT, "experiments")
OUT = os.path.dirname(os.path.abspath(__file__))
def load(p): return json.load(open(os.path.join(RES, p)))
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 300, "savefig.bbox": "tight", "pdf.fonttype": 42})
BLUE, GREY, RED, GREEN = "#2c6fb3", "#9aa0a6", "#c0392b", "#2e8b57"
def save(fig, name):
    for ext in ("pdf", "png"): fig.savefig(os.path.join(OUT, f"{name}.{ext}"))
    plt.close(fig); print("wrote", name)

# ---------------- Fig 1: transfer signal + leakage + ceiling (B1) ----------------
b1 = load("B1_baseline_ceiling/results/B1_metrics.json")
fig, ax = plt.subplots(figsize=(3.4, 3.0))
vals = [b1["leaky_mean_rho"], b1["strict_mean_rho"], b1["rprolif_mean_rho"]]
labs = ["Leaky\n(test lines in\ntraining)", "Clean\n(disjoint lines)", "Proliferation\nbaseline"]
cols = [GREY, BLUE, "#d0d0d0"]
bars = ax.bar(range(3), vals, color=cols, width=0.62, edgecolor="black", linewidth=0.5)
for i, v in enumerate(vals): ax.text(i, v + 0.006, f"{v:.3f}", ha="center", va="bottom", fontsize=8.5)
ax.set_xticks(range(3)); ax.set_xticklabels(labs)
ax.set_ylabel("Mean per-drug Spearman ρ\n(GDSC2 → CCLE/PRISM)")
ax.set_ylim(0, 0.35)
ax.annotate("", xy=(1, 0.322), xytext=(0, 0.322), arrowprops=dict(arrowstyle="<->", color="black", lw=0.8))
ax.text(0.5, 0.327, "leakage inflation", ha="center", va="bottom", fontsize=7.5)
ax.set_title(f"Cross-dataset transfer & ceiling\n{b1['n_drugs']} drugs, {int(b1['strict_frac_pos']*100)}% positive; "
             f"p={b1['wilcoxon_p_strict_vs_rprolif']:.0e} vs baseline", fontsize=8.5)
save(fig, "Fig1_transfer_ceiling")

# ---------------- Fig 2: functional-inference — BeatAML promise vs FIMM failure ----------------
b21 = load("B21_selectivity_crosscohort/results/B21_metrics.json")
b18 = load("B18_target_specificity/results/B18_metrics.json")
b20 = load("B20_fimm_external_replication/results/B20_metrics.json")
be = b21["beataml_effects"]; fe = b21["fimm_effects"]
shared = [d for d in b21["shared_drugs"]]
fig, (axA, axB) = plt.subplots(1, 2, figsize=(6.8, 3.1))
# (A) per-drug effect BeatAML vs FIMM (shared drugs)
x = np.arange(len(shared)); w = 0.38
axA.bar(x - w/2, [be[d]["effect"] for d in shared], w, label="BeatAML (AUC)", color=BLUE, edgecolor="black", lw=0.4)
axA.bar(x + w/2, [fe[d]["effect"] for d in shared], w, label="FIMM (DSS)", color=RED, edgecolor="black", lw=0.4)
axA.axhline(0, color="black", lw=0.6)
axA.set_xticks(x); axA.set_xticklabels(shared, rotation=20, ha="right")
axA.set_ylabel("Prolif-adj. inferred-FLT3-dep →\nFLT3i sensitivity (Spearman ρ)")
axA.set_title("(A) Per-drug effect does not replicate", fontsize=8.5)
axA.legend(frameon=False, fontsize=7.5, loc="lower left")
axA.text(shared.index("sorafenib"), fe["sorafenib"]["effect"] - 0.02, "sign flip", ha="center", va="top", fontsize=7, color=RED)
# (B) specificity double-dissociation gap: BeatAML (B18) vs FIMM (B20)
gaps = [b18["gap"], b20["R2_gap"]]; ps = [b18["H1_perm_p"], b20["R2_perm_p"]]
c = [GREEN, RED]
bars = axB.bar([0, 1], gaps, color=c, width=0.6, edgecolor="black", lw=0.5)
for i, (g, p) in enumerate(zip(gaps, ps)):
    axB.text(i, g + 0.004, f"gap={g:.3f}\nperm p={p:.0e}" if p < 0.01 else f"gap={g:.3f}\nperm p={p:.2f}",
             ha="center", va="bottom", fontsize=7.5)
axB.axhline(0, color="black", lw=0.6)
axB.set_xticks([0, 1]); axB.set_xticklabels(["BeatAML\n(B18)", "FIMM\n(B20)"])
axB.set_ylabel("Target-specificity gap\n(diagonal − off-diagonal ρ)")
axB.set_ylim(0, 0.16)
axB.set_title("(B) Target-specificity does not replicate", fontsize=8.5)
fig.suptitle("Functional-inference layer: promising in BeatAML, fails independent replication", fontsize=9.5, y=1.02)
save(fig, "Fig2_functional_replication")

# ---------------- Fig 3: the decisive clinical null (B10) ----------------
b10 = load("B10_tcga_outcome/results/B10_metrics.json")
fig, ax = plt.subplots(figsize=(3.6, 3.0))
vals = [b10["H1_raw_pooled_auroc"], b10["H2_within_cancer_auroc"], b10["proliferation_only_auroc"]]
ps = [b10["H1_perm_p"], b10["H2_perm_p"], None]
labs = ["Raw pooled\n(confounded)", "Within-cancer\n(controlled)", "Proliferation\nonly"]
cols = [GREY, RED, "#d0d0d0"]
ax.bar(range(3), vals, color=cols, width=0.62, edgecolor="black", lw=0.5)
ax.axhline(0.5, color="black", lw=0.8, ls="--"); ax.text(2.45, 0.505, "chance", fontsize=7, va="bottom", ha="right")
for i, (v, p) in enumerate(zip(vals, ps)):
    t = f"{v:.3f}" + (f"\np={p:.2f}" if p is not None else "")
    ax.text(i, v + 0.004, t, ha="center", va="bottom", fontsize=8)
ax.set_xticks(range(3)); ax.set_xticklabels(labs)
ax.set_ylabel("Clinical-response AUROC (TCGA)")
ax.set_ylim(0.40, 0.58)
ax.set_title(f"Human clinical prediction is cancer-type confounding\n{b10['n_drugs']} drugs, "
             f"{b10['n_within_cancer_strata']} within-cancer strata", fontsize=8.5)
save(fig, "Fig3_clinical_null")

# ---------------- Fig 4: the combinations arm — an externally-validated positive (B24/B28/B29) ----------------
b24 = load("B24_synergy_generalization/results/B24_metrics.json")
b28 = load("B28_synergy_crosscorpus/results/B28_metrics.json")
b29 = load("B29_synergy_conformal_coverage/results/B29_metrics.json")
fig, (axA, axB) = plt.subplots(1, 2, figsize=(6.8, 3.1))
# (A) generalization within-corpus vs external cross-corpus (Spearman)
labsA = ["Within-corpus\n(new combos)", "DrugComb→O'Neil\n(external)", "O'Neil→DrugComb\n(external)"]
valsA = [b24["results"]["leave_combination_out"]["model"]["spearman"],
         b28["drugcomb_to_oneil"]["spearman"], b28["oneil_to_drugcomb"]["spearman"]]
colsA = [BLUE, GREEN, GREY]
axA.bar(range(3), valsA, color=colsA, width=0.62, edgecolor="black", lw=0.5)
for i, v in enumerate(valsA): axA.text(i, v + 0.01, f"{v:.2f}", ha="center", va="bottom", fontsize=8.5)
axA.axhline(0, color="black", lw=0.6)
axA.set_xticks(range(3)); axA.set_xticklabels(labsA, fontsize=7)
axA.set_ylabel("Synergy Spearman ρ (pred vs measured)")
axA.set_ylim(0, 0.72)
axA.set_title(f"(A) Synergy generalizes & externally replicates\n(DrugComb→O'Neil: {b28['drugcomb_to_oneil']['enrichment']}× retrieval enrichment)", fontsize=8)
# (B) conformal calibration: nominal vs empirical coverage (both corpora)
axB.plot([0.75, 0.95], [0.75, 0.95], color="black", ls="--", lw=0.8, label="perfect calibration")
for corpus, mk, col in [("oneil", "o", BLUE), ("drugcomb", "s", GREEN)]:
    d = b29["corpora"][corpus]
    nom = [d[k]["nominal"] for k in d]; emp = [d[k]["empirical_coverage"] for k in d]
    axB.scatter(nom, emp, marker=mk, s=55, color=col, edgecolor="black", lw=0.5, label=corpus, zorder=3)
axB.set_xlabel("Nominal coverage"); axB.set_ylabel("Empirical coverage (unseen combos)")
axB.set_xlim(0.74, 0.96); axB.set_ylim(0.74, 0.96)
axB.legend(frameon=False, fontsize=7.5, loc="upper left")
axB.set_title("(B) Prediction intervals are calibrated", fontsize=8.5)
fig.suptitle("Drug-combination synergy: the externally-validated positive", fontsize=9.5, y=1.02)
save(fig, "Fig4_synergy_positive")

print("all figures written to", OUT)
