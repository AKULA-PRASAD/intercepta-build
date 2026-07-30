#!/usr/bin/env python3
"""
INTERCEPTA g-Rate Validation — v5.2
==================================
New validation strategy following Stein/Wilkerson/Fojo framework.

v5.2 changes vs v5.1 (audit fix, no science change):
  - Remove strict 0.05<a<0.95 boundary in fit_g_rate classification.
  - Accept biexp fit when r2>0.90 and both d,g are meaningfully
    nonzero, regardless of 'a' mixture fraction. Extreme-a fits
    (a=0.99 with small residual growing fraction) are valid biology
    and were being wrongly discarded.
  - Only retry with simpler models when biexp fit itself is poor
    (r2<=0.90), not when 'a' is extreme.
  - Audit found this bug caused 49/50 olaparib-v4.1 fits to be
    rejected, masking the fact that the model DOES produce
    clinically-appropriate regrowth dynamics.

v5.1 changes vs v5:
  - Import UnifiedODEv4_1 (includes sourced PARP emax correction per memo v2)
  - Fix KeyError crash in summarize_cohort_g when no patient has fittable g
    (previously crashed on olaparib cohort; pure-decay runs now handled cleanly)
No scientific logic changes in v5.1 itself.

Rather than matching clinical rPFS or Cox hazard ratios (both of which are
trial-design artifacts), we validate our mechanistic ODE against the growth
rate constant `g` — the exponential regrowth rate of the treatment-refractory
tumor fraction. `g` is:

  - A directly measurable biological quantity (from serial PSA or imaging)
  - Validated across 20,000+ mCRPC patients in published work
  - Directly producible by our ODE (no clinical-protocol interpretation)
  - Drug-specific and patient-population-specific

Wilkerson/Stein biexponential model:
    N(t) / N(0) = a * exp(-d*t) + (1-a) * exp(g*t)
where:
    a = initial fraction of tumor that is treatment-sensitive
    d = regression rate constant of sensitive fraction (/day)
    g = growth rate constant of refractory fraction (/day)

Primary references:
  Stein WD et al., Oncologist 2008;13:1046-1054 (n=112 mCRPC, validation)
  Stein WD et al., Clin Cancer Res 2011;17:907 (NCI 5 trials)
  Wilkerson J et al., Lancet Oncol 2017;18:143 (2,353 mCRPC, 8 trials)
  Leuva H et al., Urol Oncol 2020 (VA Veterans abi/enza)
  Zhou M et al., eBioMedicine 2024 (VA Veterans olaparib cohort)

This file imports UnifiedODEv4 (unchanged) and validates against g-rates.
Original v4 rPFS-based validation is preserved in its own file.

Author: Prasad Akula
Date:    April 21, 2026
Principle 15: validate against biologically-grounded endpoints, not trial artifacts.
"""
import os
import sys
import json
import warnings
import numpy as np
from scipy.optimize import curve_fit
from typing import Dict, List, Optional, Tuple

# Import v4 ODE (unchanged)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intercepta_unified_ode_v4_1 import (
    UnifiedODEv4, build_initial_state, _find_velocity_csv,
    _sample_patient_params, _sample_drug_overrides, _sample_state_fracs,
    trial_definitions,
)


# ===================================================================
# PUBLISHED g-VALUES (validation targets)
# ===================================================================
# Each entry: regimen identifier -> dict with:
#   g_published: point estimate (/day)
#   dt_days:     doubling time for reference
#   source:      citation
#   population:  mCRPC stage and genetic context
#   window:      acceptable range for model match (conservative ±50%)
#   confidence:  'confirmed' | 'needs_verification'
# ===================================================================

