"""End-to-end in-silico candidate discovery (INTERCEPTA pipeline, assembled).

Composes the validated modules into a working generate → screen → rank pipeline: a goal-directed BRICS genetic
algorithm (design, B33) optimizes a multi-objective of drug-likeness × synthesizability (B31) × predicted-safety
(B30 ADMET toxicity modules), and returns ranked candidate molecules with full profiles + applicability-domain flags.
Validated in B39.

HONEST SCOPE (read before use):
- This is a COMPUTATIONAL PRIORITIZATION demonstration over KNOWN chemistry (fragment recombination). Every output is
  a hypothesis, NOT a validated, novel, safe, or synthesizable-in-practice drug, and NOT a clinical/safety verdict.
- Optimizing against in-silico predictors invites gaming: the GA can find molecules the models *call* good. The
  applicability-domain flag marks candidates whose safety/synth calls are out-of-domain (unreliable). Weight scores
  accordingly.
"""
import os
import numpy as np
import pandas as pd
from rdkit import Chem

from .admet import ADMETPredictor, featurize
from .synth import SynthesizabilityScorer
from .generate import MoleculeOptimizer, qed_score, synth_score


class DiscoveryPipeline:
    """Assemble design + synthesizability + ADMET-safety into a candidate generator.

    p = DiscoveryPipeline.from_default()
    out = p.discover(pop_size=100, generations=10, top=20)   # ranked candidates + full profiles
    """

    TOX = ["herg", "ames", "dili"]                    # B30 toxicity modules used as the safety objective

    def __init__(self, admet, synth, seed=42):
        self.admet, self.synth, self.seed = admet, synth, seed

    def _tox_probs(self, X):
        """P(adverse) per toxicity module for pre-featurized X -> (n, len(TOX))."""
        return np.column_stack([self.admet.models_[t].predict(X)[0] for t in self.TOX])

    def developability(self, mol):
        """Composite F in [0,1]: drug-likeness × synthesizability × predicted-safety (higher = better)."""
        smi = Chem.MolToSmiles(mol)
        X, _ = featurize([smi])
        safety = 1.0 - float(np.mean(self._tox_probs(X)))
        return float(qed_score(mol) * synth_score(mol) * max(safety, 0.0))

    def discover(self, seed_smiles=None, pop_size=100, generations=10, top=20):
        if seed_smiles is None:
            dd = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
            df = pd.read_csv(os.path.join(dd, "tdc_gen", "chembl.tab"), sep="\t")
            col = "smiles" if "smiles" in df.columns else df.columns[-1]
            seed_smiles = df[col].dropna().sample(200, random_state=self.seed).tolist()
        seed_smiles = [Chem.MolToSmiles(m) for m in (Chem.MolFromSmiles(s) for s in seed_smiles) if m is not None]
        opt = MoleculeOptimizer(objective=self.developability, pop_size=pop_size, generations=generations, seed=self.seed)
        res = opt.optimize(seed_smiles)
        return self.profile(res["final_population"][:top]), res["history"]

    def profile(self, smiles):
        """Full per-candidate profile: developability F + components + per-module tox probs + AD flag; ranked desc by F."""
        smiles = list(smiles)
        X, valid = featurize(smiles)
        tox = self._tox_probs(X)
        ad = self.admet.predict(smiles, tasks=["herg"]).set_index("smiles")["in_domain"].reindex(smiles).fillna(False).values
        solv = self.synth.predict(smiles)["solvable_prob"].values
        rows = []
        for i, s in enumerate(smiles):
            m = Chem.MolFromSmiles(s)
            q = qed_score(m) if m else np.nan; sa = (10 - 9 * synth_score(m)) if m else np.nan
            safety = 1.0 - float(np.mean(tox[i]))
            F = (q * synth_score(m) * max(safety, 0.0)) if m else np.nan
            rows.append({"smiles": s, "developability_F": round(float(F), 4), "qed": round(float(q), 4),
                         "sa_score": round(float(sa), 4), "synth_solvable_prob": round(float(solv[i]), 4),
                         "p_herg": round(float(tox[i][0]), 4), "p_ames": round(float(tox[i][1]), 4),
                         "p_dili": round(float(tox[i][2]), 4), "predicted_safety": round(float(safety), 4),
                         "applicability_domain": "in-domain" if bool(ad[i] and valid[i]) else "low (out-of-domain)"})
        return pd.DataFrame(rows).sort_values("developability_F", ascending=False).reset_index(drop=True)

    @classmethod
    def from_default(cls, synth_subsample=50000, seed=42):
        """Fit the ADMET toxicity modules (herg/ames/dili) + synthesizability. Needs INTERCEPTA_DATA + PyTDC."""
        admet = ADMETPredictor.from_tdc(tasks=cls.TOX)
        synth = SynthesizabilityScorer.from_rascore(subsample=synth_subsample, seed=seed, conformal=False)
        return cls(admet, synth, seed=seed)
