"""INTERCEPTA engine v1 — honest mechanism-anchored drug-response ranking.

Wires together ONLY the verified signals (see ../../LEDGER.md):
  * V1/V9  learned cross-dataset expression->response transfer (per-drug Ridge, DepMap RNA-seq -> query).
  * V4-V6  verified mutation->drug mechanism markers (NRAS->MEK, NPM1->Cabo, DNMT3A->Dasatinib, FLT3-ITD->FLT3i).
  * V10    the two are COMPLEMENTARY -> combine them (proliferation-residualized), beating either alone.

HONEST SCOPE (do not overstate):
  - Effect sizes are WEAK (per-drug transfer rho ~ 0.07-0.21). Predictions are ranked hypotheses with LOW
    confidence, NOT clinical decisions.
  - Validated on ONE patient cohort (BeatAML/AML). Cross-cohort / cross-cancer validity is UNPROVEN.
  - This engine does NOT select therapy, generate molecules, or predict trial outcomes (all falsified/untested).
  - Marker adjustments apply only to the verified drug-marker pairs; all other drugs are transfer-only.
"""
import numpy as np, pandas as pd
from sklearn.linear_model import RidgeCV
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import KFold
from scipy import stats
from . import data as D
from .axes import compute_r_prolif

# Verified drug -> (marker, direction). direction=-1: mutation increases sensitivity (lowers AUC/IC50).
# Provenance: the GENOME-WIDE-ROBUST screen B5 (BH-FDR<0.05 + FLT3-ITD/prolif-deconfounded + split-replicated;
# experiments/B5_marker_discovery/results/discovered_markers.json). NRAS->MEK confirmed genome-wide;
# FLT3-ITD->FLT3i is the dominant robust axis (sorafenib BHq=4e-26, cabozantinib BHq=3.5e-17).
# CHANGED after B5: cabozantinib marker is FLT3_ITD (NOT NPM1); DNMT3A->dasatinib REMOVED — it did NOT survive
# genome-wide BH-FDR (modest pairwise effect only). See LEDGER V4/V6 refinement note + V12.
VERIFIED_MARKERS = {
    "trametinib": ("NRAS", -1), "selumetinib": ("NRAS", -1),
    "sorafenib": ("FLT3_ITD", -1), "cabozantinib": ("FLT3_ITD", -1),
}


def _z(a):
    a = np.asarray(a, float)
    s = a.std()
    return (a - a.mean()) / s if s > 0 else a - a.mean()


