"""ADMET / safety-prediction module (INTERCEPTA discovery-pipeline stage #4).

Predicts a molecule's Absorption, Distribution, Metabolism, Excretion and Toxicity properties from its structure
(SMILES) alone, using Morgan/ECFP fingerprints + RDKit physicochemical descriptors and gradient-boosted trees. One
model per property; each carries a Tanimoto-based APPLICABILITY-DOMAIN flag so predictions on chemistry unlike the
training set are marked low-confidence.

Validated in experiment B30 on the Therapeutics Data Commons (TDC) ADMET Benchmark Group (22 tasks, scaffold splits,
public leaderboard) — see prereg/B30_admet.md + LEDGER.

HONEST SCOPE (read before use):
- This is an in-silico SCREENING FILTER, NOT a safety guarantee and NOT a clinical/regulatory determination.
- Trained on public medicinal-chemistry datasets; generalization is to novel scaffolds only (scaffold split).
- Per-task performance ranges from strong to near-baseline; each prediction reports its task's benchmark metric and
  an applicability-domain flag. Treat every value as a research hypothesis, weighted by that flag.
"""
import numpy as np
import pandas as pd

NBITS = 2048
RADIUS = 2

# Fixed physicochemical descriptor panel (a priori; standard medicinal-chemistry set). Name -> RDKit Descriptors attr.
_DESCRIPTORS = [
    "MolWt", "MolLogP", "TPSA", "NumHDonors", "NumHAcceptors", "NumRotatableBonds",
    "NumAromaticRings", "FractionCSP3", "HeavyAtomCount", "RingCount", "NHOHCount",
    "NOCount", "NumAliphaticRings", "NumSaturatedRings", "LabuteASA", "BalabanJ", "BertzCT",
]

# Task -> official TDC metric (mirrors tdc.metadata.admet_metrics; kept here so the module is usable without TDC).
TASK_METRIC = {
    "caco2_wang": "mae", "hia_hou": "roc-auc", "pgp_broccatelli": "roc-auc", "bioavailability_ma": "roc-auc",
    "lipophilicity_astrazeneca": "mae", "solubility_aqsoldb": "mae", "bbb_martins": "roc-auc", "ppbr_az": "mae",
    "vdss_lombardo": "spearman", "cyp2c9_veith": "pr-auc", "cyp2d6_veith": "pr-auc", "cyp3a4_veith": "pr-auc",
    "cyp2c9_substrate_carbonmangels": "pr-auc", "cyp2d6_substrate_carbonmangels": "pr-auc",
    "cyp3a4_substrate_carbonmangels": "roc-auc", "half_life_obach": "spearman", "clearance_hepatocyte_az": "spearman",
    "clearance_microsome_az": "spearman", "ld50_zhu": "mae", "herg": "roc-auc", "ames": "roc-auc", "dili": "roc-auc",
}
CLASSIFICATION_METRICS = {"roc-auc", "pr-auc"}


def _mol(smiles):
    try:
        from rdkit import Chem
        return Chem.MolFromSmiles(str(smiles))
    except Exception:
        return None


def morgan_bits(smiles, nbits=NBITS, radius=RADIUS):
    """Morgan/ECFP bit vector as int8 array; all-zero if unparseable/rdkit unavailable."""
    m = _mol(smiles)
    if m is None:
        return np.zeros(nbits, np.int8)
    from rdkit.Chem import AllChem
    bs = AllChem.GetMorganFingerprintAsBitVect(m, radius, nBits=nbits).ToBitString()
    return np.frombuffer(bs.encode(), "u1").astype(np.int8) - ord("0")


def physchem(smiles):
    """Fixed physicochemical descriptor vector (NaN where undefined); all-NaN if unparseable/rdkit unavailable."""
    m = _mol(smiles)
    if m is None:
        return np.full(len(_DESCRIPTORS), np.nan)
    from rdkit.Chem import Descriptors
    out = np.empty(len(_DESCRIPTORS))
    for i, name in enumerate(_DESCRIPTORS):
        fn = getattr(Descriptors, name, None)
        try:
            out[i] = float(fn(m)) if fn is not None else np.nan
        except Exception:
            out[i] = np.nan
    return out


