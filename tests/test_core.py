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
    r = SynergyRanker(n_pca=4).fit(syn, expr, smi, compute_cv=True)   # compute_cv -> also sets conformal interval
    assert set(r.library_) == set(drugs)
    assert r.conformal_q_ is not None and r.conformal_q_ > 0          # calibrated prediction-interval half-width
    q = pd.DataFrame(rng.normal(size=(40, 3)), index=genes, columns=["Q1", "Q2", "Q3"])  # genes x samples
    out = r.rank_pairs(q, top=2)
    assert {"sample", "drug1", "drug2", "predicted_synergy", "ood_distance", "confidence", "pi_low", "pi_high"} <= set(out.columns)
    assert (out["pi_low"] <= out["predicted_synergy"]).all() and (out["predicted_synergy"] <= out["pi_high"]).all()
    assert out["sample"].nunique() == 3 and (out.groupby("sample").size() <= 2).all()   # top-2 per sample
    assert set(out["drug1"]) | set(out["drug2"]) <= set(drugs)
    assert r.ood_score(q).shape == (3,)


# ---- ADMET module (B30): data-free (synthetic SMILES) ----
def test_admet_featurize_shape_and_invalid():
    from intercepta.admet import featurize, NBITS, _DESCRIPTORS
    X, valid = featurize(["CCO", "c1ccccc1", "not_a_smiles"])
    assert X.shape == (3, NBITS + len(_DESCRIPTORS))
    assert valid.tolist() == [True, True, False]
    assert (X[2, :NBITS] == 0).all()                  # unparseable -> zero fingerprint
    assert np.isnan(X[2, NBITS:]).all()               # and NaN descriptors (imputed at fit time)

def test_admet_classification_learns_and_flags_domain():
    from intercepta.admet import ADMETPredictor
    # a learnable synthetic rule: aromatic (benzene-like) -> class 1, aliphatic alcohols -> class 0
    pos = ["c1ccccc1", "c1ccc(C)cc1", "c1ccc(O)cc1", "c1ccc(N)cc1", "c1ccncc1", "c1ccc2ccccc2c1"] * 4
    neg = ["CCO", "CCCO", "CCCCO", "CC(C)O", "CCCCCO", "OCCCCCC"] * 4
    smi = pos + neg; y = [1] * len(pos) + [0] * len(neg)
    p = ADMETPredictor().fit_task("bbb_martins", smi, y)      # bbb_martins is a roc-auc classification task
    out = p.predict(["c1ccccc1", "CCO", "not_a_smiles"])
    assert set(["smiles", "task", "metric", "prediction", "in_domain", "confidence"]).issubset(out.columns)
    byc = out.set_index("smiles")
    assert byc.loc["c1ccccc1", "prediction"] > byc.loc["CCO", "prediction"]   # aromatic scored higher (class 1)
    assert 0.0 <= byc.loc["c1ccccc1", "prediction"] <= 1.0                    # probability
    assert bool(byc.loc["not_a_smiles", "in_domain"]) is False               # unparseable -> out of domain
    assert np.isnan(byc.loc["not_a_smiles", "prediction"])

def test_admet_regression_and_ood_flag():
    from intercepta.admet import ADMETPredictor
    rng = np.random.default_rng(0)
    # regression task (mae); train only on small aliphatic alcohols
    train = ["CCO", "CCCO", "CCCCO", "CCCCCO", "OCCCCCC", "CC(C)O", "CCC(C)O", "OCC(C)C"] * 3
    y = [len(s) * 1.0 for s in train]                                        # target ~ length (deterministic-ish)
    p = ADMETPredictor().fit_task("lipophilicity_astrazeneca", train, y)     # mae regression task
    out = p.predict(["CCO", "c1ccc2ccccc2c1CCCCN"])                          # 2nd is far-off chemistry
    byc = out.set_index("smiles")
    assert out["prediction_type"].iloc[0] == "value"                        # regression -> raw value
    # the chemically dissimilar naphthalene-amine should be flagged out-of-applicability-domain
    assert bool(byc.loc["c1ccc2ccccc2c1CCCCN", "in_domain"]) is False
    assert bool(byc.loc["CCO", "in_domain"]) is True