PUBLISHED_G_VALUES: Dict[str, dict] = {
    # Enza first-line, reference (non-HRR) mCRPC.
    # From VA cohort analysis (Leuva 2020 / Zhou 2024 eBioMedicine,
    # reference arm to the olaparib-HRR comparison).
    'enzalutamide_non_HRR': {
        'g_published': 0.000784,
        'dt_days': 884.0,
        'source': 'VA Veterans cohort, ~8000 patients',
        'citation': 'Leuva 2020 Urol Oncol / Zhou 2024 eBioMedicine',
        'population': 'mCRPC, first-line enza, no HRR alterations',
        'window': (0.0004, 0.0015),   # ~2x either direction, biology-wide
        'confidence': 'confirmed',
    },
    'enzalutamide_HRR_altered': {
        'g_published': 0.001889,
        'dt_days': 367.0,
        'source': 'VA Veterans cohort',
        'citation': 'Zhou 2024 eBioMedicine Table 3',
        'population': 'mCRPC, first-line enza, HRR-altered',
        'window': (0.001, 0.003),
        'confidence': 'confirmed',
    },
    # Pre-treatment / untreated mCRPC growth from Stein 2011.
    # log g ranges -2.0 to -2.3 across trials -> g = 0.005 to 0.010/day.
    'mCRPC_pretreatment': {
        'g_published': 0.0075,
        'dt_days': 92.0,
        'source': 'NCI 5 trials pre-study g distribution',
        'citation': 'Stein 2011 Clin Cancer Res, log g median ~-2.15',
        'population': 'mCRPC pre-treatment or off-treatment baseline',
        'window': (0.005, 0.012),
        'confidence': 'confirmed',
    },
    # Drugs below: paper identified, but specific g-value requires
    # reading the full text. Flagged for verification.
    'docetaxel_mCRPC': {
        'g_published': None,  # TO VERIFY from Wilkerson 2017 Table 2
        'dt_days': None,
        'source': 'Wilkerson 2017 Lancet Oncol',
        'citation': 'Wilkerson 2017 Lancet Oncol, Table 2 (to retrieve)',
        'population': 'mCRPC on docetaxel, TAX-327-era',
        'window': None,
        'confidence': 'needs_verification',
        'note': ('Wilkerson 2017 reports that g increased ~5x after docetaxel '
                 'discontinuation. If off-treatment g ~0.005-0.010/day, then '
                 'on-docetaxel g ~0.001-0.002/day. Needs exact value from paper.'),
    },
    'mitoxantrone_mCRPC': {
        'g_published': None,
        'dt_days': None,
        'source': 'Wilkerson 2017 Lancet Oncol',
        'citation': 'Wilkerson 2017 Lancet Oncol, Table 2',
        'population': 'mCRPC on mitoxantrone, TAX-327-era',
        'window': None,
        'confidence': 'needs_verification',
        'note': ('Wilkerson 2017: g differentiated docetaxel from mitoxantrone. '
                 'Mitoxantrone g should be faster than docetaxel g, likely '
                 '~0.003-0.006/day. Needs exact value.'),
    },
    'abiraterone_first_line': {
        'g_published': None,
        'dt_days': None,
        'source': 'Leuva 2020 Urol Oncol',
        'citation': 'Leuva 2020 Table 2 (to retrieve)',
        'population': 'mCRPC first-line abiraterone',
        'window': None,
        'confidence': 'needs_verification',
        'note': 'Paper reports abi vs enza comparable first-line, so g similar to enza ~0.0008/day.',
    },
    'olaparib_HRR_altered': {
        'g_published': None,
        'dt_days': None,
        'source': 'Zhou 2024 eBioMedicine',
        'citation': 'Zhou 2024 Table 3 (to retrieve exact olaparib g)',
        'population': 'mCRPC HRR-altered on olaparib monotherapy',
        'window': None,
        'confidence': 'needs_verification',
    },
}


# ===================================================================
# BIEXPONENTIAL FIT (Stein/Wilkerson)
# ===================================================================

def _biexp_model(t, a, d, g):
    """N(t)/N(0) = a*exp(-d*t) + (1-a)*exp(g*t). a in [0,1], d>0, g>0."""
    return a * np.exp(-d * t) + (1.0 - a) * np.exp(g * t)


