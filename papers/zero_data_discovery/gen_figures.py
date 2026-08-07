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

# ---- Figure 1: PRIMARY validation — curated cross-Gram / cross-phylum panel (CROSSVAL_curated) ----
cv = L("CROSSVAL_curated/results/CROSSVAL_metrics.json")["summary"]["panel"]
CLADE_COL = {"gamma-proteo (Gram-)": "#3b6ea5", "Firmicute (Gram+)": "#2e8b57", "Actinobacteria": "#8a5a2b"}
HELD = {"K. pneumoniae", "S. aureus (MRSA)"}   # not in the 7-organism development panel
rows = [(name, d["clade"], d["model"], d["odds_ratio"], d["fisher_p"], d["precision"], d["recall"], name in HELD)
        for name, d in cv.items()]
rows.sort(key=lambda r: r[3])
fig, ax = plt.subplots(figsize=(8.4, 4.0))
y = np.arange(len(rows))
ax.barh(y, [r[3] for r in rows], color=[CLADE_COL.get(r[1], "#777") for r in rows], height=0.64,
        edgecolor=["black" if r[7] else "none" for r in rows], linewidth=[1.6 if r[7] else 0 for r in rows])
ax.axvline(3, ls="--", color="grey", lw=1); ax.text(3, len(rows)-0.4, " pre-registered gate (OR>3)", color="grey", fontsize=8, va="top")
for i, r in enumerate(rows):
    p = r[4]; ptxt = "p<1e-15" if (p is not None and p < 1e-15) else (f"p={p:.0e}" if p else "")
    ax.text(r[3]*1.04, i, f"OR {r[3]:.0f}  {ptxt}  (prec {r[5]:.2f}, rec {r[6]:.2f})", va="center", fontsize=7.6)
ax.set_yticks(y); ax.set_yticklabels([f"{r[0]}\n({r[2]})" for r in rows], fontsize=8.3)
ax.set_xscale("log"); ax.set_xlim(1, 250)
ax.set_xlabel("Odds ratio: FBA-essential enriched for EXPERIMENTALLY-essential genes (log scale)")
ax.set_title("Fig 1. FBA gene-essentiality vs experimental essentiality — 6 CURATED models across 3 phyla (all pass; bold outline = held-out)", fontsize=8.8, loc="left")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=CLADE_COL["gamma-proteo (Gram-)"], label="γ-proteobacteria (Gram−)"),
                   Patch(color=CLADE_COL["Firmicute (Gram+)"], label="Firmicutes (Gram+)"),
                   Patch(color=CLADE_COL["Actinobacteria"], label="Actinobacteria"),
                   Patch(facecolor="white", edgecolor="black", linewidth=1.6, label="held-out (not in dev panel)")],
          loc="lower right", fontsize=7.6, frameon=False)
save(fig, "fig1_curated_crossphylum_validation")

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


# ==================== PART II FIGURES (generalization frontier + composite) ====================
# Every value below is read from a committed reproduced-x2 experiment JSON via P(). No hand-typed numbers.
def P(path):
    d = json.load(open(os.path.join(ROOT, "experiments", path)))
    return d.get("payload", d.get("summary", d))

GREEN, RED, GREY, BLUE, GOLD = "#2e8b57", "#c1442e", "#8a8a8a", "#3b6ea5", "#c98a17"

# ---- Figure 5: FBA-essentiality across disease classes + the Plasmodium GEM swap (transfer + noise floor) ----
g4 = P("GENERALIZE4_fungal_fba/results/GENERALIZE4_metrics.json")
hf = P("HARDENF1_fungal_multi/results/HARDENF1_metrics.json")
g5 = P("GENERALIZE5_parasite_fba/results/GENERALIZE5_metrics.json")["primary"]
hp = P("HARDENP1_parasite_multi/results/HARDENP1_metrics.json")["primary"]
swap = P("PARARESOLVE1_parasite_confound/results/PARARESOLVE1_metrics.json")["swap_results"]
fig, (axA, axB) = plt.subplots(1, 2, figsize=(12.2, 4.5), gridspec_kw={"width_ratios": [1, 1], "wspace": 0.42})
# Panel A: OR by organism/class (bacteria anchor from CROSSVAL best = E.coli iML1515, read from cv)
ecoli_or = cv["E. coli"]["odds_ratio"]
barsA = [("E. coli\n(bacterium, iML1515)", ecoli_or, BLUE),
         ("S. cerevisiae\n(eukaryote)", g4["odds_ratio"], GREEN),
         ("C. albicans\n(fungal pathogen)", hf["odds_ratio"], GREEN),
         ("P. falciparum\n(parasite, iPfal19)", g5["odds_ratio"], RED),
         ("T. gondii\n(parasite, iTgo2020)", hp["odds_ratio"], GOLD)]
