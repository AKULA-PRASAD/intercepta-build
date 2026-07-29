#!/usr/bin/env python3
"""
INTERCEPTA Stage 5: Multi-Objective Pareto Ranking
===================================================
Ranks drug candidates across ALL dimensions simultaneously:
  1. Efficacy (ODE-predicted HR or PFS)
  2. Selectivity (disease cell kill / healthy cell kill)
  3. Safety (ADMET composite score)
  4. Resistance coverage (kills resistant + sensitive)
  5. Novelty (not in ClinicalTrials.gov)
  6. Synthesizability (Lipinski + drug-likeness)

Uses Pareto dominance: candidate A dominates B if A is
better in at least one dimension and not worse in any.
Non-dominated candidates form the Pareto front.

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
"""
import numpy as np
import json
import os

def pareto_front(scores):
    """Find Pareto-optimal indices. Higher = better for all dimensions."""
    n = len(scores)
    is_dominated = np.zeros(n, dtype=bool)
    
    for i in range(n):
        for j in range(n):
            if i == j: continue
            # j dominates i if j >= i in all dims and j > i in at least one
            if np.all(scores[j] >= scores[i]) and np.any(scores[j] > scores[i]):
                is_dominated[i] = True
                break
    
    return np.where(~is_dominated)[0]

def rank_candidates(candidates):
    """
    Assign Pareto rank to each candidate.
    Rank 1 = Pareto front (best). Rank 2 = front after removing rank 1. Etc.
    """
    n = len(candidates)
    ranks = np.zeros(n, dtype=int)
    remaining = set(range(n))
    current_rank = 1
    
    # Build score matrix (higher = better for all)
    score_matrix = np.array([[c['efficacy'], c['selectivity'], c['safety'],
                              c['resistance'], c['novelty'], c['synthesizability']]
                             for c in candidates])
    
    while remaining:
        # Find Pareto front of remaining
        remaining_list = sorted(remaining)
        sub_scores = score_matrix[remaining_list]
        front_in_sub = pareto_front(sub_scores)
        
        # Assign rank
        for idx in front_in_sub:
            original_idx = remaining_list[idx]
            ranks[original_idx] = current_rank
        
        # Remove from remaining
        for idx in front_in_sub:
            remaining.discard(remaining_list[idx])
        
        current_rank += 1
        
        if current_rank > n:  # safety
            break
    
    return ranks

def composite_score(candidate, weights=None):
    """Weighted composite score for final ordering within same Pareto rank."""
    if weights is None:
        # From vision: efficacy 30%, selectivity 25%, safety 20%, 
        # resistance 15%, novelty 5%, synthesizability 5%
        weights = {'efficacy': 0.30, 'selectivity': 0.25, 'safety': 0.20,
                   'resistance': 0.15, 'novelty': 0.05, 'synthesizability': 0.05}
    
    score = sum(weights[k] * candidate[k] for k in weights)
    return round(score, 3)


def build_mcrpc_candidates():
    """
    Build candidate list for mCRPC from ALL our results.
    Each candidate gets scores 0-100 in each dimension.
    """
    candidates = []
    
    # Candidate 1: Enzalutamide + Alisertib (our lead combination)
    candidates.append({
        'name': 'Enzalutamide + Alisertib',
        'type': 'combination_existing',
        'target': 'AR (enza) + AURKA (alis)',
        'efficacy': 75,  # ODE: +10.2mo for NE-high patients
        'selectivity': 80,  # enza: AR-specific, alis: 200x AURKA selective
        'safety': 60,  # alis: known toxicity profile from Phase II
        'resistance': 90,  # targets both AR-dep AND NE escape
        'novelty': 70,  # not in ClinicalTrials.gov for prostate
        'synthesizability': 100,  # both already manufactured
        'evidence': 'Escape route ODE, Beltran CCR 2019, AACR 2023',
    })
    
    # Candidate 2: Docetaxel (standard of care - baseline)
    candidates.append({
        'name': 'Docetaxel (standard)',
        'type': 'standard_of_care',
        'target': 'Tubulin (all cells)',
        'efficacy': 50,  # HR=0.76, modest benefit
        'selectivity': 20,  # kills everything
        'safety': 40,  # significant toxicity
        'resistance': 30,  # no resistance targeting
        'novelty': 0,   # standard treatment
        'synthesizability': 100,
        'evidence': 'TAX-327 trial, validated by ODE',
    })
    
    # Candidate 3: Docetaxel + Cisplatin (known failure)
    candidates.append({
        'name': 'Docetaxel + Cisplatin',
        'type': 'combination_failed',
        'target': 'Tubulin + DNA crosslink',
        'efficacy': 10,  # HR=1.003, no benefit
        'selectivity': 10,  # both cytotoxic
        'safety': 20,  # double toxicity
        'resistance': 20,  # overlapping mechanisms
        'novelty': 0,
        'synthesizability': 100,
        'evidence': 'Multiple failed trials, predicted by ODE',
    })
    
    # Candidate 4: Olaparib + CHK1 inhibitor (escape route)
    candidates.append({
        'name': 'Olaparib + CHK1 inhibitor',
        'type': 'combination_novel',
        'target': 'PARP + CHEK1 (DDR escape)',
        'efficacy': 65,  # strong biology for BRCA2-loss
        'selectivity': 70,  # targets DDR-deficient cells
        'safety': 50,  # olaparib known, CHK1i less tested
        'resistance': 80,  # blocks BRCA2→CHEK1 escape
        'novelty': 80,  # not in prostate trials
        'synthesizability': 90,  # olaparib exists, CHK1i in trials
        'evidence': 'Escape route analysis, PROfound biology',
    })
    
    # Candidate 5: Enzalutamide + MEK inhibitor (escape route)
    candidates.append({
        'name': 'Enzalutamide + MEK inhibitor',
        'type': 'combination_novel',
        'target': 'AR + MAPK (AR→MAPK escape)',
        'efficacy': 55,  # moderate escape route evidence
        'selectivity': 65,  # both targeted
        'safety': 55,  # MEK inhibitors have skin/eye toxicity
        'resistance': 60,  # blocks one escape route
        'novelty': 60,  # MEK in prostate being explored
        'synthesizability': 100,
        'evidence': 'Escape route analysis, AR→MAPK pathway',
    })
    
    # Candidate 6: INTC-002 (novel molecule - scaffold hop)
    candidates.append({
        'name': 'INTC-002 (novel AURKA)',
        'type': 'novel_molecule',
        'target': 'AURKA (designed)',
        'efficacy': 40,  # docking only, no measured IC50
        'selectivity': 20,  # NO AURKA selectivity (AURKB -9.9)
        'safety': 85,  # zero alerts, zero soft spots
        'resistance': 50,  # targets NE escape IF it works
        'novelty': 95,  # Tanimoto 0.27 to ChEMBL
        'synthesizability': 70,  # drug-like but unsynthesized
        'evidence': 'Scout 2, docking -9.3, ADMET clean',
    })
    
    return candidates

