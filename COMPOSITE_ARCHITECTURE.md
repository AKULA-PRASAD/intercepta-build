# INTERCEPTA — The fullest vision as a DISEASE-CLASS-AWARE COMPOSITE (many models → one book)

*CSO architecture synthesis. Premise (Prasad, 2026-08-05): "any disease" does NOT mean one universal model
that fits all — it means one integrated system that composes MANY validated models, each the right tool for a
biology class, unified with honest confidence and abstention. Each validated model is a paper; the integrated,
routed, governed system is the book. Grounded in the committed LEDGER; nothing here is aspiration dressed as
result.*

---

## 1. The reframe (why "one model fits all" is the wrong goal — and our own data proves it)
A single universal predictor for "any disease" is not just infeasible — our evidence shows it would be
*dishonest*, because **the signal that carries target-discovery information is different for different
biology**:
- Free-living **bacteria** → metabolic **FBA-essentiality** is strong (VERIFIED, OR 5–64, prospective-blind).
- **Eukaryote / fungal pathogen** → FBA-essentiality **transfers** (GENERALIZE4 yeast OR 4.65; HARDENF1
  *Candida* OR 13.93 — n≥2, incl. a clinical pathogen; precise-but-narrow, rich-medium → low recall).
- Host-dependent **parasite** → **GEM-dependent, NOT categorical** (corrected by HARDENP1): FBA FAILS on
  *Plasmodium* (GENERALIZE5 + HOSTCTX1/2 — iPfal19 salvage-bypass topology) but PASSES on *Toxoplasma* (HARDENP1
  OR 14.10). Host-embeddedness does not decide it; GEM topology quality does.
- **Virus** → no metabolism (FBA n/a), sequence homology fails, but **structural homology** recovers the
  drugged folds (GENERALIZE2/3, PASS).
- Human cell / **cancer** → the promising signal is **functional dependency** (V15–18), not metabolism.

So the fullest vision is a **composite**: identify the input's biology, apply the validated signal(s) that are
*known to transfer* to that biology, compose them with calibrated confidence, and **abstain** where we have no
validated signal. That is "any disease" done honestly — universal *coverage of the decision*, not a universal
*model*.

## 2. The intellectual core: WHEN does a model built on genome A transfer to genome B?
"How could one genome-modeled approach work on another?" — each signal has a specific, evidence-derived
**transfer condition**. The composite works by checking which conditions hold for the input and firing only
those signals. This is the rigorous answer to the transfer question:

| Signal (module) | Transfers from A→B **when…** | Evidence for the condition | Breaks when… |
|---|---|---|---|
| **FBA gene-essentiality** | B's GEM **topology encodes genuine biosynthetic dependence** (a quality GEM) — NOT determined by host-embeddedness | bacteria OR 5–64 (n=6); yeast OR 4.65 + *Candida* OR 13.93; **Toxoplasma OR 14.10 (host-dependent, PASSES)** | the specific GEM is salvage-bypass-heavy → essentials read dispensable (*Plasmodium*/iPfal19, GENERALIZE5/HOSTCTX1/2) — a GEM-quality failure, not a host-embeddedness rule (HARDENP1) |
| **Sequence homology** (target/drug) | B shares **detectable sequence identity** with A's known targets/drugs | INTERVENE1 9/9 canonical; bacteria panels | cross-family distance (virus: 0 hits) — GENERALIZE1 |
| **Structural homology** (Foldseek) — for target CLASS-ID | B's protein **fold is conserved** with a known target/drug + a structure exists | GENERALIZE2/3 recovers Mpro/RdRp at <10% seq id | no structure available (AF-DB viral gap) |
| **Structural REPURPOSING** (coverage) — ⚠ FALSIFIED as a coverage-expander | (does NOT transfer for coverage) | STRUCTREPURPOSE1 NEGATIVE: validates 11/11 but a random-protein null matched *more* targets than drug targets — "expanded coverage" was fold-census promiscuity | at "same-fold" TM almost any large structure set matches almost any enzyme → use structure to CONFIRM a known drug's class, NOT to widen the drugged-target set |
| **Conservation breadth** | the essential is part of a **broadly conserved core** | REACH1 AUROC 0.86 for non-metabolic essentials | lineage-specific essentials |
| **Functional dependency** (CRISPR) — ✅ VALIDATED (DEPEND1), transfer bound TESTED | a **context-specific dependency signal** exists (or an in-domain learnable expr→dep map) | **DEPEND1 G1/G2/G3 PASS**: selective dependencies recover known targets (0.80), generalize to held-out lines (0.80), label-free expr→dep beats baseline (ρ 0.36); + V13/V16–18 | does NOT transfer to a novel/zero-screen organism — **TRANSFER1**: selective signal fails organism-transfer (OR 0.90, chance); only conserved-core transfers (redundant with conservation). So it fires only where the organism itself (or its close domain) has a screen. |
| **Host-safety filter** | B's targets can be compared to the **host proteome** | ENGINE hard filter (Hart CEG2 + human homology) | host unknown |