def fit_g_rate(t: np.ndarray, N_t: np.ndarray,
               min_points: int = 10) -> Optional[dict]:
    """Fit Wilkerson biexponential to simulated N(t) trajectory.

    Returns dict with g, d, a, r2, model_type, or None if fit fails.
    model_type in {'gd', 'g_only', 'd_only'} for the three Stein cases.

    Note: Stein fits PSA; we fit total cell burden. The math is identical
    because both follow the same biexponential kinetics: sensitive cells
    die exponentially (decay rate d) while refractory cells grow
    exponentially (rate g). N(t)/N(0) is the normalized form.
    """
    if len(t) < min_points:
        return None

    N_t = np.asarray(N_t, dtype=float)
    t = np.asarray(t, dtype=float)

    # Normalize to N(0)
    N0 = N_t[0]
    if N0 <= 0:
        return None
    f = N_t / N0

    # Protect against extreme values
    if not np.all(np.isfinite(f)) or np.any(f < 0):
        return None

    # Try full biexponential (both regression and growth)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            popt, pcov = curve_fit(
                _biexp_model, t, f,
                p0=[0.9, 0.01, 0.001],
                bounds=([0.0, 1e-6, 1e-7], [1.0, 1.0, 0.1]),
                maxfev=10000,
            )
        a, d, g = popt
        pred = _biexp_model(t, a, d, g)
        ss_res = np.sum((f - pred) ** 2)
        ss_tot = np.sum((f - f.mean()) ** 2)
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

        # v5.2 AUDIT FIX: classify by fit quality and parameter meaningfulness,
        # NOT by the mixture fraction 'a'. A biexponential fit with a=0.999
        # (tumor almost fully killed but small residual growing fraction) is
        # valid biology — it describes highly effective PARP/targeted therapy.
        # The old code rejected those and retried with decay-only, losing the g.
        #
        # Parameters are at curve_fit bounds when:
        #   d near lower bound 1e-6 -> regression phase is absent
        #   g near lower bound 1e-7 -> growth phase is absent
        #   d near upper bound 1.0  -> unphysical, probably overfit noise
        #   g near upper bound 0.1  -> unphysical, same
        D_BOUND_LO = 5e-6   # 5x the curve_fit lower bound
        G_BOUND_LO = 5e-7   # 5x the curve_fit lower bound
        D_BOUND_HI = 0.9    # 90% of upper bound
        G_BOUND_HI = 0.09   # 90% of upper bound

        d_meaningful = D_BOUND_LO < d < D_BOUND_HI
        g_meaningful = G_BOUND_LO < g < G_BOUND_HI

        if r2 > 0.90 and d_meaningful and g_meaningful:
            # Both phases present and fit is good: full biexponential.
            # Accept regardless of 'a' mixture fraction.
            return {'a': float(a), 'd': float(d), 'g': float(g),
                    'r2': float(r2), 'model_type': 'gd'}
        elif r2 > 0.90 and g_meaningful and not d_meaningful:
            # Fit converged but d is negligible -> effectively growth-only.
            # Report g from the biexp fit directly.
            return {'a': 0.0, 'd': None, 'g': float(g),
                    'r2': float(r2), 'model_type': 'g_only'}
        elif r2 > 0.90 and d_meaningful and not g_meaningful:
            # Fit converged but g is negligible -> effectively decay-only.
            # Report d from the biexp fit directly.
            return {'a': 1.0, 'd': float(d), 'g': None,
                    'r2': float(r2), 'model_type': 'd_only'}
        else:
            # Biexp fit genuinely poor (r2 <= 0.90): retry with simpler
            # models in case the data is pure decay or pure growth.
            return _fit_best_simpler(t, f)
    except (RuntimeError, ValueError):
        return _fit_best_simpler(t, f)


def _fit_growth_only(t, f, prev_r2=0.0):
    """Exponential growth: f(t) = exp(g*t). Used when treatment ineffective."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            popt, _ = curve_fit(
                lambda tt, g: np.exp(g * tt), t, f,
                p0=[0.001], bounds=([1e-7], [0.1]), maxfev=5000)
        g = popt[0]
        pred = np.exp(g * t)
        ss_res = np.sum((f - pred) ** 2)
        ss_tot = np.sum((f - f.mean()) ** 2)
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
        if r2 > prev_r2:
            return {'a': 0.0, 'd': None, 'g': float(g),
                    'r2': float(r2), 'model_type': 'g_only'}
    except Exception:
        pass
    return None


def _fit_decay_only(t, f, prev_r2=0.0):
    """Exponential decay: f(t) = exp(-d*t). Used when treatment highly effective."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            popt, _ = curve_fit(
                lambda tt, d: np.exp(-d * tt), t, f,
                p0=[0.01], bounds=([1e-7], [1.0]), maxfev=5000)
        d = popt[0]
        pred = np.exp(-d * t)
        ss_res = np.sum((f - pred) ** 2)
        ss_tot = np.sum((f - f.mean()) ** 2)
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
        if r2 > prev_r2:
            return {'a': 1.0, 'd': float(d), 'g': None,
                    'r2': float(r2), 'model_type': 'd_only'}
    except Exception:
        pass
    return None


