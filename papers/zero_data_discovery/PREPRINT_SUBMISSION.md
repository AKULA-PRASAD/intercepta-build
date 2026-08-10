# bioRxiv submission bundle — "Zero-data drug discovery & a disease-class-aware composite"

**I cannot post this for you.** bioRxiv submission is a manual, authenticated web flow (your account + ORCID + author
confirmations + license choice + a public, hard-to-retract posting). Everything below is ready; posting is a ~5–10 minute
action you take. Prepared 2026-08-06 for the assembled Part I + Part II manuscript.

## Files to upload (all in `papers/zero_data_discovery/`)
- **Manuscript PDF:** `MANUSCRIPT.pdf` — 19 pages, TOC + 7 embedded figures, rendered from `REPORT.md` by pandoc/xelatex.
  This is the single file bioRxiv needs. **It is a regenerable build artifact (not committed to git, per the repo's
  no-regenerable-binaries policy); it is present on disk ready to upload, and rebuilds in one command (see *Rebuild* below).**
- **Figures (if uploaded separately / on request):** `figures/fig1…fig7_*.pdf` (300-dpi vector PDFs; PNGs alongside).
  Fig 1–4 = Part I (bacterial arc); Fig 5–7 = Part II (composite / generalization frontier).
- **Source (optional):** `REPORT.md` + `gen_figures.py` (figures regenerate deterministically from committed metrics).

## Metadata to paste
- **Title:** *Zero-data drug discovery, and a disease-class-aware composite: an honest map of which target-ID signal
  transfers to which biology — validated against experimental gene-knockouts across bacteria, a fungus, viruses, and human
  cancer, with first-class negatives and an abstaining router that knows its limits.*
  *(Optional shorter title for the portal's title field, if length-limited: "Zero-data drug discovery and a
  disease-class-aware composite: which target-ID signal transfers to which biology.")*
- **Abstract:** the **Abstract** section in `REPORT.md` is two paragraphs (Part I + Part II) totalling **~760 words** — too
  long for bioRxiv's typical ~250–350-word limit. **A trimmed abstract is required**; a ready ~300-word cut is provided in
  `ABSTRACT_SHORT.md` (use it verbatim, or trim the full Abstract yourself). Keep the full version as the manuscript's
  in-body Abstract.
- **Subject category (bioRxiv):** **Bioinformatics** (primary); secondary: **Microbiology** (or **Systems Biology**).
- **Corresponding author:** Prasad Akula — akula.pra@northeastern.edu — Northeastern University.
- **Competing interests:** *(author to confirm — default: None declared.)*
- **Funding:** *(author to confirm — default: None.)*
- **Data/code availability:** all source code, the append-only results ledger (`LEDGER.md`), per-experiment code + reproduced
  metrics (`experiments/*/`), the engine and composite router (`src/intercepta/`), and the figure generator are in the
  INTERCEPTA repository (public). Input datasets are open and referenced with checksums in `data/MANIFEST.md`; per project
  policy data files are never committed and are regenerable from the cited public sources. *(Insert the public repo URL.)*

## Decisions ONLY YOU can make first (required by the portal)
1. **Author list + order + ORCIDs.** Draft lists **Prasad Akula (corresponding)**. Confirm any co-authors. bioRxiv requires
   human authors.
2. **AI-assistance disclosure.** This manuscript and its experiments were produced with substantial AI assistance (Claude, as
   an autonomous research/engineering agent under a human-directed rigor protocol). bioRxiv asks whether AI tools were used —
   **answer yes** and keep a one-line disclosure in Author Contributions / Methods. *(Recommended wording: "Experiments,
   analysis, and manuscript drafting were performed by an AI agent (Claude) under the direction and verification of the
   corresponding author; all results are pre-registered, reproduced ×2, and committed to version control.")*
3. **License.** Recommend **CC-BY 4.0** (maximum reuse) — or CC-BY-NC-ND to restrict commercial/derivative use. Choose
   deliberately (hard to change after posting).
4. **DOIs/PMIDs in references** — optional at preprint stage; can be added in a v2 revision. Not a blocker.

## Steps (bioRxiv)
1. Sign in at biorxiv.org (institutional email + ORCID).
2. "Submit a manuscript" → new submission → paste Title + Abstract + choose category.
3. Add authors (names, affiliations, emails, ORCIDs); mark corresponding author.
4. Upload `MANUSCRIPT.pdf` (+ separate figure PDFs if prompted).
5. Choose license (#3); answer the AI-use question (**yes**, disclosed).
6. Paste the Data/Code availability statement (repo URL).
7. Submit → bioRxiv screens in ~24–48 h → assigns a DOI and posts publicly.

## Rebuild the PDF (deterministic; if you edit REPORT.md)
```
cd papers/zero_data_discovery
python ../../papers/zero_data_discovery/gen_figures.py        # regenerate figures from committed metrics
# transliterate Unicode -> ASCII-safe for pdflatex-class fonts, then render (xelatex handles the rest):
pandoc REPORT.md -o MANUSCRIPT.pdf --pdf-engine=xelatex --resource-path=.:figures \
  -V geometry:margin=1in -V fontsize=10pt -V colorlinks=true --toc --toc-depth=2 -V documentclass=article
```
*(The committed PDF was rendered from a Unicode→ASCII-transliterated copy so Greek/math symbols print correctly on the
default LaTeX fonts; the transliteration is rendering-only and does not alter `REPORT.md`.)*

## Honest note on what this preprint is (and is not)
This is a rigorous, **negatives-first** methods paper: a validated, analyst-blind (lock-before-reveal), reproducible **computational
target-PRIORITIZATION** system with a mapped generalization frontier and an abstaining router. It establishes priority,
method, and an honest evidence map. It is **not** a drug, not a validated novel target, and **not** a clinical result — the
molecule-potency, novel-target, and patient/clinical claims are explicitly gated on new experimental information (see
*Limitations* and `FAILURE_AUDIT.md`). Two central results are **negatives** (label-free dependency does not transfer to a
zero-screen organism; patient drug-response prediction fails external replication) and one is a **self-correction** — this is
the paper's integrity, not a weakness. Posting is public and effectively permanent; post when you are ready for it to be
citable and indexed.
