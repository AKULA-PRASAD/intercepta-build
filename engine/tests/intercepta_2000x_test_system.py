import numpy as np
import math
import random
import traceback

# =========================
# CONFIG
# =========================
T_HALF_RANGE = [0.1, 0.5, 1, 2, 5]
EMAX_RANGE = [0.01, 0.03, 0.05, 0.1]
EC50_RANGE = [0.1, 1, 10]
DOSE_RANGE = [0.01, 0.1, 1, 10, 100]
MU_RANGE = [0.0001, 0.001, 0.01]
GROWTH_RANGE = [0.01, 0.02, 0.05]

DT = 0.1
T_MAX = 100

TOTAL_TESTS = 0
PASS = 0
FAIL = 0

# =========================
# PK MODEL
# =========================
def pk_conc(dose, t_half, t, V=31):
    ke = math.log(2) / t_half
    C0 = dose / V
    return C0 * np.exp(-ke * t), ke

# =========================
# ODE MODEL
# =========================
def simulate(params):
    t_half, emax, ec50, dose, mu, g_s = params
    g_r = g_s / 2
    K = 1.0

    t = np.arange(0, T_MAX, DT)
    S = np.zeros_like(t)
    R = np.zeros_like(t)

    S[0] = 0.9
    R[0] = 0.1

    for i in range(1, len(t)):
        C, _ = pk_conc(dose, t_half, t[i])
        effect = (emax * C) / (ec50 + C)

        dS = g_s * S[i-1] * (1 - (S[i-1] + R[i-1]) / K) - effect * S[i-1] - mu * S[i-1]
        dR = g_r * R[i-1] * (1 - (S[i-1] + R[i-1]) / K) + mu * S[i-1]

        S[i] = max(S[i-1] + dS * DT, 0)
        R[i] = max(R[i-1] + dR * DT, 0)

    return t, S, R

# =========================
# UTIL
# =========================
def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print("FAIL:", msg)

def generate_param_grid():
    for t_half in T_HALF_RANGE:
        for emax in EMAX_RANGE:
            for ec50 in EC50_RANGE:
                for dose in DOSE_RANGE:
                    for mu in MU_RANGE:
                        for g_s in GROWTH_RANGE:
                            yield (t_half, emax, ec50, dose, mu, g_s)

# =========================
# TESTS
# =========================
def test_pk():
    global TOTAL_TESTS
    for t_half in T_HALF_RANGE:
        _, ke = pk_conc(1, t_half, 0)
        expected = math.log(2) / t_half
        check(abs(ke - expected) < 1e-6, "PK mismatch t_half=" + str(t_half))
        TOTAL_TESTS += 1

def test_ode():
    global TOTAL_TESTS
    for params in generate_param_grid():
        t, S, R = simulate(params)

        check(np.all(S >= 0), "negative S")
        check(np.all(R >= 0), "negative R")
        check(np.max(S+R) <= 1.01, "exceeds K")

        if params[3] > 0:
            check(R[-1] >= R[0], "resistance not increasing")

        TOTAL_TESTS += 4

def test_dose_response():
    global TOTAL_TESTS
    for params in random.sample(list(generate_param_grid()), 50):
        results = []
        for d in DOSE_RANGE:
            p = list(params)
            p[3] = d
            _, S, R = simulate(p)
            results.append(S[-1] + R[-1])

        ok = all(results[i] >= results[i+1] for i in range(len(results)-1))
        check(ok, "dose response fail")
        TOTAL_TESTS += 1

def test_perturbation():
    global TOTAL_TESTS
    for params in random.sample(list(generate_param_grid()), 100):
        _, S1, R1 = simulate(params)

        perturbed = [p * 1.05 for p in params]
        _, S2, R2 = simulate(perturbed)

        diff = abs((S1[-1]+R1[-1]) - (S2[-1]+R2[-1]))
        check(diff < 0.2, "unstable system")

        TOTAL_TESTS += 1

def test_extreme():
    global TOTAL_TESTS
    for params in random.sample(list(generate_param_grid()), 50):
        p = list(params)
        p[3] = 1e6

        _, S, R = simulate(p)
        check(S[-1]+R[-1] < 0.2, "extreme dose fail")

        TOTAL_TESTS += 1

def test_determinism():
    global TOTAL_TESTS
    for params in random.sample(list(generate_param_grid()), 50):
        _, S1, R1 = simulate(params)
        _, S2, R2 = simulate(params)

        check(np.allclose(S1, S2), "non deterministic")

        TOTAL_TESTS += 1

# =========================
# MAIN
# =========================
def run_all():
    print("="*60)
    print("INTERCEPTA 2000X TEST")
    print("="*60)

    test_pk()
    test_ode()
    test_dose_response()
    test_perturbation()
    test_extreme()
    test_determinism()

    print("="*60)
    print("TOTAL:", TOTAL_TESTS)
    print("PASS:", PASS)
    print("FAIL:", FAIL)
    print("="*60)

run_all()