y = np.arange(len(barsA))
axA.barh(y, [b[1] for b in barsA], color=[b[2] for b in barsA], height=0.66)
axA.axvline(3, ls="--", color="grey", lw=1); axA.text(3, -0.45, "gate OR>3", color="grey", fontsize=8, ha="center")
for i, b in enumerate(barsA): axA.text(b[1]*1.05, i, f"{b[1]:.1f}", va="center", fontsize=8.5)
axA.set_yticks(y); axA.set_yticklabels([b[0] for b in barsA], fontsize=8.2)
axA.set_xscale("log"); axA.set_xlim(0.7, 90)
axA.set_xlabel("Odds ratio (FBA-essential vs experimentally-essential, log)")
axA.set_title("Fig 5A. FBA-essentiality transfers across classes —\nbut is GEM/organism-specific for parasites", fontsize=8.8, loc="left")
axA.invert_yaxis()
# Panel B: Plasmodium GEM swap — OR spans the gate; one independent GEM passes; base rate ~invariant
order = [s for s in swap]
order.sort(key=lambda s: s["odds_ratio"])
kcol = {"reference": BLUE, "independent": RED, "same_lineage": GREY}
yy = np.arange(len(order))
axB.barh(yy, [s["odds_ratio"] for s in order], color=[kcol[s["kind"]] for s in order], height=0.66,
         edgecolor=["black" if s["gate_pass"] else "none" for s in order],
         linewidth=[1.8 if s["gate_pass"] else 0 for s in order])
axB.axvline(3, ls="--", color="grey", lw=1); axB.text(3, len(order)-0.4, " gate OR>3", color="grey", fontsize=8, va="top")
toxo_or = hp["odds_ratio"]; axB.axvline(toxo_or, ls=":", color=GOLD, lw=1.4); axB.text(toxo_or, -0.4, f"T. gondii {toxo_or:.0f}", color=GOLD, fontsize=7.5, ha="center")
for i, s in enumerate(order): axB.text(s["odds_ratio"]*1.04, i, f"{s['odds_ratio']:.2f}", va="center", fontsize=7.8)
axB.set_yticks(yy); axB.set_yticklabels([s["label"].replace("_", " ")[:22] for s in order], fontsize=7.6)
axB.set_xscale("log"); axB.set_xlim(0.7, 22)
axB.set_xlabel("Odds ratio (log)")
axB.set_title("Fig 5B. Six P. falciparum GEMs (same organism+screen)\nspan the gate: it sits at Plasmodium's noise floor", fontsize=8.8, loc="left")
from matplotlib.patches import Patch
axB.legend(handles=[Patch(color=BLUE, label="reference iPfal19"), Patch(color=RED, label="independent team"),
                    Patch(color=GREY, label="same-lineage variant"), Patch(fc="white", ec="black", label="passes gate")],
           fontsize=7, loc="lower right", frameon=False)
save(fig, "fig5_fba_generalization_and_parasite_swap")

# ---- Figure 6: Viral structural target-class recovery across 5 viruses (leakage-controlled) ----
hv = P("HARDENV1_virus_multi/results/HARDENV1_metrics.json")
pt = hv["per_target"]; tm_bar = hv["tm_bar"]
items = sorted(pt.items(), key=lambda kv: (kv[1]["virus"], kv[0]))
labels = [f"{r['virus']}: {k.split('_',1)[1]}" for k, r in items]
corr_tm = [r["best_correct_class_tm"] for _, r in items]
off_tm = [r["best_offclass_tm"] for _, r in items]
recov = [r["RECOVER"] for _, r in items]
fig, ax = plt.subplots(figsize=(9.2, 4.6))
x = np.arange(len(items)); w = 0.38
ax.bar(x - w/2, corr_tm, w, color=[GREEN if r else GREY for r in recov], label="best CORRECT-class hit (TM)")
ax.bar(x + w/2, off_tm, w, color="#d9b38c", label="best off-class hit (TM)")
ax.axhline(tm_bar, ls="--", color="grey", lw=1); ax.text(len(items)-0.5, tm_bar+0.01, f"gate TM≥{tm_bar}", color="grey", fontsize=8, ha="right")
for i, r in enumerate(recov):
    if not r: ax.text(i - w/2, corr_tm[i] + 0.015, "✗", color=RED, ha="center", fontsize=10)
