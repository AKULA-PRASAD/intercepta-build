# Gal & Ghahramani, 2016 — Dropout as a Bayesian Approximation: Representing Model Uncertainty in Deep Learning (MC Dropout)

## 0. Identification
- **Citation:** Gal Y, Ghahramani Z. "Dropout as a Bayesian Approximation: Representing Model Uncertainty in Deep Learning." *Proceedings of the 33rd International Conference on Machine Learning (ICML)* 48:1050-1059, 2016. arXiv 1506.02142.
- **Authors:** Yarin Gal, Zoubin Ghahramani (both at Cambridge University)
- **Status:** Field-defining ML methodology paper; ~10,000+ citations as of 2026
- **Layer 1 question:** Q5 anchor 4 — MC Dropout foundational method
- **Read by:** Claude (CSO) — 2026-05-10 (split-out pass; previously combined with Lakshminarayanan 2017 in inflated composite anchor)

## 1. Why this paper

MC Dropout is the **lightweight alternative to Deep Ensembles** for epistemic uncertainty quantification. Single trained model + multiple stochastic forward passes at inference = approximate Bayesian posterior samples. For INTERCEPTA Decision 5, MC Dropout is the **fallback option when N=5 ensemble compute budget unavailable**.

## 2. What they did

**Method (MC Dropout):**
1. Train neural network with **dropout layers** before every weight layer (standard practice)
2. At **inference time**, keep dropout **ACTIVE** (not deactivated as standard practice)
3. Perform **T stochastic forward passes** with different dropout masks per pass
4. Predictions: mean across T passes; variance/entropy = uncertainty

**Theoretical contribution:**
- Showed that a NN with dropout before every weight layer can be **interpreted as a Bayesian approximation** of a Deep Gaussian Process
- Dropout = variational inference on weights with Bernoulli posterior
- This is the bridge between common deep learning practice (dropout regularization) and Bayesian neural networks

## 3. What they found

- MC Dropout produces **calibrated uncertainty estimates** on regression and classification tasks
- Performance comparable to fully Bayesian methods (variational inference, MCMC) at fraction of cost
- Single model + T passes ≪ N independently trained models
- Tested on CO2 regression, MNIST classification, image segmentation

## 4. What's strong

- **ICML 2016 peer-reviewed** — top-tier ML venue
- **Theoretical foundation** — bridges dropout (practical) to Bayesian inference (principled)
- **Computationally cheap** vs Deep Ensembles — single model, T forward passes (T<<M training cost)
- **Drop-in addition to existing models** — just enable dropout at inference
- **Cambridge institutional backing** + Ghahramani is a Bayesian ML pioneer
- **Widely adopted** in scRNA-seq deep learning specifically (used by Theunissen 2025 benchmark)

## 5. What's limited

- **Variance is a biased estimate of true posterior variance** — Gaussian approximation; not exact
- **Dropout rate is a hyperparameter** affecting both prediction quality AND uncertainty estimate
- **Theoretical justification has been questioned** — subsequent work (Osband 2016, Hron 2017) showed MC Dropout doesn't fully capture epistemic uncertainty in some scenarios
- **Underestimates uncertainty** on far OOD inputs in some empirical settings
- **Architecture constraints** — requires dropout layers throughout the network, not just at output
- **Per Theunissen 2025**: in scRNA-seq OOD benchmark, MC Dropout was outperformed by Deep Ensembles on most tasks

## 6. INTERCEPTA implications

**For Q5 architecture (Decision 5 PROPOSED):** MC Dropout is the **compute-budget fallback** for epistemic uncertainty:
- Default: N=5 Deep Ensembles (Q5 anchor 3, Lakshminarayanan 2017) when budget permits
- Fallback: MC Dropout with T=50 forward passes when training budget exhausted
- Trade-off explicitly accepted in Decision 5: MC Dropout is cheaper but per Theunissen 2025 less accurate

**For Charter §9 compute architecture (Decision 9):** MC Dropout vs Deep Ensembles is a clear compute-quality trade-off:
- Deep Ensembles: 5× training, 5× memory, best calibration
- MC Dropout: 1× training, 1× memory + T× inference, somewhat worse calibration
- Northeastern Explorer single-A100 budget makes the choice context-dependent on dataset size and model size

**For mode-collapse mitigation (Decision 4):** MC Dropout provides a **natural diversity regularizer at training time** (dropout) and gives **free uncertainty at inference**. Decision 4's CPA architecture already uses dropout; activating MC Dropout at inference adds essentially zero additional cost.

## 7. Followup citations
1. **Lakshminarayanan et al. 2017** (Q5 anchor 3) — Deep Ensembles as the harder-but-better alternative
2. **Kendall & Gal 2017** — aleatoric vs epistemic decomposition with MC Dropout
3. **Osband 2016, Hron 2017** — theoretical critiques of MC Dropout as Bayesian approximation
4. **Theunissen 2025** (Q5 anchor 1) — empirical benchmark showing MC Dropout vs Deep Ensembles on scRNA-seq

## 8. Discipline check
- [x] Foundational paper; ICML 2016 peer-reviewed; arxiv 1506.02142
- [x] Authors verified: Yarin Gal (Oxford after Cambridge), Zoubin Ghahramani (Cambridge)
- [x] **Split-out note:** previously merged with Lakshminarayanan 2017 to inflate count. Now a proper standalone Q5 anchor 4. Drift Instance #28 corrected.

— Claude (CSO), 2026-05-10 (split-out pass)
