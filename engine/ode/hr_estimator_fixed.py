"""
INTERCEPTA — Fixed HR Estimator
================================
Replaces the broken median-ratio HR in intercepta_engine_v1.py
and intercepta_phenotype_ode_v1.py

WHAT WAS WRONG:
    hr = median_ctrl / median_trt
    This is NOT a hazard ratio. It's just a ratio of medians.
    Valid ONLY under exponential survival — almost never true.

WHAT THIS REPLACES IT WITH:
    1. Log-rank test (p-value for survival difference)
    2. Cox proportional hazards (true HR with 95% CI)
    3. Kaplan-Meier median survival estimates

INSTALL:
    pip install lifelines

USAGE — drop-in replacement for estimate_hr() in both ODE files:
    from hr_estimator_fixed import estimate_hr_proper
    result = estimate_hr_proper(ctrl_ttps, trt_ttps, duration_days)
"""

import numpy as np

try:
    from lifelines import KaplanMeierFitter, CoxPHFitter
    from lifelines.statistics import logrank_test
    import pandas as pd
    LIFELINES_AVAILABLE = True
except ImportError:
    LIFELINES_AVAILABLE = False
    print("WARNING: lifelines not installed. Run: pip install lifelines")
    print("Falling back to median-ratio method (less accurate).")


def estimate_hr_proper(ctrl_ttps: np.ndarray,
                       trt_ttps: np.ndarray,
                       duration_days: float = 1825) -> dict:
    """
    Estimate hazard ratio using proper survival analysis.

    Parameters
    ----------
    ctrl_ttps : array of progression times for control arm (days)
                Use duration_days for censored patients (no progression)
    trt_ttps  : array of progression times for treatment arm (days)
    duration_days : study duration — used to identify censored patients

    Returns
    -------
    dict with:
        hr          : hazard ratio (treatment vs control)
        hr_ci_lower : 95% CI lower bound
        hr_ci_upper : 95% CI upper bound
        logrank_p   : log-rank test p-value
        median_ctrl_months : KM median TTP, control arm
        median_trt_months  : KM median TTP, treatment arm
        benefit_months     : median TTP difference
        n_events_ctrl      : progressions in control
        n_events_trt       : progressions in treatment
        method      : which method was used
    """
    ctrl_ttps = np.array(ctrl_ttps)
    trt_ttps = np.array(trt_ttps)

    # Event indicator: 1 = progressed, 0 = censored (no progression by study end)
    ctrl_events = (ctrl_ttps < duration_days).astype(int)
    trt_events = (trt_ttps < duration_days).astype(int)

    n_events_ctrl = int(ctrl_events.sum())
    n_events_trt = int(trt_events.sum())

    if LIFELINES_AVAILABLE:
        # ── Log-rank test ──
        lr = logrank_test(
            ctrl_ttps, trt_ttps,
            event_observed_A=ctrl_events,
            event_observed_B=trt_events
        )
        logrank_p = float(lr.p_value)

        # ── Cox proportional hazards for HR + CI ──
        df = pd.DataFrame({
            'duration': np.concatenate([ctrl_ttps, trt_ttps]),
            'event':    np.concatenate([ctrl_events, trt_events]),
            'arm':      np.concatenate([
                np.zeros(len(ctrl_ttps)),   # 0 = control
                np.ones(len(trt_ttps))      # 1 = treatment
            ])
        })

        try:
            cph = CoxPHFitter()
            cph.fit(df, duration_col='duration', event_col='event')
            summary = cph.summary

            hr = float(np.exp(summary.loc['arm', 'coef']))
            hr_ci_lower = float(np.exp(summary.loc['arm', 'coef lower 95%']))
            hr_ci_upper = float(np.exp(summary.loc['arm', 'coef upper 95%']))
        except Exception as e:
            # Cox can fail if too few events — fall back to log-rank HR estimate
            print(f"  Cox model failed ({e}), using log-rank HR estimate")
            hr, hr_ci_lower, hr_ci_upper = _logrank_hr_estimate(
                ctrl_ttps, trt_ttps, ctrl_events, trt_events)

        # ── Kaplan-Meier median survival ──
        kmf_ctrl = KaplanMeierFitter()
        kmf_trt = KaplanMeierFitter()
        kmf_ctrl.fit(ctrl_ttps, ctrl_events)
        kmf_trt.fit(trt_ttps, trt_events)

        median_ctrl = float(kmf_ctrl.median_survival_time_)
        median_trt = float(kmf_trt.median_survival_time_)

        # Handle inf median (> 50% not progressed)
        if np.isinf(median_ctrl):
            median_ctrl = duration_days
        if np.isinf(median_trt):
            median_trt = duration_days

        method = 'cox_ph + logrank + kaplan_meier'

    else:
        # ── Fallback: median ratio (old broken method, clearly labeled) ──
        median_ctrl = float(np.median(ctrl_ttps))
        median_trt = float(np.median(trt_ttps))
        hr = median_ctrl / median_trt if median_trt > 0 else 1.0
        hr_ci_lower = hr * 0.7   # rough approximation only
        hr_ci_upper = hr * 1.3
        logrank_p = float('nan')
        method = 'median_ratio_FALLBACK_install_lifelines'
        print("WARNING: Using inaccurate median-ratio HR. Install lifelines!")

    benefit_months = (median_trt - median_ctrl) / 30.44

    return {
        'hr': float(hr),
        'hr_ci_lower': float(hr_ci_lower),
        'hr_ci_upper': float(hr_ci_upper),
        'logrank_p': float(logrank_p) if not np.isnan(logrank_p) else None,
        'median_ctrl_months': median_ctrl / 30.44,
        'median_trt_months': median_trt / 30.44,
        'benefit_months': float(benefit_months),
        'n_events_ctrl': n_events_ctrl,
        'n_events_trt': n_events_trt,
        'n_patients': len(ctrl_ttps),
        'method': method,
    }


