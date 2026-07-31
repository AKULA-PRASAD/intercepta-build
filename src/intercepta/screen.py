"""intercepta.screen — the consolidated virtual-screening + prioritization ENGINE.

Composes the validated pieces of the program into one usable tool:
  * a ligand-based activity QSAR (Morgan+physchem -> HGB) with a Tanimoto **applicability-domain** gate and
    AD-adaptive **conformal** uncertainty (the `_TaskModel` machinery validated in B30b / B42 / B46);
  * the **active-learning loop** validated in B51 (model-guided batch selection recovers real actives far faster
    than random) — greedy / uncertainty / UCB acquisition.

HONEST SCOPE. This is a retrospective, in-silico prioritization engine. `score()` ranks candidate molecules with a
*calibrated confidence* (applicability domain + conformal), and `active_learning_select()` chooses the most informative
batch to "test" next. Enrichment is validated on scaffold/novel-chemistry splits and the unbiased LIT-PCBA benchmark
(median AUROC ~0.78, B46) but drops on genuinely novel chemistry (B45) and is NOT prospectively confirmed. Outputs are
computational HYPOTHESES, not validated actives/drugs; a high score is not proven activity, and out-of-domain rows are
low-confidence. Not a clinical or safety determination; not wet-lab.
"""
import numpy as np
import pandas as pd

from intercepta.admet import featurize, _TaskModel


def _acquire(strategy, p, k, rng, kappa=1.0):
    """Indices of the top-k pool items to test next, given predicted P(active) `p`. Deterministic tie-break by index."""
    if strategy == "random":
        return rng.permutation(len(p))[:k]
    if strategy == "greedy":
        score = p
    elif strategy == "uncertainty":
        score = p * (1.0 - p)
    elif strategy == "ucb":
        score = p + kappa * np.sqrt(p * (1.0 - p))
    else:
        raise ValueError(f"unknown strategy {strategy!r}; use random|greedy|uncertainty|ucb")
    return np.lexsort((np.arange(len(score)), -score))[:k]