def _fit_best_simpler(t, f):
    """Try both growth-only and decay-only, return best."""
    g_fit = _fit_growth_only(t, f)
    d_fit = _fit_decay_only(t, f)
    if g_fit and d_fit:
        return g_fit if g_fit['r2'] > d_fit['r2'] else d_fit
    return g_fit or d_fit


# ===================================================================
# PER-PATIENT g-RATE COHORT
# ===================================================================

def simulate_cohort_with_g_extraction(
        drug_list: List[str],
        velocity_csv: Optional[str],
        brca_profile_name: str,
        state_fracs: Dict[str, float],
        duration_days: int,
        n_patients: int,
        random_state: int = 42,
        fit_window_days: int = 540,
) -> List[dict]:
    """Simulate heterogeneous cohort and fit g-rate to each patient's N(t).

    fit_window_days: only fit biexponential over first N days post-baseline.
    Stein/Wilkerson fit was over treatment duration (typically 6-18 months).
    Longer windows risk capturing multi-phase behavior the biexponential
    can't represent.
    """
    rng = np.random.RandomState(random_state)
    per_patient_fits = []

    for i in range(n_patients):
        burden_factor = float(np.exp(rng.normal(0, 0.25)))
        N0_i = min(0.15 * burden_factor, 0.8)

        param_overrides = _sample_patient_params(rng)
        drug_overrides = _sample_drug_overrides(drug_list, rng)
        patient_state_fracs = _sample_state_fracs(state_fracs, rng)

        model = UnifiedODEv4(
            brca_profile_name=brca_profile_name,
            param_overrides=param_overrides,
            drug_overrides=drug_overrides,
        )
        model.set_drugs(drug_list, duration_days)

        y0 = build_initial_state(velocity_csv, model.N, N0_i, patient_state_fracs)
        res = model.simulate(y0, duration_days)
        if not res['success']:
            per_patient_fits.append({'success': False, 'patient': i})
            continue

        t = res['t']
        N_t = res['N_t']
        # Fit window
        mask = t <= fit_window_days
        if mask.sum() < 20:
            per_patient_fits.append({'success': False, 'patient': i,
                                     'reason': 'insufficient_timepoints'})
            continue

        fit = fit_g_rate(t[mask], N_t[mask])
        if fit is None:
            per_patient_fits.append({'success': False, 'patient': i,
                                     'reason': 'fit_failed'})
            continue

        fit['success'] = True
        fit['patient'] = i
        fit['N0'] = float(N0_i)
        fit['final_N_over_N0'] = float(N_t[-1] / N_t[0]) if N_t[0] > 0 else None
        per_patient_fits.append(fit)

    return per_patient_fits


def summarize_cohort_g(fits: List[dict]) -> dict:
    """Compute median, IQR, quantiles of g across successfully-fit patients."""
    g_values = [f['g'] for f in fits
                if f.get('success') and f.get('g') is not None]
    d_values = [f['d'] for f in fits
                if f.get('success') and f.get('d') is not None]
    n_total = len(fits)
    n_fit = sum(1 for f in fits if f.get('success'))

    # Always return the full schema, even when no g could be fit.
    # Driver iterates stats['model_types'] unconditionally, so we must
    # populate it whether or not any patient gave a fittable g-rate.
    model_type_counts = {
        'gd':     sum(1 for f in fits if f.get('model_type') == 'gd'),
        'g_only': sum(1 for f in fits if f.get('model_type') == 'g_only'),
        'd_only': sum(1 for f in fits if f.get('model_type') == 'd_only'),
    }
    if not g_values:
        return {
            'n_total': n_total,
            'n_fit': n_fit,
            'n_with_g': 0,
            'n_with_d': len(d_values),
            'median_g': None,
            'iqr_g': None,
            'mean_g': None,
            'median_d': float(np.median(d_values)) if d_values else None,
            'model_types': model_type_counts,
        }

    g_arr = np.array(g_values)
    return {
        'n_total': n_total,
        'n_fit': n_fit,
        'n_with_g': len(g_values),
        'n_with_d': len(d_values),
        'median_g': float(np.median(g_arr)),
        'iqr_g': [float(np.percentile(g_arr, 25)),
                  float(np.percentile(g_arr, 75))],
        'mean_g': float(np.mean(g_arr)),
        'median_d': float(np.median(d_values)) if d_values else None,
        'model_types': model_type_counts,
    }


