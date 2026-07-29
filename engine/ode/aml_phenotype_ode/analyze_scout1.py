#!/usr/bin/env python3
"""
INTERCEPTA — Analyze Scout 1 Results
Classifies 769 compounds by population target, estimates ODE parameters,
and identifies optimal novel combinations.

Run: python3 scripts/analyze_scout1.py
"""
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

RESULTS = os.path.join(os.path.dirname(__file__), '..', 'results')

print("=" * 70)
print("INTERCEPTA — Scout 1 Analysis & ODE Integration")
print("=" * 70)

df = pd.read_csv(os.path.join(RESULTS, 'scout1_chembl_hits.csv'))
print(f"\n[1/5] Loaded {len(df)} compounds from Scout 1")

# ═══ Analysis ═══
print(f"\n[2/5] Compound analysis:")
print(f"  Unique ChEMBL IDs: {df.chembl_id.nunique()}")
print(f"  Approved drugs: {df.is_approved.sum()}")
print(f"  Clinical-stage: {df.is_clinical.sum()}")
print(f"  Novel (pre-clinical): {(~df.is_clinical).sum()}")
print(f"  Multi-target: {(df.n_net_targets > 1).sum()}")

print(f"\n  Activity by target:")
print(f"  {'Target':<10} {'Count':>6} {'Median IC50':>12} {'Best IC50':>10} {'Approved':>9}")
print(f"  {'-'*10} {'-'*6} {'-'*12} {'-'*10} {'-'*9}")

for target in sorted(df.target_gene.unique()):
    tdf = df[df.target_gene == target]
    print(f"  {target:<10} {len(tdf):>6} {tdf.activity_nM.median():>11.1f}nM "
          f"{tdf.activity_nM.min():>9.2f}nM {tdf.is_approved.sum():>9}")

# ═══ Population classification ═══
print(f"\n[3/5] Classify by population targeting:")

SENSITIVE_TARGETS = {"AR", "CDK4", "CDK6", "MDM2", "MAP2K1", "MAPK1"}
RESISTANT_TARGETS = {"PARP1", "PARP2", "ATM", "ATR", "CHEK1", "CHEK2", "EZH2", "AURKA"}
ESCAPE_TARGETS = {"PIK3CA", "PIK3CB", "AKT1", "MTOR", "KRAS", "BRAF"}
IMMUNE_TARGETS = {"CD274"}
APOPTOSIS_TARGETS = {"BCL2", "MCL1"}

def classify_population(target):
    if target in SENSITIVE_TARGETS: return "sensitive"
    if target in RESISTANT_TARGETS: return "resistant"
    if target in ESCAPE_TARGETS: return "escape_route"
    if target in IMMUNE_TARGETS: return "immune"
    if target in APOPTOSIS_TARGETS: return "apoptosis"
    return "other"

df['population_target'] = df.target_gene.apply(classify_population)

for pop in ['sensitive', 'resistant', 'escape_route', 'immune', 'apoptosis']:
    sub = df[df.population_target == pop]
    if len(sub) > 0:
        print(f"  {pop:<15} {len(sub):>4} compounds (best IC50: {sub.activity_nM.min():.2f}nM)")

# ═══ Estimate ODE emax ═══
print(f"\n[4/5] Estimate ODE drug parameters:")

BASE_EMAX = 0.005

def estimate_emax(row):
    ic50_nM = max(row['activity_nM'], 0.1)
    potency = np.clip(np.log10(100 / ic50_nM), -1, 3)
    emax_scale = BASE_EMAX * (1 + 0.5 * potency)
    pop = row['population_target']
    if pop == "sensitive":    return emax_scale, emax_scale * 0.15
    elif pop == "resistant":  return emax_scale * 0.20, emax_scale
    elif pop == "escape_route": return emax_scale * 0.40, emax_scale * 0.60
    elif pop == "apoptosis":  return emax_scale * 0.30, emax_scale * 0.70
    else: return emax_scale * 0.50, emax_scale * 0.50

emax_s_list, emax_r_list = [], []
for _, row in df.iterrows():
    es, er = estimate_emax(row)
    emax_s_list.append(round(es, 6))
    emax_r_list.append(round(er, 6))