def featurize(smiles_iter, nbits=NBITS, radius=RADIUS):
    """SMILES iterable -> (X, valid_mask). X = [morgan bits | physchem descriptors] (descriptors NOT yet imputed)."""
    bits, desc, valid = [], [], []
    for s in smiles_iter:
        m = _mol(s)
        valid.append(m is not None)
        bits.append(morgan_bits(s, nbits, radius))
        desc.append(physchem(s))
    X = np.hstack([np.vstack(bits).astype(np.float32), np.vstack(desc).astype(np.float32)])
    return X, np.array(valid, bool)


def _conf_quantile(scores, alpha):
    """Inductive-conformal (1-alpha) quantile with finite-sample correction; inf if calibration set too small."""
    scores = np.asarray(scores, float)
    n = len(scores)
    if n == 0:
        return float("inf")
    k = int(np.ceil((n + 1) * (1 - alpha)))
    return float("inf") if k > n else float(np.sort(scores)[k - 1])


class _TaskModel:
    """One fitted ADMET property model: featurizer config + GBT + Tanimoto applicability-domain gate.

    Optional conformal uncertainty (validated in B30b, reproduced x2): when conformal=True, fit holds out a
    calibration split, and predict_conformal() emits AD-adaptive (Mondrian) prediction intervals (regression) or
    prediction sets (classification) — empirical coverage matches nominal on scaffold-split test (B30b Aim 2/3).
    """

    def __init__(self, task, metric, seed=42, nbits=NBITS, radius=RADIUS, conformal=False, conformal_alpha=0.1):
        self.task, self.metric, self.seed, self.nbits, self.radius = task, metric, seed, nbits, radius
        self.is_classification = metric in CLASSIFICATION_METRICS
        self.model_ = self.desc_median_ = self.n_desc_ = None
        self._train_bits = None            # packed training fingerprints for Tanimoto AD
        self.ad_threshold_ = None          # 95th pct of training NN Tanimoto distance
        self.n_train_ = None
        self.conformal, self.alpha = conformal, conformal_alpha
        self.q_ = None; self.qbin_ = None; self.ad_edges_ = None   # AD-adaptive (Mondrian) conformal quantiles

    def _split_impute(self, X, fit=False):
        nb = self.nbits
        bits, desc = X[:, :nb], X[:, nb:]
        if fit:
            self.desc_median_ = np.nanmedian(desc, axis=0)
            self.desc_median_ = np.where(np.isfinite(self.desc_median_), self.desc_median_, 0.0)
            self.n_desc_ = desc.shape[1]
        desc = np.where(np.isfinite(desc), desc, self.desc_median_)
        return np.hstack([bits, desc])

    def fit(self, X, y):
        from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
        y = np.asarray(y, float)
        # conformal: hold out a deterministic calibration split; fit model + AD on the proper-train portion only.
        if self.conformal and len(y) >= 60:
            idx = np.random.default_rng(self.seed).permutation(len(y))
            ncal = max(20, int(0.2 * len(y)))
            cal_idx, fit_idx = idx[:ncal], idx[ncal:]
        else:
            fit_idx = np.arange(len(y)); cal_idx = np.array([], int)
        Xi = self._split_impute(X[fit_idx], fit=True)
        yf = y[fit_idx]
        if self.is_classification:
            self.model_ = HistGradientBoostingClassifier(random_state=self.seed, max_iter=300,
                                                          learning_rate=0.06, max_depth=6).fit(Xi, yf.astype(int))
        else:
            self.model_ = HistGradientBoostingRegressor(random_state=self.seed, max_iter=300,
                                                        learning_rate=0.06, max_depth=6).fit(Xi, yf)
        # applicability domain: pack proper-train fingerprints, calibrate threshold on training NN Tanimoto distance
        self._train_bits = np.packbits(X[fit_idx, :self.nbits].astype(bool), axis=1)
        self.n_train_ = len(fit_idx)
        self.ad_threshold_ = float(np.percentile(self._train_nn_distance(), 95))
        if self.conformal and len(cal_idx) > 0:               # calibrate AD-adaptive (Mondrian) conformal quantiles
            Xc = self._split_impute(X[cal_idx], fit=False); yc = y[cal_idx]
            if self.is_classification:
                proba = self.model_.predict_proba(Xc); s = 1.0 - proba[np.arange(len(yc)), yc.astype(int)]
            else:
                s = np.abs(yc - self.model_.predict(Xc))
            self.q_ = _conf_quantile(s, self.alpha)
            adc = 1.0 - self._tanimoto_to_train(np.packbits(X[cal_idx, :self.nbits].astype(bool), axis=1))
            self.ad_edges_ = np.quantile(adc, [1 / 3, 2 / 3]); cbin = np.digitize(adc, self.ad_edges_)
            self.qbin_ = {b: (_conf_quantile(s[cbin == b], self.alpha) if int((cbin == b).sum()) >= 10 else self.q_)
                          for b in (0, 1, 2)}
        return self

    # ---- Tanimoto applicability domain ----
    def _tanimoto_to_train(self, packed_query):
        """Max Tanimoto similarity of each packed query fp to the training set. Returns (nq,)."""
        tb = np.unpackbits(self._train_bits, axis=1).astype(np.float32)      # ntrain x nbits
        qb = np.unpackbits(packed_query, axis=1).astype(np.float32)          # nq x nbits
        inter = qb @ tb.T                                                    # nq x ntrain
        a = qb.sum(1)[:, None]; b = tb.sum(1)[None, :]
        with np.errstate(divide="ignore", invalid="ignore"):
            tani = inter / (a + b - inter)
        tani = np.where(np.isfinite(tani), tani, 0.0)
        return tani.max(1)

    def _train_nn_distance(self):
        """Leave-one-out nearest-neighbor Tanimoto DISTANCE (1 - sim) within the training set."""
        tb = np.unpackbits(self._train_bits, axis=1).astype(np.float32)
        inter = tb @ tb.T
        s = tb.sum(1)
        with np.errstate(divide="ignore", invalid="ignore"):
            tani = inter / (s[:, None] + s[None, :] - inter)
        np.fill_diagonal(tani, -np.inf)                                      # exclude self
        tani = np.where(np.isfinite(tani), tani, 0.0)
        return 1.0 - tani.max(1)

    def predict(self, X):
        """Returns (value, ad_distance, in_domain). value = probability (classification) or property (regression)."""
        Xi = self._split_impute(X, fit=False)
        if self.is_classification:
            val = self.model_.predict_proba(Xi)[:, 1]
        else:
            val = self.model_.predict(Xi)
        packed_q = np.packbits(X[:, :self.nbits].astype(bool), axis=1)
        ad_dist = 1.0 - self._tanimoto_to_train(packed_q)
        in_domain = ad_dist <= self.ad_threshold_
        return val, ad_dist, in_domain

    def predict_conformal(self, X):
        """Like predict(), plus AD-adaptive (Mondrian) conformal outputs (needs conformal=True fit).
        Regression -> (val, ad, indom, pi_low, pi_high, None, None);
        classification -> (val, ad, indom, None, None, set_str, set_size)."""
        val, ad, indom = self.predict(X)
        if self.q_ is None:
            return val, ad, indom, None, None, None, None
        bins = np.digitize(ad, self.ad_edges_) if self.ad_edges_ is not None else np.zeros(len(ad), int)
        qv = np.array([self.qbin_.get(int(b), self.q_) for b in bins])
        Xi = self._split_impute(X, fit=False)
        if self.is_classification:
            proba = self.model_.predict_proba(Xi)                       # (n, 2)
            in_set = (1.0 - proba) <= qv[:, None]
            sets = ["{" + ",".join(str(k) for k in np.where(r)[0]) + "}" for r in in_set]
            return val, ad, indom, None, None, sets, in_set.sum(1)
        return val, ad, indom, val - qv, val + qv, None, None


