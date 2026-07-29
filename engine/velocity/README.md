# engine/velocity — scVelo RNA-velocity pipeline
Computes spliced/unspliced velocity + latent_time on scRNA (≈46k cells).
## HONEST STATUS (see ../../verification/RNA_VELOCITY_FEASIBILITY.md)
The novel "time-machine / pre-resistant-cell detection" idea is **NOT TESTABLE on current data** — there is no
per-cell drug-response/resistance ground truth to validate velocity-derived predictions against. Architecturally
interesting, empirically untested. Do NOT claim it detects pre-resistance.
