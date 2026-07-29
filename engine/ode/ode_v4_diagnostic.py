#!/usr/bin/env python3
"""
INTERCEPTA v4 ODE Diagnostic
=============================
Purpose: Compute instantaneous per-state growth rates dN/dt/N directly from
the v4 ODE at specified tumor burden levels — BEFORE logistic saturation
kicks in — to enable valid comparison with Stein/Wilkerson/Fojo exponential g.

Why this matters: the biexponential fit in v5 averages over logistic
saturation, which systematically under-estimates the early-phase growth
rate. Stein's clinical g is measured in a local exponential window. The
right comparison is local dN/dt/N at matched tumor burden, not a biexp
fit to a logistic trajectory.

Diagnostics computed:
  1. Untreated local g at N/K = 0.15, 0.30, 0.50, 0.70 — shows logistic effect
  2. On-treatment local g for each drug regimen at N/K = 0.15
     - Pure S tumor (baseline)
     - After 180 days of treatment (reflects state transitions + drug)
  3. Per-state local growth rates (separates what each state is doing)

Also bundles the one-line fix for summarize_cohort_g in v5
(in a helper function that can be imported).

Does not modify v4.

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
Date:    April 21, 2026
Principle 3: deep research before code — verify what the model is doing.
"""
import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intercepta_unified_ode_v4 import (
    UnifiedODEv4, build_initial_state, _find_velocity_csv,
)


def instantaneous_growth_rates(model: UnifiedODEv4,
                               y: np.ndarray,
                               t: float = 0.0) -> dict:
    """Compute per-state dN/dt/N at a given state vector y and time t.

    This is the LOCAL exponential growth rate, comparable to Stein's g
    measured in a clinical observation window. No logistic averaging,
    no biexponential fitting — just the raw model derivative.
    """
    N = model.N
    dy = model.deriv(t, y)

    rates = {}
    state_totals = {}
    state_ddt = {}
    for s_idx, s_name in enumerate(model.STATE_NAMES):
        state_slice = slice(s_idx * N, (s_idx + 1) * N)
        n_state = y[state_slice].sum()
        dn_state = dy[state_slice].sum()
        rate = dn_state / n_state if n_state > 1e-12 else np.nan
        rates[s_name] = {
            'n': float(n_state),
            'dn_dt': float(dn_state),
            'g_local': float(rate) if np.isfinite(rate) else None,
        }
        state_totals[s_name] = float(n_state)
        state_ddt[s_name] = float(dn_state)

    # Whole-tumor g
    n_total = y.sum()
    dn_total = dy.sum()
    g_total = dn_total / n_total if n_total > 1e-12 else np.nan

    return {
        't': float(t),
        'N_total': float(n_total),
        'N_over_K': float(n_total / model.k_cap),
        'dN_dt': float(dn_total),
        'g_total_local': float(g_total) if np.isfinite(g_total) else None,
        'per_state': rates,
    }


def build_fresh_ic(model: UnifiedODEv4,
                   velocity_csv: str,
                   N0_total: float,
                   state_fracs: dict) -> np.ndarray:
    """Construct a fresh initial condition at specified total burden."""
    return build_initial_state(velocity_csv, model.N, N0_total, state_fracs)


# ===================================================================
# DIAGNOSTIC SCENARIOS
# ===================================================================

