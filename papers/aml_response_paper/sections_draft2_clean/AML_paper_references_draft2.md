# AML Paper — References (Draft 2 — top 5 verified)

**Working title:** *Mechanism-class structure of multi-modal drug response prediction in acute myeloid leukemia: Where ML works, where it doesn't, and why*

**Target journal:** Briefings in Bioinformatics

**Status:** DRAFT 2 — Top 5 most-critical references verified via web search 2026-05-10. Remaining 18 entries still flagged **[VERIFY]** for future verification session. Per principle P15 (only correct, honest, real science).

**Predecessor:** `AML_paper_references_draft1.md` (preserved per P16)

**Authors:** Prasad Akula, Claude (CSO/AI co-founder)

**Date:** 2026-05-10

---

## Changelog (vs Draft 1)

**5 references verified via web search (PubMed + CrossRef + journal websites):**

1. **Bottomly et al., 2022** — DOI confirmed `10.1016/j.ccell.2022.07.002`
2. **Tyner et al., 2018** — DOI confirmed `10.1038/s41586-018-0623-z`
3. **Andreatta and Carmona, 2021** — DOI confirmed `10.1016/j.csbj.2021.06.043`
4. **Van Galen et al., 2019** — DOI confirmed `10.1016/j.cell.2019.01.031`
5. **Ke et al., 2017** — URL confirmed (NeurIPS 2017, no DOI by convention)

**18 entries remain [VERIFY]** for future session — DiNardo, Döhner, Falini, Galanis, Geeleher, Howlader, Iorio, Lee, Perl, Pollyea, Stein, Stone, Thiede, Wang (Crenolanib), Zeng, plus 5 paper-identification ambiguous entries (Chen, Ding, Tercan, Wang abstract, Howlader format).

**No changes to citation order or count.** This is incremental verification, not restructuring.

---

## Verified Reference List (selected entries)

### Bottomly et al., 2022 — VERIFIED 2026-05-10

**Bottomly D, Long N, Schultz AR, Kurtz SE, Tognon CE, Johnson K, Abel M, Agarwal A, Avaylon S, Benton E, Blucher A, Borate U, Braun TP, Brown J, Bryant J, Burke R, Carlos A, Chang BH, Cho HJ, Christy S, Coblentz C, Cohen AM, d'Almeida A, Cook R, Danilov A, Dao K-HT, Degnin M, Demir D, Dibb J, Eide CA, English I, Hagler S, Harrelson H, Henson R, Hilberg S, Huang R, Joshi SK, Kaempf A, Kosaka Y, Laderas T, Lawhead M, Lee H, Leonard JT, Lin C, Lind EF, Liu SQ, Lo P, Loriaux MM, Luty S, Maxson JE, Macey T, Martinez J, Minnier J, Monteblanco A, Mori M, Morrow Q, Nelson D, Ramsdill J, Rofelty A, Rogers A, Romine KA, Ryabinin P, Saultz JN, Sampson DA, Savage SL, Schuff R, Searles R, Smith RL, Spurgeon SE, Sweeney T, Swords RT, Thapa A, Thiel-Klare K, Traer E, Wagner J, Wilmot B, Wolf J, Wu G, Yates A, Zhang H, Cogle CR, Collins RH, Deininger MW, Hourigan CS, Jordan CT, Lin TL, Martinez ME, Pallapati RR, Pollyea DA, Pomicter AD, Watts JM, Weir SJ, Druker BJ, McWeeney SK, Tyner JW.** Integrative analysis of drug response and clinical outcome in acute myeloid leukemia. *Cancer Cell* 40(8):850-864.e9, 2022 Aug 8 (Epub Jul 21). 

**DOI: 10.1016/j.ccell.2022.07.002** ✓
**PMID: 35868306** ✓
**Cohort scale (per paper):** 805 patients (942 specimens) — INTERCEPTA used 520 from Waves 1+2 harmonized.

---

### Tyner et al., 2018 — VERIFIED 2026-05-10

