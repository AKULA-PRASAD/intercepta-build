# INTERCEPTA → CARB‑X: honest fit assessment, strategy, and pitch

*Author draft, 2026‑08. Grounded in the CARB‑X 2026 funding round announcement and INTERCEPTA's committed results (LEDGER.md). Written to the project's charter: truth over vision — no overstatement of readiness.*

---

## PART 0 — The brutal‑honest fit assessment (read this first)

**CARB‑X does not fund what we have today.** Three hard facts:

1. **Stage.** CARB‑X therapeutic themes require a **molecule with confirmed in‑vitro activity against a specific bacterial target that inhibits viability in culture**, entering at **hit‑to‑lead**. We have **zero** molecules with confirmed antibacterial activity. Our docking output (ENGINE molecule bridge) is explicitly *pose‑plausible hypotheses, not validated actives*.
2. **Theme mismatch.** The 2026 "Novel Chemistry" theme is restricted to **five pre‑specified targets** (ribosome, PBPs, Type II topoisomerases, LpxH, LolCDE). Our value is *discovering* targets — orthogonal to a fixed‑target chemistry call.
3. **Timing + capability bar.** The 2026 Expression‑of‑Interest window (Apr 8–22, 2026) has **closed**. And academic applicants must "demonstrate capabilities expected of a drug‑development industry partner" — a solo computational effort with no wet‑lab does not, yet.

**Conclusion:** A CARB‑X application *from our current state* would be desk‑rejected. CARB‑X is a **stage‑gated destination**, not a near‑term funder. This document therefore does two honest things: (A) defines the **shortest credible path to becoming CARB‑X‑eligible**, and (B) provides the pitch content to use *once we reach the entry bar* — plus the funders that actually fit our current stage (Part 4).

**What we genuinely have (the honest asset):** a reproducible, zero‑data target‑prioritization **engine** whose core signal (FBA gene‑essentiality) is **experimentally validated against gene‑knockout data in five bacteria, two of them held out of development** (E. coli OR 64, M. tuberculosis 7.9, P. aeruginosa 23, K. pneumoniae 63, A. baumannii 13; all clear a pre‑registered OR>3, p<0.01 gate), with calibrated confidence and honest abstention. That is a real, publishable capability — and a credible *enabling technology* narrative — but it is a **platform + validated method**, not a drug asset.

---

## PART 1 — The product concept (what a CARB‑X‑bound program looks like)