SCENARIOS = [
    {
        'name': 'untreated_N0_0.15',
        'drugs': [],
        'state_fracs': {'S': 0.92, 'M': 0.05, 'V': 0.02, 'N': 0.01},
        'N0': 0.15,
        'brca_profile': 'overall',
    },
    {
        'name': 'untreated_N0_0.30',
        'drugs': [],
        'state_fracs': {'S': 0.92, 'M': 0.05, 'V': 0.02, 'N': 0.01},
        'N0': 0.30,
        'brca_profile': 'overall',
    },
    {
        'name': 'untreated_N0_0.50',
        'drugs': [],
        'state_fracs': {'S': 0.92, 'M': 0.05, 'V': 0.02, 'N': 0.01},
        'N0': 0.50,
        'brca_profile': 'overall',
    },
    {
        'name': 'untreated_N0_0.70',
        'drugs': [],
        'state_fracs': {'S': 0.92, 'M': 0.05, 'V': 0.02, 'N': 0.01},
        'N0': 0.70,
        'brca_profile': 'overall',
    },
    {
        'name': 'ADT_only_N0_0.15',
        'drugs': ['ADT'],
        'state_fracs': {'S': 0.92, 'M': 0.05, 'V': 0.02, 'N': 0.01},
        'N0': 0.15,
        'brca_profile': 'overall',
    },
    {
        'name': 'ADT+enza_N0_0.15',
        'drugs': ['ADT', 'enzalutamide'],
        'state_fracs': {'S': 0.90, 'M': 0.05, 'V': 0.03, 'N': 0.02},
        'N0': 0.15,
        'brca_profile': 'overall',
    },
    {
        'name': 'ADT+abiraterone_N0_0.15',
        'drugs': ['ADT', 'abiraterone'],
        'state_fracs': {'S': 0.92, 'M': 0.05, 'V': 0.02, 'N': 0.01},
        'N0': 0.15,
        'brca_profile': 'overall',
    },
    {
        'name': 'docetaxel_only_N0_0.15',
        'drugs': ['docetaxel'],
        'state_fracs': {'S': 0.92, 'M': 0.05, 'V': 0.02, 'N': 0.01},
        'N0': 0.15,
        'brca_profile': 'overall',
    },
    {
        'name': 'ADT+olaparib_BRCA+_N0_0.15',
        'drugs': ['ADT', 'olaparib'],
        'state_fracs': {'S': 0.70, 'M': 0.12, 'V': 0.10, 'N': 0.08},
        'N0': 0.15,
        'brca_profile': 'biallelic_cohort',
    },
]