class InterceptaEngine:
    """Fit per-drug transfer models on cell lines; predict + rank drug response for query tumors."""

    def __init__(self, topn_genes=2000, alphas=(10.0, 100.0, 1000.0)):
        self.topn = topn_genes
        self.alphas = list(alphas)
        self.models_ = {}          # drug -> fitted RidgeCV
        self.genes_ = None         # shared feature genes
        self.fitted_drugs_ = []
        self.drug_cv_rho_ = {}     # drug -> 5-fold CV Spearman on training cells (per-drug reliability estimate)
        self._pca = None           # OOD: PCA on training expression
        self._nn = None            # OOD: kNN on training PCs
        self.seed = 42

    def fit(self, drugs=None, compute_calibration=True, label_source="gdsc"):
        """Train per-drug Ridge on DepMap RNA-seq expression -> drug response.
        label_source='gdsc': GDSC LN_IC50 (labels via COSMIC<->DepMap). 'prism': PRISM AUC (on DepMap cells,
        ~1400 drugs — broader coverage). If compute_calibration: also per-drug CV reliability + OOD detector."""
        self.label_source = label_source
        dx = D.load_depmap_expression()
        self._dx_cols = set(dx.columns)
        self.genes_ = list(dx.columns[dx.var(0).values.argsort()[::-1]][: self.topn])  # top-variance genes
        self._dxz = D.z_rows(dx[self.genes_].T).fillna(0.0)      # genes x cells
        if label_source == "prism":
            pr = D.load_prism()                                  # depmap_id, name, auc (on DepMap cells)
            pr = pr[pr["depmap_id"].isin(self._dxz.columns)]
            gl = {d.lower(): d for d in pr["name"].unique()}
            def train_xy(dk):
                t = pr[pr["name"] == gl[dk]].groupby("depmap_id")["auc"].mean()
                t = t[t.index.isin(self._dxz.columns)]
                return (self._dxz[t.index.values].T.values, t.values) if len(t) >= 30 else (None, None)
        else:
            cos2dep, _ = D.load_cosmic_depmap_map()
            gdsc = D.load_gdsc_response()
            gdsc = gdsc[gdsc["COSMIC_ID"].isin(cos2dep)].copy()
            gdsc["DepMap_ID"] = gdsc["COSMIC_ID"].map(cos2dep)
            gdsc = gdsc[gdsc["DepMap_ID"].isin(dx.index)]
            gl = {d.lower(): d for d in gdsc["DRUG_NAME"].unique()}
            def train_xy(dk):
                t = gdsc[gdsc["DRUG_NAME"] == gl[dk]].dropna(subset=["LN_IC50"]).drop_duplicates("DepMap_ID")
                t = t[t["DepMap_ID"].isin(self._dxz.columns)]
                return (self._dxz[t["DepMap_ID"].values].T.values, t["LN_IC50"].values) if len(t) >= 30 else (None, None)
        want = [d.lower() for d in drugs] if drugs else list(gl)
        for dk in want:
            if dk not in gl:
                continue
            Xtr, ytr = train_xy(dk)
            if Xtr is None:
                continue
            self.models_[dk] = RidgeCV(alphas=self.alphas).fit(Xtr, ytr)
            if compute_calibration and len(ytr) >= 25:      # per-drug reliability = 5-fold CV Spearman
                kf = KFold(5, shuffle=True, random_state=self.seed); cvp = np.empty(len(ytr))
                for tri, tei in kf.split(Xtr):
                    cvp[tei] = RidgeCV(alphas=self.alphas).fit(Xtr[tri], ytr[tri]).predict(Xtr[tei])
                self.drug_cv_rho_[dk] = float(stats.spearmanr(cvp, ytr)[0])
        self.fitted_drugs_ = sorted(self.models_)
        if compute_calibration:                              # OOD detector: PCA + kNN on training expression
            Xall = self._dxz.T.values
            self._pca = PCA(n_components=min(20, Xall.shape[1]), random_state=self.seed).fit(Xall)
            self._nn = NearestNeighbors(n_neighbors=10).fit(self._pca.transform(Xall))
        return self

    def ood_score(self, expr):
        """Out-of-distribution score per query sample = mean distance to 10 nearest TRAINING cells in PC space.
        Higher = further from the cell-line training distribution = less trustworthy (patients are inherently OOD)."""
        if self._pca is None:
            return pd.Series(np.nan, index=expr.columns)
        xz = D.z_rows(expr.reindex(self.genes_).fillna(0.0)).fillna(0.0)
        d, _ = self._nn.kneighbors(self._pca.transform(xz.T.values))
        return pd.Series(d.mean(1), index=expr.columns)

    def predict_transfer(self, expr):
        """expr: genes(symbol) x samples DataFrame. Returns samples x drugs predicted LN_IC50 (z per drug)."""
        xz = D.z_rows(expr.reindex(self.genes_).fillna(0.0)).fillna(0.0)   # align to feature genes; z, NaN-safe
        X = xz.T.values
        out = {dk: _z(m.predict(X)) for dk, m in self.models_.items()}
        return pd.DataFrame(out, index=expr.columns)

    def rank(self, expr, mutations=None):
        """Combined mechanism-anchored ranking per sample.
        expr: genes x samples. mutations: optional DataFrame samples x {NRAS,NPM1,DNMT3A,FLT3_ITD} in {0,1}.
        Returns long DataFrame [sample, drug, transfer_z, marker, combined_score, confidence].
        combined_score: higher = predicted MORE SENSITIVE. = -(transfer_z) + marker_bonus.
        """
        pred = self.predict_transfer(expr)                       # samples x drugs (z LN_IC50; higher=resistant)
        ood = self.ood_score(expr)                               # per-sample OOD distance
        ood_med = ood.median()                                   # B6-validated confidence gate (low OOD = more accurate)
        rows = []
        for s in pred.index:
            for dk in pred.columns:
                tz = float(pred.loc[s, dk])
                marker_val, mk_name = np.nan, None
                bonus = 0.0
                if dk in VERIFIED_MARKERS and mutations is not None:
                    mk_name, direction = VERIFIED_MARKERS[dk]
                    if mk_name in mutations.columns and s in mutations.index and np.isfinite(mutations.loc[s, mk_name]):
                        marker_val = float(mutations.loc[s, mk_name])
                        bonus = -direction * marker_val          # sensitizing mutation -> +bonus (more sensitive)
                combined = -tz + bonus                           # higher = more sensitive
                od = float(ood.get(s, np.nan))
                # confidence from the ONLY validated axis (B6 H2): low-OOD samples are more accurate.
                # Still capped at MODERATE — absolute accuracy is weak; reliability axis was NOT calibrated (B6 H1 null).
                conf = "LOW" if not np.isfinite(od) else ("MODERATE" if od <= ood_med else "LOW")
                rows.append({"sample": s, "drug": dk, "transfer_z": round(tz, 4),
                             "marker": mk_name, "marker_present": marker_val,
                             "combined_score": round(combined, 4),
                             "drug_cv_reliability": (round(self.drug_cv_rho_[dk], 4) if dk in self.drug_cv_rho_ else np.nan),
                             "ood_distance": (round(od, 4) if np.isfinite(od) else np.nan),
                             "confidence": conf})
        return pd.DataFrame(rows)


def load_beataml_mutation_matrix():
    """Build BeatAML per-rnaseq-sample {NRAS,DNMT3A,NPM1,FLT3_ITD} 0/1 matrix (for demo/validation)."""
    clin = D.load_beataml_clinical().dropna(subset=["dbgap_rnaseq_sample"]).copy()
    wes = D.load_beataml_wes_gene_status(["NRAS", "DNMT3A"])
    import pandas as pd
    wraw = pd.read_csv(D._bp("beataml_wes_wv1to4_mutations_dbgap.txt"), sep="\t", usecols=["dbgap_sample_id"])
    tested = set(wraw["dbgap_sample_id"].unique())

    def pos(x):
        s = str(x).strip().lower()
        return 1.0 if s in ("positive", "yes", "mutated", "pos") else (0.0 if s in ("negative", "no", "wildtype", "wt", "neg") else np.nan)

    def wes_call(dna, gs):
        return np.nan if (pd.isna(dna) or dna not in tested) else (1.0 if dna in gs else 0.0)

    clin["NPM1"] = clin["NPM1"].map(pos)
    clin["FLT3_ITD"] = clin["FLT3-ITD"].map(pos)
    clin["NRAS"] = clin["dbgap_dnaseq_sample"].map(lambda d: wes_call(d, wes["NRAS"]))
    clin["DNMT3A"] = clin["dbgap_dnaseq_sample"].map(lambda d: wes_call(d, wes["DNMT3A"]))
    return clin.set_index("dbgap_rnaseq_sample")[["NRAS", "DNMT3A", "NPM1", "FLT3_ITD"]]
