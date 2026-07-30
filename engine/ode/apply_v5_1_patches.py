#!/usr/bin/env python3
"""
INTERCEPTA v5 -> v5.1 patch
============================

Two minimal changes to intercepta_g_rate_validation_v5.py to produce
intercepta_g_rate_validation_v5_1.py:

Change A — Import v4.1 instead of v4.
  The v4.1 ODE has the two sourced corrections from memo v2:
  olaparib/talazoparib emax_parp 0.15 -> 0.015 and R_MAX citation update.
  All other logic identical.

Change B — Fix the KeyError crash in summarize_cohort_g.
  When no patient produces a fittable g (e.g., olaparib in v4 where the
  kill was so complete that only pure-decay fits succeed), the early-
  return dict at line 349 omits 'model_types', 'mean_g', 'median_d',
  'n_with_d'. The driver then crashes on `stats['model_types']`.
  Fix: always return the full schema; populate fields with None/zero
  when there's no data.

Neither change affects any scientific quantity. This is purely
plumbing: correct target + crash-safe output.

Run from ~/INTERCEPTA/code/:
    python3 apply_v5_1_patches.py

Author: Prasad Akula
Date:    April 21, 2026
"""
import os
import sys


def apply_patch(src_path: str, dst_path: str):
    if not os.path.exists(src_path):
        print(f"ERROR: source file not found: {src_path}")
        sys.exit(1)

    with open(src_path) as f:
        src = f.read()

    # --- Change A: import v4 -> v4_1 ---
    # Original import block in v5 looks like:
    #     from intercepta_unified_ode_v4 import (
    #         UnifiedODEv4, build_initial_state, _find_velocity_csv,
    #         _sample_patient_params, _sample_drug_overrides, _sample_state_fracs,
    #         trial_definitions,
    #     )
    old_import = "from intercepta_unified_ode_v4 import ("
    new_import = "from intercepta_unified_ode_v4_1 import ("
    if old_import not in src:
        print("ERROR: expected v4 import line not found. Aborting.")
        sys.exit(2)
    src = src.replace(old_import, new_import)

    # Also update any descriptive strings that reference the model version
    src = src.replace(
        "Model:    UnifiedODEv4 (unchanged from rPFS validation)",
        "Model:    UnifiedODEv4.1 (with sourced PARP correction + Stein R_MAX cite)"
    )
    src = src.replace(
        "'model': 'INTERCEPTA Unified ODE v4 + g-rate validation v5'",
        "'model': 'INTERCEPTA Unified ODE v4.1 + g-rate validation v5.1'"
    )

    # --- Change B: fix the early-return schema in summarize_cohort_g ---
    # The broken early-return omits keys the driver needs.
    old_early_return = """    if not g_values:
        return {'n_total': n_total, 'n_fit': n_fit, 'n_with_g': 0,
                'median_g': None, 'iqr_g': None}"""
    new_early_return = """    # Always return the full schema, even when no g could be fit.
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
        }"""
    if old_early_return not in src:
        print("ERROR: summarize_cohort_g early-return block not found exactly. Aborting.")
        sys.exit(3)
    src = src.replace(old_early_return, new_early_return)

    # Also update the main return block to use the already-computed
    # model_type_counts dict for consistency.
    old_main_return_tail = """        'mean_g': float(np.mean(g_arr)),
        'median_d': float(np.median(d_values)) if d_values else None,
        'model_types': {
            'gd': sum(1 for f in fits if f.get('model_type') == 'gd'),
            'g_only': sum(1 for f in fits if f.get('model_type') == 'g_only'),
            'd_only': sum(1 for f in fits if f.get('model_type') == 'd_only'),
        },
    }"""
    new_main_return_tail = """        'mean_g': float(np.mean(g_arr)),
        'median_d': float(np.median(d_values)) if d_values else None,
        'model_types': model_type_counts,
    }"""
    if old_main_return_tail not in src:
        print("WARNING: main return tail not matched exactly; skipping that minor cleanup.")
    else:
        src = src.replace(old_main_return_tail, new_main_return_tail)

    # --- Update docstring header ---
    old_header = "INTERCEPTA g-Rate Validation — v5"
    new_header = "INTERCEPTA g-Rate Validation — v5.1"
    if old_header in src:
        src = src.replace(old_header, new_header, 1)  # only the first (title) occurrence

    # Add version note to the module docstring
    old_version_line = "Rather than matching clinical rPFS or Cox hazard ratios"
    if old_version_line in src:
        prepend = (
            "v5.1 changes vs v5:\n"
            "  - Import UnifiedODEv4_1 (includes sourced PARP emax correction per memo v2)\n"
            "  - Fix KeyError crash in summarize_cohort_g when no patient has fittable g\n"
            "    (previously crashed on olaparib cohort; pure-decay runs now handled cleanly)\n"
            "No scientific logic changes in v5.1 itself.\n\n"
        )
        src = src.replace(old_version_line, prepend + old_version_line)

    # Also update the argparse default save path so we don't overwrite v5 results
    src = src.replace(
        "default='../results/unified_v5_g_validation.json'",
        "default='../results/unified_v5_1_g_validation.json'"
    )

    with open(dst_path, 'w') as f:
        f.write(src)
    print(f"v5.1 written: {dst_path}")
    print(f"  - Import:               v4 -> v4_1")
    print(f"  - summarize_cohort_g:   fixed KeyError on zero-g-fit cohorts")
    print(f"  - Default output path:  unified_v5_1_g_validation.json")


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else 'intercepta_g_rate_validation_v5.py'
    dst = sys.argv[2] if len(sys.argv) > 2 else 'intercepta_g_rate_validation_v5_1.py'
    apply_patch(src, dst)