**Product:** a novel‑mechanism, **direct‑acting small‑molecule inhibitor of MurB** (UDP‑N‑acetylenolpyruvylglucosamine reductase; peptidoglycan biosynthesis) with **whole‑cell activity against carbapenem‑resistant Gram‑negative priority pathogens** — *Klebsiella pneumoniae* and *Acinetobacter baumannii* (WHO critical; CARB‑X priority; the same pathogens named in CARB‑X's neonatal‑sepsis theme).

**Why MurB (data‑driven, honestly bounded):**
- INTERCEPTA independently prioritizes MurB from **zero drug data** as its top broad‑spectrum druggable target — fpocket druggability **0.95**, FBA‑essential in **5/7** bacteria, **host‑absent** (humans have no peptidoglycan → intrinsic selectivity), and **experimentally essential in all three tested pathogens** (E. coli, M. tb, K. pneumoniae; PREDVAL).
- MurB is **biochemically tractable**: micromolar inhibitors are published (3,5‑dioxopyrazolidines, IC₅₀ 4–7 µM; tetrazoles), a validated **HTS fluorescence assay** exists (nanomolar product detection), and **crystal structures** are available.
- **The unmet gap = the opportunity, stated honestly:** demonstrated whole‑cell MurB‑inhibitor activity to date is essentially **Gram‑positive only** (MRSA/VRE/PRSP, MIC 0.25–16 µg/mL). **No MurB inhibitor has achieved useful Gram‑negative whole‑cell activity** — the classic Gram‑negative permeability/efflux barrier. A program that cracks Gram‑negative MurB inhibition would be genuinely novel and directly on‑theme for CARB‑X's #1 theme (direct‑acting Gram‑negative therapeutics).

**What the engine adds beyond "MurB is known":** for *studied* pathogens, MurB itself is not a novel target — be honest about that. The engine's differentiators are (i) it reaches the *same* validated‑essential/host‑absent/druggable conclusion **with zero activity data**, which is what matters for **novel/emerging/engineered pathogens where nothing is known** (the biodefense / pandemic‑response angle), and (ii) it does so with **calibrated confidence and honest abstention** — it says when it doesn't know. MurB is the *de‑risked entry vehicle*; the platform is the durable asset.

---

## PART 2 — The pathway to CARB‑X eligibility (stage‑gated milestones)

| Stage | Deliverable | Evidence produced | Fundable by | ~Cost / time |
|---|---|---|---|---|
| **S0 (done)** | Zero‑data engine + validated essentiality signal (5 organisms) + honest target dossier | Committed, reproduced ×2; preprint | (self / compute) | done |
| **S1 (next — see validation protocol)** | Genetic **target validation** of MurB in K. pneumoniae + A. baumannii: essentiality + **vulnerability** (CRISPRi titration) | Wet‑lab confirmation the target is essential *and* vulnerable to partial inhibition | NIH R21/NIAID, Gates, academic collaborator, INCATE | ~$50–150k, 6–12 mo |
| **S2** | **Biochemical assay + hit‑finding**: recombinant Gram‑neg MurB, HTS/fragment/DEL screen → confirmed biochemical inhibitors | Validated hits with target engagement | NIH R01, INCATE, seed/accelerator | ~$200–500k, 12–18 mo |
| **S3 = CARB‑X entry** | **Hit‑to‑lead**: hits with **confirmed whole‑cell activity** (MIC) vs CRE K. pneumoniae / CRAB, target‑specific mechanism, tractable SAR | The exact CARB‑X minimum entry criterion | **CARB‑X** (+ CHEAD/Broad on‑ramp) | CARB‑X staged, milestone‑based (historically ~$1–4M+ total; verify current TPP) |

**The gating risk is S3, and it is real:** the Gram‑negative whole‑cell hurdle is where most antibacterial programs die. We must not pretend otherwise. The S1→S2 work is cheap and de‑risking; the honest go/no‑go is *"can a biochemical MurB hit be made to penetrate a Gram‑negative and kill it?"* — that question, answered either way, is worth doing.

---

## PART 3 — The pitch (concept‑paper content, for the CARB‑X‑eligible stage or an enabling‑tech partner)

**Title:** *Zero‑data target discovery enabling first‑in‑class Gram‑negative MurB inhibitors for carbapenem‑resistant Klebsiella and Acinetobacter.*

**Problem.** CRE and CRAB are WHO‑critical, with collapsing treatment options; the pipeline is thin and target‑poor. Existing discovery is bottlenecked on *which* target to pursue in a new/resistant organism, and validated Gram‑negative targets remain undrugged.

**Solution / innovation.** INTERCEPTA is a computational engine that, from a pathogen genome and **zero activity data**, produces a **safe, confidence‑tiered, provenance‑tagged target shortlist** — composing mechanistic gene‑essentiality (experimentally validated, 5 organisms, 2 held‑out), metabolic chokepoint, cross‑organism conservation, a non‑metabolic‑recall signal, and a **hard host‑non‑homology safety filter**. It nominates MurB as a top host‑absent, druggable, broad‑spectrum Gram‑negative target and provides the enabling map for a focused hit‑finding campaign.

**Plan.** S1 genetic validation (essentiality + vulnerability, CRISPRi) → S2 biochemical assay + hit‑finding → S3 whole‑cell Gram‑negative hit‑to‑lead (CARB‑X entry).

**Differentiator vs field.** (i) **Generality:** the engine works on any/novel pathogen (validated on two held‑out WHO pathogens) — directly relevant to emerging‑threat/biodefense response; (ii) **Honesty by construction:** calibrated confidence + abstention (it flags what it cannot know), the opposite of black‑box hype; (iii) **Reproducible + pre‑registered** (every result reproduced ×2, negatives reported).

**Team gap (stated honestly).** Current: strong computational method, no wet‑lab, no med‑chem. **Ask includes** a wet‑lab microbiology collaborator (CRISPRi) and, at S2+, a med‑chem/assay partner or CRO. This is the single biggest execution risk and the reason S1 is framed as a *collaboration*, not a solo effort.

**Scope/honesty statement (include verbatim).** *All target nominations are computational hypotheses; the essentiality enrichment is experimentally validated, the drug‑target/selectivity/clinical claims are not. Candidate molecules to date are pose‑plausible only. No wet‑lab has been performed by us. The Gram‑negative whole‑cell hurdle is unproven for this target and is the primary program risk.*

---

## PART 4 — The funders that actually fit our current stage (do these FIRST)

CARB‑X is S3. Our S1 is best funded by:

1. **NIH / NIAID** — R21 (exploratory, ~$275k/2yr, ideal for target validation) or R01; NIAID explicitly funds AMR target validation. Best fit for S1.
2. **Gates Foundation / Gates‑funded AMR & neglected‑disease calls** — fund method + validation for high‑burden pathogens.
3. **INCATE** (Incubator for Antibacterial Therapies in Europe) and similar antibacterial incubators — very early, target‑validation‑stage friendly; small non‑dilutive + mentorship.
4. **CARB‑X CHEAD / Broad Institute (Collaborative Hub for Early Antibiotic Discovery)** — the academic *early‑discovery* on‑ramp associated with CARB‑X; a route to biochemical assay + hit‑finding support (S2) for academic investigators. **Highest‑leverage relationship to build now.**
5. **An academic microbiology collaborator** — the cheapest path of all: a lab already running Mobile‑CRISPRi in K. pneumoniae / A. baumannii could do S1 essentiality+vulnerability as a co‑authored study at near‑zero cash cost. **This is the recommended first move.**

**Recommended sequence:** (1) publish the preprint (credibility) → (2) email 3–5 CRISPRi‑capable micro labs with the target dossier + the validation protocol, proposing a co‑authored validation → (3) in parallel, submit an R21/INCATE built on the same protocol → (4) engage CHEAD → (5) reach S3 → apply to CARB‑X's next round.

---

## Sources
- CARB‑X 2026 funding round (themes, entry criteria, timeline): https://carb-x.org/carb-x-news/carb-x-launches-2026-funding-round-to-address-global-burden-of-amr/ ; https://www.cidrap.umn.edu/antimicrobial-stewardship/carb-x-targets-4-product-themes-new-funding-round
- CARB‑X novel‑chemistry theme: https://carb-x.org/carb-x-news/carb-x-announces-new-chemistry-focused-theme-ahead-of-2026-funding-call/
- CARB‑X hit‑to‑lead entry / CHEAD (Broad): https://www.broadinstitute.org/infectious-disease-and-microbiome/carb-x-collaborative-hub-early-antibiotic-discovery ; https://www.niaid.nih.gov/research/carb-x
- MurB target + inhibitors + HTS assay: https://journals.asm.org/doi/10.1128/aac.50.2.556-564.2006 ; https://pubmed.ncbi.nlm.nih.gov/22068704/ ; https://pubmed.ncbi.nlm.nih.gov/29363274/
- INTERCEPTA evidence: repository LEDGER.md (VAL‑ESS ×5 organisms, PREDVAL, DRUGGABLE, ENGINE), papers/zero_data_discovery/REPORT.md.
