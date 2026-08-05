# Novel‑target validation protocol — MurB in carbapenem‑resistant *K. pneumoniae* and *A. baumannii*

*Pre‑registered wet‑lab protocol (INTERCEPTA charter: predictions and go/no‑go thresholds fixed BEFORE data). Grounded in published Mobile‑CRISPRi methods for these pathogens and the known MurB biochemistry. This is the S1 step that converts an INTERCEPTA computational prediction into experimental target validation — the single highest‑leverage, lowest‑cost move toward real value.*

---

## 1. Objective & rationale

Convert INTERCEPTA's top computational prediction from *hypothesis* → *experimentally validated antibacterial target* by establishing, in the two WHO‑critical Gram‑negative pathogens, that **MurB is (a) essential, (b) vulnerable to partial inhibition, and (c) produces an on‑pathway cell‑wall phenotype on depletion** — the three properties a target must have to justify a hit‑finding campaign.

**Target:** MurB (UDP‑N‑acetylenolpyruvylglucosamine reductase; peptidoglycan step). *K. pneumoniae* MGH78578 accession **A6TGM9**; *A. baumannii* ortholog (map by reciprocal best hit; gene `murB`).

**Prior support (why this is not a blind bet):** INTERCEPTA — fpocket druggability 0.95, FBA‑essential 5/7 bacteria, host‑absent, experimentally essential in E. coli/M. tb/K. pneumoniae (PREDVAL/VAL‑ESS). Literature — validated‑essential peptidoglycan enzyme; micromolar inhibitors, HTS assay and crystal structures exist; whole‑cell activity shown in Gram‑positives, **not yet Gram‑negatives** (the opportunity).

---

## 2. Pre‑registered predictions & success criteria (fixed before data)