df['est_emax_s'] = emax_s_list
df['est_emax_r'] = emax_r_list

print(f"\n  Top SENSITIVE-targeting compounds:")
sens = df[df.population_target == 'sensitive'].sort_values('activity_nM').head(8)
for _, r in sens.iterrows():
    print(f"    {r['name'][:30]:<30} {r.target_gene:<8} IC50={r.activity_nM:>8.2f}nM "
          f"emax_s={r.est_emax_s:.5f}  {'[APPROVED]' if r.is_approved else ''}")

print(f"\n  Top RESISTANT-targeting compounds:")
res = df[df.population_target == 'resistant'].sort_values('activity_nM').head(8)
for _, r in res.iterrows():
    print(f"    {r['name'][:30]:<30} {r.target_gene:<8} IC50={r.activity_nM:>8.2f}nM "
          f"emax_r={r.est_emax_r:.5f}  {'[APPROVED]' if r.is_approved else ''}")

print(f"\n  Top ESCAPE ROUTE blockers:")
esc = df[df.population_target == 'escape_route'].sort_values('activity_nM').head(5)
for _, r in esc.iterrows():
    print(f"    {r['name'][:30]:<30} {r.target_gene:<8} IC50={r.activity_nM:>8.2f}nM  "
          f"{'[APPROVED]' if r.is_approved else ''}")

# ═══ Novel combinations ═══
print(f"\n[5/5] Top predicted novel combinations:")
print(f"  (S-killer + R-killer = covers both populations)\n")

best_s = df[df.population_target == 'sensitive'].sort_values('activity_nM').head(5)
best_r = df[df.population_target == 'resistant'].sort_values('activity_nM').head(5)

rank = 0
combos = []
for _, s_row in best_s.iterrows():
    for _, r_row in best_r.iterrows():
        if s_row.chembl_id == r_row.chembl_id:
            continue
        rank += 1
        score = s_row.est_emax_s + r_row.est_emax_r
        combos.append({
            'rank': rank,
            's_name': s_row['name'][:25],
            's_target': s_row.target_gene,
            's_ic50': s_row.activity_nM,
            'r_name': r_row['name'][:25],
            'r_target': r_row.target_gene,
            'r_ic50': r_row.activity_nM,
            'combined_score': score,
            's_approved': s_row.is_approved,
            'r_approved': r_row.is_approved,
        })
        if rank >= 10:
            break
    if rank >= 10:
        break

combos.sort(key=lambda c: c['combined_score'], reverse=True)
for i, c in enumerate(combos, 1):
    novel_tag = ""
    if not c['s_approved'] and not c['r_approved']:
        novel_tag = " [BOTH NOVEL]"
    elif not c['s_approved'] or not c['r_approved']:
        novel_tag = " [PARTIALLY NOVEL]"
    
    print(f"  #{i}: {c['s_name']:<25} ({c['s_target']}, {c['s_ic50']:.1f}nM)")
    print(f"     + {c['r_name']:<25} ({c['r_target']}, {c['r_ic50']:.1f}nM)")
    print(f"     Combined emax score: {c['combined_score']:.5f}{novel_tag}")
    print()

# Save enriched data
df.to_csv(os.path.join(RESULTS, 'scout1_enriched.csv'), index=False)

# Save combination predictions
combo_df = pd.DataFrame(combos)
combo_df.to_csv(os.path.join(RESULTS, 'scout1_novel_combos.csv'), index=False)

print(f"{'='*70}")
print(f"ANALYSIS COMPLETE")
print(f"  {len(df)} compounds classified and parameterized")
print(f"  {(df.population_target=='sensitive').sum()} sensitive-targeting")
print(f"  {(df.population_target=='resistant').sum()} resistant-targeting")
print(f"  {(df.population_target=='escape_route').sum()} escape-route blockers")
print(f"  {len(combos)} novel combinations predicted")
print(f"  Saved: results/scout1_enriched.csv")
print(f"  Saved: results/scout1_novel_combos.csv")
print(f"{'='*70}")
