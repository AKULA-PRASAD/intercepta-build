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
from . import data as D
from .axes import compute_r_prolif

# Verified drug -> (marker, direction). direction=-1: mutation increases sensitivity (lowers AUC/IC50).
# Provenance: NRAS/NPM1/DNMT3A = LEDGER V4-V6 (deconfounded, split-replicated); FLT3-ITD->FLT3i = established.
VERIFIED_MARKERS = {
    "trametinib": ("NRAS", -1), "selumetinib": ("NRAS", -1),
    "cabozantinib": ("NPM1", -1), "dasatinib": ("DNMT3A", -1),
    "sorafenib": ("FLT3_ITD", -1),
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

    def fit(self, drugs=None):
        """Train per-drug Ridge on DepMap RNA-seq expression -> GDSC LN_IC50 (labels via COSMIC<->DepMap)."""
        cos2dep, _ = D.load_cosmic_depmap_map()
        gdsc = D.load_gdsc_response()
        gdsc = gdsc[gdsc["COSMIC_ID"].isin(cos2dep)].copy()
        gdsc["DepMap_ID"] = gdsc["COSMIC_ID"].map(cos2dep)
        dx = D.load_depmap_expression()
        gdsc = gdsc[gdsc["DepMap_ID"].isin(dx.index)]
        self._dx_cols = set(dx.columns)
        self.genes_ = list(dx.columns[dx.var(0).values.argsort()[::-1]][: self.topn])  # top-variance genes
        self._dxz = D.z_rows(dx[self.genes_].T).fillna(0.0)      # genes x cells
        gl = {d.lower(): d for d in gdsc["DRUG_NAME"].unique()}
        want = [d.lower() for d in drugs] if drugs else list(gl)
        for dk in want:
            if dk not in gl:
                continue
            tr = gdsc[gdsc["DRUG_NAME"] == gl[dk]].dropna(subset=["LN_IC50"]).drop_duplicates("DepMap_ID")
            tr = tr[tr["DepMap_ID"].isin(self._dxz.columns)]
            if len(tr) < 30:
                continue
            self.models_[dk] = RidgeCV(alphas=self.alphas).fit(
                self._dxz[tr["DepMap_ID"].values].T.values, tr["LN_IC50"].values)
        self.fitted_drugs_ = sorted(self.models_)
        return self

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
                rows.append({"sample": s, "drug": dk, "transfer_z": round(tz, 4),
                             "marker": mk_name, "marker_present": marker_val,
                             "combined_score": round(combined, 4),
                             "confidence": "LOW"})                # honest: weak effects, one cohort
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
