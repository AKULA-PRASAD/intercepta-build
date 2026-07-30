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


# ================================ multi-objective (NSGA-II) ================================

def _dominates(a, b):
    """a dominates b (both maximize): a >= b on all objectives and a > b on at least one."""
    return bool(np.all(a >= b) and np.any(a > b))


def _fast_non_dominated_sort(F):
    """F: (n, m) maximize. Returns a list of fronts (each a list of row indices), best first."""
    n = len(F); S = [[] for _ in range(n)]; ndom = np.zeros(n, int); fronts = [[]]
    for p in range(n):
        for q in range(n):
            if p == q:
                continue
            if _dominates(F[p], F[q]):
                S[p].append(q)
            elif _dominates(F[q], F[p]):
                ndom[p] += 1
        if ndom[p] == 0:
            fronts[0].append(p)
    i = 0
    while fronts[i]:
        nxt = []
        for p in fronts[i]:
            for q in S[p]:
                ndom[q] -= 1
                if ndom[q] == 0:
                    nxt.append(q)
        i += 1; fronts.append(nxt)
    return [f for f in fronts if f]


def _crowding_distance(Ff):
    """Ff: (k, m). NSGA-II crowding distance per point (boundary points -> inf)."""
    k, m = Ff.shape; dist = np.zeros(k)
    if k <= 2:
        return np.full(k, np.inf)
    for j in range(m):
        order = np.argsort(Ff[:, j]); dist[order[0]] = dist[order[-1]] = np.inf
        rng = Ff[order[-1], j] - Ff[order[0], j]
        if rng == 0:
            continue
        for i in range(1, k - 1):
            dist[order[i]] += (Ff[order[i + 1], j] - Ff[order[i - 1], j]) / rng
    return dist


class ParetoOptimizer(MoleculeOptimizer):
    """Multi-objective BRICS-GA with NSGA-II selection (non-dominated sort + crowding distance) and an optional
    applicability-domain feasibility constraint (feasible individuals are always preferred to infeasible). Validated
    in B41. `objective_vec`: callable mol -> np.array of m objective values (all higher=better). `feasible`:
    optional callable mol -> bool (in the reliable/applicability domain)."""

    def __init__(self, objective_vec, feasible=None, pop_size=100, generations=10, seed=42, max_frag=600):
        super().__init__(objective="qed", pop_size=pop_size, generations=generations, seed=seed, max_frag=max_frag)
        self.objective = "pareto"; self.objective_vec = objective_vec; self.feasible = feasible

    def _F(self, mols):
        return np.vstack([np.asarray(self.objective_vec(m), float) for m in mols])

    def _feas(self, mols):
        return np.array([bool(self.feasible(m)) for m in mols]) if self.feasible else np.ones(len(mols), bool)

    def _select(self, F, feas, k):
        """Constrained NSGA-II selection of k indices: feasible first (NDS+crowding), then infeasible by objective sum."""
        idx_feas = np.where(feas)[0]; chosen = []
        if len(idx_feas):
            fronts = _fast_non_dominated_sort(F[idx_feas])
            for fr in fronts:
                gi = idx_feas[fr]
                if len(chosen) + len(gi) <= k:
                    chosen.extend(gi.tolist())
                else:
                    cd = _crowding_distance(F[gi]); chosen.extend(gi[np.argsort(-cd)][: k - len(chosen)].tolist()); break
        if len(chosen) < k:                                   # fill from infeasible by summed objective (fallback)
            inf = np.where(~feas)[0]; inf = inf[np.argsort(-F[inf].sum(1))]
            chosen.extend(inf[: k - len(chosen)].tolist())
        return chosen

    def optimize(self, seed_smiles):
        pop = list(dict.fromkeys(Chem.MolToSmiles(m) for m in self._mols(seed_smiles)))
        history = []
        for g in range(self.generations):
            mols = self._mols(pop); F = self._F(mols); feas = self._feas(mols)
            parents_idx = self._select(F, feas, self.pop_size)
            parents = [pop[i] for i in parents_idx]
            f0 = _fast_non_dominated_sort(F[np.where(feas)[0]]) if feas.any() else [[]]
            history.append({"generation": g, "n": len(pop), "n_feasible": int(feas.sum()),
                            "front0_size": int(len(f0[0])) if f0 and len(f0[0]) else 0})
            frag = self._fragments(self._mols(parents))
            offspring = self._generate(frag, self.pop_size, rng_seed=self.seed + g + 1)
            pop = list(dict.fromkeys(parents + offspring))
            if len(pop) < 2:
                break
        mols = self._mols(pop); F = self._F(mols); feas = self._feas(mols)
        fi = np.where(feas)[0]
        front0 = fi[_fast_non_dominated_sort(F[fi])[0]].tolist() if len(fi) else []
        return {"objective": "pareto", "history": history, "population": pop, "F": F, "feasible": feas,
                "front0_idx": front0, "smiles": pop}
