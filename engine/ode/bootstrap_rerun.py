"""
bootstrap_rerun.py
==================
Reruns the docetaxel HR bootstrap using Cox PH (not median ratio).
n=1000 bootstrap samples for stable CI.

Fixes: bootstrap_stability.json (currently uses broken median-ratio HR)
Output: results/bootstrap_stability.json (overwritten with correct values)

Run: python3 code/bootstrap_rerun.py
Runtime: 20-40 minutes
"""
import os, sys, json, time, warnings
import numpy as np
import pandas as pd
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intercepta_engine_v1 import PKModel, VirtualCohort
from hr_estimator_fixed import estimate_hr_proper

BASE    = os.path.expanduser('~/INTERCEPTA/')
RESULTS = BASE + 'results/'

print("="*60)
print("BOOTSTRAP RERUN — COX PH, n=1000")
print("="*60)

# ── Parameters ──────────────────────────────────────────────
# From calibrated params
BASE_PARAMS = {
    'g_s': 0.006, 'g_r': 0.003, 'K': 1.0,
    'mu': 3e-5,   'nu': 0,
    'S0': 0.45,   'R0': 0.08,
    'd_natural': 0.001
}
DRUG_PARAMS = {
    'name':     'docetaxel',
    'emax_s':   0.05,
    'emax_r':   0.003,
    'ec50':     0.00987,
    'hill_n':   1.5
}
N_PATIENTS    = 50      # per bootstrap sample
DURATION_DAYS = 1825    # 5 years (matches CHAARTED follow-up)
N_BOOTSTRAP   = 1000
CLINICAL_HR   = 0.61    # CHAARTED published HR (TAX-327)
RANDOM_SEED   = 42

print(f"\nParameters:")
print(f"  Base: {BASE_PARAMS}")
print(f"  Drug: {DRUG_PARAMS}")
print(f"  n_patients: {N_PATIENTS}, duration: {DURATION_DAYS}d")
print(f"  n_bootstrap: {N_BOOTSTRAP}")
print(f"  Target HR: {CLINICAL_HR} (CHAARTED)")

# ── Load existing results (if any) ──────────────────────────
out_path = RESULTS + 'bootstrap_stability.json'
if os.path.exists(out_path):
    with open(out_path) as f:
        existing = json.load(f)
    print(f"\nExisting bootstrap: method='{existing.get('method','?')}', "
          f"n={existing.get('n_bootstrap',0)}, "
          f"HR={existing.get('doc_hr_mean','?')}")
    print("Will overwrite with correct Cox PH results.")

# ── Run bootstrap ────────────────────────────────────────────
print(f"\nRunning {N_BOOTSTRAP} bootstrap iterations...")
print("(Each = simulate 50 patients, compute Cox PH HR)")
print("Progress: ", end='', flush=True)

pk = PKModel('docetaxel')
drug_config = [{
    'name':       DRUG_PARAMS['name'],
    'pk_model':   pk,
    'emax_s':     DRUG_PARAMS['emax_s'],
    'emax_r':     DRUG_PARAMS['emax_r'],
    'ec50':       DRUG_PARAMS['ec50'],
    'hill_n':     DRUG_PARAMS['hill_n'],
}]

hrs          = []
ci_lowers    = []
ci_uppers    = []
logrank_ps   = []
n_events_all = []
t0 = time.time()

for i in range(N_BOOTSTRAP):
    seed = RANDOM_SEED + i
    try:
        vc   = VirtualCohort(n_patients=N_PATIENTS, random_state=seed)
        pts  = vc.generate_patients(BASE_PARAMS)
        ctrl = vc.simulate_cohort(pts, [], DURATION_DAYS)
        trt  = vc.simulate_cohort(pts, drug_config, DURATION_DAYS)

        ct = np.array([r['progression_time'] or DURATION_DAYS for r in ctrl])
        tt = np.array([r['progression_time'] or DURATION_DAYS for r in trt])

        n_events = int(np.sum(ct < DURATION_DAYS) + np.sum(tt < DURATION_DAYS))

        if n_events < 5:
            # Too few events — skip (this sample has 0 informative data)
            continue

        r = estimate_hr_proper(ct, tt, DURATION_DAYS)
        hrs.append(r['hr'])
        ci_lowers.append(r['hr_ci_lower'])
        ci_uppers.append(r['hr_ci_upper'])
        logrank_ps.append(r['logrank_p'])
        n_events_all.append(n_events)

    except Exception:
        continue

    if (i+1) % 100 == 0:
        n_done = len(hrs)
        elapsed = time.time()-t0
        rate = (i+1)/elapsed
        remaining = (N_BOOTSTRAP - i - 1)/rate
        mean_hr = np.mean(hrs) if hrs else float('nan')
        print(f"\n  {i+1}/{N_BOOTSTRAP}: {n_done} valid, "
              f"mean_HR={mean_hr:.3f}, "
              f"{remaining:.0f}s remaining", flush=True)