# ===================================================================
# VALIDATION DRIVER
# ===================================================================
# Map each trial regimen to the published g-value it should match.
# Format: trial_name -> (drug_list, target_key, brca_profile, state_fracs, duration)
# ===================================================================

# Define which regimens we can score against g-published values.
# For now: anything using enza alone or enza+ADT can map to
# enzalutamide_non_HRR. Mixed regimens (combos) have no direct g-published
# value and are reported observationally only.

G_VALIDATION_REGIMENS: Dict[str, dict] = {
    'enza_first_line_noHRR': {
        'drugs': ['ADT', 'enzalutamide'],
        'target_key': 'enzalutamide_non_HRR',
        'brca_profile': 'overall',
        'state_fracs': {'S': 0.90, 'M': 0.05, 'V': 0.03, 'N': 0.02},
        'duration_days': 1825,
        'description': 'First-line ADT+enza in non-HRR mCRPC',
    },
    'enza_first_line_HRR': {
        'drugs': ['ADT', 'enzalutamide'],
        'target_key': 'enzalutamide_HRR_altered',
        'brca_profile': 'hrr_cohort',
        'state_fracs': {'S': 0.85, 'M': 0.06, 'V': 0.06, 'N': 0.03},
        'duration_days': 1825,
        'description': 'First-line ADT+enza in HRR-altered mCRPC',
    },
    'untreated_mCRPC': {
        'drugs': [],  # no treatment
        'target_key': 'mCRPC_pretreatment',
        'brca_profile': 'overall',
        'state_fracs': {'S': 0.92, 'M': 0.05, 'V': 0.02, 'N': 0.01},
        'duration_days': 365,  # shorter window for pure growth
        'description': 'Untreated mCRPC baseline growth',
    },
    # Regimens below: observational only until we have confirmed g-target
    'docetaxel_mono_mCRPC': {
        'drugs': ['docetaxel'],
        'target_key': 'docetaxel_mCRPC',
        'brca_profile': 'overall',
        'state_fracs': {'S': 0.90, 'M': 0.05, 'V': 0.03, 'N': 0.02},
        'duration_days': 1825,
        'description': 'Docetaxel monotherapy mCRPC (TAX-327-like)',
    },
    'mitoxantrone_mono_mCRPC': {
        'drugs': ['mitoxantrone'],
        'target_key': 'mitoxantrone_mCRPC',
        'brca_profile': 'overall',
        'state_fracs': {'S': 0.90, 'M': 0.05, 'V': 0.03, 'N': 0.02},
        'duration_days': 1825,
        'description': 'Mitoxantrone monotherapy mCRPC (TAX-327 control)',
    },
    'olaparib_HRR_post_ARSI': {
        'drugs': ['ADT', 'olaparib'],
        'target_key': 'olaparib_HRR_altered',
        'brca_profile': 'biallelic_cohort',
        'state_fracs': {'S': 0.70, 'M': 0.12, 'V': 0.10, 'N': 0.08},
        'duration_days': 1825,
        'description': 'Olaparib in BRCA+ post-ARSI mCRPC (PROfound-like)',
    },
}


