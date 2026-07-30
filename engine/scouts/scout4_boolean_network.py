#!/usr/bin/env python3
"""
INTERCEPTA Scout 4 v2: Boolean Network Perturbation
====================================================
Uses Signor 3.0 directed causal edges (19,727) with 247 feedback loops.
Boolean logic: gene ON if any activator ON AND no inhibitor ON.
Perturbation: fix target OFF, find new steady state.
Compensation: genes that flip ON in perturbed steady state.

This replaces the failed heat diffusion model (v1).
No compromises on the science.

Author: Prasad Akula
"""
import numpy as np
import pandas as pd
import json
from collections import defaultdict

class BooleanNetwork:
    """Boolean network with directed activation/inhibition edges."""
    
    def __init__(self, edges_csv, expression_filter=None):
        """
        Args:
            edges_csv: Signor directed edges (source, target, direction)
            expression_filter: set of genes expressed in target tissue
        """
        edges = pd.read_csv(edges_csv)
        
        # Build directed graph
        self.activators = defaultdict(set)   # gene -> set of activators
        self.inhibitors = defaultdict(set)   # gene -> set of inhibitors
        self.all_genes = set()
        
        for _, r in edges.iterrows():
            src, tgt, dirn = r['source'], r['target'], r['direction']
            if expression_filter and (src not in expression_filter or tgt not in expression_filter):
                continue
            
            if dirn == 'activation':
                self.activators[tgt].add(src)
            elif dirn == 'inhibition':
                self.inhibitors[tgt].add(src)
            
            self.all_genes.add(src)
            self.all_genes.add(tgt)
        
        self.genes = sorted(self.all_genes)
        self.N = len(self.genes)
        
        # Count feedback loops
        self.feedback_loops = []
        for tgt, acts in self.activators.items():
            for act in acts:
                if tgt in self.inhibitors.get(act, set()):
                    self.feedback_loops.append((act, tgt, 'negative'))
        for tgt, inhs in self.inhibitors.items():
            for inh in inhs:
                if tgt in self.inhibitors.get(inh, set()):
                    self.feedback_loops.append((inh, tgt, 'double_negative'))
        
        n_act = sum(len(v) for v in self.activators.values())
        n_inh = sum(len(v) for v in self.inhibitors.values())
        print(f'Boolean Network: {self.N} genes, {n_act} activations, {n_inh} inhibitions, {len(self.feedback_loops)} feedback loops')
    
    def update_gene(self, gene, state):
        """Boolean update rule for one gene.
        ON if: (any activator is ON) AND (no inhibitor is ON)
        If no regulators: stays in current state (autonomous)
        """
        acts = self.activators.get(gene, set())
        inhs = self.inhibitors.get(gene, set())
        
        if not acts and not inhs:
            return state.get(gene, True)  # no regulation = autonomous
        
        # Any activator ON?
        has_activation = False
        if acts:
            has_activation = any(state.get(a, False) for a in acts)
        else:
            has_activation = True  # no activators needed = constitutive
        
        # Any inhibitor ON?
        has_inhibition = any(state.get(i, False) for i in inhs)
        
        # ON if activated AND NOT inhibited
        return has_activation and not has_inhibition
    
    def find_steady_state(self, initial_state, fixed_genes=None, max_iter=200):
        """Run Boolean network to steady state.
        
        Args:
            initial_state: dict gene -> True/False
            fixed_genes: dict gene -> True/False (clamped, e.g. drug target)
            max_iter: maximum iterations
        
        Returns:
            dict: steady state gene -> True/False
        """
        if fixed_genes is None:
            fixed_genes = {}
        
        state = dict(initial_state)
        state.update(fixed_genes)
        
        for iteration in range(max_iter):
            new_state = {}
            for gene in self.genes:
                if gene in fixed_genes:
                    new_state[gene] = fixed_genes[gene]
                else:
                    new_state[gene] = self.update_gene(gene, state)
            
            # Check convergence
            if all(new_state.get(g) == state.get(g) for g in self.genes):
                return new_state, iteration
            
            state = new_state
        
        return state, max_iter  # may be cycling
    
    def perturb(self, target_gene, disease_state=None):
        """
        Simulate drug blocking target_gene.
        
        1. Start from disease state (all disease genes ON)
        2. Fix target to OFF (drug blocks it)
        3. Find new steady state
        4. Compare: which genes CHANGED?
        
        Returns:
            compensators: genes that turned ON (were OFF, now ON)
            casualties: genes that turned OFF (were ON, now OFF)
            unchanged: genes that stayed the same
        """
        # Disease state: all genes ON (tumor signaling active)
        if disease_state is None:
            disease_state = {g: True for g in self.genes}
        
        # Unperturbed steady state
        baseline, base_iter = self.find_steady_state(disease_state)
        
        # Perturbed: target blocked
        perturbed, pert_iter = self.find_steady_state(
            disease_state, fixed_genes={target_gene: False})
        
        compensators = []  # OFF→ON (gained activity when target blocked)
        casualties = []     # ON→OFF (lost activity)
        unchanged = []
        
        for gene in self.genes:
            if gene == target_gene:
                continue
            
            base_val = baseline.get(gene, False)
            pert_val = perturbed.get(gene, False)
            
            if not base_val and pert_val:
                compensators.append(gene)
            elif base_val and not pert_val:
                casualties.append(gene)
            else:
                unchanged.append(gene)
        
        return {
            'target': target_gene,
            'compensators': compensators,
            'casualties': casualties,
            'n_compensators': len(compensators),
            'n_casualties': len(casualties),
            'n_unchanged': len(unchanged),
            'baseline_iter': base_iter,
            'perturbed_iter': pert_iter,
        }
    
    def find_combination_targets(self, target_gene, drug_targets=None):
        """
        After blocking target_gene, find what compensates.
        Then check if compensators are druggable.
        This gives RATIONAL combination design.
        """
        result = self.perturb(target_gene)
        
        if drug_targets is None:
            return result
        
        druggable_compensators = []
        for comp in result['compensators']:
            drugs = drug_targets.get(comp, [])
            if drugs:
                druggable_compensators.append({
                    'gene': comp,
                    'drugs': drugs[:5],
                    'type': 'TRUE_COMPENSATOR',
                })
        
        result['druggable_compensators'] = druggable_compensators
        return result
    
    def test_combination(self, target1, target2, disease_state=None):
        """Test blocking two targets simultaneously."""
        if disease_state is None:
            disease_state = {g: True for g in self.genes}
        
        # Single perturbations
        single1 = self.find_steady_state(disease_state, {target1: False})[0]
        single2 = self.find_steady_state(disease_state, {target2: False})[0]
        combo = self.find_steady_state(disease_state, {target1: False, target2: False})[0]
        baseline = self.find_steady_state(disease_state)[0]
        
        # Count ON genes in each
        base_on = sum(1 for g in self.genes if baseline.get(g, False))
        s1_on = sum(1 for g in self.genes if single1.get(g, False))
        s2_on = sum(1 for g in self.genes if single2.get(g, False))
        combo_on = sum(1 for g in self.genes if combo.get(g, False))
        
        # Synergy: combo disrupts MORE than sum of singles
        expected_additive = base_on - (base_on - s1_on) - (base_on - s2_on)
        synergy = expected_additive - combo_on  # positive = synergistic
        
        return {
            'target1': target1,
            'target2': target2,
            'baseline_on': base_on,
            'single1_on': s1_on,
            'single2_on': s2_on,
            'combo_on': combo_on,
            'disruption_single1': base_on - s1_on,
            'disruption_single2': base_on - s2_on,
            'disruption_combo': base_on - combo_on,
            'synergy_score': synergy,
            'is_synergistic': synergy > 0,
        }


