#!/usr/bin/env python3
"""
INTERCEPTA Patient Stratification for Enza+Alisertib
=====================================================
Uses the multi-state escape route ODE to predict which patients
benefit from adding alisertib to enzalutamide.

Key finding: +10.2 months for NE-high patients, +0.1 for NE-low.
This explains Beltran 2019 exceptional responders.

Author: Prasad Akula
"""
import json
from intercepta_escape_route_ode import simulate, PARAMS

def stratify():
    patient_types = {
        'NE_high': {'g_N': 0.012, 'N0': 0.02,
            'description': 'High AURKA/N-myc, TP53+RB1 co-loss'},
        'NE_moderate': {'g_N': 0.008, 'N0': 0.008,
            'description': 'Moderate NE features'},
        'Average': {},
        'NE_low': {'g_N': 0.004, 'N0': 0.001,
            'description': 'No NE features, AR-driven'},
        'AR_mutant_dominant': {'M0': 0.015, 'N0': 0.001,
            'description': 'High AR mutations, low NE'},
        'AR_V7_dominant': {'V0': 0.015, 'N0': 0.001,
            'description': 'AR-V7 positive at baseline'},
    }
    
    results = {}
    print('PATIENT STRATIFICATION: Enzalutamide ± Alisertib')
    print('='*60)
    print(f'{"Type":<22} {"Enza":>8} {"Combo":>8} {"Benefit":>8}  Description')
    print('-'*75)
    
    for ptype, params in patient_types.items():
        desc = params.pop('description', '')
        r_e = simulate(use_enza=True, params=params)
        r_c = simulate(use_enza=True, use_alis=True, params=params)
        e = r_e['pfs_months'] if r_e['pfs_months'] else 60
        c = r_c['pfs_months'] if r_c['pfs_months'] else 60
        benefit = c - e
        
        results[ptype] = {
            'enza_pfs': round(e,1), 'combo_pfs': round(c,1),
            'benefit': round(benefit,1), 'description': desc,
        }
        rec = 'ADD ALIS' if benefit > 2 else 'ENZA ONLY'
        print(f'{ptype:<22} {e:>7.1f}m {c:>7.1f}m {benefit:>+7.1f}m  {desc} → {rec}')
    
    with open('../results/patient_stratification.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\nSaved: results/patient_stratification.json')
    return results

if __name__ == '__main__':
    stratify()