def test_admet_unknown_task_raises():
    from intercepta.admet import ADMETPredictor
    with pytest.raises(ValueError):
        ADMETPredictor().fit_task("not_a_task", ["CCO"], [1.0])


# ---- ADMET conformal uncertainty (B30b), data-free ----
def _synth_alcohols(n):
    import numpy as np
    base = ["CCO", "CCCO", "CCCCO", "CCCCCO", "OCCCCCC", "CC(C)O", "CCC(C)O", "OCC(C)C", "CCCCCCCO", "OCCCCCCCC"]
    return [base[i % len(base)] for i in range(n)]

def test_admet_conformal_regression_intervals():
    from intercepta.admet import ADMETPredictor
    smi = _synth_alcohols(120); y = [float(len(s)) for s in smi]          # >=60 -> conformal split activates
    p = ADMETPredictor(conformal=True).fit_task("lipophilicity_astrazeneca", smi, y)
    out = p.predict(["CCO", "CCCCO"]).set_index("smiles")
    assert {"pi_low", "pi_high"}.issubset(out.columns)                    # regression -> intervals
    assert (out["pi_low"] <= out["prediction"]).all() and (out["prediction"] <= out["pi_high"]).all()
    assert "conformal_set" not in out.columns                             # not a classification output

def test_admet_conformal_classification_set():
    from intercepta.admet import ADMETPredictor
    pos = ["c1ccccc1", "c1ccc(C)cc1", "c1ccc(O)cc1", "c1ccncc1", "c1ccc2ccccc2c1", "c1ccc(N)cc1"]
    neg = ["CCO", "CCCO", "CCCCO", "CC(C)O", "OCCCCCC", "CCC(C)O"]
    smi = (pos + neg) * 10; y = ([1] * len(pos) + [0] * len(neg)) * 10     # 120 samples
    p = ADMETPredictor(conformal=True).fit_task("bbb_martins", smi, y)
    out = p.predict(["c1ccccc1", "CCO"]).set_index("smiles")
    assert {"conformal_set", "set_size"}.issubset(out.columns)            # classification -> prediction sets
    assert out["set_size"].between(0, 2).all()
    assert out.loc["c1ccccc1", "conformal_set"].startswith("{") and out.loc["c1ccccc1", "conformal_set"].endswith("}")
    assert "pi_low" not in out.columns

def test_admet_conformal_default_off_backcompat():
    from intercepta.admet import ADMETPredictor
    smi = _synth_alcohols(120); y = [float(len(s)) for s in smi]
    out = ADMETPredictor().fit_task("lipophilicity_astrazeneca", smi, y).predict(["CCO"])   # conformal default off
    assert not {"pi_low", "pi_high", "conformal_set", "set_size"} & set(out.columns)        # unchanged schema


# ---- synthesizability module (B31), data-free ----
def test_sa_score_orders_simple_vs_complex():
    from intercepta.synth import sa_score
    assert sa_score("c1ccccc1") < sa_score("C1CC2CCC3C(CCC4CC(O)CCC34C)C2C1")   # benzene easier than a steroid-like
    assert np.isnan(sa_score("not_a_smiles"))
    v = sa_score(["CCO", "c1ccccc1"]); assert len(v) == 2 and np.isfinite(v).all()