class VirtualScreener:
    """Fit a ligand-based activity model from known actives/inactives, then score candidates with calibrated
    confidence, or run the B51 active-learning loop.

    Usage:
        vs = VirtualScreener().fit(actives_smiles, inactives_smiles)
        ranked = vs.score(candidate_smiles)                       # DataFrame ranked by p_active + AD/conformal
        out = vs.active_learning_select(pool, oracle, rounds=10)  # model-guided batch selection (B51)
    """

    def __init__(self, name="target", seed=42, conformal=True):
        self.name, self.seed, self.conformal = name, seed, conformal
        self.model_ = None
        self.n_actives_ = self.n_inactives_ = None

    def fit(self, actives_smiles, inactives_smiles):
        actives_smiles = [s for s in actives_smiles if s]
        inactives_smiles = [s for s in inactives_smiles if s]
        smiles = list(actives_smiles) + list(inactives_smiles)
        y = np.array([1] * len(actives_smiles) + [0] * len(inactives_smiles), dtype=int)
        X, valid = featurize(smiles)
        X, y = X[valid], y[valid]
        if len(np.unique(y)) < 2:
            raise ValueError("need both actives and inactives (with parseable SMILES) to fit")
        self.model_ = _TaskModel(self.name, "roc-auc", seed=self.seed, conformal=self.conformal).fit(X, y)
        self.n_actives_, self.n_inactives_ = int((y == 1).sum()), int((y == 0).sum())
        return self

    def _predict(self, smiles):
        X, valid = featurize(list(smiles))
        if self.model_.conformal and self.model_.q_ is not None:
            val, ad, indom, _, _, sets, sz = self.model_.predict_conformal(X)
        else:
            val, ad, indom = self.model_.predict(X); sets = sz = None
        val = np.where(valid, val, np.nan)
        indom = indom & valid
        return val, ad, indom, sets, sz, valid

    def score(self, candidate_smiles, top=None):
        """Rank candidates by predicted P(active) with an applicability-domain flag and (if conformal) a prediction
        set. Returns a tidy DataFrame; out-of-domain rows are flagged low-confidence."""
        if self.model_ is None:
            raise RuntimeError("call fit() first")
        smiles = list(candidate_smiles)
        val, ad, indom, sets, sz, valid = self._predict(smiles)
        rows = []
        for i, s in enumerate(smiles):
            row = {"smiles": s, "p_active": (float(val[i]) if valid[i] else np.nan),
                   "ad_distance": float(ad[i]), "in_domain": bool(indom[i]),
                   "confidence": "in-domain" if indom[i] else "low (out-of-applicability-domain)"}
            if sets is not None:
                row["conformal_set"] = (sets[i] if valid[i] else None)
                row["set_size"] = (int(sz[i]) if valid[i] else np.nan)
            rows.append(row)
        out = pd.DataFrame(rows).sort_values(["p_active"], ascending=False, na_position="last").reset_index(drop=True)
        out.insert(0, "rank", np.arange(1, len(out) + 1))
        return out.head(top) if top else out

    def active_learning_select(self, pool_smiles, oracle, rounds=10, batch=50, strategy="ucb", seed=1,
                               seed_batch=None):
        """Run the B51 model-guided active-learning loop over an unlabelled `pool_smiles`. `oracle(smiles)->0/1`
        reveals a label only when a molecule is selected ("tested"). Returns a dict with the tested molecules per
        round, the cumulative actives-found curve, and the final fitted model. strategy: random|greedy|uncertainty|ucb.
        """
        pool = list(pool_smiles)
        X, valid = featurize(pool)
        keep = np.where(valid)[0]
        pool = [pool[i] for i in keep]; X = X[keep]
        n = len(pool); rng = np.random.default_rng(seed)
        seed_batch = seed_batch if seed_batch is not None else min(batch, n)
        labelled = set(rng.permutation(n)[:seed_batch].tolist())
        labels = {i: int(oracle(pool[i])) for i in labelled}
        found = [sum(labels.values())]; tested = [len(labelled)]; rounds_log = []
        for _ in range(rounds):
            unl = np.array([i for i in range(n) if i not in labelled])
            if len(unl) == 0:
                break
            yl = np.array([labels[i] for i in labelled])
            if len(np.unique(yl)) < 2:
                p = np.full(len(unl), 0.5)
            else:
                m = _TaskModel(self.name, "roc-auc", seed=self.seed).fit(X[list(labelled)], yl)
                p = m.predict(X[unl])[0]
            sel_local = _acquire(strategy, p, min(batch, len(unl)), rng)
            sel = unl[sel_local]
            picks = [pool[i] for i in sel]
            for i in sel:
                labels[i] = int(oracle(pool[i])); labelled.add(int(i))
            rounds_log.append({"tested_smiles": picks, "n_new_actives": int(sum(labels[i] for i in sel))})
            found.append(sum(labels.values())); tested.append(len(labelled))
        return {"strategy": strategy, "n_pool": n, "tested_curve": tested, "actives_found_curve": found,
                "total_tested": tested[-1], "total_actives_found": found[-1], "rounds": rounds_log}

    # ---- convenience constructor from a TDC HTS single-target set (open data) ----
    @classmethod
    def from_hts(cls, name, n_inactive=10000, path=None, seed=42, conformal=True):
        """Fit from a TDC HTS bioactivity target (needs PyTDC + network/cache). All actives + a seeded inactive sample."""
        import os
        from tdc.single_pred import HTS
        path = path or os.path.join(os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data"), "tdc_bio")
        d = HTS(name=name, path=path).get_data().dropna(subset=["Y", "Drug"])
        act = d[d["Y"] == 1]["Drug"].tolist()
        inact = d[d["Y"] == 0].sample(n=min(n_inactive, int((d["Y"] == 0).sum())), random_state=seed)["Drug"].tolist()
        return cls(name=name, seed=seed, conformal=conformal).fit(act, inact)