print(f"\n\nCompleted: {len(hrs)} valid iterations out of {N_BOOTSTRAP}")

if len(hrs) < 100:
    print(f"WARNING: Only {len(hrs)} valid iterations. "
          "Results may be unreliable.")
    if len(hrs) < 10:
        print("FATAL: Too few valid iterations.")
        sys.exit(1)

hrs = np.array(hrs)
ci_lowers = np.array(ci_lowers)
ci_uppers = np.array(ci_uppers)
logrank_ps = np.array(logrank_ps)

# ── Results ─────────────────────────────────────────────────
hr_mean   = float(np.mean(hrs))
hr_median = float(np.median(hrs))
hr_std    = float(np.std(hrs))
hr_ci_lower = float(np.percentile(hrs, 2.5))
hr_ci_upper = float(np.percentile(hrs, 97.5))
clinical_in_ci = bool(hr_ci_lower <= CLINICAL_HR <= hr_ci_upper)
mean_events = float(np.mean(n_events_all))

print(f"\n{'='*50}")
print(f"BOOTSTRAP RESULTS (Cox PH, n={len(hrs)} valid iterations)")
print(f"{'='*50}")
print(f"\n  Docetaxel HR distribution:")
print(f"  Mean:         {hr_mean:.3f}")
print(f"  Median:       {hr_median:.3f}")
print(f"  Std:          {hr_std:.3f}")
print(f"  95% CI:       [{hr_ci_lower:.3f}, {hr_ci_upper:.3f}]")
print(f"  Mean events:  {mean_events:.0f}/{N_PATIENTS*2} per iteration")
print(f"\n  Published CHAARTED HR: {CLINICAL_HR}")
print(f"  CI contains published: {clinical_in_ci}")

if clinical_in_ci:
    print(f"\n  ✓ CHAARTED HR=0.61 IS within simulated CI=[{hr_ci_lower:.3f},{hr_ci_upper:.3f}]")
    print("  The simulation is consistent with the published trial.")
else:
    gap = min(abs(hr_ci_lower-CLINICAL_HR), abs(hr_ci_upper-CLINICAL_HR))
    print(f"\n  ✗ CHAARTED HR=0.61 NOT in CI=[{hr_ci_lower:.3f},{hr_ci_upper:.3f}]")
    print(f"  Gap from CI: {gap:.3f}. Recalibration needed.")

# Significance
sig = np.sum(logrank_ps < 0.05)
print(f"\n  Significant (p<0.05): {sig}/{len(hrs)} iterations "
      f"({sig/len(hrs)*100:.0f}%)")

# ── Save ─────────────────────────────────────────────────────
result = {
    'method':              'cox_ph',
    'n_bootstrap':         len(hrs),
    'n_patients_per_iter': N_PATIENTS,
    'duration_days':       DURATION_DAYS,
    'base_params':         BASE_PARAMS,
    'drug_params':         DRUG_PARAMS,
    'doc_hr_mean':         hr_mean,
    'doc_hr_median':       hr_median,
    'doc_hr_std':          hr_std,
    'doc_hr_ci95':        [hr_ci_lower, hr_ci_upper],
    'doc_hr_all':          hrs.tolist(),
    'clinical_hr_chaarted':CLINICAL_HR,
    'clinical_in_ci':      clinical_in_ci,
    'pct_significant':     float(sig/len(hrs)),
    'mean_events_per_iter':mean_events,
    'timestamp':           pd.Timestamp.now().isoformat(),
}

with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)

print(f"\n  Saved: {out_path}")
print(f"  Total runtime: {(time.time()-t0)/60:.1f} minutes")

print("\n" + "="*60)
print("BOOTSTRAP RERUN COMPLETE")
print("The invalid median-ratio bootstrap has been replaced.")
print("="*60)