class ADMETPredictor:
    """Predict ADMET/safety properties for molecules (SMILES). Fit per-task GBT models, then `predict` a batch of
    SMILES to get every property + an applicability-domain flag per property.

    Usage:
        p = ADMETPredictor().fit_task("bbb_martins", train_smiles, train_y)   # one property
        p = ADMETPredictor.from_tdc(tasks=[...])                              # all/some TDC tasks, on full train_val
        out = p.predict(["CCO", "c1ccccc1"])                                  # tidy DataFrame
    """

    def __init__(self, seed=42, nbits=NBITS, radius=RADIUS, conformal=False):
        self.seed, self.nbits, self.radius = seed, nbits, radius
        self.conformal = conformal        # emit AD-adaptive conformal intervals/sets (B30b-validated)
        self.models_ = {}                 # task -> _TaskModel
        self.task_metric_ = {}            # task -> metric

    def fit_task(self, task, smiles, y, metric=None, conformal=None):
        metric = metric or TASK_METRIC.get(task)
        if metric is None:
            raise ValueError(f"unknown task {task!r}; pass metric= explicitly")
        conf = self.conformal if conformal is None else conformal
        X, _ = featurize(smiles, self.nbits, self.radius)
        tm = _TaskModel(task, metric, self.seed, self.nbits, self.radius, conformal=conf).fit(X, y)
        self.models_[task] = tm
        self.task_metric_[task] = metric
        return self

    def predict(self, smiles, tasks=None, tidy=True):
        """Predict properties for a list of SMILES. Returns a tidy DataFrame [smiles, task, metric, prediction,
        prediction_type, ad_distance, in_domain, confidence] (tidy=True) or a wide value matrix (tidy=False).
        When a task model was fit with conformal=True, tidy rows also carry AD-adaptive conformal uncertainty:
        regression -> pi_low/pi_high; classification -> conformal_set/set_size (B30b-validated coverage)."""
        if not self.models_:
            raise RuntimeError("no fitted tasks; call fit_task() or from_tdc() first")
        smiles = list(smiles)
        tasks = list(tasks or self.models_.keys())
        X, valid = featurize(smiles, self.nbits, self.radius)
        rows, wide = [], {}
        for task in tasks:
            tm = self.models_[task]
            use_conf = tm.conformal and tm.q_ is not None
            if use_conf:
                val, ad, indom, lo, hi, sets, sz = tm.predict_conformal(X)
            else:
                val, ad, indom = tm.predict(X); lo = hi = sets = sz = None
            val = np.where(valid, val, np.nan)                 # unparseable SMILES -> NaN
            indom = indom & valid
            wide[task] = val
            ptype = "probability" if tm.is_classification else "value"
            for i, (s, v, d, dom) in enumerate(zip(smiles, val, ad, indom)):
                row = {"smiles": s, "task": task, "metric": tm.metric, "prediction": v,
                       "prediction_type": ptype, "ad_distance": float(d), "in_domain": bool(dom),
                       "confidence": "in-domain" if dom else "low (out-of-applicability-domain)"}
                if use_conf and not tm.is_classification:
                    row["pi_low"] = (float(lo[i]) if valid[i] else np.nan)
                    row["pi_high"] = (float(hi[i]) if valid[i] else np.nan)
                elif use_conf and tm.is_classification:
                    row["conformal_set"] = (sets[i] if valid[i] else None)
                    row["set_size"] = (int(sz[i]) if valid[i] else np.nan)
                rows.append(row)
        if tidy:
            return pd.DataFrame(rows)
        w = pd.DataFrame(wide, index=smiles); w.index.name = "smiles"
        return w

    # ---- convenience constructor from the TDC ADMET benchmark (open data) ----
    @classmethod
    def from_tdc(cls, tasks=None, path=None, seed=42, **kw):
        """Fit on the full official `train_val` of each TDC ADMET task (deployment models). Needs PyTDC + network
        (or a cached TDC dir at `path` / $INTERCEPTA_DATA/tdc_admet). Returns a fitted ADMETPredictor."""
        import os
        from tdc.benchmark_group import admet_group
        path = path or os.path.join(os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data"), "tdc_admet")
        g = admet_group(path=path)
        tasks = tasks or list(g.dataset_names)
        self = cls(seed=seed, **kw)
        for task in tasks:
            b = g.get(task)
            tv = b["train_val"]
            self.fit_task(task, tv["Drug"].tolist(), tv["Y"].values)
        return self
