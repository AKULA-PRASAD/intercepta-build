"""Real unit tests for the INTERCEPTA engine core. Run WITHOUT the large external data (synthetic/mocked),
so they are fast and CI-able. Integration tests that need INTERCEPTA_DATA are separate (the experiments/).
"""
import numpy as np
import pandas as pd
import pytest
from scipy import stats

from intercepta.metrics import bh_fdr, per_drug_spearman, paired_wilcoxon, permutation_p
from intercepta.splits import disjoint_train_cosmics
from intercepta.axes import compute_r_prolif, CELL_CYCLE, REPLICATION, GROWTH, QUIESCENCE
from intercepta import engine as E


# ---- metrics ----
def test_bh_fdr_monotone_and_bounded():
    p = np.array([0.001, 0.01, 0.5, 0.9])
    q = bh_fdr(p)
    assert np.all((q >= 0) & (q <= 1))
    assert q[0] <= q[1] <= q[2] <= q[3]          # BH preserves order
    assert q[-1] == pytest.approx(0.9, abs=1e-9)  # largest p * n/n

def test_bh_fdr_nan_safe():
    q = bh_fdr([0.01, np.nan, 0.02])
    assert np.isnan(q[1]) and np.isfinite(q[0]) and np.isfinite(q[2])

def test_per_drug_spearman_perfect():
    assert per_drug_spearman([1, 2, 3, 4], [4, 5, 6, 7]) == pytest.approx(1.0)
    assert per_drug_spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)

def test_paired_wilcoxon_runs():
    w, p = paired_wilcoxon([0.3, 0.4, 0.5, 0.2], [0.1, 0.2, 0.1, 0.0])
    assert 0 <= p <= 1

def test_permutation_p_deterministic():
    fn = lambda rng: rng.normal()
    a = permutation_p(0.0, fn, k=500, seed=42)
    b = permutation_p(0.0, fn, k=500, seed=42)
    assert a == b and 0 < a <= 1


# ---- splits (leakage correction) ----
def test_disjoint_train_removes_test_cosmics():
    tr = pd.DataFrame({"COSMIC_ID": ["1", "2", "3", "4"], "y": [0, 1, 2, 3]})
    dep2cos = {"D2": "2", "D3": "3"}
    out = disjoint_train_cosmics(tr, ["D2", "D3"], dep2cos)
    assert set(out["COSMIC_ID"]) == {"1", "4"}   # test lines 2,3 removed


# ---- axes ----
def test_r_prolif_sigmoid_bounded_and_responsive():
    genes = CELL_CYCLE + REPLICATION + GROWTH + QUIESCENCE
    rng = np.random.default_rng(0)
    expr = pd.DataFrame(rng.normal(size=(len(set(genes)), 20)), index=sorted(set(genes)),
                        columns=[f"s{i}" for i in range(20)])
    r = compute_r_prolif(expr)
    assert r.notna().all() and ((r > 0) & (r < 1)).all()   # sigmoid output in (0,1)
    # raising proliferation genes in one sample raises its score vs lowering them
    hi = expr.copy(); hi.loc[CELL_CYCLE, "s0"] += 5; hi.loc[GROWTH, "s0"] += 5
    lo = expr.copy(); lo.loc[CELL_CYCLE, "s0"] -= 5
    assert compute_r_prolif(hi)["s0"] > compute_r_prolif(lo)["s0"]


# ---- engine.rank (mocked fit; no external data) ----
class _LinModel:
    def predict(self, X):
        return X[:, 0]           # deterministic linear readout

def _fake_engine(genes):
    eng = E.InterceptaEngine()
    eng.genes_ = list(genes)
    eng.models_ = {"trametinib": _LinModel(), "gemcitabine": _LinModel()}
    eng.fitted_drugs_ = ["gemcitabine", "trametinib"]
    eng.drug_cv_rho_ = {}
    eng._pca = None; eng._nn = None    # OOD unavailable -> confidence LOW
    return eng

def test_engine_rank_shape_and_columns():
    genes = [f"G{i}" for i in range(10)]
    eng = _fake_engine(genes)
    expr = pd.DataFrame(np.random.default_rng(1).normal(size=(10, 6)), index=genes,
                        columns=[f"p{i}" for i in range(6)])
    out = eng.rank(expr)
    assert set(["sample", "drug", "transfer_z", "combined_score", "confidence"]).issubset(out.columns)
    assert len(out) == 6 * 2                          # samples x fitted drugs
    assert (out["confidence"] == "LOW").all()         # OOD unavailable -> LOW

