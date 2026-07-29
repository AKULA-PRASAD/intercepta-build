"""Synergy ranking module (INTERCEPTA combinations arm).

Turns the VALIDATED result V23 (B24/B25: drug-combination synergy generalizes to unseen combinations of a KNOWN
drug library; leave-combination-out Spearman ~0.6, replicated across O'Neil + DrugComb) into a usable tool: given a
tumor/cell expression profile, rank the most synergistic drug pairs from a defined library, with OOD-gated
confidence.

HONEST SCOPE (read before use):
- Validated at the CELL-LINE level (Loewe synergy); NOT a clinical predictor.
- Works for combinations of drugs IN the training library (known drugs). It does NOT generalize to novel drugs
  (B25/B26 — leave-drug-out is weak) — `rank_pairs` therefore only scores pairs from the fitted library.
- Confidence is capped at MODERATE and gated by out-of-distribution distance; every score is a research hypothesis.
"""
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import HistGradientBoostingRegressor
from itertools import combinations

NBITS = 1024


def _morgan(smiles, nbits=NBITS):
    """Order-invariant Morgan/ECFP4 fingerprint (needs rdkit); zeros if unparseable/unavailable."""
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
    except Exception:
        return np.zeros(nbits, np.int8)
    m = Chem.MolFromSmiles(str(smiles))
    if m is None:
        return np.zeros(nbits, np.int8)
    bs = AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=nbits).ToBitString()
    return np.frombuffer(bs.encode(), "u1").astype(np.int8) - ord("0")