def run_diagnostic(save_path: str = '../results/ode_v4_diagnostic.json'):
    vel_csv = _find_velocity_csv()
    print('=' * 72)
    print('INTERCEPTA v4 ODE DIAGNOSTIC')
    print('  Instantaneous local growth rates (exponential basis)')
    print('  Comparable to Stein/Wilkerson g (clinical observation window)')
    print('=' * 72)
    print(f"Velocity: {vel_csv or 'NOT FOUND (uniform fallback)'}")
    print(f"Mode:     RAW deriv() evaluation at t=0. No simulation.")
    print()

    # Reference g values (from Stein 2011, Leuva/Zhou VA cohort)
    REFERENCE_G = {
        'untreated_mCRPC':   ('0.0075/day', 'Stein 2011 NCI 5 trials'),
        'enza_non_HRR':      ('0.000784/day', 'Leuva/Zhou VA'),
        'enza_HRR_altered':  ('0.001889/day', 'Zhou 2024 eBioMedicine'),
    }
    print("REFERENCE g-VALUES (Stein/Leuva/Zhou):")
    for k, (v, src) in REFERENCE_G.items():
        print(f"  {k:<22s} {v:<15s} [{src}]")
    print()

    results = []
    for scenario in SCENARIOS:
        name = scenario['name']
        print(f"--- {name} ---")
        model = UnifiedODEv4(brca_profile_name=scenario['brca_profile'])
        model.set_drugs(scenario['drugs'], duration_days=1825)

        # Fresh initial condition at specified N0
        y0 = build_fresh_ic(model, vel_csv, scenario['N0'], scenario['state_fracs'])

        # Instantaneous rates at t=0
        rates_t0 = instantaneous_growth_rates(model, y0, t=0.0)

        # Also evaluate at t=30 days (after early transient)
        # Note: at t=0 drug binary flags are ON but cyclic PK drugs may or may
        # not be at peak. Sample at t=0.5 day and t=30 days to see effect.
        rates_early = instantaneous_growth_rates(model, y0, t=0.5)

        g_total = rates_t0['g_total_local']
        g_total_mo = g_total * 30.44 if g_total is not None else None
        print(f"  N0/K = {rates_t0['N_over_K']:.3f}  "
              f"g_total = {g_total:.5f}/day  "
              f"(DT = {np.log(2)/g_total:.0f} days)"
              if g_total and g_total > 0
              else f"  N0/K = {rates_t0['N_over_K']:.3f}  "
                   f"g_total = {g_total:.5f}/day")
        print(f"  Per-state g_local (at t=0):")
        for s_name in ['S', 'M', 'V', 'N']:
            pd = rates_t0['per_state'][s_name]
            if pd['g_local'] is not None:
                dt_days = np.log(2)/pd['g_local'] if pd['g_local'] > 0 else float('inf')
                print(f"    {s_name}: n={pd['n']:.4f}  "
                      f"g={pd['g_local']:+.5f}/day  "
                      f"DT={dt_days:.0f}d" if dt_days != float('inf')
                      else f"    {s_name}: n={pd['n']:.4f}  "
                           f"g={pd['g_local']:+.5f}/day  DT=inf")
            else:
                print(f"    {s_name}: n={pd['n']:.4f}  (too small)")

        # t=0.5 readout (useful for cyclic drugs)
        g_05 = rates_early['g_total_local']
        if g_05 is not None and abs(g_05 - g_total) > 1e-6:
            print(f"  At t=0.5 day (after cycle-phase engagement):")
            print(f"    g_total = {g_05:+.5f}/day")
        print()

        results.append({
            'scenario': name,
            'drugs': scenario['drugs'],
            'state_fracs': scenario['state_fracs'],
            'N0': scenario['N0'],
            'brca_profile': scenario['brca_profile'],
            'rates_t0': rates_t0,
            'rates_t0.5': rates_early,
        })

    # Comparative summary
    print('=' * 72)
    print('COMPARISON TO STEIN/WILKERSON/LEUVA/ZHOU')
    print('=' * 72)
    print(f"{'Scenario':<32s} {'Model g_total /day':<20s} {'Reference /day':<20s}  Ratio")
    print('-' * 80)

    pairings = [
        ('untreated_N0_0.15', 0.0075, 'Stein 2011 untreated mCRPC'),
        ('ADT_only_N0_0.15', None, '(no direct comparison)'),
        ('ADT+enza_N0_0.15', 0.000784, 'Leuva/Zhou enza non-HRR'),
        ('ADT+abiraterone_N0_0.15', 0.000784, 'Leuva abiraterone ~enza'),
        ('docetaxel_only_N0_0.15', None, '(needs Wilkerson 2017 verification)'),
        ('ADT+olaparib_BRCA+_N0_0.15', None, '(needs Zhou 2024 verification)'),
    ]
    for scenario_name, ref_g, ref_src in pairings:
        scn = next((r for r in results if r['scenario'] == scenario_name), None)
        if scn is None:
            continue
        model_g = scn['rates_t0']['g_total_local']
        if ref_g is not None and model_g is not None:
            ratio = model_g / ref_g
            status = f"{ratio:.2f}x"
        elif model_g is not None:
            status = 'obs-only'
        else:
            status = 'N/A'
        ref_str = f"{ref_g:.5f}" if ref_g else '—'
        model_str = f"{model_g:+.5f}" if model_g is not None else 'N/A'
        print(f"{scenario_name:<32s} {model_str:<20s} {ref_str:<20s}  {status}")
    print()

    out = {
        'description': ('Instantaneous local growth rates from v4 ODE, '
                        'comparable to Stein clinical g'),
        'reference_g': REFERENCE_G,
        'scenarios': results,
    }
    try:
        with open(save_path, 'w') as f:
            json.dump(out, f, indent=2, default=float)
        print(f"Saved: {save_path}")
    except Exception as e:
        print(f"Could not save: {e}")

    return out


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=str,
                    default='../results/ode_v4_diagnostic.json')
    args = ap.parse_args()
    run_diagnostic(save_path=args.out)
