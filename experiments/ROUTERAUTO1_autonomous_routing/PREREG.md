# ROUTERAUTO1 — PRE-REGISTRATION (frozen BEFORE evaluation)

**Build:** an AUTONOMOUS biology-class detector that classifies a raw input into the composite router's routing
class from OBJECTIVE, computable features — completing manuscript **limitation 12** ("the composite router's
class detector is minimal … the class is currently HAND-SPECIFIED"). The detector is a pure FRONT-END: it
selects the class, then the UNCHANGED COMPOSITE1/2/3 transfer-gate logic fires exactly what was validated for
that class. It must NOT change any committed routing verdict, and it does NOT attempt to predict a-priori
whether a signal will transfer for a novel organism (that stays the capped/flagged COMPOSITE3 uncertainty).

## 0. Integrity constraints (self-imposed)
- Deterministic, no RNG, CPU-only, zero budget, open data; NO data committed; NO git commit/push.
- The detector has **ZERO fitted parameters**. Every rule/threshold is derived from biology and stated HERE,
  before any label is scored. Because nothing is fitted to the evaluation organisms, **leave-one-out ==
  full evaluation** (no train/test leakage is possible). No threshold is tuned to the labels.
- Reproduce the metrics payload x2 BYTE-IDENTICAL (SHA-256 over sorted-key JSON, provenance excluded).

## 1. Input
`ProteomeFeatures` (objective, each computable from a proteome by a cited method) + descriptors:
`n_proteins`, `has_translation_machinery` (ribosomal proteins + aaRS present ⇒ a self-translating cell),
`domain_of_life` ∈ {bacteria, archaea, eukaryota} (universal marker genes), `has_viral_hallmark`
(polyprotein/capsid/conserved drugged viral fold), `has_analyzable_structure` (≥1 pLDDT-confident fold homolog,
DARK1), `is_human_proteome`; DECLARED `host_dependent` (metabolic host-embeddedness — NOT sequence-derivable);
DATA `has_curated_gem`, `has_dependency_screen`.

## 2. Pre-registered detection rules (ordered; first match wins)
- **R0** declared class wins (backward compatible with the hand-specified path).
- **R1 VIRUS** ⇔ `n_proteins ≤ 60` **AND** `has_translation_machinery is False` **AND** `has_viral_hallmark
  is True`. *Tiny-alone is NOT enough* — the minimal detector's `size≤60 ⇒ VIRUS` rule would mis-fire on a
  small DARK-protein set; requiring a positive viral hallmark is the fix. (viral = tiny + acellular + hallmark)
- **R2 HUMAN_CANCER** ⇔ `is_human_proteome is True` **AND** `has_dependency_screen is True`.
  - **R2b** human but NO screen ⇒ ABSTAIN (require `has_dependency_screen`): DEPEND1/COMPOSITE2 is
    data-dependent; without a screen no signal transfers.
- **R3 CELLULAR** (`has_translation_machinery is True`), branch on `domain_of_life`:
  - **R3a** bacteria ⇒ BACTERIUM; **R3b** archaea ⇒ ARCHAEON (BLIND6 route);
  - **R3c** eukaryota: host_dependent True ⇒ HOST_DEPENDENT_PARASITE; False ⇒ FREE_EUKARYOTE; **None ⇒
    ABSTAIN** (require `host_dependent`) — free-living vs host-embedded is NOT sequence-derivable.
  - **R3d** cellular but domain unresolved ⇒ ABSTAIN (require `domain_of_life`).
- **R4 DARK/UNSUPPORTED** ⇒ ABSTAIN — no positive class marker fired (fail-safe; DARK1).

Class→signal firing is the UNCHANGED router gate: BACTERIUM/ARCHAEON/FREE_EUKARYOTE ⇒ FBA(+conservation)
full-grade shortlist; VIRUS ⇒ structural class-ID; HUMAN_CANCER ⇒ functional-dependency; HOST_DEPENDENT_PARASITE
⇒ FBA capped+flagged IF a curated GEM exists else abstain; UNKNOWN ⇒ abstain. (ARCHAEON is newly added to the
FBA/conservation full-grade domain — evidence: BLIND6 M. maripaludis curated iMR539, prospective-blind
git-committed-before-reveal, FBA-essentiality PASS OR 4.23. Additive; changes no prior committed verdict.)

## 3. Evaluation panel (every committed organism the arc has a signal-outcome for)
Bacteria (6): E. coli (VAL-ESS), K. pneumoniae (CROSSVAL/VAL-ESS-KP), N. gonorrhoeae (BLIND1), C. jejuni
(BLIND2), B. theta (BLIND3), S. pneumoniae (BLIND4). Archaeon (1): M. maripaludis (BLIND6). Free-living
eukaryote (3): K. phaffii (BLIND5), C. albicans (HARDENF1), S. cerevisiae (GENERALIZE4). Host-dependent
parasites (3): Toxoplasma (HARDENP1, curated GEM), Plasmodium (GENERALIZE5, curated GEM), T. brucei (BLIND7,
only a sparse de-novo carve — **no curated GEM**). Viruses (5): SARS-CoV-2, HIV, Influenza, HCV, HSV
(GENERALIZE3 + HARDENV1). Human cancer (1): melanoma/DepMap (DEPEND1). **FAIL-SAFE (2, hard):** DARK proteins
(DARK1) and a NOVEL zero-screen host-dependent parasite (TRANSFER1). Total = 21 inputs.

**"Empirically-correct" routing** = the class that routes to the signal that actually PASSED / correctly
abstained. Note (stated before scoring): for a FULL-GRADE class the correct routing is to FIRE the class
signal; the a-posteriori gate pass/fail of one particular GEM is NOT a routing error (consistent with
COMPOSITE3 firing Plasmodium capped though it a-posteriori failed). So S. pneumoniae (BLIND4 sub-threshold),
Plasmodium (noise-floor FAIL) still route correctly (fire the class signal, capped where COMPOSITE3 caps).
T. brucei has NO curated GEM ⇒ its correct route is ABSTAIN (the genuine-null reach-limit → fail safe).

## 4. Pre-registered SUCCESS GATES
- **G-CLEAR:** 100% of the 19 clear (non-fail-safe) inputs are detected into the correct class AND produce the
  correct fire/abstain (correct output_type; the empirically-correct discovery signal in `signals_fired`, or
  empty on a correct abstention).
- **G-FAILSAFE (HARD):** 100% of the 2 fail-safe inputs (DARK proteins; novel zero-screen parasite) ABSTAIN
  with ZERO signals fired. A single mis-fire on a fail-safe case = a HARD FAIL of the whole experiment.
- **G-NOREG:** the full existing pytest suite still passes (no committed routing verdict changed).
- **OVERALL PASS ⇔ G-CLEAR ∧ G-FAILSAFE ∧ G-NOREG.**

## 5. Honestly reported boundaries (integrity over coverage)
The detector ABSTAINS rather than guess on: eukaryote free-living-vs-host-dependent without the declared flag;
a human proteome without a dependency screen; a cellular input with an unresolved domain marker; any input with
no positive class marker (dark). These abstentions are counted as CORRECT only where abstention is the honest
answer; they are reported as boundaries, not hidden.

## 6. Scope
Automates class-detection + routing only. Does NOT predict a-priori signal transfer for a novel organism
(capped/flagged per COMPOSITE3). Outputs are confidence-tiered candidate HYPOTHESES, not validated drug targets,
not wet-lab, not clinical.