class SynergyRanker:
    """Rank synergistic drug pairs (from a fixed library) for a query expression profile.

    fit(synergy, cell_expr, smiles): synergy = DataFrame[Drug1_ID, Drug2_ID, Cell, Y(=Loewe)];
    cell_expr = DataFrame cells x genes (training cells, same key as synergy['Cell']);
    smiles = {drug_id: SMILES}. Reproducible, deterministic.
    """

    def __init__(self, seed=42, n_pca=20, nbits=NBITS):
        self.seed, self.n_pca, self.nbits = seed, n_pca, nbits
        self.genes_ = self.library_ = self._fp = self._scaler = self._pca = self._nn = self._model = None
        self.cv_leave_combination_rho_ = self.ood_threshold_ = None

    # ---- internal featurization ----
    def _cell_pca(self, expr_cells_by_genes):
        X = expr_cells_by_genes.reindex(columns=self.genes_).fillna(0.0).values
        return self._pca.transform(self._scaler.transform(X))

    def _pair_feat(self, cell_pc_row, d1, d2):
        f1, f2 = self._fp[d1], self._fp[d2]
        return np.concatenate([cell_pc_row, (f1 + f2).astype(np.int8), (f1 & f2).astype(np.int8)])

    # ---- fit ----
    def fit(self, synergy, cell_expr, smiles, compute_cv=True):
        self.genes_ = list(cell_expr.columns)
        self.library_ = sorted(set(synergy["Drug1_ID"]) | set(synergy["Drug2_ID"]))
        self._fp = {d: _morgan(smiles[d], self.nbits) for d in self.library_ if d in smiles}
        self.library_ = [d for d in self.library_ if d in self._fp]
        syn = synergy[synergy["Drug1_ID"].isin(self._fp) & synergy["Drug2_ID"].isin(self._fp)
                      & synergy["Cell"].isin(cell_expr.index)].reset_index(drop=True)
        # cell representation: standardize genes -> PCA (fit on training cells)
        cells = list(cell_expr.index)
        self._scaler = StandardScaler().fit(cell_expr.values)
        self._pca = PCA(n_components=min(self.n_pca, len(cells) - 1), random_state=self.seed).fit(self._scaler.transform(cell_expr.values))
        cellpc = pd.DataFrame(self._pca.transform(self._scaler.transform(cell_expr.values)), index=cells)
        self._nn = NearestNeighbors(n_neighbors=min(10, len(cells))).fit(cellpc.values)
        # ABSOLUTE OOD threshold, calibrated on the training cells' own neighbor distances (excl. self):
        # a query beyond the 95th percentile of training in-distribution distance is flagged low-confidence.
        dtr, _ = self._nn.kneighbors(cellpc.values)
        self.ood_threshold_ = float(np.percentile(dtr[:, 1:].mean(1), 95)) if dtr.shape[1] > 1 else float(dtr.mean())
        # assemble training matrix
        X = np.vstack([self._pair_feat(cellpc.loc[r.Cell].values, r.Drug1_ID, r.Drug2_ID) for r in syn.itertuples()])
        y = syn["Y"].values.astype(float)
        self._model = HistGradientBoostingRegressor(random_state=self.seed, max_iter=300, learning_rate=0.06, max_depth=6).fit(X, y)
        if compute_cv:
            self.cv_leave_combination_rho_ = self._cv_leave_combination(syn, cellpc)
        return self

    def _cv_leave_combination(self, syn, cellpc):
        """Honest self-validation: leave-drug-combination-out CV Spearman (the property the tool relies on)."""
        from sklearn.model_selection import GroupKFold
        from scipy import stats
        pair = (syn["Drug1_ID"] + "|" + syn["Drug2_ID"]).apply(lambda s: "|".join(sorted(s.split("|")))).values
        X = np.vstack([self._pair_feat(cellpc.loc[r.Cell].values, r.Drug1_ID, r.Drug2_ID) for r in syn.itertuples()])
        y = syn["Y"].values.astype(float); oof = np.full(len(y), np.nan)
        for tr, te in GroupKFold(min(5, len(set(pair)))).split(X, y, pair):
            mdl = HistGradientBoostingRegressor(random_state=self.seed, max_iter=300, learning_rate=0.06, max_depth=6).fit(X[tr], y[tr])
            oof[te] = mdl.predict(X[te])
        return float(stats.spearmanr(oof, y)[0])

    # ---- inference ----
    def ood_score(self, expr):
        """expr: genes x samples. Mean distance to 10 nearest TRAINING cells in PC space (higher = less trustworthy)."""
        pc = self._cell_pca(expr.T)
        d, _ = self._nn.kneighbors(pc)
        return pd.Series(d.mean(1), index=expr.columns)

    def rank_pairs(self, expr, library=None, top=20):
        """expr: genes x samples DataFrame. Returns ranked synergistic pairs per sample from the KNOWN library.
        Columns: sample, drug1, drug2, predicted_synergy, ood_distance, confidence."""
        if self._model is None:
            raise RuntimeError("call fit() first")
        lib = [d for d in (library or self.library_) if d in self._fp]
        pairs = list(combinations(sorted(lib), 2))
        pc = self._cell_pca(expr.T)                      # samples x n_pca
        ood = self.ood_score(expr)
        rows = []
        for si, s in enumerate(expr.columns):
            X = np.vstack([self._pair_feat(pc[si], a, b) for a, b in pairs])
            pred = self._model.predict(X)
            od = float(ood.get(s, np.nan))
            conf = "low (out-of-distribution)" if od > self.ood_threshold_ else "moderate"
            for (a, b), p in zip(pairs, pred):
                rows.append({"sample": s, "drug1": a, "drug2": b, "predicted_synergy": round(float(p), 3),
                             "ood_distance": round(od, 3), "confidence": conf})
        out = pd.DataFrame(rows).sort_values(["sample", "predicted_synergy"], ascending=[True, False])
        return out.groupby("sample", group_keys=False).head(top).reset_index(drop=True) if top else out

    # ---- convenience constructor from the cached open O'Neil data + DepMap expression ----
    @classmethod
    def from_oneil(cls, data_dir=None, **kw):
        import os, re
        from . import data as D
        dd = data_dir or os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
        syn = pd.read_parquet(os.path.join(dd, "oneil_synergy.parquet")).rename(columns={"Cell_Line_ID": "Cell"})
        smiles = pd.read_parquet(os.path.join(dd, "oneil_smiles.parquet")).set_index("id")["smiles"].to_dict()
        rna = D.load_depmap_expression()
        meta = pd.read_csv(os.path.join(dd, "depmap_meta.csv"))
        norm = lambda x: re.sub(r"[^a-z0-9]", "", str(x).lower())
        n2a = {}
        for _, r in meta.iterrows():
            for c in ["stripped_cell_line_name", "CCLE_Name", "cell_line_name"]:
                v = r.get(c)
                if pd.notna(v):
                    n2a[norm(str(v).split("_")[0] if c == "CCLE_Name" else v)] = r["DepMap_ID"]
        syn["Cell"] = syn["Cell"].map(lambda c: n2a.get(norm(c)))
        syn = syn.dropna(subset=["Cell"])
        cells = [c for c in syn["Cell"].unique() if c in rna.index]
        cell_expr = rna.loc[cells]
        return cls(**kw).fit(syn[syn["Cell"].isin(cells)], cell_expr, smiles)
