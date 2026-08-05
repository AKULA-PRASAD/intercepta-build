"""Generate the zero-data preprint figures DIRECTLY from committed experiment metrics (no hand-typed numbers) — every
value is read from experiments/*/results/*.json, so each figure is traceable to a reproduced-x2 experiment. Deterministic.
Env: intercepta-build (matplotlib). Output: papers/zero_data_discovery/figures/*.png (+ .pdf).
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures"); os.makedirs(FIG, exist_ok=True)
def L(p): return json.load(open(os.path.join(ROOT, "experiments", p)))
def save(fig, name):
    for ext in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"{name}.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig); print("wrote", name)

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 200})
PANEL, HELDOUT = "#3b6ea5", "#c1442e"

# ---- Figure 1: five-organism experimental validation of FBA-essentiality ----
ec = L("VALIDATE_essentiality/results/VALIDATE_essentiality.json")["summary"]
mt = L("VALIDATE_essentiality/results/VALIDATE_essentiality_mtb.json")["summary"]
kp = L("VALIDATE_essentiality/results/VALIDATE_essentiality_kp.json")["summary"]
deg = L("VALIDATE_essentiality/results/VALIDATE_essentiality_deg.json")["summary"]["organisms"]
rows = [  # (label, source, odds_ratio, fisher_p, held_out)
    ("E. coli",        "PEC knockouts",   ec["odds_ratio"], ec["fisher_p"], False),
    ("P. aeruginosa",  "Turner Tn-seq",   deg["paeruginosa"]["odds_ratio"], deg["paeruginosa"]["fisher_p"], False),
    ("M. tuberculosis","DeJesus Tn-seq",  mt["odds_ratio"], mt["fisher_p"], False),
    ("A. baumannii",   "Wang INSeq",      deg["abaumannii"]["odds_ratio"], deg["abaumannii"]["fisher_p"], True),
    ("K. pneumoniae",  "CRISPRi/Tn-seq",  kp["odds_ratio"], kp["fisher_p"], True),
]
rows.sort(key=lambda r: r[2])
fig, ax = plt.subplots(figsize=(7.2, 3.6))
y = np.arange(len(rows)); ors = [r[2] for r in rows]
cols = [HELDOUT if r[4] else PANEL for r in rows]
ax.barh(y, ors, color=cols, height=0.62)
ax.axvline(3, ls="--", color="grey", lw=1); ax.text(3, len(rows)-0.35, " pre-registered gate (OR>3)", color="grey", fontsize=8, va="top")
for i, r in enumerate(rows):
    p = r[3]; ptxt = "p<1e-15" if (p is not None and p < 1e-15) else (f"p={p:.1e}" if p else "")
    ax.text(r[2]*1.03, i, f"OR {r[2]:.0f}  {ptxt}", va="center", fontsize=8)
ax.set_yticks(y); ax.set_yticklabels([f"{r[0]}\n({r[1]})" for r in rows], fontsize=8.5)
ax.set_xscale("log"); ax.set_xlim(1, 300); ax.set_xlabel("Odds ratio: FBA-essential enriched for EXPERIMENTALLY-essential genes (log scale)")
ax.set_title("Fig 1. FBA gene-essentiality validated against experimental knockout data in 5 bacteria", fontsize=10, loc="left")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=PANEL, label="development panel"), Patch(color=HELDOUT, label="held-out WHO pathogen")],
          loc="lower right", fontsize=8, frameon=False)
save(fig, "fig1_five_organism_validation")

# ---- Figure 2: mechanism (FBA-essentiality) breaks the conservation ceiling (MET1) ----
m1 = L("MET1_fba_essentiality_targets/results/MET1_metrics.json"); m1 = m1.get("summary", m1)
cons = m1["cv_auroc_conservation_only"]; both = m1["cv_auroc_conservation_plus_essentiality"]; d = m1["cv_delta_auroc_essentiality_adds"]
fig, ax = plt.subplots(figsize=(4.6, 3.7))
bars = ax.bar([0, 1], [cons, both], color=["#9aa7b1", "#2e8b57"], width=0.6)
ax.set_xticks([0, 1]); ax.set_xticklabels(["conservation\nonly", "conservation +\nFBA-essentiality"], fontsize=9)
ax.set_ylim(0.5, max(both, 0.8) + 0.06); ax.set_ylabel("Held-out (5-fold CV) AUROC, target recovery")
for b, v in zip(bars, [cons, both]): ax.text(b.get_x()+b.get_width()/2, v+0.005, f"{v:.3f}", ha="center", fontsize=9)
ax.annotate("", xy=(1, both), xytext=(1, cons), arrowprops=dict(arrowstyle="<->", color="black"))
ax.text(1.06, (cons+both)/2, f"ΔAUROC +{d:.3f}\n(OR essential↔target {m1['H1_odds_ratio']:.1f})", fontsize=8, va="center")
ax.set_title("Fig 2. Mechanism breaks the conservation ceiling\n(E. coli iML1515; the one orthogonal signal)", fontsize=9.5, loc="left")
save(fig, "fig2_mechanism_ceiling_break")

# ---- Figure 3: condition-robustness is a validated target-quality filter (CONDROB1) ----
c1 = L("CONDROB1_condition_robust/results/CONDROB1_metrics.json")["summary"]; h1 = c1["H1_pec_enrichment"]
fig, ax = plt.subplots(figsize=(4.6, 3.7))
vals = [h1["all_pec_precision"], h1["core_pec_precision"]]
bars = ax.bar([0, 1], vals, color=["#9aa7b1", "#2e8b57"], width=0.6)
ax.set_xticks([0, 1]); ax.set_xticklabels([f"all FBA-essential\n(n={h1['all_essential_n']})", f"condition-robust\n(all media, n={h1['core_n']})"], fontsize=9)
ax.set_ylim(0, 1.0); ax.set_ylabel("Fraction EXPERIMENTALLY essential (PEC)")
for b, v in zip(bars, vals): ax.text(b.get_x()+b.get_width()/2, v+0.02, f"{v:.0%}", ha="center", fontsize=10)
ax.text(0.5, 0.93, f"+{(vals[1]-vals[0]):.2f} enrichment", ha="center", fontsize=9, color="#2e8b57")
ax.set_title("Fig 3. Condition-robustness is a validated quality axis\n(essential across nutrient environments → more often real)", fontsize=9.5, loc="left")
save(fig, "fig3_condition_robustness")

# ---- Figure 4: multi-axis best-intervention scorecard + validation (BESTINT1) ----
b = L("BESTINT1_multiaxis_score/results/BESTINT1_metrics.json"); rk = b["ranking"]; val = b["summary"]["validation_vs_experimental_essentiality"]
top = rk[:15]; axes_names = ["druggability", "breadth", "resistance-\nrobust", "condition-\nrobust"]
M = np.array([[r["druggability"], r["breadth_frac"], r["resistance_robust"], r["condition_robust"]] for r in top])
fig, (axh, axs) = plt.subplots(1, 2, figsize=(12.0, 4.6), gridspec_kw={"width_ratios": [1.3, 1], "wspace": 0.55})
im = axh.imshow(M, aspect="auto", cmap="YlGn", vmin=0, vmax=1)
axh.set_yticks(range(len(top))); axh.set_yticklabels([f"{r['gene']}  ({r['best_intervention_score']:.2f})" for r in top], fontsize=8)
axh.set_xticks(range(4)); axh.set_xticklabels(axes_names, fontsize=8)
axh.set_title("Fig 4a. Multi-axis best-intervention scorecard\n(top 15 nominated targets; cell = axis value)", fontsize=9.5, loc="left")
fig.colorbar(im, ax=axh, fraction=0.046, pad=0.04, label="axis value (0–1)")
# scatter: score vs experimental essentiality
xs = [r["best_intervention_score"] for r in rk if r["exp_essential_orgs"] is not None]
ys = [r["exp_essential_orgs"] for r in rk if r["exp_essential_orgs"] is not None]
jit = (np.random.default_rng(0).random(len(ys)) - 0.5) * 0.18
axs.scatter(xs, np.array(ys)+jit, s=22, color=PANEL, alpha=0.75, edgecolor="none")
axs.set_xlabel("best-intervention score"); axs.set_ylabel("# organisms experimentally essential (of 3)")
axs.set_yticks([0, 1, 2, 3])
axs.set_title(f"Fig 4b. Score vs experimental essentiality\nSpearman ρ={val['spearman_score_vs_expEssOrgs']}, p={val['p']} (n={val['n']})", fontsize=9.5, loc="left")
save(fig, "fig4_best_intervention_scorecard")

print("all figures ->", FIG)