def test_synth_scorer_learns_and_flags_domain():
    from intercepta.synth import SynthesizabilityScorer
    # learnable synthetic rule: aromatics -> solvable(1), aliphatic alcohols -> unsolvable(0)
    pos = ["c1ccccc1", "c1ccc(C)cc1", "c1ccc(O)cc1", "c1ccncc1", "c1ccc2ccccc2c1", "c1ccc(N)cc1"]
    neg = ["CCO", "CCCO", "CCCCO", "CC(C)O", "OCCCCCC", "CCC(C)O"]
    smi = (pos + neg) * 10; solvable = ([1] * len(pos) + [0] * len(neg)) * 10     # 120 samples -> conformal on
    p = SynthesizabilityScorer(conformal=True).fit(smi, solvable)
    out = p.predict(["c1ccccc1", "CCO", "not_a_smiles"]).set_index("smiles")
    assert {"solvable_prob", "sa_score", "ad_distance", "in_domain", "conformal_set", "set_size"}.issubset(out.columns)
    assert out.loc["c1ccccc1", "solvable_prob"] > out.loc["CCO", "solvable_prob"]   # aromatic scored more solvable
    assert 0.0 <= out.loc["c1ccccc1", "solvable_prob"] <= 1.0
    assert bool(out.loc["not_a_smiles", "in_domain"]) is False
    assert np.isnan(out.loc["not_a_smiles", "solvable_prob"])

def test_synth_scorer_requires_fit():
    from intercepta.synth import SynthesizabilityScorer
    with pytest.raises(RuntimeError):
        SynthesizabilityScorer().predict(["CCO"])


# ---- integration MVP (B32): composition logic, data-free (mocked modules) ----
def test_developability_prioritizer_composition():
    from intercepta.integrate import DevelopabilityPrioritizer, PANEL
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    nfeat = len(PANEL) + 2
    rng = np.random.default_rng(0)

    class _MockADMET:
        def predict(self, smiles, tasks=None, tidy=True):
            n = len(smiles)
            if tasks == ["herg"]:                                  # AD proxy call
                return pd.DataFrame({"smiles": smiles, "in_domain": [True] * n})
            return pd.DataFrame(rng.random((n, len(PANEL))), columns=PANEL, index=smiles)   # tidy=False wide
    class _MockSynth:
        def predict(self, smiles):
            return pd.DataFrame({"solvable_prob": rng.random(len(smiles))})

    # real scaler+logistic fit on tiny synthetic training features
    Xtr = rng.random((40, nfeat)); ytr = (Xtr[:, 0] > 0.5).astype(int)
    scaler = StandardScaler().fit(Xtr); lr = LogisticRegression(max_iter=500).fit(scaler.transform(Xtr), ytr)
    p = DevelopabilityPrioritizer(_MockADMET(), _MockSynth(), scaler, lr,
                                  PANEL + ["synth_solvable_prob", "sa_score"], np.zeros(nfeat))
    out = p.predict(["CCO", "c1ccccc1", "CC(=O)O"])
    assert {"developability_risk", "synth_solvable_prob", "sa_score", "applicability_domain"}.issubset(out.columns)
    assert set(PANEL).issubset(out.columns)
    assert out["developability_risk"].between(0, 1).all()
    assert (out["developability_risk"].values == np.sort(out["developability_risk"].values)[::-1]).all()  # ranked desc


# ---- goal-directed generation (B33), data-free (RDKit BRICS only) ----
def test_generate_objectives_bounded_and_directional():
    from intercepta.generate import qed_score, synth_score, developability, OBJECTIVES
    from rdkit import Chem
    m = Chem.MolFromSmiles("CC(=O)Oc1ccccc1C(=O)O")
    assert 0.0 <= qed_score(m) <= 1.0 and 0.0 <= synth_score(m) <= 1.0 and 0.0 <= developability(m) <= 1.0
    # a trivial molecule is more synthesizable than a stereocenter-dense natural product (morphine)
    assert synth_score(Chem.MolFromSmiles("CCO")) > synth_score(
        Chem.MolFromSmiles("CN1CC[C@]23c4c5ccc(O)c4O[C@H]2[C@@H](O)C=C[C@H]3[C@H]1C5"))
    assert set(OBJECTIVES) == {"multi", "qed"}

