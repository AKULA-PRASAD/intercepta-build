#!/usr/bin/env python3
"""
INTERCEPTA Unified Tumor Dynamics ODE
======================================
Combines continuous phenotype structure (resistance gradient)
with discrete escape route states (pathway switching).

Architecture: 4 states × 20 bins = 80 compartments
  State S (AR-dependent): 20 phenotype bins
  State M (AR-mutant): 20 phenotype bins
  State V (AR-V7): 20 phenotype bins
  State N (NE-like): 20 phenotype bins

Within each state: phenotypic drift (diffusion + selection)
Between states: escape transitions (mutation, splicing, plasticity)
Drug effects: depend on BOTH state AND phenotype bin

No published model combines these. This is Novel Technology.

Validation targets:
  Docetaxel HR ~0.69 (phenotype model)
  Enzalutamide PFS ~14.8mo (escape model)
  Doc+Cis HR ~1.0 (combination failure)
  Enza+Alis: NE-high +10mo, NE-low +0.1mo

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
"""
import numpy as np
from scipy.integrate import solve_ivp
import json

class UnifiedTumorODE:
    """4-state × 20-bin phenotype-escape tumor dynamics."""
    
    N_BINS = 20
    N_STATES = 4  # S, M, V, N
    STATE_NAMES = ['S', 'M', 'V', 'N']
    
    def __init__(self, params=None):
        self.p = {
            # Phenotype structure
            'N_bins': 20,
            'r_max': 0.00678,      # max growth rate (from PSA doubling)
            'alpha_r': 0.4,         # growth penalty at resistant end
            'K': 1.0,               # carrying capacity
            'd_nat': 0.001,         # natural death
            'beta': 8.27e-4,        # phenotypic drift (from velocity)
            
            # State-specific growth modifiers
            'g_mod_S': 1.0,         # AR-dependent: baseline
            'g_mod_M': 1.1,         # AR-mutant: slightly faster
            'g_mod_V': 1.0,         # AR-V7: similar
            'g_mod_N': 1.3,         # NE-like: most aggressive
            
            # Escape transition rates (under AR-targeted therapy pressure)
            'mu_SM': 1e-4,          # S→M (AR point mutations)
            'mu_SV': 5e-5,          # S→V (splice variants)
            'mu_SN': 2e-5,          # S→N (NE plasticity)
            
            # Drug parameters
            'emax': 0.153,          # max kill rate (from GDSC)
        }
        if params:
            self.p.update(params)
        
        self.N = self.p['N_bins']
        self.dx = 1.0 / self.N
        self.x = np.array([(i + 0.5) / self.N for i in range(self.N)])
        
        # State indices in flattened array
        # y = [S_0, S_1, ..., S_19, M_0, ..., M_19, V_0, ..., V_19, N_0, ..., N_19]
        self.total_vars = self.N_STATES * self.N
        
        self.drugs = []
    
    def add_drug(self, name, ec50_per_bin, cmax_free, half_life_days,
                 dose_times, state_effects=None):
        """
        Add a drug with state-specific and bin-specific effects.
        
        Args:
            ec50_per_bin: array of EC50 per phenotype bin (shape: N_bins)
            cmax_free: free Cmax in uM
            half_life_days: elimination half-life
            dose_times: array of dosing times (days)
            state_effects: dict mapping state → effect multiplier
                e.g. {'S': 1.0, 'M': 0.0, 'V': 0.0, 'N': 0.0} for AR-dependent drug
        """
        if state_effects is None:
            state_effects = {'S': 1.0, 'M': 1.0, 'V': 1.0, 'N': 1.0}
        
        self.drugs.append({
            'name': name,
            'ec50': np.array(ec50_per_bin),
            'cmax': cmax_free,
            'ke': np.log(2) / half_life_days,
            'doses': np.array(dose_times),
            'state_effects': state_effects,
        })
    
    def concentration(self, drug, t):
        """Compute drug concentration at time t."""
        c = 0.0
        for td in drug['doses']:
            if t >= td:
                dt = t - td
                if dt < 10 / drug['ke']:  # ~10 half-lives
                    c += drug['cmax'] * np.exp(-drug['ke'] * dt)
        return c
    
    def _get_state(self, y, state_idx):
        """Extract bins for one state from flattened array."""
        start = state_idx * self.N
        return y[start:start + self.N]
    
    def _set_state(self, dy, state_idx, values):
        """Set derivative for one state in flattened array."""
        start = state_idx * self.N
        dy[start:start + self.N] = values
    
    def deriv(self, t, y):
        """ODE right-hand side for 80-compartment model."""
        p = self.p
        y = np.maximum(y, 0)
        
        # Total tumor burden (all states, all bins)
        N_total = np.sum(y)
        logistic = 1 - N_total / p['K']
        
        # Get states
        states = [self._get_state(y, s) for s in range(self.N_STATES)]
        g_mods = [p['g_mod_S'], p['g_mod_M'], p['g_mod_V'], p['g_mod_N']]
        
        # Drug concentrations
        drug_concs = [self.concentration(d, t) for d in self.drugs]
        
        # Compute derivatives for each state
        dy = np.zeros(self.total_vars)
        
        for s in range(self.N_STATES):
            n = states[s]
            dn = np.zeros(self.N)
            
            for i in range(self.N):
                # Growth (state-modified)
                g = p['r_max'] * g_mods[s] * (1 - p['alpha_r'] * self.x[i]) * n[i] * logistic
                
                # Natural death
                d = p['d_nat'] * n[i]
                
                # Drug kill (each drug, state-specific and bin-specific)
                kill = 0
                for drug_idx, drug in enumerate(self.drugs):
                    C = drug_concs[drug_idx]
                    if C > 0:
                        state_mult = drug['state_effects'].get(
                            self.STATE_NAMES[s], 0)
                        if state_mult > 0:
                            kill += p['emax'] * state_mult * \
                                C**1.5 / (drug['ec50'][i]**1.5 + C**1.5) * n[i]
                
                # Phenotypic diffusion (within state)
                if i == 0:
                    diff = p['beta'] * (n[1] - n[0]) / self.dx**2
                elif i == self.N - 1:
                    diff = p['beta'] * (n[self.N-2] - n[self.N-1]) / self.dx**2
                else:
                    diff = p['beta'] * (n[i-1] - 2*n[i] + n[i+1]) / self.dx**2
                
                dn[i] = g - d - kill + diff
            
            # Escape transitions (only from S state, only under AR therapy)
            if s == 0:  # S state
                ar_therapy_active = any(
                    drug['state_effects'].get('S', 0) > 0.5 and
                    drug['state_effects'].get('M', 0) < 0.5
                    and self.concentration(drug, t) > 0
                    for drug in self.drugs
                )
                
                if ar_therapy_active:
                    # S→M, S→V, S→N transitions
                    dn -= p['mu_SM'] * n  # loss from S
                    dn -= p['mu_SV'] * n
                    dn -= p['mu_SN'] * n
                    
                    # Add to M, V, N states
                    dy[1*self.N:(1+1)*self.N] += p['mu_SM'] * n  # gain to M
                    dy[2*self.N:(2+1)*self.N] += p['mu_SV'] * n  # gain to V
                    dy[3*self.N:(3+1)*self.N] += p['mu_SN'] * n  # gain to N
            
            self._set_state(dy, s, self._get_state(dy, s) + dn)
        
        return dy
    
    def simulate(self, y0, t_end, dt=1.0):
        """Run simulation.
        
        Args:
            y0: initial state (80-element array)
            t_end: end time in days
            dt: output timestep
        """
        t_eval = np.arange(0, t_end + dt, dt)
        
        sol = solve_ivp(self.deriv, (0, t_end), y0, t_eval=t_eval,
                        method='RK45', rtol=1e-7, atol=1e-11, max_step=1.0)
        
        if not sol.success:
            print(f'  WARNING: solver failed at t={sol.t[-1]:.0f}')
        
        # Compute totals per state
        totals = {}
        for s in range(self.N_STATES):
            state_y = sol.y[s*self.N:(s+1)*self.N, :]
            totals[self.STATE_NAMES[s]] = np.sum(state_y, axis=0)
        totals['total'] = sum(totals.values())
        
        # Find PFS
        total = totals['total']
        nadir = np.min(total)
        nadir_i = np.argmin(total)
        total0 = total[0]
        threshold = max(2 * nadir, total0 * 1.25)
        
        pfs = None
        for j in range(nadir_i + 1, len(sol.t)):
            if sol.t[j] - sol.t[nadir_i] > 60 and total[j] > threshold:
                pfs = sol.t[j]
                break
        
        return {
            'sol': sol,
            'totals': totals,
            'pfs_days': pfs,
            'pfs_months': pfs / 30.44 if pfs else None,
            'nadir': nadir,
            'nadir_day': sol.t[nadir_i],
        }
    
    @staticmethod
    def make_initial_state(velocity_csv, N_bins=20, N0=0.15,
                           frac_M=0.02, frac_V=0.02, frac_N=0.03):
        """Create initial 80-element state from velocity data.
        
        S state: initialized from velocity distribution (93% of tumor)
        M, V, N states: small initial fractions
        """
        from intercepta_phenotype_ode_v1 import load_velocity_distribution
        
        n0_raw, _ = load_velocity_distribution(velocity_csv, N_bins)
        
        y0 = np.zeros(4 * N_bins)
        
        # S state: velocity distribution, scaled
        frac_S = 1.0 - frac_M - frac_V - frac_N
        y0[0:N_bins] = n0_raw * N0 * frac_S
        
        # M, V, N states: uniform across bins, small fractions
        y0[1*N_bins:2*N_bins] = N0 * frac_M / N_bins
        y0[2*N_bins:3*N_bins] = N0 * frac_V / N_bins
        y0[3*N_bins:4*N_bins] = N0 * frac_N / N_bins
        
        return y0


