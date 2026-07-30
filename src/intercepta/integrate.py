"""Integrated developability prioritizer (INTERCEPTA platform MVP).

Composes the independently-validated modules — B30 ADMET/safety + B31 synthesizability — into (a) a per-molecule
module PROFILE and (b) a single composite **developability risk** (predicted probability of clinical-toxicity
failure).

HONEST SCOPE — read before use (B32 result is a FIRST-CLASS NEGATIVE):
- Experiment B32 tested "whole > parts" on the held-out ClinTox outcome (leakage-free scaffold split) and it
  FAILED: the composite (AUROC 0.819±0.011) did NOT beat the single best module output (plasma-protein-binding
  ppbr_az, ~0.83), and a direct structure model (0.857) beat both. So this composite is a **convenience
  aggregator + interpretable profile**, NOT a validated improvement over using the single best ADMET endpoint.
- Use the per-module PROFILE (each column is a B30/B31-validated module) for interpretability; do not treat the
  composite `developability_risk` as better than its best component.
- A research PRIORITIZATION signal only — NOT a clinical/regulatory safety determination, NOT a prediction of trial
  success. Small positive class (~103), scaffold-split, survivorship-confounded. Every score is a hypothesis.
"""
import os
import numpy as np
import pandas as pd

from .admet import ADMETPredictor, featurize, NBITS
from .synth import SynthesizabilityScorer, sa_score

PANEL = ["herg", "ames", "dili", "ld50_zhu", "cyp3a4_veith", "bioavailability_ma",
         "bbb_martins", "ppbr_az", "clearance_microsome_az", "half_life_obach"]


class DevelopabilityPrioritizer:
    """Fit once (`from_default`), then `predict(smiles)` -> per-molecule module profile + composite risk.

    p = DevelopabilityPrioritizer.from_default()
    out = p.predict(["CC(=O)Oc1ccccc1C(=O)O", ...])   # columns: PANEL preds + synth + sa + developability_risk + AD
    """

    def __init__(self, admet, synth, scaler, logistic, feat_names, medians):
        self.admet, self.synth = admet, synth
        self.scaler, self.logistic = scaler, logistic
        self.feat_names, self.medians = feat_names, medians

    def _features(self, smiles):
        admet_wide = self.admet.predict(smiles, tidy=False)[PANEL]
        solv = self.synth.predict(smiles)["solvable_prob"].values
        sa = np.asarray(sa_score(smiles), float)
        M = np.column_stack([admet_wide.values, solv, sa]).astype(float)
        M = np.where(np.isfinite(M), M, self.medians)         # impute with training medians
        return M, admet_wide, solv, sa

    def predict(self, smiles):
        """Tidy DataFrame: smiles + the 10 ADMET predictions + synth_solvable_prob + sa_score + developability_risk
        (composite probability of clinical-tox failure; higher = riskier) + applicability_domain flag."""
        smiles = list(smiles)
        M, admet_wide, solv, sa = self._features(smiles)
        risk = self.logistic.predict_proba(self.scaler.transform(M))[:, 1]
        ood = self.admet.predict(smiles, tasks=["herg"])                # reuse a module's Tanimoto AD as a proxy
        indom = ood.set_index("smiles")["in_domain"].reindex(smiles).fillna(False).values
        out = pd.DataFrame({"smiles": smiles})
        for c in PANEL:
            out[c] = admet_wide[c].values
        out["synth_solvable_prob"] = solv
        out["sa_score"] = sa
        out["developability_risk"] = risk                              # composite, in [0,1]
        out["applicability_domain"] = ["in-domain" if d else "low (out-of-domain)" for d in indom]
        return out.sort_values("developability_risk", ascending=False).reset_index(drop=True)

    # ---- default constructor: fit modules + composite on the open ClinTox outcome (leakage-free) ----
    @classmethod
    def from_default(cls, synth_subsample=50000, seed=42):
        """Fit the ADMET panel (own TDC data) + synthesizability (RAscore) + the composite logistic (on ClinTox,
        leakage-controlled). Needs INTERCEPTA_DATA (tdc_admet, rascore) + PyTDC. Deterministic."""
        from rdkit import Chem
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from tdc.single_pred import Tox
        DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
        canon = lambda s: (Chem.MolToSmiles(Chem.MolFromSmiles(str(s))) if Chem.MolFromSmiles(str(s)) else None)
        admet = ADMETPredictor.from_tdc(tasks=PANEL)
        synth = SynthesizabilityScorer.from_rascore(subsample=synth_subsample, seed=seed, conformal=False)
        ct = Tox(name="clintox", path=os.path.join(DATA, "tdc_tox")).get_data().dropna(subset=["Drug"])
        ct = ct.assign(canon=[canon(s) for s in ct["Drug"]]).dropna(subset=["canon"]).drop_duplicates("canon")
        # leakage: drop ClinTox molecules seen by any module
        from tdc.benchmark_group import admet_group
        g = admet_group(path=os.path.join(DATA, "tdc_admet"))
        seen = set()
        for t in PANEL:
            seen |= set(filter(None, (canon(s) for s in g.get(t)["train_val"]["Drug"])))
        rs = pd.read_csv(os.path.join(DATA, "rascore", "data", "uspto_chembl_classification_train.csv"))
        rs = rs.iloc[np.random.default_rng(seed).permutation(len(rs))[:synth_subsample]]
        seen |= set(filter(None, (canon(s) for s in rs["smi"])))
        ct = ct[~ct["canon"].isin(seen)].reset_index(drop=True)
        smiles = ct["Drug"].tolist(); yv = ct["Y"].values.astype(int)
        admet_wide = admet.predict(smiles, tidy=False)[PANEL]
        solv = synth.predict(smiles)["solvable_prob"].values
        sa = np.asarray(sa_score(smiles), float)
        feat_names = PANEL + ["synth_solvable_prob", "sa_score"]
        M = np.column_stack([admet_wide.values, solv, sa]).astype(float)
        medians = np.nanmedian(np.where(np.isfinite(M), M, np.nan), axis=0)
        medians = np.where(np.isfinite(medians), medians, 0.0)
        M = np.where(np.isfinite(M), M, medians)
        scaler = StandardScaler().fit(M)
        logistic = LogisticRegression(max_iter=1000, C=1.0).fit(scaler.transform(M), yv)
        return cls(admet, synth, scaler, logistic, feat_names, medians)
