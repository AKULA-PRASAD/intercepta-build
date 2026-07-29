#!/usr/bin/env python3
"""
AML ODE v6: 4-Compartment with Resistance Evolution
====================================================
Blast-sensitive + Blast-resistant + LSC + Normal

Resistance mechanism (from published literature):
  - Venetoclax targets BCL2-dependent primitive blasts
  - Monocytic blasts are MCL1-dependent → intrinsically resistant
  - Under venetoclax pressure, BCL2-dep cells die, MCL1-dep expand
  - This is CLONAL SELECTION, not de novo mutation
  - ~30% primary non-responders (pre-existing resistant fraction)
  - Almost all responders eventually relapse via resistant expansion

Sources:
  - Cell Death Dis 2024: venetoclax resistance mechanisms
  - Cancer Discov 2020: monocytic subclones confer resistance  
  - PMC 9255248: MCL1 upregulation timeline
  - VIALE-A: 70% response, median OS 14.7mo
  - BeatAML dataset: M4/M5 show higher venetoclax AUC (resistant)

Parameter derivation:
  - Resistant fraction at diagnosis: 10-30% (monocytic component)
  - Resistant cells: same growth rate, NOT killed by venetoclax
  - Selection: venetoclax kills sensitive, resistant expand to fill
  - No new transition rate needed — it is competitive selection
"""
import numpy as np
from scipy.integrate import solve_ivp
import json, time

# Load base parameters
with open('../results/aml_ode_parameters.json') as f:
    P = json.load(f)

# Add competition and resistance parameters
P.update({
    # Normal hematopoiesis (from v5)
    'r_normal': 0.05, 'd_normal': 0.02, 'N0': 0.60,
    'death_threshold': 0.10, 'suppress': 0.11,
    
    # Resistant blast fraction at diagnosis
    # Source: "~30% primary non-responders" + monocytic AML fraction
    # Conservative: 15% resistant at diagnosis
    'frac_resistant': 0.15,
    
    # Resistant blasts: same growth, NOT killed by BCL2 inhibitor
    # MCL1-dependent, not BCL2-dependent
    'r_res': 0.039,   # same as sensitive blasts
    'd_res': 0.026,   # same baseline death
    
    # De novo resistance: sensitive → resistant under drug pressure
    # From "MCL1 upregulation over several months of venetoclax"
    # Estimate: ~0.1%/day transition rate under drug pressure
    'mu_resistance': 1e-3,
    
    # G-CSF supportive care
    'gcsf_threshold': 0.20,
    'gcsf_boost': 5.0,
    'dose_hold_threshold': 0.15,
    'dose_reduction': 0.5,
})

def precompute_pk(drug, t_end):
    """Pre-compute PK on 0.5-day grid."""
    dt = 0.5
    t_grid = np.arange(0, t_end+dt, dt)
    C = np.zeros(len(t_grid))
    ke = drug['ke']
    cmax = drug['cmax']
    for td in drug['doses']:
        si = max(0, int(td/dt))
        end_i = min(si + int(10/ke/dt)+1, len(t_grid))
        for i in range(si, end_i):
            elapsed = t_grid[i] - td
            if elapsed >= 0:
                C[i] += cmax * np.exp(-ke * elapsed)
    return t_grid, C, dt

