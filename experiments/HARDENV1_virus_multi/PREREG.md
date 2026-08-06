# HARDENV1 — pre-registered CROSS-VIRUS structural target-class recovery (harden GENERALIZE2/3 from n=1 to n>1)

**Registered (Stage 1) BEFORE any scoring against the known drug-target answer.** The reference panel, the
per-virus leakage exclusions, the per-target correct-class ground truth, and the numeric gate below are FROZEN
before Foldseek is run/scored.

## Background (committed)
- **GENERALIZE1 (FAIL, sha d58f9e7e):** at e<=1e-5, SARS-CoV-2 proteins have ZERO non-coronaviral drugged-*sequence*
  homolog. Cross-family viral sequence identity is below detection.
- **GENERALIZE2 (PASS, sha f8f7d1be):** Foldseek-TM recovered Mpro->3C-protease and RdRp->HCV-NS5B, but only as a
  hand-picked 2-target capability test.
- **GENERALIZE3 (PASS, sha e877dcd3...):** BLIND multi-class structural screen on SARS-CoV-2: nsp5/Mpro->protease
  (TM 0.462) and nsp12/RdRp->polymerase (TM 0.473) both recovered correct class from a 31-structure, 13-class
  corona-free panel. **n=1 virus.**

## What HARDENV1 does
Tests whether blind STRUCTURAL homology recovers the correct drugged-enzyme CLASS for known clinically drugged
viral targets on **4 MORE viruses** (HIV-1, Influenza A, HCV, HSV-1), turning the n=1 SARS-CoV-2 result into n>1.
Reuses GENERALIZE3's cleaned-chain + Foldseek-TMalign approach exactly (`--alignment-type 1`, query-normalized
qtmscore, longest/target chain cleaning, standard-AA + MSE-as-MET, drop ligands/ions/waters/nucleic acids).

## FROZEN query set (viral drug targets; clinically drugged; experimental PDB) — protein : PDB(chosen chain) : correct class
- **HIV_RT**  : 1RT1 (chain A, p66, ~538 res) : **polymerase** — drugged by NRTIs/NNRTIs (zidovudine, efavirenz).
- **HIV_PR**  : 1HXW (chain A, ~99 res)        : **protease** (aspartic) — protease inhibitors (ritonavir, in 1HXW).
- **HIV_IN**  : 1ITG (chain A, catalytic core, ~142 res) : **nuclease** (RNase-H-like/DDE) — INSTIs (raltegravir, dolutegravir).
- **FLU_NA**  : 2HU4 (chain A, head, ~385 res) : **glycosidase** (sialidase) — oseltamivir, zanamivir.
- **FLU_PA**  : 4AWM (chain A, endonuclease domain, ~178 res) : **nuclease** (PD-(D/E)xK) — baloxavir marboxil.
- **HCV_NS3** : 1A1R (chain B, protease domain, ~179 res) : **protease** (chymotrypsin-like serine) — grazoprevir/glecaprevir.
- **HCV_NS5B**: 4WTG (chain A, ~535 res)        : **polymerase** — sofosbuvir, dasabuvir.
- **HSV_TK**  : 2KI5 (chain B, ~308 res)        : **kinase** (P-loop NMP/nucleoside kinase) — activates acyclovir/ganciclovir.
- **HSV_POL** : 2GV9 (chain B, ~1035 res)       : **polymerase** (B-family) — acyclovir-TP / foscarnet target.

Cleaning rule (fixed): for BOTH queries and references, keep the SINGLE LONGEST protein chain (most CA residues;
standard AAs + MSE->MET; drop all other chains/ligands/ions/waters/nucleic acids). Verified above that the longest
protein chain is the target enzyme in every query PDB (e.g. 1RT1 A = catalytic p66; 1A1R B = NS3 protease, the
short NS4A cofactor peptides are dropped).

## FROZEN reference panel (37 structures, 14 classes) = GENERALIZE3's 31 + 6 additions
Base 31 (GENERALIZE3, unchanged): proteases 4cha,1ppb,1cqq,9pap,1hxw,1tlp; polymerases 4wtg,3hvt,1kln;
kinases 1m17,1hck,1atp,2src; gpcrs 2rh1,1f88,3eml; reductases 1rx2,1hw9; methyltransferases 1vid,2adm;
nuclear_receptors 1err,2prg,1e3g; ion_channel 1bl8; nucleases 7rsa,1rnb; helicases 1pjr,3pjr; lyase 2cba;
esterase 1acj; phosphatase 2hnp.
**6 additions (to guarantee each test target has a plausible SAME-FOLD, DIFFERENT-FAMILY correct-class analog):**
- **2sil** — *bacterial (Salmonella) sialidase* : **glycosidase** (new class; six-bladed beta-propeller, the fold of
  influenza NA — cross-family analog for FLU_NA).
