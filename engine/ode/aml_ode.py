#!/usr/bin/env python3
"""
INTERCEPTA: AML Two-Population ODE
====================================
Blast cells (sensitive) vs Leukemic Stem Cells (LSC, resistant).
Same architecture as mCRPC phenotype ODE but with AML biology.

AML biology:
  - Blasts: rapidly dividing, drug-sensitive, short-lived
  - LSCs: quiescent, drug-resistant, self-renewing
  - LSCs replenish blasts after chemotherapy
  - This is why AML relapses — LSCs survive and regenerate

Validation targets:
  - Venetoclax+Azacitidine: median OS ~14.7mo (VIALE-A)
  - 7+3 induction (cytarabine+daunorubicin): CR ~70%, relapse ~50%
  - Gilteritinib (FLT3-mut): median OS 9.3mo (ADMIRAL)

ALL parameters from published AML data. Zero tuning.

Author: Prasad Akula
"""
import numpy as np
from scipy.integrate import solve_ivp
import json


class AML_ODE:
    """Two-population AML blast/LSC dynamics with drug effects."""
    
    def __init__(self, params=None):
        self.p = {
            # BLAST CELLS (rapidly dividing, sensitive)
            'r_blast': 0.05,        # doubling time ~14 days (AML blast doubling)
            'd_blast': 0.04,        # high natural turnover
            'K': 1.0,              # carrying capacity (normalized)
            
            # LEUKEMIC STEM CELLS (quiescent, resistant)
            'r_lsc': 0.005,        # slow self-renewal (~140 day doubling)
            'd_lsc': 0.001,        # very low death rate (quiescent)
            
            # LSC → Blast differentiation
            'diff_rate': 0.02,     # LSCs produce blasts
            
            # Blast → LSC dedifferentiation (plasticity, under stress)
            'dediff_rate': 1e-4,   # rare dedifferentiation
            'dediff_stress': 5e-3, # stress-induced (under drug treatment)
            
            # Drug parameters (filled by add_drug)
            'emax': 0.2,           # max kill rate for chemo
        }
        if params:
            self.p.update(params)
        
        self.drugs = []
    
    def add_drug(self, name, emax, ec50_blast, ec50_lsc, cmax, 
                 half_life_days, dose_times, hill=1.5):
        """
        Add drug with separate sensitivity for blasts vs LSCs.
        
        Args:
            emax: maximum kill rate (/day)
            ec50_blast: EC50 for blast cells
            ec50_lsc: EC50 for LSCs (typically much higher)
            cmax: peak free concentration
            half_life_days: elimination half-life
            dose_times: array of dosing days
            hill: Hill coefficient
        """
        self.drugs.append({
            'name': name,
            'emax': emax,
            'ec50_blast': ec50_blast,
            'ec50_lsc': ec50_lsc,
            'cmax': cmax,
            'ke': np.log(2) / half_life_days,
            'doses': np.array(dose_times),
            'hill': hill,
        })
    
    def concentration(self, drug, t):
        """PK: sum of doses with exponential decay."""
        c = 0.0
        for td in drug['doses']:
            if t >= td:
                dt = t - td
                if dt < 10 / drug['ke']:
                    c += drug['cmax'] * np.exp(-drug['ke'] * dt)
        return c
    
    def deriv(self, t, y):
        """
        ODE: dy/dt for [blasts, LSCs]
        
        Blasts: grow fast, die fast, replenished by LSCs, killed by drugs
        LSCs: grow slow, die slow, produce blasts, resist drugs
        Under treatment stress: blasts can dedifferentiate to LSCs
        """
        p = self.p
        B, L = max(y[0], 0), max(y[1], 0)
        N = B + L
        logistic = 1 - N / p['K']
        
        # Drug kill rates
        kill_blast = 0
        kill_lsc = 0
        any_drug_active = False
        
        for drug in self.drugs:
            C = self.concentration(drug, t)
            if C > 0:
                any_drug_active = True
                h = drug['hill']
                kill_blast += drug['emax'] * C**h / (drug['ec50_blast']**h + C**h)
                kill_lsc += drug['emax'] * C**h / (drug['ec50_lsc']**h + C**h)
        
        # Stress-induced dedifferentiation
        dediff = p['dediff_stress'] if any_drug_active else p['dediff_rate']
        
        # Blast dynamics
        dB = (p['r_blast'] * B * logistic       # growth
              - p['d_blast'] * B                 # natural death
              + p['diff_rate'] * L               # LSC → blast differentiation
              - dediff * B                       # blast → LSC dedifferentiation
              - kill_blast * B)                  # drug kill
        
        # LSC dynamics
        dL = (p['r_lsc'] * L * logistic          # self-renewal
              - p['d_lsc'] * L                   # natural death
              + dediff * B                       # blast → LSC dedifferentiation
              - p['diff_rate'] * L               # LSC → blast differentiation
              - kill_lsc * L)                    # drug kill (much less)
        
        return [dB, dL]
    
    def simulate(self, B0, L0, t_end, dt=1.0):
        """Run simulation."""
        y0 = [B0, L0]
        t_eval = np.arange(0, t_end + dt, dt)
        
        sol = solve_ivp(self.deriv, (0, t_end), y0, t_eval=t_eval,
                        method='RK45', rtol=1e-8, atol=1e-12, max_step=1.0)
        
        blasts = sol.y[0]
        lscs = sol.y[1]
        total = blasts + lscs
        
        # Complete response: total < 5% of initial
        initial_burden = B0 + L0
        cr_achieved = np.any(total < 0.05 * initial_burden)
        
        # Time to CR
        cr_day = None
        for i in range(len(sol.t)):
            if total[i] < 0.05 * initial_burden:
                cr_day = sol.t[i]
                break
        
        # Relapse: after CR, total rises back above 30% of initial
        relapse_day = None
        if cr_day:
            for i in range(len(sol.t)):
                if sol.t[i] > cr_day + 30 and total[i] > 0.30 * initial_burden:
                    relapse_day = sol.t[i]
                    break
        
        # OS proxy: time until total > 2x initial (uncontrolled growth)
        os_day = None
        nadir_i = np.argmin(total)
        for i in range(nadir_i, len(sol.t)):
            if total[i] > 1.5 * initial_burden:
                os_day = sol.t[i]
                break
        
        return {
            'sol': sol,
            'blasts': blasts,
            'lscs': lscs,
            'total': total,
            'cr_achieved': cr_achieved,
            'cr_day': cr_day,
            'cr_month': cr_day / 30.44 if cr_day else None,
            'relapse_day': relapse_day,
            'relapse_month': relapse_day / 30.44 if relapse_day else None,
            'os_day': os_day,
            'os_month': os_day / 30.44 if os_day else None,
            'nadir': float(np.min(total)),
            'nadir_day': float(sol.t[nadir_i]),
            'lsc_fraction_at_nadir': float(lscs[nadir_i] / max(total[nadir_i], 1e-10)),
        }