def main():
    print('INTERCEPTA SCOUT 4 v2: BOOLEAN NETWORK')
    print('='*60)
    
    # Load expression filter (hematopoietic for AML)
    immune = pd.read_csv('../results/step13_immune_expression.csv', index_col=0)
    immune = immune[~immune.index.duplicated(keep='first')]
    hemato_cols = [c for c in immune.columns if any(x in c.lower() 
                   for x in ['monocyte','t cell','b cell','nk cell'])]
    hemato_expr = immune[hemato_cols].max(axis=1)
    aml_expressed = set(hemato_expr[hemato_expr > 5].index)
    print(f'AML expression filter: {len(aml_expressed)} genes')
    
    # Build Boolean network
    net = BooleanNetwork('../results/signor_directed_edges.csv',
                         expression_filter=aml_expressed)
    
    # Load drug targets
    gdsc = pd.read_excel('../data/gdsc/GDSC2_fitted_dose_response.xlsx')
    drug_targets = {}
    for _, r in gdsc[['DRUG_NAME','PUTATIVE_TARGET']].drop_duplicates().iterrows():
        for t in str(r['PUTATIVE_TARGET']).split(','):
            t = t.strip()
            if t not in drug_targets: drug_targets[t] = []
            drug_targets[t].append(r['DRUG_NAME'])
    
    # Perturb each AML driver
    aml_drivers = ['FLT3','IDH1','IDH2','DNMT3A','NPM1','KIT','TP53',
                   'NRAS','KRAS','RUNX1','CEBPA','TET2']
    
    all_results = {}
    for driver in aml_drivers:
        if driver not in net.all_genes:
            print(f'\n  {driver}: NOT IN NETWORK')
            continue
        
        result = net.find_combination_targets(driver, drug_targets)
        all_results[driver] = result
        
        print(f'\n  {driver} blocked:')
        print(f'    Casualties (lose activity): {result["n_casualties"]}')
        print(f'    TRUE compensators (gain activity): {result["n_compensators"]}')
        
        if result['compensators']:
            print(f'    Compensators: {result["compensators"][:8]}')
        
        if result.get('druggable_compensators'):
            print(f'    DRUGGABLE compensators:')
            for dc in result['druggable_compensators'][:3]:
                print(f'      {dc["gene"]}: {dc["drugs"][:3]}')
    
    # Test key combinations
    print(f'\n{"="*60}')
    print(f'COMBINATION SYNERGY TESTING')
    
    combos_to_test = []
    for driver, result in all_results.items():
        if result.get('druggable_compensators'):
            for dc in result['druggable_compensators'][:2]:
                combos_to_test.append((driver, dc['gene']))
    
    for t1, t2 in combos_to_test[:10]:
        if t1 in net.all_genes and t2 in net.all_genes:
            syn = net.test_combination(t1, t2)
            status = 'SYNERGISTIC' if syn['is_synergistic'] else 'additive'
            print(f'  {t1} + {t2}: disruption {syn["disruption_combo"]} (single {syn["disruption_single1"]}+{syn["disruption_single2"]}) → {status} (synergy={syn["synergy_score"]})')
    
    # Save
    with open('../results/scout4_boolean_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f'\nSaved: results/scout4_boolean_results.json')

if __name__ == '__main__':
    main()
