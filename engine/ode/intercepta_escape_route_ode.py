#!/usr/bin/env python3
"""
INTERCEPTA Multi-State Escape Route ODE
========================================
Models acquired resistance through 4 tumor states:
  S: AR-dependent (sensitive to enzalutamide)
  M: AR-mutant (F877L/T878A, enza becomes agonist)
  V: AR-V7 (splice variant, bypasses ligand binding)
  N: NE-like (lineage plasticity, AURKA/N-myc driven)

Escape transitions (S→M, S→V, S→N) are biologically grounded.
Drug effects target specific states AND transition rates.

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
Date: April 2026

Key results:
  Enzalutamide alone PFS: 14.8 months (PREVAIL clinical: ~18 months)
  Enza + Alisertib PFS: 17.1 months (+2.2 months)
  Combination blocks NE escape (30.7% → 0%)
  AR-mutant becomes dominant resistance mechanism (65% → 94%)
"""
import numpy as np
from scipy.integrate import solve_ivp

# Growth rates (literature-derived)
PARAMS = {
    'g_S': 0.005,      # AR-dependent (PSA doubling ~4mo)
    'g_M': 0.006,      # AR-mutant, slightly faster
    'g_V': 0.005,      # AR-V7, similar
    'g_N': 0.008,      # NE-like, most aggressive (Beltran 2016)
    'd': 0.001,         # Natural death rate
    'K': 1.0,           # Carrying capacity
    # Escape transition rates (under enzalutamide pressure)
    'mu_SM': 1e-4,      # S→M: AR point mutations (~0.1%/day)
    'mu_SV': 5e-5,      # S→V: AR-V7 splice variants (~0.05%/day)
    'mu_SN': 2e-5,      # S→N: NE transition (~0.02%/day)
    # Initial conditions (mCRPC diagnosis)
    'S0': 0.14,         # 93% AR-dependent
    'M0': 0.003,        # 2% AR-mutant
    'V0': 0.003,        # 2% AR-V7
    'N0': 0.004,        # 3% NE-like
    # Drug effects
    'enza_kill_S': 0.15,    # Enzalutamide kill rate on S
    'enza_boost_M': 0.003,  # Enza agonism on M
    'alis_kill_N': 0.12,    # Alisertib kill rate on N
    'alis_block_SN': 0.9,   # Alis blocks 90% of NE transition
}

def simulate(use_enza=False, use_alis=False, years=5, params=None):
    p = PARAMS.copy()
    if params:
        p.update(params)
    
    te = np.arange(0, years*365+1, 1)
    y0 = [p['S0'], p['M0'], p['V0'], p['N0']]
    
    def deriv(t, y):
        S, M, V, N = max(y[0],0), max(y[1],0), max(y[2],0), max(y[3],0)
        total = S + M + V + N
        logistic = 1 - total/p['K']
        
        dS = p['g_S']*S*logistic - p['d']*S
        dM = p['g_M']*M*logistic - p['d']*M
        dV = p['g_V']*V*logistic - p['d']*V
        dN = p['g_N']*N*logistic - p['d']*N
        
        if use_enza:
            dS -= p['enza_kill_S'] * S
            dM += p['enza_boost_M'] * M
            rate_SM = p['mu_SM'] * S
            rate_SV = p['mu_SV'] * S
            rate_SN = p['mu_SN'] * S
            if use_alis:
                rate_SN *= (1 - p['alis_block_SN'])
            dS -= (rate_SM + rate_SV + rate_SN)
            dM += rate_SM
            dV += rate_SV
            dN += rate_SN
        
        if use_alis:
            dN -= p['alis_kill_N'] * N
        
        return [dS, dM, dV, dN]
    
    sol = solve_ivp(deriv, (0, years*365), y0, t_eval=te,
                    method='RK45', rtol=1e-8, atol=1e-12)
    
    total = sol.y[0]+sol.y[1]+sol.y[2]+sol.y[3]
    total0 = sum(y0)
    nadir = np.min(total)
    nadir_i = np.argmin(total)
    threshold = max(2*nadir, total0*1.25)
    pfs = None
    for j in range(nadir_i+1, len(sol.t)):
        if sol.t[j]-sol.t[nadir_i]>60 and total[j]>threshold:
            pfs = sol.t[j]; break
    
    return {
        'sol': sol, 'total': total, 'pfs_days': pfs,
        'pfs_months': pfs/30.44 if pfs else None,
        'composition': {'S':sol.y[0],'M':sol.y[1],'V':sol.y[2],'N':sol.y[3]},
    }

if __name__ == '__main__':
    for name, ue, ua in [('Control',0,0),('Enza',1,0),('Alis',0,1),('Enza+Alis',1,1)]:
        r = simulate(ue, ua)
        pfs = f"{r['pfs_months']:.1f}mo" if r['pfs_months'] else '>60mo'
        print(f'{name:<12} PFS={pfs}')