- **4pep** — *pepsin* : **protease** (aspartic; non-viral aspartic-protease analog for HIV_PR).
- **2ren** — *renin* : **protease** (aspartic; drugged by aliskiren; 2nd non-viral aspartic analog for HIV_PR).
- **1rve** — *EcoRV restriction endonuclease* : **nuclease** (PD-(D/E)xK fold — analog for FLU_PA).
- **2rn2** — *E. coli RNase H* : **nuclease** (RNase-H fold — analog for HIV_IN).
- **4ake** — *adenylate kinase* : **kinase** (P-loop NMP-kinase fold — analog for HSV_TK).
The panel spans 14 classes; each target must WIN its correct class against ~13 off-class distractors — a genuine
multi-class discrimination, not a 2-way default.

## LEAKAGE CONTROL (mandatory, per virus; FROZEN)
Each reference carries a viral-family tag. When testing a virus, ALL references whose family == the test virus's
family are EXCLUDED from that query's ranking, so a recovery is genuine CROSS-FAMILY structural transfer, never a
self-match. Family tags on viral refs: 1cqq=picornavirus, 1hxw=retrovirus, 3hvt=retrovirus, 4wtg=flavivirus
(all other refs = nonviral). Exclusions applied:
- **HIV-1** targets (retrovirus): exclude {1hxw (HIV protease), 3hvt (HIV RT)}. (Note 1HXW & 4WTG double as query
  structures; family exclusion also removes any exact self-structure.)
- **HCV** targets (flavivirus): exclude {4wtg (HCV NS5B)}.
- **Influenza A** targets (orthomyxovirus): exclude {} (none in panel).
- **HSV-1** targets (herpesvirus): exclude {} (none in panel).
After exclusion, every target still retains >=1 correct-class analog from a different family (e.g. HIV_RT keeps
HCV-NS5B + Klenow polymerases; HCV_NS5B keeps HIV-RT + Klenow; HCV_NS3 keeps chymotrypsin/thrombin serine proteases).

## PRE-REGISTERED GATE (frozen before scoring)
For each target t: best hit = the retained (non-excluded) reference with max qtmscore; its class = predicted class.
- **Per-target RECOVER(t)** := (predicted_class(t) == correct_class(t)) AND (best qtmscore >= **0.40**)  [same bar as G2/G3].
- **Off-class win margin(t)** := best qtmscore among correct-class refs  minus  best qtmscore among off-class refs
  (positive => the correct class genuinely wins, not just clears 0.40).
- **Aggregate recovery fraction** := (# targets with RECOVER==True) / (# targets, =9).
- **Random/off-class baseline**: a target picking a class at random from the 14 panel classes recovers correct
  class with probability ~1/14 = 0.071; the gate must beat this by a wide margin.
- **PASS** (hardens cross-virus generality) <=> aggregate recovery fraction > 0.5 (majority of the 9 targets recover)
  AND at least 3 of the 4 viruses have >=1 target that recovers correct class.
- **PARTIAL** <=> some targets recover but not a majority, or fewer than 3 viruses carry a recovery.
- **NEGATIVE** <=> recovery at/near the random baseline (<=1/9 targets) — reported first-class, not re-run.

## Disclosed confounds (fixed)
1. **qtmscore is query-length-normalized** (identical to G2/G3). Very large multidomain queries score low even with a
   real domain match — **HSV_POL (~1035 res)** is expected to be at high risk of a size-driven sub-0.40 miss (the
   same effect that sank SARS-CoV-2 spike in G3). Reported honestly as-is, not upgraded.
2. In-silico structural class-ID on EXPERIMENTAL structures; **not wet-lab**; establishes cross-virus generality
   (or its limit) of the structural signal, not a deployed pipeline.
3. Class labels are COARSE functional classes (as in G3: "protease" spans serine/cysteine/aspartic/metallo). A hit
   to any protease counts as protease-class-correct.
4. Recovery is scored only on targets with a usable experimental structure (all 9 confirmed downloadable/cleanable).

## What PASS / PARTIAL / NEGATIVE mean
PASS = blind structural homology recovers the correct drugged class for a MAJORITY of known viral drug targets across
>=3 additional viruses, above a broad multi-class off-class baseline and with leakage-excluded same-family analogs —
GENERALIZE3's SARS-CoV-2 result is not a one-off; the structural bridge is a CROSS-VIRUS property. PARTIAL/NEGATIVE =
the signal is virus/target-specific or weaker than G3 implied — honest boundary of cross-virus generality.