def run_v6(drugs=None, t_end=1095):
    """4-compartment: Bs (sensitive blast) + Br (resistant blast) + L (LSC) + N (normal)."""
    
    # Pre-compute PK
    pk = []
    if drugs:
        for d in drugs:
            tg, cg, dt = precompute_pk(d, t_end)
            pk.append((tg, cg, dt, d))
    
    # Initial conditions
    B_total = P['B0']
    Bs0 = B_total * (1 - P['frac_resistant'])
    Br0 = B_total * P['frac_resistant']
    L0 = P['L0']
    N0 = P['N0']
    
    def deriv(t, y):
        Bs, Br, L, N = max(y[0],0), max(y[1],0), max(y[2],0), max(y[3],0)
        T = Bs + Br + L + N
        logistic = max(1 - T/P['K'], 0)
        
        # Supportive care
        r_n = P['r_normal']
        dose_mult = 1.0
        if N < P['gcsf_threshold']: r_n *= P['gcsf_boost']
        if N < P['dose_hold_threshold']: dose_mult *= P['dose_reduction']
        
        # Drug effects
        kbs, kbr, kl = 0, 0, 0
        stress = False
        for tg, cg, dt, d in pk:
            idx = min(int(t/dt), len(cg)-1)
            C = cg[idx] * dose_mult
            if C > 1e-10:
                stress = True
                h = d.get('hill', 1.5)
                # Sensitive blasts: full drug effect
                kbs += d['emax'] * C**h / (d['ec50_b']**h + C**h)
                # Resistant blasts: reduced effect (MCL1 bypass)
                resist_factor = d.get('resist_factor', 0.1)  # 10% kill of resistant
                kbr += d['emax'] * resist_factor * C**h / (d['ec50_b']**h + C**h)
                # LSC: very resistant
                kl += d['emax'] * C**h / (d['ec50_l']**h + C**h)
        
        dediff = P['dediff_stress'] if stress else P['dediff_base']
        d_norm_eff = P['d_normal'] + P['suppress'] * (Bs + Br)
        kn = 0.3 * kbs  # normal cells partially sensitive
        
        # Transition: sensitive → resistant under drug pressure
        mu = P['mu_resistance'] if stress else 0
        
        # Sensitive blasts
        dBs = (P['r_blast']*Bs*logistic - P['d_blast']*Bs 
               + P['diff_rate']*L*0.85  # LSC produce mostly sensitive
               - dediff*Bs - kbs*Bs - mu*Bs)
        
        # Resistant blasts
        dBr = (P['r_res']*Br*logistic - P['d_res']*Br
               + P['diff_rate']*L*0.15  # LSC produce some resistant
               - kbr*Br + mu*Bs)  # gain from sensitive→resistant
        
        # LSC
        dL = (P['r_lsc']*L*logistic - P['d_lsc']*L
              + dediff*(Bs+Br) - P['diff_rate']*L - kl*L)
        
        # Normal
        dN = r_n*N*logistic - d_norm_eff*N - kn*N
        
        return [dBs, dBr, dL, dN]
    
    t0 = time.time()
    sol = solve_ivp(deriv, (0,t_end), [Bs0, Br0, L0, N0],
                    t_eval=np.arange(0,t_end+1,1),
                    method='LSODA', rtol=1e-6, atol=1e-9, max_step=2.0)
    elapsed = time.time() - t0
    
    Bs, Br, L, N = sol.y[0], sol.y[1], sol.y[2], sol.y[3]
    B_total = Bs + Br
    leuk = B_total + L
    
    # CR: leukemic burden < 5% of initial
    init_leuk = P['B0'] + P['L0']
    cr_day = None
    for i in range(len(sol.t)):
        if leuk[i] < 0.05 * init_leuk:
            cr_day = sol.t[i]; break
    
    # Death: normal < threshold
    death_day = None
    for i in range(len(sol.t)):
        if N[i] < P['death_threshold']:
            death_day = sol.t[i]; break
    
    # Relapse: after CR, leukemic burden > 20%
    nadir_i = np.argmin(leuk)
    rel_day = None
    if cr_day:
        for i in range(nadir_i+1, len(sol.t)):
            if sol.t[i] > cr_day + 30 and leuk[i] > 0.20:
                rel_day = sol.t[i]; break
    
    # Progression death: after relapse, normal drops below threshold
    prog_death = None
    if rel_day:
        for i in range(int(rel_day), len(sol.t)):
            if N[i] < P['death_threshold']:
                prog_death = sol.t[i]; break
    
    os_day = death_day or prog_death
    
    # Resistant fraction over time
    res_frac_nadir = Br[nadir_i] / max(B_total[nadir_i], 1e-15)
    res_frac_end = Br[-1] / max(B_total[-1], 1e-15)
    
    return {
        'cr': cr_day is not None,
        'cr_mo': round(cr_day/30.44, 1) if cr_day else None,
        'rel_mo': round(rel_day/30.44, 1) if rel_day else None,
        'os_mo': round(os_day/30.44, 1) if os_day else None,
        'cause': ('marrow_failure' if death_day and not rel_day 
                  else 'relapse_then_failure' if prog_death 
                  else 'alive'),
        'normal_min': round(float(np.min(N)), 4),
        'res_frac_nadir': round(float(res_frac_nadir), 3),
        'res_frac_end': round(float(res_frac_end), 3),
        'time_sec': round(elapsed, 1),
    }