- **H1 (essentiality).** CRISPRi knockdown of `murB` reduces viable count by **≥100‑fold (≥2 log CFU/mL)** on full induction vs uninduced, with **≥2 independent sgRNAs**, in **both** pathogens. *Pass* = met in both; *partial* = one pathogen; *fail/falsified* = no significant defect (→ MurB is not essential under test conditions; report honestly and down‑weight the prediction for that organism).
- **H2 (vulnerability).** Titrated knockdown produces a **dose‑dependent** fitness cost, with a defined **vulnerability index** (fraction knockdown at which growth rate drops 50%, GR50). *High vulnerability* (GR50 reached at modest knockdown) strengthens druggability; *low vulnerability* (only near‑complete knockdown matters) is an honest negative for tractability.
- **H3 (on‑pathway phenotype).** MurB depletion yields the expected **cell‑wall‑stress morphology** (rounding/bulging/lysis by microscopy) and/or sensitization to sub‑MIC cell‑wall antibiotics — confirming the phenotype is peptidoglycan‑specific, not a generic sick‑cell artifact.
- **H4 (permeability probe, optional S1d).** Existing Gram‑positive MurB inhibitors (e.g., 3,5‑dioxopyrazolidines) gain measurable whole‑cell activity in an **efflux‑deficient / outer‑membrane‑permeabilized** strain (e.g., *tolC*/*acrB* mutant, or polymyxin‑B‑nonapeptide co‑treatment) but not the wild type → directly tests whether the Gram‑negative gap is **permeability/efflux** (druggable by chemistry) vs **intrinsic target inaccessibility** (harder). This single experiment de‑risks the whole program's central question cheaply.

---

## 3. Methods

**System:** Mobile‑CRISPRi (Tn7‑integrated, inducible dCas9 + sgRNA; delivered by conjugation), published and Addgene‑available for both *K. pneumoniae* (Mobile‑CRISPRi‑seq) and *A. baumannii* (essential‑gene knockdown / vulnerability studies). Inducer: aTc or IPTG per the chosen kit; titratable by inducer dilution.

**Strains:** ≥1 reference + ≥1 **carbapenem‑resistant clinical isolate** per species (relevance to the CRE/CRAB indication). Confirm `murB` presence/identity by sequencing.

**sgRNA design:** 2–3 sgRNAs targeting the non‑template strand within the first ~5–20% of the `murB` ORF (strong repression); off‑target check vs the genome.

**Controls (mandatory):**
- *Positive essential control:* knockdown of a known essential gene (e.g., `ftsZ` or a 50S ribosomal gene) → strong defect (assay works).
- *Negative non‑essential control:* knockdown of a dispensable gene (e.g., a known non‑essential locus) → no defect (specificity).
- *Non‑targeting sgRNA* → no defect (baseline burden).
- All conditions ± inducer.

**Assays:**
1. **Essentiality (H1):** growth curves (OD600) + **spot‑titer CFU** on ±inducer, ≥3 biological replicates. Endpoint = log CFU reduction on induction.
2. **Vulnerability (H2):** inducer gradient (e.g., 6–8 doses) → knockdown gradient (confirm by RT‑qPCR of `murB` at 2–3 doses) → growth‑rate vs knockdown → compute GR50 / vulnerability index.
3. **Phenotype (H3):** phase‑contrast/fluorescence microscopy of depleted vs control (membrane/cell‑wall stain); optional checkerboard with a sub‑MIC β‑lactam for on‑pathway sensitization.
4. **Permeability probe (H4, optional):** MIC of published MurB inhibitors vs WT, efflux‑deficient, and permeabilized strains.

**Rigor (charter):** predictions/thresholds fixed here (pre‑registration); ≥3 biological replicates; blinded microscopy scoring where feasible; raw data + analysis deposited; the whole readout reproduced independently (2nd operator or 2nd isolate). Negative/partial results reported first‑class.

---

## 4. Go/no‑go, cost, timeline

| Step | Output | Go criterion | ~Time | ~Cost (in a CRISPRi‑capable lab) |
|---|---|---|---|---|
| S1a strain build | Mobile‑CRISPRi murB strains + controls, 2 species | strains validated | 1–2 mo | reagents ~$1–5k (Addgene plasmids + cloning) |
| S1b essentiality (H1) | log CFU reduction | ≥2‑log, ≥2 sgRNAs, both species | +1–2 mo | consumables ~$2–5k |
| S1c vulnerability (H2) | GR50 / vulnerability index | dose‑dependent cost | +1–2 mo | ~$2–5k |
| S1d phenotype + permeability (H3/H4) | cell‑wall phenotype; permeability verdict | on‑pathway phenotype confirmed | +2 mo | ~$3–10k (compounds/microscopy) |

**Total S1:** ~6–9 months; **cash ~$8–25k** if embedded in a collaborating academic lab (most personnel/equipment absorbed), or **~$50–150k** as a funded standalone (R21/INCATE, includes salary). **Cheapest path: a co‑authored study with a lab already running Mobile‑CRISPRi in these pathogens** — near‑zero incremental cash.

---

## 5. What each outcome means (honest interpretation)

- **All pass (H1–H3):** MurB is a validated, vulnerable, on‑pathway target in CRE/CRAB → justifies S2 biochemical assay + hit‑finding. **This is the result that unlocks grants/partners** and makes a future CARB‑X application credible.
- **H1 pass, H2 low vulnerability:** essential but only near‑complete inhibition works → honestly a *weaker* drug target (hard to achieve enough inhibition pharmacologically); report and re‑prioritize (the engine's #2/#3 targets, e.g., MurG/MraY/MEP‑pathway ispE, become the next candidates).
- **H4 informative either way:** if permeabilization rescues activity → the gap is chemistry‑solvable (efflux/permeability) → strong rationale for a Gram‑negative‑focused med‑chem campaign. If not → intrinsic difficulty; pivot target.
- **H1 fail (no defect):** MurB is **not essential** in that pathogen under these conditions → our computational prediction is **falsified for that organism**; we report it plainly (a first‑class negative) and it recalibrates the engine. *This is a real possibility and reporting it honestly is the point.*

---

## 6. Honest risks & limitations

1. **The Gram‑negative whole‑cell hurdle is the program's central, unsolved risk** — a validated target and a biochemical inhibitor frequently fail to yield whole‑cell Gram‑negative activity (permeability + efflux). S1d probes it early on purpose; do not proceed to expensive med‑chem before it is understood.
2. **CRISPRi caveats:** polar effects on downstream genes in an operon (design controls / complementation), incomplete knockdown, and condition‑dependence (rich vs minimal media) — essentiality is medium‑dependent, as our own FBA caveats note.
3. **Target novelty is modest for studied pathogens** — MurB is a known essential class; the honest novelty is (a) Gram‑negative whole‑cell inhibition and (b) the *engine's* zero‑data generality, not the target's identity.
4. **We have no wet‑lab** — this protocol *requires* a microbiology collaborator or funded lab; it is written to be handed to one.

---

## Sources
- Mobile‑CRISPRi in *K. pneumoniae* (essential‑gene knockdown / antimicrobial‑target screen): https://journals.asm.org/doi/10.1128/aem.00956-23
- CRISPRi essential‑gene vulnerabilities in *A. baumannii*: https://journals.asm.org/doi/10.1128/mbio.02051-23 ; https://journals.asm.org/doi/full/10.1128/jb.00565-20
- Mobile‑CRISPRi overview/reagents: https://blog.addgene.org/mobile-crispri-bringing-crispri-to-diverse-bacteria
- MurB inhibitors / HTS assay / structures: https://journals.asm.org/doi/10.1128/aac.50.2.556-564.2006 ; https://pubmed.ncbi.nlm.nih.gov/22068704/ ; https://pubmed.ncbi.nlm.nih.gov/29363274/
- INTERCEPTA prior support: repository LEDGER.md (DRUGGABLE, PREDVAL, VAL‑ESS), papers/zero_data_discovery/REPORT.md.