ax.set_xticks(x); ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=7.6)
ax.set_ylabel("Foldseek TM-score to reference"); ax.set_ylim(0, 0.85)
nrec = hv["n_recover"]; nt = hv["n_targets"]; nv = hv["n_viruses"]
ax.set_title(f"Fig 6. STRUCTURE recovers viral drug-target class where sequence gives 0 — {nrec}/{nt} targets across {nv} viruses\n(own-family excluded from reference; correct class > off-class where green exceeds tan)", fontsize=8.6, loc="left")
ax.legend(fontsize=8, loc="upper right", frameon=False)
save(fig, "fig6_viral_structural_recovery")

# ---- Figure 7: Human-cancer dependency — validated target-ID + patient relevance + the two negatives ----
dep = P("DEPEND1_functional_dependency/results/DEPEND1_metrics.json")
f3 = P("F3CLIN1_dependency_patient_relevance/results/F3CLIN1_metrics.json")
tr = P("TRANSFER1_labelfree_zeroscreen/results/TRANSFER1_metrics.json")
fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.8, 4.4), gridspec_kw={"width_ratios": [1, 1], "wspace": 0.42})
# Left: DEPEND1 recovery (train/held-out) + null; and label-free rho vs baseline
g1 = dep["G1"]["recovery_top10"]; g2 = dep["G2_test"]["recovery_top10"]; nullr = dep["null_recovery_top10"]
rho_m = dep["G3"]["median_abs_rho_model"]; rho_b = dep["G3"]["median_abs_rho_own_expr"]
barsL = [("known-target\nrecovery@10", g1, GREEN), ("HELD-OUT lines\nrecovery@10", g2, GREEN),
         ("random\nnull", nullr, GREY), ("label-free\nexpr→dep |ρ|", rho_m, BLUE), ("own-expr\nbaseline |ρ|", rho_b, GREY)]
xx = np.arange(len(barsL))
axL.bar(xx, [b[1] for b in barsL], color=[b[2] for b in barsL], width=0.66)
for i, b in enumerate(barsL): axL.text(i, b[1]+0.015, f"{b[1]:.2f}" if b[1] >= 0.01 else f"{b[1]:.4f}", ha="center", fontsize=8)
axL.set_xticks(xx); axL.set_xticklabels([b[0] for b in barsL], fontsize=7.6)
axL.set_ylabel("recovery fraction / |Spearman ρ|"); axL.set_ylim(0, 1.0)
axL.set_title("Fig 7A. Functional-dependency target-ID (DepMap):\nrecovers known targets, generalizes held-out, learnable label-free", fontsize=8.6, loc="left")
# Right: patient-driver enrichment (F3CLIN1) surviving study-bias, vs the two negatives
f_or = f3["fisher_2x2"]["OR"]; mh_or = f3["guard_c_mantel_haenszel"]["mh_or"]
# DECISIVE TRANSFER1 negative: SELECTIVE signal AMONG ortholog-havers (i.e. BEYOND mere conservation) = chance.
# (Not scoring_over_U.b_selective=1.96, which is inflated by unconditioned conservation — using that would
#  misrepresent a first-class negative as a near-miss.)
tr_sel = tr["decisive_beyond_conservation_among_ortholog_havers"]["selective_only"]["odds_ratio"]  # 0.90
tr_cons = tr["scoring_over_U"]["NULL_A_conservation"]["odds_ratio"]  # conservation-only null over universe
barsR = [("patient-driver\nenrichment (raw)", f_or, GREEN),
         ("...study-bias\ncorrected (M-H)", mh_or, GREEN),
         ("label-free transfer,\nSELECTIVE beyond\nconservation (zero-screen)", tr_sel, RED),
         ("conservation-only\n(what DOES transfer,\nbut redundant)", tr_cons, GREY)]
xr = np.arange(len(barsR))
axR.bar(xr, [b[1] for b in barsR], color=[b[2] for b in barsR], width=0.66)
axR.axhline(1.0, ls="-", color="black", lw=0.8); axR.axhline(2.0, ls="--", color="grey", lw=1); axR.text(len(barsR)-0.5, 2.03, "OR=2", color="grey", fontsize=8, ha="right")
for i, b in enumerate(barsR): axR.text(i, b[1]+0.05, f"{b[1]:.2f}", ha="center", fontsize=8.5)
axR.set_xticks(xr); axR.set_xticklabels([b[0] for b in barsR], fontsize=7.3)
axR.set_ylabel("Odds ratio"); axR.set_ylim(0, 3.2)
axR.set_title("Fig 7B. Patient relevance is REAL (survives study-bias),\nbut label-free transfer to a novel organism is NOT (a first-class negative)", fontsize=8.4, loc="left")
save(fig, "fig7_human_dependency_and_negatives")

print("Part II figures done.")