**The unifying law:** a signal transfers exactly as far as the *biological invariant it rides on* is conserved
— metabolism-structure for FBA, sequence for mmseqs, fold for Foldseek, core-genome for conservation,
dependency-wiring for CRISPR. The composite is honest precisely because it refuses to apply a signal outside
its transfer condition (→ abstain), instead of forcing one model onto biology it does not fit.

## 3. The architecture: router → validated modules → governed composite
```
            ┌─────────────────────────────────────────────────────────────┐
  INPUT ───▶│  (0) BIOLOGY-CLASS DETECTOR                                  │
 genome/    │      genome→proteome; GEM buildable? homologs? structures?   │
 proteome/  │      → class ∈ {bacterium, free-euk, host-dep parasite,      │
 sample     │        virus, human/cancer, unknown}                         │
            └───────────────┬─────────────────────────────────────────────┘
                            ▼    (apply ONLY signals whose transfer condition holds)
     ┌───────────────────────────────────────────────────────────────────────────┐
     │  VALIDATED MODULE LIBRARY (each = a "paper", independently validated)        │
     │  FBA-essentiality · chokepoint · conservation-breadth · structural-homology  │
     │  · sequence-repurposing · structural-repurposing · resistance-robustness     │
     │  · condition-robustness · functional-dependency · host-safety(hard filter)   │
     └───────────────┬───────────────────────────────────────────────────────────┘
                     ▼
     ┌───────────────────────────────────────────────────────────────────────────┐
     │  (8) GOVERNED COMPOSITE (already built + validated: DiscoveryEngine)          │
     │  z-scored tiered RANK composition · calibrated confidence (CALIB1) ·          │
     │  ABSTENTION where no validated signal · provenance tiers · failure-mode report│
     └───────────────┬───────────────────────────────────────────────────────────┘
                     ▼   honest, confidence-tiered, provenance-tagged, ABSTAINING target shortlist
```
The governed-composite layer **already exists and is validated** (ENGINE, CALIB1, BESTINT1) — the missing piece
is making the **class-detector + transfer-condition gating EXPLICIT**, so the system applies FBA to a bacterium,
structure to a virus, dependency to a host-embedded case, and *abstains* rather than emitting a bacterial-style
answer for a parasite (which GENERALIZE5 shows would be wrong).

## 4. Honest coverage map (what the composite can claim TODAY, by class)
| Class | Signal(s) that fire | Tier today | Composite status |
|---|---|---|---|
| Bacterium (free-living) | FBA + chokepoint + breadth + structure + safety + resistance + condition | **VERIFIED** | shipped (ENGINE, ENGINE-AB, SAUREUS, CROSSVAL, BLIND1) |
| Free-living eukaryote/fungus | FBA(weaker) + breadth | COMPUTED/VERIFIED | validated enrichment (GENERALIZE4) |
| Virus | structural-homology (+ structural-repurposing) | COMPUTED | PASS, structure-gated (GENERALIZE3; STRUCTREPURPOSE1 pending) |
| Human / cancer (TARGET-ID) | **functional-dependency (DEPEND1)** | **COMPUTED (validated + held-out generalization + patient-relevance bridge)** | selective dependency recovers known targets, generalizes to disjoint lines, + label-free arm (DEPEND1 G1/G2/G3); **F3CLIN1: enriched for patient-tumor drivers (OR 2.55, survives study-bias)**. Cell-line target-ID; NOT patient drug-response (tested-negative: B20/B10/B17) and NOT clinical outcome |
| Host-dependent parasite | **FBA IF a good-topology curated GEM exists** (Toxoplasma PASS OR 14.10) — flag elevated uncertainty (Plasmodium fails on a salvage-heavy GEM); dependency path ABSTAINS for zero-screen | MIXED (FBA GEM-dependent; label-free dependency GATED) | HARDENP1: FBA works with a quality GEM, not categorically gated. TRANSFER1: label-free dependency does NOT transfer to a zero-screen parasite (only conserved-core, redundant with REACH1). Net: try FBA w/ a curated GEM (uncertain a-priori), else conserved-core via conservation. |
| Unknown organism | detector + whatever conditions hold | ENGINEERING | the honest general case: apply-what-transfers, abstain otherwise |

## 5. "Papers → book" — the publication/deliverable structure
Each validated model is a standalone contribution (paper); the book is the integrated, routed, governed system.
- **Paper A** — Label-free target-ID for pathogens: FBA-essentiality validated across 6 organisms +
  prospective-blind (VAL-ESS*, CROSSVAL, BLIND1). *(strongest; ready)*
- **Paper B** — The generalization frontier: which signal transfers to which disease class, and why
  (GENERALIZE1–5 + HOSTCTX1–2 + the transfer-condition law §2). *(novel, honest, includes the negatives)*
