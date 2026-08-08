# Anticipated reviews — red-team of the zero-data-discovery manuscript

*A pre-submission adversarial review of `REPORT.md`, written under the Constitution (truth over vision). Purpose: state
the sharpest objections a hostile-but-fair reviewer will raise, at full strength, BEFORE an editor does — and answer each
honestly, marking where the objection is already conceded in the paper, where it is genuinely mitigated, and where it is
**open / potentially fatal**. This is not a rebuttal to win; it is a map of the paper's true attack surface so we submit
to the right venue with the right framing, and pre-empt the revisions we can already see coming. Every objection is
cross-referenced to the manuscript claim it targets and the committed experiment behind it.*

**Bottom line up front (honest):** the manuscript's *validity* is strong — the claims are heavily caveated, the negatives
are first-class, and nothing material is overstated relative to its own limitations section. The paper's real risk is
**novelty/impact framing**, not correctness: its central positive (FBA essentiality enriches for experimental essentiality)
is largely known, and two framing words — "prospective-blind" and "law" — promise more than retrodiction-against-public-data
and an n=19 correlational synthesis deliver. The paper is a strong fit for a **methods / rigorous-negatives venue**
(PLoS Comp Biol, Bioinformatics, GigaScience, eLife) and a poor fit for a high-impact discovery venue that will read
"any disease" as the headline. Frame to the former; soften the two words; foreground the genuinely novel pieces (the
abstaining router + transfer-condition operationalization + the MET4 study-bias negative + the domain-crossing blind suite).

---

## Tier 1 — the objections most likely to decide the paper's fate

### R1. "The central positive is not novel." — **HIGH (impact), LOW (validity); CONCEDED**
*Targets:* the FBA-essentiality result (Findings §MET, VAL-ESS, Fig 1) and the DepMap selective-dependency result (§Human cancer).
> That FBA/GEM single-gene-deletion essentiality is enriched for experimental knockout essentiality has been shown many
> times since the 2000s (iML1515 and predecessors were validated exactly this way). That selective DepMap dependencies
> recover known cancer targets is standard DepMap analysis. Where is the new science?

