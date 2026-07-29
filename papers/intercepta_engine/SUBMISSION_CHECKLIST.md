# Submission checklist — INTERCEPTA engine manuscript

## Done (in-repo, reproducible)
- [x] Full manuscript draft (`MANUSCRIPT.md`): title, author/affiliation block, highlights, abstract (~250 w),
      author summary, results (§2.1–2.8), discussion, methods, figures, data/code availability, contributions,
      reproducibility statement, numbered references.
- [x] Three figures generated from committed metrics only (`figures/make_figures.py` → Fig1/2/3, PDF+PNG @300 dpi).
- [x] Every quantitative claim traces to a reproduced-×2 metrics JSON; all analyses pre-registered (`prereg/`).
- [x] Cover letter (`COVER_LETTER.md`) framing the rigorous-negative contribution + candidate journals.
- [x] Data manifest with sha256/MD5 + access class (`data/MANIFEST.md`); controlled data (BeatAML) not redistributed.

## Human-gated before submission (require author decisions / external lookups — not fabricated here)
- [ ] **Finalize author list, order, affiliations, ORCIDs, and contribution statement.** (Draft lists P.A. only,
      with an explicit AI-assistance disclosure — confirm each target journal's policy on AI-assisted analysis.)
- [ ] **Add DOIs/PMIDs** to all references and verify page numbers against primary sources (draft gives
      author/title/journal/year/volume; DOIs intentionally not invented).
- [ ] **Choose target journal** and reformat to its style (abstract structure, reference style, figure specs,
      word/section limits). Primary candidate: PLOS Computational Biology (welcomes rigorous negatives + methods).
- [ ] Suggested / opposed reviewers.
- [ ] Data-use / ethics statement wording for controlled BeatAML (dbGaP phs001657) per journal template; confirm
      the dbGaP DUA permits the described secondary use and the release scope.
- [ ] Confirm FIMM/Malani (Zenodo 7370747, CC-BY 4.0) attribution wording per CC-BY terms.
- [ ] Preprint decision (bioRxiv/medRxiv) and licensing.
- [ ] Optional: expand Methods into a standalone supplement; add a supplementary table of all 177 B5 markers and
      all per-drug transfer ρ.

## Notes
- No claim in the manuscript exceeds what a committed metrics file supports; two central results are negatives
  (B10 clinical, B20/B21 functional external replication) reported as first-class.
- If a reviewer requests a second external clinical/functional cohort, that is the Track-1 prospective design
  (`docs/TRACK1_PROTOCOL.md`), which is beyond the scope of the present (retrospective/public-data) paper.