**Tyner JW, Tognon CE, Bottomly D, Wilmot B, Kurtz SE, Savage SL, Long N, Schultz AR, Traer E, Abel M, Agarwal A, Blucher A, Borate U, Bryant J, Burke R, Carlos A, Carpenter R, Carroll J, Chang BH, Coblentz C, d'Almeida A, Cook R, Danilov A, Dao K-HT, Degnin M, Devine D, Dibb J, Edwards DK 5th, Eide CA, English I, Glover J, Henson R, Ho H, Jemal A, Johnson K, Johnson R, Junio B, Kaempf A, Leonard J, Lin C, Liu SQ, Lo P, Loriaux MM, Luty S, Macey T, [88 authors total],...Druker BJ.** Functional genomic landscape of acute myeloid leukaemia. *Nature* 562(7728):526-531, 2018 Oct 25 (Epub Oct 17).

**DOI: 10.1038/s41586-018-0623-z** ✓
**PMID: 30333627** ✓
**Cohort scale (per paper):** 672 tumor specimens / 562 patients (Waves 1+2). INTERCEPTA's analysis built on this initial release.

---

### Andreatta and Carmona, 2021 — VERIFIED 2026-05-10

**Andreatta M, Carmona SJ.** UCell: Robust and scalable single-cell gene signature scoring. *Computational and Structural Biotechnology Journal* 19:3796-3798, 2021 (Jun 30).

**DOI: 10.1016/j.csbj.2021.06.043** ✓
**PMC: PMC8271111** ✓
**Method (per paper):** Mann-Whitney U statistic-based gene signature scoring; robust to dataset size and heterogeneity. INTERCEPTA's KAALCURA implementation uses UCell as the per-cell signature scoring engine over MSigDB Hallmark gene sets.

---

### Van Galen et al., 2019 — VERIFIED 2026-05-10

**Van Galen P, Hovestadt V, Wadsworth MH II, Hughes TK, Griffin GK, Battaglia S, Verga JA, Stephansky J, Pastika TJ, Lombardi Story J, Pinkus GS, Pozdnyakova O, Galinsky I, Stone RM, Graubert TA, Shalek AK, Aster JC, Lane AA, Bernstein BE.** Single-Cell RNA-Seq Reveals AML Hierarchies Relevant to Disease Progression and Immunity. *Cell* 176(6):1265-1281.e24, 2019 Mar 7 (Epub Feb 28).

**DOI: 10.1016/j.cell.2019.01.031** ✓
**PMID: 30827681** ✓
**PMC: PMC6515904** ✓
**Cohort scale (per paper):** 38,410 cells from 40 bone marrow aspirates (16 AML patients + 5 healthy donors). INTERCEPTA's cross-dataset H3 analysis aggregates these cells by author cell-type label and uses Prog-like population for KAALCURA R_prolif comparison.
**GEO accession:** GSE116256 (confirmed in INTERCEPTA Methods §"Cross-dataset validation")

---

### Ke et al., 2017 — VERIFIED 2026-05-10

**Ke G, Meng Q, Finley T, Wang T, Chen W, Ma W, Ye Q, Liu T-Y.** LightGBM: A Highly Efficient Gradient Boosting Decision Tree. In: *Advances in Neural Information Processing Systems 30 (NIPS 2017)*. Curran Associates, Inc.; 2017. p. 3146-3154.

**URL: https://papers.nips.cc/paper/6907-lightgbm-a-highly-efficient-gradient-boosting-decision-tree** ✓
**DOI: None (NeurIPS 2017 conference papers do not have DOIs by convention)**
**Method (per paper):** Gradient Boosting Decision Tree with Gradient-based One-Side Sampling (GOSS) and Exclusive Feature Bundling (EFB). INTERCEPTA uses LightGBM (Python package version 4.6.0) as the per-drug binary classifier with locked default hyperparameters per pre-registered specification.

---

## Remaining [VERIFY] entries (18 entries; future session)

These entries have author/title/year from training memory but DOIs flagged for future web-search verification:

1. **DiNardo et al., 2020** — Likely DOI: 10.1056/NEJMoa2012971 (NEJM 383(7):617-629)
2. **Döhner et al., 2017** — Likely DOI: 10.1182/blood-2016-08-733196 (Blood 129(4):424-447)
3. **Falini et al., 2005** — Likely DOI: 10.1056/NEJMoa041974 (NEJM 352(3):254-266)
4. **Galanis et al., 2014** — Likely DOI: 10.1182/blood-2013-10-529313 (Blood 123(1):94-100)
5. **Geeleher et al., 2014** — Likely DOI: 10.1186/gb-2014-15-3-r47 (Genome Biology 15(3):R47)
6. **Howlader et al., 2024** — SEER Cancer Statistics Review (web URL convention varies)
7. **Iorio et al., 2016** — Likely DOI: 10.1016/j.cell.2016.06.017 (Cell 166(3):740-754)
8. **Lee et al., 2018** — Likely DOI: 10.1038/s41467-017-02465-5 (Nat Commun 9(1):42)
9. **Perl et al., 2019** — Likely DOI: 10.1056/NEJMoa1902688 (NEJM 381(18):1728-1740)
10. **Pollyea et al., 2018** — Likely DOI: 10.1038/s41591-018-0233-1 (Nat Med 24(12):1859-1866)
11. **Stein et al., 2017** — Likely DOI: 10.1182/blood-2017-04-779405 (Blood 130(6):722-731)
12. **Stone et al., 2017** — Likely DOI: 10.1056/NEJMoa1614359 (NEJM 377(5):454-464)
13. **Thiede et al., 2002** — Likely DOI: 10.1182/blood.v99.12.4326 (Blood 99(12):4326-4335)
14. **Wang et al., 2017 (Crenolanib clinical)** — Likely ASH 2017 abstract; needs identification
15. **Zeng et al., 2022** — Likely DOI: 10.1038/s41591-022-01819-x (Nat Med 28(6):1212-1223)
16. **Benjamini and Hochberg, 1995** — Likely DOI: 10.1111/j.2517-6161.1995.tb02031.x (J R Stat Soc Series B 57(1):289-300)

**Plus 5 paper-identification flags from Draft 1:**
17. **Chen et al., 2024** — Multiple candidates; needs paper match
18. **Ding et al., 2023** — Multiple candidates; needs paper match
19. **Tercan et al., 2025** — Most ambiguous; needs paper match
20. **Wang et al., 2017 abstract** — ASH abstract vs full paper distinction
21. **Howlader et al., 2024** — SEER citation format conventions

---

## Discipline check

**P15 (only correct, honest, real science):**
- ✓ 5 verified DOIs are from primary sources (PubMed, journal websites, NeurIPS proceedings)
- ✓ Author names checked against multiple sources
- ✓ No DOIs fabricated for the 18 unverified entries — they remain explicitly flagged
- ✓ "Likely DOI" format used for unverified entries with explicit acknowledgment of uncertainty

**P16 (preserve past work):**
- ✓ Draft 1 file (`AML_paper_references_draft1.md`) preserved in outputs
- ✓ Draft 2 is incremental verification, not restructuring

**Anti-fabrication discipline:**
- ✓ Every verified entry has source URL or PMID
- ✓ Verification dates documented
- ✓ Process repeatable: future CSO can follow same web search and reach same DOIs

---

## CSO action items

| # | Item | Effort |
|---|---|---|
| 1 | Verify remaining 13 [VERIFY] DOIs (clinical/method papers) | 0.5 session web search |
| 2 | Identify 5 [VERIFY] papers (Chen, Ding, Tercan, Wang abstract, Howlader format) | 0.5 session web search |
| 3 | Update master manuscript references section with all verified entries | 30 min |
| 4 | Reformat to *Briefings in Bioinformatics* numerical citation style at submission | 30 min |

**Total to complete reference verification:** ~1 session web search + 1 hour formatting.

---

*Reference Draft 2 complete. 5 of 23 verified (22% complete). Remainder bounded for future session. P15 discipline enforced; no fabrication.*

— Prasad Akula (CEO) & Claude (CSO)
2026-05-10