- **Paper C** — Structural bridge for emerging viruses (GENERALIZE2/3) + structural repurposing
  (STRUCTREPURPOSE1, pending).
- **Paper D** — Why metabolic essentiality fails host-embedded biology and the dependency redirection
  (HOSTCTX1/2 negatives → functional-dependency; unifies with the human line). *(a rigorous negative + a
  direction — high-value, rare)*
- **Paper E** — The governed composite: calibrated confidence, abstention, provenance (ENGINE, CALIB1,
  BESTINT1) — the book's binding.
- **Paper F** — The target→intervention loop and its honest ceiling: repurposing recovers known pharmacology in
  both validated arms (INTERVENE1 bacteria 9/9; INTERVENE2 cancer 10/10) but existing-drug coverage is narrow
  (bacteria 1/32 novel; cancer 6.8% drugged / 93.2% undrugged) — the F4 de-novo-chemistry ceiling, quantified.

## 6. Connected plan — what building the book requires next (ranked, evidence-based)
1. ~~**Make the router explicit (COMPOSITE1)**~~ **✅ BUILT + VERIFIED (759c8b7).** `src/intercepta/
   composite_router.py` wraps the DiscoveryEngine with an explicit transfer-condition gate. 14/14 data-free
   unit tests; reproduced ×2 (sha f8e98243). Three pre-registered routings hold: bacterium→FBA+composite
   shortlist (cores present, top-20 == committed ENGINE); virus→structural class-ID (FBA correctly NOT fired);
   **host-dependent parasite→ABSTENTION** (the decisive integrity test — refuses the wrong FBA answer). The
   spine exists. Next: as DEPEND1 (Wave 3) validates a functional-dependency signal, the router's currently
   "NOT BUILT → never fires" gate for host-embedded biology gets un-gated to that signal.
2. ~~**Wave 3 — functional-dependency layer**~~ **✅ BUILT + VERIFIED (DEPEND1, 5b3cb7a): G1/G2/G3 PASS** —
   selective dependency recovers known cancer targets (0.80), **generalizes to held-out disjoint lines** (the
   F3 gap), and a **label-free expr→dependency** arm beats baseline (the zero-data case). The signal
   host-embedded biology needs now exists and generalizes. **✅ WIRED (router v2 / COMPOSITE2, 58f9e5d):** the
   router now FIRES functional-dependency for the human/cancer class (skin→SOX10, KRAS-hotspot→KRAS, both rank
   #1; FBA gated out), while the novel parasite STILL ABSTAINS (transfer-condition-precise: no parasite screen;
   label-free not organism-transferred). 16/16 unit tests, reproduced ×2 (sha aebe8543). Remaining honest gaps:
   cell-line not clinical; parasite un-gating awaits label-free organism-transfer — **now TESTED (TRANSFER1,
   37caa0d): it does NOT transfer.** The selective-dependency signal fails organism-transfer to a zero-screen
   parasite (OR 0.90, chance); only conserved-core transfers, redundant with conservation. So the router's
   novel-parasite abstention is now **empirically justified**, not a placeholder — a genuine boundary of
   zero-data host-embedded discovery: for a novel host-embedded pathogen with no screen we can honestly offer
   only the conserved-core (via conservation, ~28% coverage), never selective targets.
3. **STRUCTREPURPOSE1** — DONE, NEGATIVE: structural repurposing validates known pharmacology (11/11) but does
   NOT expand novel coverage (promiscuity; null matched more than drug targets). Consequence: the intervention
   module honestly covers only the drugged-homolog fraction; novel-target intervention is de-novo-gated (F4),
   not repurposing-fixable — do not claim expanded coverage.
4. **Harden the frontier n>1 per class** (more viruses/fungi/parasites) so the routing table's entries are
   population-grade, not n=1 probes.
5. **Confront F3 honestly** — external replication of the human dependency layer, or downgrade the human claim.

## 7. The non-compromise line (so the book is true)
The composite's integrity IS its abstention: it must say "no validated signal for this class" (parasite today)
rather than emit a confident-looking answer. "Any disease" is delivered as **universal honest decision
coverage** — a real answer where a signal transfers, an explicit abstention where none does — never as a
universal model that pretends to fit biology it has been shown (GENERALIZE5/HOSTCTX1/2) not to fit.

**This abstention is now empirically stress-tested at the extreme (DARK1).** At the dark-proteome boundary —
proteins with no sequence homolog, no usable structure, no reference ligand (the vision's own named deepest
frontier) — the composite **abstained on 22/22 dark proteins with zero false-confident calls**, while still
firing on 20/20 analyzable controls (fail-safe *and* discriminating). Crucially, 7/22 dark proteins had an
*ungated* structural TM ≥ 0.5 to a real drugged fold — would-be false-confident calls suppressed **only** by the
pLDDT confidence gate: the abstention machinery is not decorative, it is load-bearing and it held. This is the
strongest evidence that the composite fails *safe* — it is honest at exactly the edge where a naive system would
hallucinate a target.
