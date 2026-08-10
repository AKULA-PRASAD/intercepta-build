# R3 — ingestion → R2 auto-re-test: SUMMARY (corrected, artifact-controlled)

Feeds R2 powered public datasets (LIT-PCBA, property-matched) with scaffold-leave-out splits so the NOVEL
test holds MANY genuinely-novel actives (23–327 per target vs thrombin's 5). Reproducible; per-target
metrics + `frontier_log.json`.

## The honest arc (falsify-first, applied to our own instrument)
1. **RAW run:** the `>0.60 CI-lower` alarm fired **4/7** (FEN1 novel 0.908, GBA 0.821, PKM2 0.789, ALDH1 0.694)
   — looked like the extrapolation wall breaking.
2. **CONTROL:** a PROPERTY-ONLY model (8 bulk descriptors, no ECFP) alone reached novel AUROC up to **0.816**
   (FEN1) — i.e., most of the "novel" signal is generic property/decoy bias, the LIT-PCBA artifact the repo's
   own `B54` documents.
3. **CORRECTED gate (now enforced in R2):** WALL_BREAKING requires ECFP NOVEL CI-lower > 0.60 **AND**
   (ECFP NOVEL AUROC − property_baseline NOVEL AUROC) > 0.10. Result: **5/7 WALL_HOLDS**; only **PKM2 (+0.13)**
   and **ALDH1 (+0.10)** retain a small residual beyond property bias.

## Verdict: the extrapolation wall LARGELY HOLDS on powered evidence.
The 2/7 residual is small and still confounded (ECFP encodes property information) → a **follow-up trigger,
not a claim**. The value of the episode: the instrument threw a false positive, the property control caught
it as a known artifact, and the pre-registered gate was corrected. `property_artifact_control.json` records
the control; `PREREG.md` records the correction.
