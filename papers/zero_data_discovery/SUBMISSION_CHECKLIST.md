# Submission checklist — zero_data_discovery preprint (bioRxiv)

Tick before posting. Items marked **[AUTHOR]** need a human decision; the rest are prepared.

## Content ready
- [x] Manuscript assembled (Part I bacterial arc + Part II composite/generalization) — `REPORT.md`
- [x] Abstract (full, in-body) + short portal abstract (~317 w) — `ABSTRACT_SHORT.md`
- [x] Figures 1–7 generated from committed metrics (PNG + 300-dpi PDF) — `figures/`, `gen_figures.py`
- [x] Manuscript PDF rendered (19 pp, 7 embedded figures) — `MANUSCRIPT.pdf` (local build artifact; rebuild command in bundle)
- [x] Every quantitative claim traces to a reproduced-×2, pre-registered experiment (`LEDGER.md`)
- [x] Limitations section (12 items incl. Part II bounds) + `FAILURE_AUDIT.md` cross-referenced
- [x] References (35, incl. all Part II data/method sources)
- [x] Data/code availability statement (repo + `data/MANIFEST.md` checksums; data never redistributed)

## [AUTHOR] decisions required by the portal
- [ ] **Author list + order + ORCIDs** (draft: Prasad Akula, corresponding)
- [ ] **Repo URL** to insert in the Data/Code availability statement + bundle
- [ ] **License** (recommend CC-BY 4.0; hard to change post-posting)
- [ ] **AI-assistance disclosure** — answer bioRxiv's AI question **yes**; keep the one-line disclosure (wording in bundle)
- [ ] **Competing interests / Funding** — confirm defaults (None / None) or amend
- [ ] **Category** — confirm Bioinformatics (primary) + secondary
- [ ] (optional) DOIs/PMIDs in references — can defer to v2

## Pre-flight integrity check (do once more before posting — posting is public + permanent)
- [ ] Title/abstract claim only what the LEDGER supports (target-PRIORITIZATION, not drugs/clinical)
- [ ] No figure or number is hand-typed — all from `gen_figures.py` / committed JSON (verified: Fig 7B corrected to the
      decisive conservation-conditioned OR 0.90, not the inflated 1.96)
- [ ] Negatives and the self-correction are stated plainly, not buried
- [ ] PDF opens, TOC links work, all 7 figures render with correct symbols (Greek/math present)

## What I (the AI agent) cannot do
Actual posting is a manual, authenticated web action (your bioRxiv account + ORCID + license + author confirmations). I have
prepared every file and all metadata; the ~5–10-minute submission is yours to perform when ready.