def main():
    print('INTERCEPTA STAGE 5: PARETO MULTI-OBJECTIVE RANKING')
    print('='*60)
    
    candidates = build_mcrpc_candidates()
    
    # Compute Pareto ranks
    ranks = rank_candidates(candidates)
    
    # Compute composite scores
    for i, c in enumerate(candidates):
        c['pareto_rank'] = int(ranks[i])
        c['composite_score'] = composite_score(c)
    
    # Sort by rank then composite score
    candidates.sort(key=lambda c: (c['pareto_rank'], -c['composite_score']))
    
    print(f'\nRANKED CANDIDATES (Pareto + composite):')
    print(f'{"Rank":>4} {"Score":>6} {"Name":<30} {"Eff":>4} {"Sel":>4} {"Saf":>4} {"Res":>4} {"Nov":>4} {"Syn":>4}')
    print('-'*75)
    for c in candidates:
        print(f'{c["pareto_rank"]:>4} {c["composite_score"]:>6.1f} {c["name"]:<30} '
              f'{c["efficacy"]:>4} {c["selectivity"]:>4} {c["safety"]:>4} '
              f'{c["resistance"]:>4} {c["novelty"]:>4} {c["synthesizability"]:>4}')
    
    print(f'\nPARETO FRONT (Rank 1):')
    front = [c for c in candidates if c['pareto_rank'] == 1]
    for c in front:
        print(f'  {c["name"]}')
        print(f'    Score: {c["composite_score"]}')
        print(f'    Evidence: {c["evidence"]}')
    
    # Honest assessment
    print(f'\nHONEST ASSESSMENT OF SCORES:')
    print(f'  Efficacy scores are from ODE predictions (validated for doc)')
    print(f'  Selectivity scores are from mechanism + docking')
    print(f'  Safety scores are from ADMET (computed, not measured)')
    print(f'  Resistance scores are from escape route analysis')
    print(f'  Novelty scores are from ClinicalTrials.gov search')
    print(f'  Synthesizability: 100 for existing drugs, estimated for novel')
    print()
    print(f'  LIMITATION: Scores are on 0-100 scale assigned by us.')
    print(f'  There is no published standard for these specific scores.')
    print(f'  The RANKING ORDER is more meaningful than the numbers.')
    print(f'  Pareto dominance is objective. Score values are subjective.')
    
    # Save
    output = {
        'method': 'Pareto multi-objective ranking',
        'dimensions': ['efficacy','selectivity','safety','resistance','novelty','synthesizability'],
        'weights': {'efficacy':0.30,'selectivity':0.25,'safety':0.20,
                   'resistance':0.15,'novelty':0.05,'synthesizability':0.05},
        'candidates': [{k:v for k,v in c.items()} for c in candidates],
        'honest_note': 'Score values 0-100 are assigned based on available evidence. Ranking order is more reliable than absolute values.',
    }
    with open('../results/pareto_ranking_mcrpc.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f'\nSaved: results/pareto_ranking_mcrpc.json')

if __name__ == '__main__':
    main()