def validate():
    """Validate unified model reproduces both phenotype and escape results."""
    print('INTERCEPTA UNIFIED ODE VALIDATION')
    print('='*60)
    
    model = UnifiedTumorODE()
    y0 = model.make_initial_state('../results/velocity_star_latent_time.csv')
    
    print(f'Model: {model.total_vars} compartments (4 states × 20 bins)')
    print(f'Initial: S={np.sum(y0[:20]):.4f} M={np.sum(y0[20:40]):.4f} V={np.sum(y0[40:60]):.4f} N={np.sum(y0[60:80]):.4f}')
    
    # Test 1: Control (no drug)
    ctrl = model.simulate(y0.copy(), 1825)
    print(f'\n  Control: PFS={ctrl["pfs_months"]:.1f}mo' if ctrl['pfs_months'] else '\n  Control: no progression')
    
    # Test 2: Docetaxel (cytotoxic, affects all states equally)
    model_doc = UnifiedTumorODE()
    ec50_doc = np.exp(np.linspace(np.log(0.0035), np.log(0.342), 20))
    dose_times_doc = np.array([i*21 for i in range(6)])
    model_doc.add_drug('Docetaxel', ec50_doc, 0.0937, 11.1/24,
                       dose_times_doc,
                       state_effects={'S':1.0, 'M':1.0, 'V':1.0, 'N':1.0})
    
    doc = model_doc.simulate(y0.copy(), 1825)
    doc_hr = ctrl['pfs_days'] / doc['pfs_days'] if (ctrl['pfs_days'] and doc['pfs_days']) else 0
    print(f'  Docetaxel: PFS={doc["pfs_months"]:.1f}mo HR={doc_hr:.3f} (target ~0.69)')
    
    # Test 3: Enzalutamide (AR-targeted, S only)
    model_enza = UnifiedTumorODE()
    ec50_enza = np.exp(np.linspace(np.log(0.1), np.log(100), 20))
    dose_times_enza = np.arange(0, 1826)
    model_enza.add_drug('Enzalutamide', ec50_enza, 0.8936, 5.8,
                        dose_times_enza,
                        state_effects={'S':1.0, 'M':0.0, 'V':0.0, 'N':0.0})
    
    enza = model_enza.simulate(y0.copy(), 1825)
    print(f'  Enzalutamide: PFS={enza["pfs_months"]:.1f}mo (target ~14.8)')
    
    # Test 4: Enza + Alisertib (S + N targeted)
    model_combo = UnifiedTumorODE()
    model_combo.add_drug('Enzalutamide', ec50_enza, 0.8936, 5.8,
                         dose_times_enza,
                         state_effects={'S':1.0, 'M':0.0, 'V':0.0, 'N':0.0})
    ec50_alis = np.exp(np.linspace(np.log(0.09), np.log(190), 20))
    dose_times_alis = []
    for cycle in range(100):
        for day in range(7):
            for dose in range(2):
                dose_times_alis.append(cycle*21 + day + dose*0.5)
    model_combo.add_drug('Alisertib', ec50_alis, 0.0029, 23/24,
                         np.array(dose_times_alis[:2000]),
                         state_effects={'S':0.0, 'M':0.0, 'V':0.0, 'N':1.0})
    
    combo = model_combo.simulate(y0.copy(), 1825)
    
    # Composition at 2 years
    if enza['sol'].success:
        t2y = min(730, len(enza['sol'].t)-1)
        i2y = np.argmin(np.abs(enza['sol'].t - 730))
        enza_comp = {s: np.sum(enza['sol'].y[s*20:(s+1)*20, i2y]) for s in range(4)}
        enza_total = sum(enza_comp.values())
        if enza_total > 0:
            print(f'  Enza @2y: S={enza_comp[0]/enza_total*100:.0f}% M={enza_comp[1]/enza_total*100:.0f}% V={enza_comp[2]/enza_total*100:.0f}% N={enza_comp[3]/enza_total*100:.0f}%')
    
    print(f'  Enza+Alis: PFS={combo["pfs_months"]:.1f}mo' if combo['pfs_months'] else '  Enza+Alis: no progression')
    
    # Patient stratification (NE-high vs NE-low)
    print(f'\n  PATIENT STRATIFICATION:')
    for label, n0_frac in [('NE-high', 0.10), ('NE-low', 0.005)]:
        y0_strat = model.make_initial_state(
            '../results/velocity_star_latent_time.csv',
            N0=0.15, frac_N=n0_frac)
        
        m_e = UnifiedTumorODE()
        m_e.add_drug('Enzalutamide', ec50_enza, 0.8936, 5.8,
                     dose_times_enza, state_effects={'S':1.0,'M':0.0,'V':0.0,'N':0.0})
        r_e = m_e.simulate(y0_strat.copy(), 1825)
        
        m_c = UnifiedTumorODE()
        m_c.add_drug('Enzalutamide', ec50_enza, 0.8936, 5.8,
                     dose_times_enza, state_effects={'S':1.0,'M':0.0,'V':0.0,'N':0.0})
        m_c.add_drug('Alisertib', ec50_alis, 0.0029, 23/24,
                     np.array(dose_times_alis[:2000]),
                     state_effects={'S':0.0,'M':0.0,'V':0.0,'N':1.0})
        r_c = m_c.simulate(y0_strat.copy(), 1825)
        
        e_pfs = r_e['pfs_months'] if r_e['pfs_months'] else 60
        c_pfs = r_c['pfs_months'] if r_c['pfs_months'] else 60
        benefit = c_pfs - e_pfs
        print(f'    {label}: enza={e_pfs:.1f}mo combo={c_pfs:.1f}mo benefit={benefit:+.1f}mo')
    
    # Summary
    print(f'\n  VALIDATION SUMMARY:')
    targets = {
        'Control PFS': ('~7mo', ctrl['pfs_months']),
        'Docetaxel HR': ('~0.69', doc_hr),
        'Enzalutamide PFS': ('~14.8mo', enza['pfs_months']),
    }
    for name, (target, actual) in targets.items():
        actual_str = f'{actual:.1f}' if actual else 'N/A'
        print(f'    {name}: target={target} actual={actual_str}')
    
    # Save results
    results = {
        'model': 'Unified 4-state x 20-bin ODE',
        'compartments': 80,
        'control_pfs': ctrl['pfs_months'],
        'docetaxel_hr': round(doc_hr, 3) if doc_hr else None,
        'docetaxel_pfs': doc['pfs_months'],
        'enzalutamide_pfs': enza['pfs_months'],
        'combo_pfs': combo['pfs_months'],
    }
    with open('../results/unified_ode_validation.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\n  Saved: results/unified_ode_validation.json')

if __name__ == '__main__':
    validate()