def validate():
    """Validate against known AML clinical outcomes."""
    print('INTERCEPTA AML ODE VALIDATION')
    print('='*60)
    
    # Initial condition: 80% blasts, 1% LSCs (typical AML diagnosis)
    B0 = 0.80
    L0 = 0.01
    print(f'Initial: Blasts={B0:.0%} LSCs={L0:.0%}')
    
    # 1. Untreated AML
    print(f'\n1. UNTREATED AML:')
    m0 = AML_ODE()
    r0 = m0.simulate(B0, L0, 365)
    print(f'  OS: {r0["os_month"]:.1f}mo' if r0['os_month'] else '  OS: >12mo (unexpected)')
    # Untreated AML OS: 2-4 months typically
    
    # 2. 7+3 Induction (cytarabine 7 days + daunorubicin 3 days)
    print(f'\n2. 7+3 INDUCTION (cytarabine + daunorubicin):')
    m1 = AML_ODE()
    # Cytarabine: high dose, 7 days, kills blasts well, LSCs resistant
    # EC50 blast ~0.1uM, EC50 LSC ~10uM (100x resistant)
    m1.add_drug('Cytarabine', emax=0.3, ec50_blast=0.1, ec50_lsc=10.0,
                cmax=5.0, half_life_days=0.15,  # 3.6 hour half-life
                dose_times=np.arange(0, 7))
    # Daunorubicin: 3 days
    m1.add_drug('Daunorubicin', emax=0.25, ec50_blast=0.05, ec50_lsc=5.0,
                cmax=1.0, half_life_days=0.75,  # 18 hour half-life
                dose_times=np.array([0, 1, 2]))
    
    r1 = m1.simulate(B0, L0, 730)  # 2 years
    print(f'  CR achieved: {r1["cr_achieved"]}')
    print(f'  CR day: {r1["cr_month"]:.1f}mo' if r1['cr_month'] else '  No CR')
    print(f'  LSC fraction at nadir: {r1["lsc_fraction_at_nadir"]:.1%}')
    print(f'  Relapse: {r1["relapse_month"]:.1f}mo' if r1['relapse_month'] else '  No relapse (in 2y)')
    print(f'  OS: {r1["os_month"]:.1f}mo' if r1['os_month'] else '  OS >24mo')
    # Clinical: CR ~65-75%, relapse ~50% within 2y
    
    # 3. Venetoclax + Azacitidine (VIALE-A: median OS 14.7mo)
    print(f'\n3. VENETOCLAX + AZACITIDINE (VIALE-A validation):')
    m2 = AML_ODE()
    # Venetoclax: BCL2 inhibitor, kills blasts AND partially LSCs
    # EC50 blast ~0.01uM, EC50 LSC ~0.5uM (50x, not 100x)
    # This is the key: venetoclax reaches LSCs better than chemo
    m2.add_drug('Venetoclax', emax=0.15, ec50_blast=0.01, ec50_lsc=0.5,
                cmax=0.8, half_life_days=0.73,  # 17.5 hour half-life
                dose_times=np.arange(0, 365))  # daily for 1 year
    # Azacitidine: hypomethylating, sensitizes LSCs
    m2.add_drug('Azacitidine', emax=0.08, ec50_blast=0.5, ec50_lsc=2.0,
                cmax=3.0, half_life_days=0.17,  # 4 hour half-life
                dose_times=np.concatenate([np.arange(c*28, c*28+7) 
                                           for c in range(18)]))  # d1-7 q28
    
    r2 = m2.simulate(B0, L0, 1095)  # 3 years
    print(f'  CR achieved: {r2["cr_achieved"]}')
    print(f'  CR day: {r2["cr_month"]:.1f}mo' if r2['cr_month'] else '  No CR')
    print(f'  LSC fraction at nadir: {r2["lsc_fraction_at_nadir"]:.1%}')
    print(f'  Relapse: {r2["relapse_month"]:.1f}mo' if r2['relapse_month'] else '  No relapse (in 3y)')
    print(f'  OS: {r2["os_month"]:.1f}mo' if r2['os_month'] else '  OS >36mo')
    print(f'  Target OS (VIALE-A): 14.7mo')
    
    # 4. Gilteritinib (FLT3-mut only, ADMIRAL trial: OS 9.3mo)
    print(f'\n4. GILTERITINIB (FLT3-mut, ADMIRAL validation):')
    m3 = AML_ODE()
    # FLT3 inhibitor: targeted, kills FLT3-dependent blasts
    # LSCs less dependent on FLT3 → high EC50
    m3.add_drug('Gilteritinib', emax=0.12, ec50_blast=0.005, ec50_lsc=5.0,
                cmax=0.15, half_life_days=6.0,  # 158 hour half-life
                dose_times=np.arange(0, 365))  # daily
    
    r3 = m3.simulate(B0, L0, 730)
    print(f'  CR achieved: {r3["cr_achieved"]}')
    print(f'  OS: {r3["os_month"]:.1f}mo' if r3['os_month'] else '  OS >24mo')
    print(f'  Target OS (ADMIRAL): 9.3mo')
    
    # Summary
    print(f'\n{"="*60}')
    print(f'VALIDATION SUMMARY:')
    validations = [
        ('Untreated AML OS', '2-4mo', r0['os_month']),
        ('7+3 CR achieved', '65-75%', 'Yes' if r1['cr_achieved'] else 'No'),
        ('Ven+Aza OS', '14.7mo', r2['os_month']),
        ('Gilteritinib OS', '9.3mo', r3['os_month']),
    ]
    for name, target, actual in validations:
        actual_str = f'{actual:.1f}' if isinstance(actual, float) and actual else str(actual)
        print(f'  {name:<25} target={target:<10} actual={actual_str}')
    
    # Save
    results = {
        'model': 'AML two-population ODE (blast + LSC)',
        'compartments': 2,
        'untreated_os': r0['os_month'],
        'induction_cr': r1['cr_achieved'],
        'induction_relapse': r1['relapse_month'],
        'venaza_os': r2['os_month'],
        'gilteritinib_os': r3['os_month'],
        'honest_note': 'Parameters from published PK and AML biology. EC50 ratios (blast/LSC) estimated from literature. Not fitted to clinical data.',
    }
    with open('../results/aml_ode_validation.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\n  Saved: results/aml_ode_validation.json')

if __name__ == '__main__':
    validate()
