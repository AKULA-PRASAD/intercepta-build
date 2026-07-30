"""Goal-directed molecular design (INTERCEPTA pipeline module #2).

A BRICS fragment-recombination genetic algorithm that OPTIMIZES a developability objective over known chemistry.
Molecules are valid by construction (BRICS reassembles chemically-sensible fragments). Validated in experiment B33.

HONEST SCOPE (read before use):
- This is goal-directed OPTIMIZATION of cheminformatics proxies (RDKit QED + Contrib SAscore) over KNOWN chemistry
  via fragment recombination — a design/optimization demonstration, NOT de novo discovery of real, better, or
  practically-synthesizable drugs. Every output is a COMPUTATIONAL HYPOTHESIS, not a validated molecule.
- Deterministic given a seed; reproduce ×2.
"""
import os
import random
import numpy as np
from rdkit import Chem
from rdkit.Chem import BRICS, QED

_SASCORER = None


def _sascorer():
    global _SASCORER
    if _SASCORER is None:
        import sys
        from rdkit.Chem import RDConfig
        sys.path.append(os.path.join(RDConfig.RDContribDir, "SA_Score"))
        import sascorer
        _SASCORER = sascorer
    return _SASCORER


def qed_score(mol):
    return float(QED.qed(mol))


def synth_score(mol):
    """Synthesizability in [0,1] (higher = easier): (10 - SAscore)/9, clipped."""
    sa = float(_sascorer().calculateScore(mol))
    return float(np.clip((10.0 - sa) / 9.0, 0.0, 1.0))


def developability(mol):
    """Multi-objective: drug-likeness AND synthesizability (QED × synth), in [0,1]."""
    return qed_score(mol) * synth_score(mol)


OBJECTIVES = {"multi": developability, "qed": qed_score}


class MoleculeOptimizer:
    """Elitist BRICS-fragment GA for goal-directed molecular optimization.

    opt = MoleculeOptimizer(objective="multi", pop_size=100, generations=10, seed=42)
    result = opt.optimize(seed_smiles)   # -> dict(history, best_smiles, best_score, final_population, metrics)
    """

    def __init__(self, objective="multi", pop_size=100, generations=10, elite_frac=0.2, seed=42, max_frag=600):
        if callable(objective):                       # custom fitness fn (mol -> float), e.g. DiscoveryPipeline
            self.objective, self.fitness = "custom", objective
        elif objective in OBJECTIVES:
            self.objective, self.fitness = objective, OBJECTIVES[objective]
        else:
            raise ValueError(f"objective must be one of {list(OBJECTIVES)} or a callable")
        self.pop_size, self.generations = pop_size, generations
        self.elite_k = max(1, int(elite_frac * pop_size))
        self.seed, self.max_frag = seed, max_frag

    def _mols(self, smiles):
        out = []
        for s in smiles:
            m = Chem.MolFromSmiles(str(s))
            if m is not None:
                out.append(m)
        return out

    def _fragments(self, mols):
        frags = set()
        for m in mols:
            try:
                frags |= set(BRICS.BRICSDecompose(m))
            except Exception:
                pass
        frag_mols = [Chem.MolFromSmiles(f) for f in sorted(frags)]
        return [f for f in frag_mols if f is not None][: self.max_frag]

    def _generate(self, frag_mols, n, rng_seed):
        """Deterministic BRICS recombination -> up to n valid unique canonical SMILES."""
        random.seed(rng_seed)                       # BRICSBuild scrambles reagents via the `random` module
        out, seen = [], set()
        if len(frag_mols) < 2:
            return out
        try:
            builder = BRICS.BRICSBuild(frag_mols, scrambleReagents=True, maxDepth=2)
            for i, prod in enumerate(builder):
                if i >= n * 6 or len(out) >= n:      # bounded search
                    break
                try:
                    prod.UpdatePropertyCache()
                    s = Chem.MolToSmiles(prod)
                    if s and s not in seen and Chem.MolFromSmiles(s) is not None:
                        seen.add(s); out.append(s)
                except Exception:
                    continue
        except Exception:
            pass
        return out

    def optimize(self, seed_smiles):
        rng = np.random.default_rng(self.seed)
        pop = list(dict.fromkeys(Chem.MolToSmiles(m) for m in self._mols(seed_smiles)))
        history = []
        for g in range(self.generations):
            mols = self._mols(pop)
            scores = np.array([self.fitness(m) for m in mols])
            order = np.argsort(-scores)
            elite_idx = order[: self.elite_k]
            elites = [pop[i] for i in elite_idx]
            history.append({"generation": g, "best": round(float(scores.max()), 4),
                            "mean": round(float(scores.mean()), 4), "n": len(pop)})
            # selection pressure: rebuild fragment pool from the elites, generate offspring
            frag_mols = self._fragments(self._mols(elites))
            offspring = self._generate(frag_mols, self.pop_size - self.elite_k, rng_seed=self.seed + g + 1)
            pop = list(dict.fromkeys(elites + offspring))
            if len(pop) < 2:
                break
        mols = self._mols(pop)
        scores = np.array([self.fitness(m) for m in mols])
        order = np.argsort(-scores)
        best_i = int(order[0])
        return {"objective": self.objective, "history": history,
                "best_smiles": pop[best_i], "best_score": round(float(scores[best_i]), 4),
                "final_best": round(float(scores.max()), 4), "final_mean": round(float(scores.mean()), 4),
                "final_population": [pop[i] for i in order]}