def run_g_validation(n_patients: int = 50,
                     save_path: str = '../results/unified_v5_g_validation.json'):
    """Run g-rate validation across regimens with published g-targets."""
    vel_csv = _find_velocity_csv()
    print('=' * 72)
    print('INTERCEPTA v5 — g-RATE VALIDATION')
    print('  Stein/Wilkerson/Fojo framework')
    print('=' * 72)
    print(f"Velocity: {vel_csv or 'NOT FOUND (uniform fallback)'}")
    print(f"Cohort:   {n_patients} patients per regimen (heterogeneous)")
    print(f"Model:    UnifiedODEv4.1 + g-fit v5.2 (audit-corrected boundary logic)")
    print(f"Endpoint: biexponential g via scipy.curve_fit on simulated N(t)")
    print()

    summary = {}
    confirmed_pass = 0
    confirmed_total = 0

    for regimen_name, spec in G_VALIDATION_REGIMENS.items():
        target_key = spec['target_key']
        target = PUBLISHED_G_VALUES[target_key]

        print(f"--- {regimen_name} ---")
        print(f"  Drugs: {spec['drugs'] or '(none — untreated)'}")
        print(f"  Target: {target_key}  "
              f"({'CONFIRMED' if target['confidence']=='confirmed' else 'UNVERIFIED'})")

        fits = simulate_cohort_with_g_extraction(
            drug_list=spec['drugs'],
            velocity_csv=vel_csv,
            brca_profile_name=spec['brca_profile'],
            state_fracs=spec['state_fracs'],
            duration_days=spec['duration_days'],
            n_patients=n_patients,
            random_state=42,
        )

        stats = summarize_cohort_g(fits)
        model_g = stats['median_g']

        print(f"  Fit success: {stats['n_fit']}/{stats['n_total']}  "
              f"(g-fits: {stats['n_with_g']})")
        print(f"  Model types: {stats['model_types']}")

        result = {
            'regimen': regimen_name,
            'drugs': spec['drugs'],
            'target_key': target_key,
            'target_confidence': target['confidence'],
            'target_g': target['g_published'],
            'target_citation': target['citation'],
            'model_median_g': model_g,
            'model_iqr_g': stats['iqr_g'],
            'n_with_g_fit': stats['n_with_g'],
            'n_patients': n_patients,
            'model_types': stats['model_types'],
        }

        # Only score PASS/FAIL against confirmed targets
        if target['confidence'] == 'confirmed' and model_g is not None:
            confirmed_total += 1
            lo, hi = target['window']
            passed = (lo <= model_g <= hi)
            if passed:
                confirmed_pass += 1
            result['passed'] = passed
            result['target_window'] = [lo, hi]
            ratio = model_g / target['g_published']
            print(f"  Published g: {target['g_published']:.4g}/day  "
                  f"(DT {target['dt_days']:.0f} days)")
            print(f"  Model g:     {model_g:.4g}/day  "
                  f"(DT {np.log(2)/model_g:.0f} days)"
                  if model_g > 0 else f"  Model g:     {model_g:.4g}/day (DT inf)")
            print(f"  Ratio model/published: {ratio:.2f}x")
            print(f"  Acceptable window: [{lo:.4g}, {hi:.4g}]/day  "
                  f"|  {'PASS' if passed else 'FAIL'}")
        else:
            result['passed'] = None
            if model_g is not None:
                print(f"  Model g:     {model_g:.4g}/day  "
                      f"(DT {np.log(2)/model_g:.0f} days)  OBSERVATIONAL")
            else:
                print(f"  Model g:     insufficient g-fits  OBSERVATIONAL")
            if target.get('note'):
                print(f"  Note: {target['note']}")

        print()
        summary[regimen_name] = result

    print('=' * 72)
    print(f"CONFIRMED TARGETS: {confirmed_pass}/{confirmed_total} pass")
    print(f"OBSERVATIONAL:     {len(G_VALIDATION_REGIMENS) - confirmed_total} regimens")
    print('=' * 72)
    print()
    print("Confirmed targets are those with g-published values verified")
    print("from the literature. Observational regimens produce model g-values")
    print("to be compared once target g-values are retrieved from the source")
    print("papers (Wilkerson 2017, Leuva 2020, Zhou 2024 full text).")

    out = {
        'model': 'INTERCEPTA Unified ODE v4.1 + g-rate validation v5.2 (audit-corrected fitter)',
        'framework': 'Stein/Wilkerson/Fojo biexponential',
        'n_patients_per_regimen': n_patients,
        'confirmed_pass': confirmed_pass,
        'confirmed_total': confirmed_total,
        'regimens': summary,
        'published_targets': {k: {x: v[x] for x in v if x != 'note'}
                              for k, v in PUBLISHED_G_VALUES.items()},
    }

    try:
        with open(save_path, 'w') as f:
            json.dump(out, f, indent=2, default=float)
        print(f"\nResults saved: {save_path}")
    except Exception as e:
        print(f"\nCould not save to {save_path}: {e}")

    return out


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=50)
    ap.add_argument('--out', type=str,
                    default='../results/unified_v5_2_g_validation.json')
    args = ap.parse_args()
    run_g_validation(n_patients=args.n, save_path=args.out)