def test_generate_optimizer_improves_and_valid():
    from intercepta.generate import MoleculeOptimizer, developability
    from rdkit import Chem
    seeds = ["CCOC(=O)c1ccccc1", "O=C(O)c1ccccc1N", "COc1ccc(CCN)cc1", "CC(=O)Nc1ccc(O)cc1",
             "c1ccc(-c2ccccc2)cc1", "CCN(CC)CCOC(=O)c1ccccc1", "O=S(=O)(N)c1ccccc1", "Cc1ccc(S(N)(=O)=O)cc1"]
    opt = MoleculeOptimizer(objective="multi", pop_size=20, generations=3, seed=42)
    res = opt.optimize(seeds)
    assert res["final_population"] and all(Chem.MolFromSmiles(s) is not None for s in res["final_population"])  # valid
    seed_best = max(developability(Chem.MolFromSmiles(s)) for s in seeds)
    assert res["final_best"] >= seed_best - 1e-9          # elitism: never worse than the best seed
    assert len(res["history"]) >= 1 and 0.0 <= res["best_score"] <= 1.0

def test_generate_optimizer_deterministic():
    from intercepta.generate import MoleculeOptimizer
    seeds = ["CCOC(=O)c1ccccc1", "O=C(O)c1ccccc1N", "COc1ccc(CCN)cc1", "CC(=O)Nc1ccc(O)cc1", "c1ccc(-c2ccccc2)cc1"]
    a = MoleculeOptimizer(pop_size=15, generations=2, seed=7).optimize(seeds)
    b = MoleculeOptimizer(pop_size=15, generations=2, seed=7).optimize(seeds)
    assert a["best_smiles"] == b["best_smiles"] and a["final_best"] == b["final_best"]   # seeded determinism

def test_generate_bad_objective_raises():
    from intercepta.generate import MoleculeOptimizer
    with pytest.raises(ValueError):
        MoleculeOptimizer(objective="not_an_objective")

def test_generate_accepts_callable_objective():
    from intercepta.generate import MoleculeOptimizer, qed_score
    from rdkit import Chem
    opt = MoleculeOptimizer(objective=lambda m: qed_score(m), pop_size=12, generations=2, seed=1)
    res = opt.optimize(["CCOC(=O)c1ccccc1", "O=C(O)c1ccccc1N", "COc1ccc(CCN)cc1", "CC(=O)Nc1ccc(O)cc1", "c1ccc(-c2ccccc2)cc1"])
    assert res["objective"] == "custom" and 0.0 <= res["best_score"] <= 1.0
    assert all(Chem.MolFromSmiles(s) is not None for s in res["final_population"])


# ---- end-to-end discovery pipeline (B39), data-free (small synthetic fits) ----
def test_discovery_pipeline_end_to_end():
    from intercepta.admet import ADMETPredictor
    from intercepta.synth import SynthesizabilityScorer
    from intercepta.discover import DiscoveryPipeline
    from rdkit import Chem
    pos = ["c1ccccc1", "c1ccc(C)cc1", "c1ccc(O)cc1", "c1ccncc1", "c1ccc2ccccc2c1", "c1ccc(N)cc1"]
    neg = ["CCO", "CCCO", "CCCCO", "CC(C)O", "OCCCCCC", "CCC(C)O"]
    smi = (pos + neg) * 10; ylab = ([1] * len(pos) + [0] * len(neg)) * 10
    admet = ADMETPredictor()
    for t in DiscoveryPipeline.TOX:                     # fit herg/ames/dili on synthetic (all roc-auc classification)
        admet.fit_task(t, smi, ylab)
    synth = SynthesizabilityScorer(conformal=False).fit(smi, ylab)
    pipe = DiscoveryPipeline(admet, synth, seed=1)
    out, hist = pipe.discover(seed_smiles=pos + neg, pop_size=12, generations=2, top=5)
    cols = {"smiles", "developability_F", "qed", "sa_score", "p_herg", "p_ames", "p_dili", "predicted_safety", "applicability_domain"}
    assert cols.issubset(out.columns) and len(out) <= 5
    assert out["developability_F"].between(0, 1).all()
    assert (out["developability_F"].values == np.sort(out["developability_F"].values)[::-1]).all()   # ranked desc
    assert all(Chem.MolFromSmiles(s) is not None for s in out["smiles"])                             # valid candidates
    assert len(hist) >= 1
