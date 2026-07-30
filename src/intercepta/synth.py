"""Synthesizability scorer (INTERCEPTA pipeline module #5).

Predicts **retrosynthetic solvability** — the probability that an automated CASP tool (AiZynthFinder, USPTO
reaction templates) can find a synthesis route to a molecule — from its SMILES. Validated in experiment B31 on the
open RAscore/ChEMBL benchmark (structure-only GBT beats the trivial + SAscore baselines on a scaffold split; see
LEDGER). Reuses the ADMET featurizer + Tanimoto applicability-domain + conformal machinery so the chemistry modules
share one representation and one uncertainty framework. Also emits the fast RDKit SAscore heuristic as a
complementary signal.

HONEST SCOPE (read before use):
- Predicts ALGORITHMIC retrosynthetic solvability (USPTO templates + a fixed building-block stock) — a
  *computational proxy* for synthesizability, NOT a guarantee a molecule can be made in a real lab, and dependent on
  the CASP tool/templates/stock baked into the training labels.
- Scaffold-split generalization only. A research screening signal, not a chemistry verdict.
"""
import os
import numpy as np
import pandas as pd

from .admet import featurize, _TaskModel, NBITS, RADIUS

_SA = None


def sa_score(smiles):
    """RDKit Contrib SAscore (Ertl & Schuffenhauer 2009): 1 (easy) .. 10 (hard). NaN if unparseable. No download."""
    global _SA
    if _SA is None:
        import sys
        from rdkit.Chem import RDConfig
        sys.path.append(os.path.join(RDConfig.RDContribDir, "SA_Score"))
        import sascorer
        _SA = sascorer
    from rdkit import Chem
    one = isinstance(smiles, str)
    out = []
    for s in ([smiles] if one else smiles):
        try:
            m = Chem.MolFromSmiles(str(s))
            out.append(float(_SA.calculateScore(m)) if m is not None else float("nan"))
        except Exception:
            out.append(float("nan"))
    return out[0] if one else np.array(out)


class SynthesizabilityScorer:
    """Score molecules by predicted retrosynthetic solvability. fit(smiles, solvable) then predict(smiles).

    p = SynthesizabilityScorer.from_rascore()          # fit on the open RAscore/ChEMBL solvability labels
    out = p.predict(["CCO", "c1ccccc1"])               # tidy DataFrame with solvable_prob, sa_score, AD + conformal
    """

    def __init__(self, seed=42, nbits=NBITS, radius=RADIUS, conformal=True):
        self.seed, self.nbits, self.radius, self.conformal = seed, nbits, radius, conformal
        self._tm = None

    def fit(self, smiles, solvable):
        """smiles: iterable of SMILES; solvable: 0/1 labels (1 = a retrosynthetic route was found)."""
        X, _ = featurize(smiles, self.nbits, self.radius)
        y = np.asarray(solvable, float)
        self._tm = _TaskModel("synthesizability", "roc-auc", seed=self.seed, nbits=self.nbits,
                              radius=self.radius, conformal=self.conformal).fit(X, y)
        return self

    def predict(self, smiles):
        """Tidy DataFrame: [smiles, solvable_prob, sa_score, ad_distance, in_domain, confidence,
        (conformal_set, set_size if conformal)]. solvable_prob in [0,1] (higher = more likely synthesizable)."""
        if self._tm is None:
            raise RuntimeError("call fit() or from_rascore() first")
        smiles = list(smiles)
        X, valid = featurize(smiles, self.nbits, self.radius)
        use_conf = self._tm.conformal and self._tm.q_ is not None
        if use_conf:
            val, ad, indom, _, _, sets, sz = self._tm.predict_conformal(X)
        else:
            val, ad, indom = self._tm.predict(X); sets = sz = None
        sa = sa_score(smiles)
        rows = []
        for i, s in enumerate(smiles):
            dom = bool(indom[i] and valid[i])
            row = {"smiles": s, "solvable_prob": (float(val[i]) if valid[i] else np.nan),
                   "sa_score": (float(sa[i]) if np.isfinite(sa[i]) else np.nan),
                   "ad_distance": float(ad[i]), "in_domain": dom,
                   "confidence": "in-domain" if dom else "low (out-of-applicability-domain)"}
            if use_conf:
                row["conformal_set"] = (sets[i] if valid[i] else None)
                row["set_size"] = (int(sz[i]) if valid[i] else np.nan)
            rows.append(row)
        return pd.DataFrame(rows)

    # ---- convenience constructor from the open RAscore/ChEMBL solvability labels ----
    @classmethod
    def from_rascore(cls, data_dir=None, subsample=50000, seed=42, conformal=True, **kw):
        """Fit on RAscore's ChEMBL solvability training labels (open; AiZynthFinder/USPTO). Needs the RAscore data
        at `$INTERCEPTA_DATA/rascore/data/uspto_chembl_classification_train.csv`. Seeded subsample bounds runtime."""
        dd = data_dir or os.path.join(os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data"), "rascore", "data")
        df = pd.read_csv(os.path.join(dd, "uspto_chembl_classification_train.csv"))
        if subsample and len(df) > subsample:
            df = df.iloc[np.random.default_rng(seed).permutation(len(df))[:subsample]].reset_index(drop=True)
        return cls(seed=seed, conformal=conformal, **kw).fit(df["smi"].tolist(), df["activity"].values)
