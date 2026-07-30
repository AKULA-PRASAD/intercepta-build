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

    def __init__(self, admet, synth, seed=42, target_model=None, target_name=None):
        self.admet, self.synth, self.seed = admet, synth, seed
        self.target_model, self.target_name = target_model, target_name   # optional QSAR for target-conditioning (B40)

    def _tox_probs(self, X):
        """P(adverse) per toxicity module for pre-featurized X -> (n, len(TOX))."""
        return np.column_stack([self.admet.models_[t].predict(X)[0] for t in self.TOX])

    def developability(self, mol):
        """Composite F in [0,1]: drug-likeness × synthesizability × predicted-safety [× P(target-active) if
        target-conditioned] (higher = better)."""
        smi = Chem.MolToSmiles(mol)
        X, _ = featurize([smi])
        safety = 1.0 - float(np.mean(self._tox_probs(X)))
        F = qed_score(mol) * synth_score(mol) * max(safety, 0.0)
        if self.target_model is not None:
            F *= float(self.target_model.predict(X)[0][0])                # × P(active against the target)
        return float(F)

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
        p_act = self.target_model.predict(X)[0] if self.target_model is not None else None
        rows = []
        for i, s in enumerate(smiles):
            m = Chem.MolFromSmiles(s)
            q = qed_score(m) if m else np.nan; sa = (10 - 9 * synth_score(m)) if m else np.nan
            safety = 1.0 - float(np.mean(tox[i]))
            F = (q * synth_score(m) * max(safety, 0.0)) if m else np.nan
            row = {"smiles": s, "qed": round(float(q), 4), "sa_score": round(float(sa), 4),
                   "synth_solvable_prob": round(float(solv[i]), 4), "p_herg": round(float(tox[i][0]), 4),
                   "p_ames": round(float(tox[i][1]), 4), "p_dili": round(float(tox[i][2]), 4),
                   "predicted_safety": round(float(safety), 4),
                   "applicability_domain": "in-domain" if bool(ad[i] and valid[i]) else "low (out-of-domain)"}
            if p_act is not None:
                pa = float(p_act[i]); F = (F * pa) if m else np.nan
                row["p_target_active"] = round(pa, 4)
            row["developability_F"] = round(float(F), 4)
            rows.append(row)
        return pd.DataFrame(rows).sort_values("developability_F", ascending=False).reset_index(drop=True)

    @classmethod
    def from_default(cls, synth_subsample=50000, seed=42, target_hts=None):
        """Fit the ADMET toxicity modules (herg/ames/dili) + synthesizability. Needs INTERCEPTA_DATA + PyTDC.
        If `target_hts` (a TDC HTS dataset name, e.g. 'hiv') is given, also fit + attach a target-activity QSAR to
        condition generation on that target (B40)."""
        admet = ADMETPredictor.from_tdc(tasks=cls.TOX)
        synth = SynthesizabilityScorer.from_rascore(subsample=synth_subsample, seed=seed, conformal=False)
        tgt = build_target_qsar(target_hts, seed=seed) if target_hts else None
        return cls(admet, synth, seed=seed, target_model=tgt, target_name=target_hts)


def build_target_qsar(hts_name, n_inactive=10000, seed=42, data_dir=None):
    """Fit a target-activity QSAR (admet._TaskModel classification + Tanimoto AD) from a TDC HTS dataset name
    (e.g. 'hiv'). Trains on all actives + a seeded inactive subsample. Validated in B40 (HIV scaffold AUROC 0.81)."""
    from tdc.single_pred import HTS
    from .admet import _TaskModel
    dd = data_dir or os.path.join(os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data"), "tdc_bio")
    d = HTS(name=hts_name, path=dd).get_data().dropna(subset=["Y", "Drug"])
    act = d[d["Y"] == 1]
    inact = d[d["Y"] == 0].sample(n=min(n_inactive, int((d["Y"] == 0).sum())), random_state=seed)
    df = pd.concat([act, inact]).reset_index(drop=True)
    X, _ = featurize(df["Drug"].tolist())
    return _TaskModel(hts_name, "roc-auc", seed=42).fit(X, df["Y"].values.astype(int))
