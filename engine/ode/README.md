# engine/ode — phenotype & PK/PD ODE models
Two-population / 80-compartment phenotype ODEs for tumor dynamics and drug response (mCRPC, AML, GBM).
## HONEST STATUS (see ../../docs/audits/INTERCEPTA_Validation_Limitations_v1.md, ../../LEDGER.md)
- Use as a **directional combination/therapy-RANKING** tool driven by mechanistic plausibility — **NOT** a
  quantitative clinical-outcome predictor. It does NOT predict trial HRs.
- Trial validation: **2/6** Framework-A trials pass; **0/3** growth-rate comparisons pass their acceptance
  window (CHAARTED direction inverted).
- **RETRACTED:** the earlier "5/5 trials validated" / "HR=0.687" claims used an invalid median-ratio
  estimator. Corrected to 3/5 (Cox PH), then to 2/6. Do not cite the old numbers.
Key files: intercepta_phenotype_ode_v1.py (primary), intercepta_unified_ode*.py, aml_ode*.py, hr_estimator_fixed.py.