**Honest response.** We concede this directly — limitation (14) already states the transfer-condition law "is a synthesis
over largely-known biology… the contribution is the *operational* rule, not new molecular biology." The novel contributions
are not the per-signal validations but: (i) the **operational transfer-condition rule** (when to *fire vs abstain* per
biology class) realized as a working **abstaining router** with a proven fail-safe edge (DARK1: 22/22 abstain, 0 false
calls); (ii) the **domain-crossing prospective-blind protocol** (lock-before-reveal across all three domains of life,
including an archaeon) which is a rigor design the field rarely runs; (iii) the **MET4 study-bias negative** (network
centrality's "mechanism" signal collapses +0.128→−0.004 under a study-intensity control) — a genuinely useful,
underreported negative; (iv) the **honest negative map** as a coherent object.
**Verdict:** not fatal to validity, but **decisive for venue**. If we submit anywhere that expects a novel biological
*finding* as the headline, this objection sinks it. Mitigation is framing: lead with the *method + rigor + negatives +
operational composition*, and say plainly the per-signal validations are confirmations, not discoveries. Do **not** let
"any disease" be the abstract's first promise.

### R2. "'Prospective-blind' is retrodiction against public data dressed up." — **HIGH; PARTIALLY CONCEDED**
*Targets:* the abstract's "prospective-blind suite across all three domains of life," the BLIND1–7 table, the title's
"pre-registered prospective validation."
> The "blind" is a git commit made before *you* consulted an experimental file that already existed in a public database.
> Nothing was predicted before it was measured in the world — the answer existed the whole time. Calling this "prospective"
> and "predicts, not postdicts" overstates a well-ordered retrodiction. And BLIND1 had its truth-set remapped *after* an
> inconclusive first adjudication — how blind is that?

**Honest response.** Limitation (1) already concedes this exactly: "prospective only in the held-out sense… not a
prospective wet-lab test." The blindness is **version-control-enforced analyst blindness** (the git history is an audit
trail that the predictions were fixed before the analyst pulled the answer) — real and better than typical retrodiction,
but not world-prospective. The BLIND1 remap is disclosed in-line (the predictions stayed hash-locked; only the
experimental set's namespace was fixed by sequence homology). **Verdict:** the *substance* is honestly disclosed, but the
**word "prospective" in the title and abstract is doing rhetorical work the design doesn't fully support** and will draw
this exact fire. **Requested self-revision:** downgrade "prospective-blind" → "analyst-blind (lock-before-reveal)" or
"pre-registered held-out," and state once, up front, that no prediction preceded a real-world measurement. This costs
nothing and removes the single most quotable overclaim.

### R3. "The gate was calibrated on bacteria, then eukaryote failures were explained post-hoc, and FAIRGATE is HARKing." — **MEDIUM-HIGH; CONCEDED**
*Targets:* the OR>3 gate, the prokaryote/eukaryote split narrative, META1, FAIRGATE1, Methods "base-rate-fair gate."
> You set OR>3 on bacteria, both blind eukaryotes failed, and then you produced a meta-analysis (META1) and a new gate
> (FAIRGATE1) that reinterpret the failures as "real signal compressed below a bacteria-calibrated bar." That is
> hypothesizing after results are known. The fair gate improves the story you already saw.

**Honest response.** Limitation (13) concedes this in full and is unusually candid: FAIRGATE "was *not* pre-registered…
treat it as a proposed, invariance-validated methodological improvement, not a pre-registered confirmatory result." The
mitigations are real and load-bearing: (a) FAIRGATE is validated by a **data-independent** argument (a within-*organism*
PASS↔FAIL flip on the identical iPfal19 model across two screens of different base rate, plus a simulation), not by
improving the suite's pass rate; (b) **no committed OR-gate verdict is flipped** — the blind FAILs stay FAILs on the
record; (c) it is recommended only for *future* tests. **Verdict:** honestly handled, but a strict reviewer will still
want the post-hoc analyses **clearly walled off** — recommend moving META1/FAIRGATE to an explicitly-labeled "Exploratory /
post-hoc" subsection so no reader mistakes them for confirmatory. Keep the committed verdicts as the headline.

### R4. "'Any disease' and 'transfer-condition law' overclaim from n≈6 classes and n=19 organisms." — **MEDIUM-HIGH; PARTIALLY CONCEDED**
*Targets:* the title/North-Star framing, the "law" (Part II, Table), META1 (n=19, correlational).
> Six disease classes with one abstention is not "any disease." A ρ=+0.55 correlation over 19 heterogeneous organisms with
> different truth-sets and GEM sources is not a "law" — it's a suggestive trend from a small, confounded sample. The
> multivariable model is admittedly underpowered.

**Honest response.** The paper already reframes "any disease" as "**honest decision coverage, not a universal model**"
(abstract, conclusion) and concedes n and confounds in limitations (7) and in META1's own scope line ("retrospective,
small-n, correlational, heterogeneous truth-sets/GEM-sources as confounds"). But the **word "law"** is a target the same
way "prospective" is. **Requested self-revision:** demote "transfer-condition **law**" → "transfer-condition **principle**"
or "…**heuristic**" throughout (it is an operational rule, not a physical law — we say as much in limitation 14). Keep
"any disease → decision coverage" framing; it is defensible. **Verdict:** not fatal; a terminology fix removes most of the
sting.

---

## Tier 2 — objections that will shape required revisions

### R5. "High precision, low recall (9–25%) — is this useful for discovery?" — **MEDIUM; CONCEDED (2)**
FBA is metabolic-scoped and misses 75–91% of essentials. **Response:** the validated deployment mode is
precision-at-top-of-list + **abstention** for zero-data triage (the engine reports rank-not-label at genome scale by
construction), and the conservation-breadth axis explicitly recovers non-metabolic essentials the engine's FBA arm is
blind to (K. pneumoniae demo: dnaE/ileS/leuS/secA/topA). Honest, conceded, and the recall bound is stated everywhere it
matters. Reviewer may still want a precision-at-k / enrichment curve foregrounded over the odds ratio — cheap to add.

### R6. "Viral structural recovery leans on TM 0.41–0.49, below the 0.5 same-fold convention." — **MEDIUM; CONCEDED (8)**
The 7/9 "recover correct class" sits below the conventional same-fold cutoff, and short all-α proteins can produce
fold-promiscuity artifacts. **Response:** the claim is deliberately **class-ID, not fold-identity**; the gate is disclosed
at TM≥0.4, promiscuity artifacts are disclosed and excluded from the gated claim (Fig 6 greys the two misses), and AlphaFold
DB excludes viral structures (coverage gate, stated). A reviewer may reasonably ask for a **null distribution of
off-class TM** to show 0.41–0.49 is above chance for these query sizes — we should add that null explicitly rather than
rely on the best-off-class bar in Fig 6.

### R7. "The cancer recovery@10=0.80 vs 6×10⁻⁴ null is a trivial baseline; known targets are the most-studied." — **MEDIUM; PARTIALLY MITIGATED**
Recovery against a *random-gene* null is weak (known cancer genes are easy to hit). **Response:** the study-bias objection
is the one that matters and it is addressed *separately* — F3CLIN1 applies a publication-matched null and a
Mantel–Haenszel stratified OR (2.72) and still finds patient-driver enrichment; and recovery holds on **held-out cell
lines** (0.80), which the random null does not explain. **But** the recovery@10 headline number itself should be reported
next to a **study-intensity-matched** null in-line (not only in F3CLIN1), because as printed it invites this objection. A
reviewer will likely require it.

### R8. "The parasite section is a wash — verdict flips with screen technology; why is it in the paper?" — **LOW-MEDIUM; INTENTIONAL**
n=2, OR spans 0.86–3.07 across GEMs, the P. berghei screen flips pass/fail. **Response:** it is included *as* an honest
boundary and a **retracted rule** (the "host-embedded fails" rule we made at n=1 and falsified with Toxoplasma) — an
integrity demonstration, and the clean same-species-CRISPR test is data-gated (stated). **Verdict:** defensible and
arguably a strength, but an editor may ask to compress it to the supplement. Keep the retraction visible in the main text
(it is the paper's clearest self-correction); the six-model swap detail can move to supplementary.

### R9. "De-novo CarveMe / default-medium GEMs over-call biosynthesis essentials." — **MEDIUM; CONCEDED (5) + partly answered (Fig 3)**
Default-medium FBA marks biosynthesis genes essential that a nutrient-replete host would rescue. **Response:** exactly why
the **condition-robustness axis** exists (Fig 3: condition-robust essentials are 79% vs 48% experimentally essential,
+0.32) — it quantifies and partly resolves the medium-dependence caveat, and flags host-bypassable biosynthesis targets.
Conceded and instrumented. Reviewer may want condition-robustness applied to the blind suite too (currently a
bacteria-panel result).

### R10. "Reproduce-×2 byte-identical demonstrates determinism, not replication." — **LOW; TRUE, REFRAME**
Correct. **Response:** we should not (and the paper does not) claim ×2 as independent replication — it guards against
non-determinism and uncommitted state. The *replication* claims are the **held-out organisms** (K. pneumoniae, A.
baumannii never in development) and the domain-crossing blind suite. Ensure the Methods sentence doesn't let "reproduced
×2" be read as robustness; it currently says "byte-identical … excluding the verdict," which is fine — leave as is but
never lean on it for a robustness claim in the response to reviewers.

---

## Tier 3 — minor / editorial (pre-empt in submission)

- **R11. Single author, "to be finalized."** An editor will query authorship/affiliation. Resolve before submission
  (correspondent + any contributors) rather than submitting with the bracketed placeholder in the byline.
- **R12. Title length.** The current title is ~60 words. Most venues cap it; prepare a ≤25-word title (e.g.
  *"An honest map of which zero-data target-ID signal transfers to which biology: FBA gene-essentiality across three
  domains, first-class negatives, and an abstaining router"*).
- **R13. Data availability with "data never committed."** Reviewers must be able to reproduce; ensure MANIFEST checksums +
  the exact public accessions are sufficient to regenerate every input, and that the code runs from a clean checkout with
  only `INTERCEPTA_DATA` set. State the CPU-only/arm64 constraint (GNINA/CUDA infeasibility) up front so a Linux/GPU
  reviewer doesn't flag the docking result as under-powered by choice.
- **R14. Figure-count / 5-virus vs 4-in-Fig6 mismatch.** Already footnoted (Fig 6 shows 4 hardening viruses; SARS-CoV-2 is
  the separate blind result), but a skimming reviewer will "catch" it — consider a one-line caption note or adding the
  SARS-CoV-2 point to Fig 6 to remove the apparent discrepancy.

---

## What would genuinely sink the paper (fatal scenarios) — and our honest exposure

1. **Editor decides novelty is insufficient for the venue.** *Real and likely at high-impact venues* (see R1). Mitigation
   is entirely venue selection + framing; the science does not change. **This is our single biggest risk.**
2. **A reviewer demonstrates a lock was not actually pre-reveal.** *Low probability* — git history is the audit trail and
   the one adjudication fix (BLIND1) is disclosed with the predictions hash-verified unchanged. Not exposed unless the
   disclosure itself is read as insufficient; keep the git SHAs and the hash in the supplement so the audit is trivial.
3. **A reviewer shows the fair-gate reinterpretation changed a committed verdict.** *Not exposed* — no committed verdict is
   flipped; this is checkable and we should hand the reviewer the check.
4. **A reviewer wants ANY wet-lab.** *Exposed but honest* — the paper states the next rung is experimental, not
   computational. Only fatal if submitted to a venue that requires experimental validation; not fatal at a
   methods/negative-results venue. (This is exactly why the turnkey CRISPRi design in
   `experiments/CRISPRIDESIGN1_wetlab_ready/` + `docs/EXPERIMENTAL_VALIDATION.md` matters: it shows the experimental path
   is specified and cheap, even though unrun.)

## The revisions we should make BEFORE submitting (all cheap, all honest)
1. ✅ **APPLIED 2026-08-08.** Downgraded **"prospective-blind" → "analyst-blind (lock-before-reveal)"** and
   **"transfer-condition law" → "transfer-condition principle"** throughout the manuscript, + an explicit abstract clause
   ("*analyst*-blindness against existing public knockout data — version-control-enforced ordering — NOT a wet-lab
   prospective test"). Removes the two most quotable overclaims at zero cost to substance. (Remaining R2/R4-adjacent uses of
   "prospective" in REPORT.md are the honest caveats — "prospective assays/wet-lab/data", "prospective only in the held-out
   sense … not a prospective wet-lab test" — and are left as-is.)
2. Wall off **META1/FAIRGATE into an explicitly-labeled "Exploratory (post-hoc)" subsection** (R3).
3. Add an **off-class TM null** for the viral result (R6) and a **study-intensity-matched null** next to the cancer
   recovery@10 headline (R7).
4. Add a **≤25-word title** and resolve **authorship** (R11–R12).
5. Lead the abstract with **method + rigor + negatives + operational composition**; make "any disease → decision coverage"
   a *reframe*, not the opening promise (R1).

## Recommended venue (honest fit)
**Primary:** PLoS Computational Biology or GigaScience (rigor + negatives + reproducibility are valued; no wet-lab
required). **Secondary:** Bioinformatics (Original Paper) or eLife. **Not recommended as first choice:** any journal whose
readership expects a novel therapeutic finding — the honest-map/negatives framing will read as insufficient novelty (R1).
The preprint (bioRxiv) is unconditionally appropriate and already prepared.

---
*This document is a pre-submission self-critique, not a claim about the paper's quality. It is deliberately harsher than a
real reviewer to leave no surprise. Where it recommends softening a word, that is an integrity fix (matching the claim to
the evidence), not a retreat from a defensible result.*