def _logrank_hr_estimate(ctrl_ttps, trt_ttps, ctrl_events, trt_events):
    """Simple HR from observed/expected events (Mantel-Haenszel approximation)."""
    n_ctrl = len(ctrl_ttps)
    n_trt = len(trt_ttps)

    o_ctrl = ctrl_events.sum()
    o_trt = trt_events.sum()

    # Expected events under null hypothesis
    n_total = n_ctrl + n_trt
    o_total = o_ctrl + o_trt

    if n_total == 0 or o_total == 0:
        return 1.0, 0.5, 2.0

    e_ctrl = o_total * n_ctrl / n_total
    e_trt = o_total * n_trt / n_total

    if e_ctrl == 0 or e_trt == 0:
        return 1.0, 0.5, 2.0

    hr = (o_trt / e_trt) / (o_ctrl / e_ctrl)

    # Approximate CI using Greenwood formula
    var_log_hr = 1/o_ctrl + 1/o_trt if o_ctrl > 0 and o_trt > 0 else 1.0
    se = np.sqrt(var_log_hr)

    hr_ci_lower = hr * np.exp(-1.96 * se)
    hr_ci_upper = hr * np.exp(+1.96 * se)

    return float(hr), float(hr_ci_lower), float(hr_ci_upper)


# ── Quick test ──
if __name__ == '__main__':
    np.random.seed(42)

    # Simulate control arm: exponential survival, median 12 months
    ctrl = np.random.exponential(scale=365, size=100)
    ctrl = np.clip(ctrl, 0, 1825)

    # Simulate treatment arm: median 18 months (HR ~ 0.67)
    trt = np.random.exponential(scale=548, size=100)
    trt = np.clip(trt, 0, 1825)

    result = estimate_hr_proper(ctrl, trt, duration_days=1825)

    print("HR estimator test (true HR ≈ 0.67):")
    print(f"  HR = {result['hr']:.3f} (95% CI: {result['hr_ci_lower']:.3f}–{result['hr_ci_upper']:.3f})")
    print(f"  Log-rank p = {result['logrank_p']:.4f}" if result['logrank_p'] else "  Log-rank p = N/A")
    print(f"  Control median: {result['median_ctrl_months']:.1f} mo")
    print(f"  Treatment median: {result['median_trt_months']:.1f} mo")
    print(f"  Benefit: {result['benefit_months']:+.1f} mo")
    print(f"  Method: {result['method']}")