def test_engine_marker_bonus_direction():
    """A sensitizing marker (NRAS for trametinib) must RAISE combined_score (=more sensitive)."""
    genes = [f"G{i}" for i in range(6)]
    eng = _fake_engine(genes)
    expr = pd.DataFrame(np.zeros((6, 2)), index=genes, columns=["p0", "p1"])
    mut = pd.DataFrame({"NRAS": [1.0, 0.0]}, index=["p0", "p1"])
    out = eng.rank(expr, mutations=mut)
    tram = out[out["drug"] == "trametinib"].set_index("sample")
    # p0 is NRAS-mut (sensitizing) -> higher combined_score than wildtype p1
    assert tram.loc["p0", "combined_score"] > tram.loc["p1", "combined_score"]


# ---- data sha256 gate ----
def test_data_verify_rejects_mismatch(monkeypatch, tmp_path):
    from intercepta import data as D
    f = tmp_path / "x.txt"; f.write_text("hello")
    monkeypatch.setattr(D, "_manifest", lambda: {"x.txt": "0" * 64})
    with pytest.raises(RuntimeError):
        D.verify("x.txt", str(f))
    # matching hash passes
    monkeypatch.setattr(D, "_manifest", lambda: {"x.txt": D.sha256(str(f))})
    D.verify("x.txt", str(f))


# ---- functional-inference layer (V15-V18): expression -> inferred dependency ----
def test_engine_functional_inference_recovers_relationship():
    genes = [f"G{i}" for i in range(10)]
    eng = E.InterceptaEngine(); eng.genes_ = genes
    rng = np.random.default_rng(3)
    cells = [f"c{i}" for i in range(150)]
    expr = pd.DataFrame(rng.normal(size=(10, 150)), index=genes, columns=cells)     # genes x cells
    tgt = -2.0 * expr.loc["G0"].values + 0.1 * rng.normal(size=150)                  # dependency = -2*G0
    crispr = pd.DataFrame({"TGT": tgt}, index=cells)                                 # cells x gene
    eng.fit_dependency(["TGT"], crispr_df=crispr, expr_df=expr)
    assert "TGT" in eng.dep_models_
    q = pd.DataFrame(rng.normal(size=(10, 40)), index=genes, columns=[f"q{i}" for i in range(40)])
    inf = eng.infer_dependency(q)
    assert inf.shape == (40, 1) and "TGT" in inf.columns
    # inferred TGT effect tracks -G0 -> negatively correlated with query G0
    assert stats.spearmanr(inf["TGT"].values, q.loc["G0"].values)[0] < -0.3

def test_rescued_targets_declared():
    assert {"FLT3", "BCL2", "CDK9", "AURKA"} == E.InterceptaEngine.RESCUED_TARGETS


def test_synergy_ranker_mechanics_and_ranking():
    from intercepta.synergy import SynergyRanker
    rng = np.random.default_rng(0)
    genes = [f"G{i}" for i in range(40)]; cells = [f"ACH-{i:04d}" for i in range(12)]
    expr = pd.DataFrame(rng.normal(size=(12, 40)), index=cells, columns=genes)         # cells x genes
    drugs = ["D0", "D1", "D2", "D3"]
    smi = {"D0": "CCO", "D1": "CCN", "D2": "c1ccccc1", "D3": "CC(=O)O"}                 # valid SMILES
    rows = [(drugs[a], drugs[b], c, expr.loc[c, "G0"] * (a + 1) + rng.normal(0, 0.2))
            for a in range(4) for b in range(a + 1, 4) for c in cells]
    syn = pd.DataFrame(rows, columns=["Drug1_ID", "Drug2_ID", "Cell", "Y"])
    r = SynergyRanker(n_pca=4).fit(syn, expr, smi, compute_cv=False)
    assert set(r.library_) == set(drugs)
    q = pd.DataFrame(rng.normal(size=(40, 3)), index=genes, columns=["Q1", "Q2", "Q3"])  # genes x samples
    out = r.rank_pairs(q, top=2)
    assert list(out.columns) == ["sample", "drug1", "drug2", "predicted_synergy", "ood_distance", "confidence"]
    assert out["sample"].nunique() == 3 and (out.groupby("sample").size() <= 2).all()   # top-2 per sample
    # scores are sorted descending within each sample; only KNOWN-library drugs are scored
    assert set(out["drug1"]) | set(out["drug2"]) <= set(drugs)
    assert r.ood_score(q).shape == (3,)