def main():
    print('AML ODE v6: 4-COMPARTMENT RESISTANCE MODEL')
    print('='*60)
    print(f'Compartments: Bs(sensitive) + Br(resistant) + LSC + Normal')
    print(f'Resistant fraction at diagnosis: {P["frac_resistant"]:.0%}')
    print(f'Resistance mechanism: clonal selection (MCL1 vs BCL2)')
    print()
    
    # 1. Untreated
    r0 = run_v6(drugs=None, t_end=365)
    print(f'1. UNTREATED: OS={r0["os_mo"]}mo (target 2-4) [{r0["time_sec"]}s]')
    
    # 2. 7+3
    drugs_73 = [
        {'name':'AraC','emax':0.3,'ec50_b':0.1,'ec50_l':500.0,
         'cmax':0.4,'ke':np.log(2)/0.125,
         'doses':np.arange(0,7,1.0/24),'hill':1.5,
         'resist_factor':0.8},  # chemo kills resistant too (not targeted)
        {'name':'Dauno','emax':0.25,'ec50_b':0.05,'ec50_l':50.0,
         'cmax':1.0,'ke':np.log(2)/0.83,
         'doses':np.array([0,1,2]),'hill':1.5,
         'resist_factor':0.8},
    ]
    r1 = run_v6(drugs=drugs_73, t_end=730)
    print(f'2. 7+3: CR={r1["cr"]} rel={r1["rel_mo"]} OS={r1["os_mo"]} [{r1["time_sec"]}s]')
    print(f'   Res frac: nadir={r1["res_frac_nadir"]:.0%} end={r1["res_frac_end"]:.0%}')
    
    # 3. Venetoclax + Azacitidine
    drugs_va = [
        {'name':'Ven','emax':0.15,'ec50_b':0.001,'ec50_l':1.0,
         'cmax':0.003,'ke':np.log(2)/0.73,
         'doses':np.arange(0,540),'hill':1.5,
         'resist_factor':0.05},  # TARGETED: resistant cells barely killed
        {'name':'Aza','emax':0.06,'ec50_b':0.5,'ec50_l':50.0,
         'cmax':3.5,'ke':np.log(2)/0.17,
         'doses':np.concatenate([np.arange(c*28,c*28+7) for c in range(20)]),
         'hill':1.0,
         'resist_factor':0.5},  # HMA partially kills resistant
    ]
    r2 = run_v6(drugs=drugs_va, t_end=1095)
    print(f'3. VEN+AZA: CR={r2["cr"]} rel={r2["rel_mo"]} OS={r2["os_mo"]} (target 14.7) [{r2["time_sec"]}s]')
    print(f'   Res frac: nadir={r2["res_frac_nadir"]:.0%} end={r2["res_frac_end"]:.0%}')
    print(f'   Cause: {r2["cause"]}')
    
    # 4. Gilteritinib
    drugs_g = [
        {'name':'Gilt','emax':0.10,'ec50_b':0.002,'ec50_l':100.0,
         'cmax':0.2,'ke':np.log(2)/6.6,
         'doses':np.arange(0,365),'hill':1.5,
         'resist_factor':0.3},  # FLT3i has some activity on resistant
    ]
    r3 = run_v6(drugs=drugs_g, t_end=730)
    print(f'4. GILT: CR={r3["cr"]} OS={r3["os_mo"]} (target 9.3) [{r3["time_sec"]}s]')
    print(f'   Res frac: nadir={r3["res_frac_nadir"]:.0%} end={r3["res_frac_end"]:.0%}')
    
    # Scorecard
    print(f'\n{"="*60}')
    print('SCORECARD:')
    for n,t,a in [('Untreated','2-4mo',r0['os_mo']),('7+3 CR','Yes',r1['cr']),
                  ('Ven+Aza OS','14.7mo',r2['os_mo']),('Gilt OS','9.3mo',r3['os_mo'])]:
        print(f'  {n:<18} target={t:<10} actual={str(a) if a else ">endpoint"}')
    
    # Save
    def clean(o):
        if isinstance(o,(np.bool_,bool)):return bool(o)
        if isinstance(o,(np.integer,)):return int(o)
        if isinstance(o,(np.floating,)):return float(o)
        if isinstance(o,dict):return{k:clean(v)for k,v in o.items()}
        if isinstance(o,list):return[clean(v)for v in o]
        return o
    
    with open('../results/aml_ode_v6_validation.json','w') as f:
        json.dump(clean({
            'model':'AML 4-comp: Bs+Br+LSC+Normal with resistance selection',
            'key_mechanism':'MCL1-dependent monocytic clones resist venetoclax, expand under selection',
            'sources':['Cell Death Dis 2024','Cancer Discov 2020','VIALE-A','BeatAML'],
            'untreated':r0,'induction':r1,'venaza':r2,'gilteritinib':r3,
        }),f,indent=2)
    print(f'\nSaved: results/aml_ode_v6_validation.json')

if __name__ == '__main__':
    main()
