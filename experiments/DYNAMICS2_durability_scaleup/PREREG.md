# DYNAMICS2 — Firming up (or bounding) the contact-residue durability signal by EXPANDING n (PRE-REGISTRATION)

**Frozen BEFORE any ESM scoring of the expanded set.** Author: DYNAMICS2 module. Env: miniforge
`intercepta` (torch + transformers, CPU-only, offline HF cache). Zero budget. Data →
`$INTERCEPTA_DATA/dynamics2/`; NEVER committed. NEVER git commit.

## What this is (and is NOT)
DYNAMICS1 (PASS, reproduced x2, sha `fb6984c0…`) found that **mean ESM-2 masked-marginal Shannon
entropy over drug-CONTACT residues** separates HIGH- vs LOW-resistance-liability targets at
**AUROC 0.839 / MWU p 0.029 (n=15, 7 HIGH/8 LOW)** — but the significance was **n-FRAGILE**
(drop-substrate p 0.051; clinical-drug-only 7H/3L p 0.117). DYNAMICS2 is a genuine
**out-of-(original-)sample robustness test**: the SCORING METHOD IS FROZEN (DYNAMICS1's exact
pipeline and code, reused verbatim); the ONLY thing that changes is that the labeled target set is
EXPANDED (n≥25, more balanced, and BROADENED beyond antibacterial to antiviral/antifungal). This is
NOT tuning. If adding cross-drug-class targets DROPS the AUROC, that is a real generalization bound
and is reported as such. No inconvenient target is dropped to preserve significance.

## THE FROZEN METHOD (verbatim from DYNAMICS1 — NOT changed here)
- Structure = a drug-BOUND experimental PDB (mmCIF from RCSB). Drug-CONTACT residue = protein
  residue with any heavy atom within **4.5 Å** of any heavy atom of the frozen ligand CCD.
- Contact parsing: `_atom_site` from mmCIF; heavy atoms only (drop H/D); first altloc only; protein
  residue = standard AA or a mapped modified residue **using DYNAMICS1's exact AAMAP** (MSE→M,
  KCX→K, …; residues NOT in that map are omitted as gaps — unchanged frozen behavior). Scoring chain
  = the single `label_asym_id` with the most contact residues (ties → lexicographic). Chain ESM
  sequence = its modelled residues ordered by `label_seq_id` (unmodelled/unmapped gaps omitted).
- Metric = `facebook/esm2_t30_150M_UR50D` (cached), CPU, eval, `torch.manual_seed(0)`, float32,
  window 1022 centred on median contact if len>1022. **Per-contact tolerance = masked-marginal
  Shannon entropy over the 20 canonical AA (nats).** **Target feature = MEAN entropy over the
  target's contact residues** (higher = more mutationally tolerant = more resistance-liable). This is
  the PRIMARY score. Secondary (reported, not gated): MAX contact entropy; mean substitution-LLR.
- The extraction + ESM code is copied byte-for-byte from `DYNAMICS1/run.py` (same functions
  `parse_atoms`, `extract_contacts`, `masked_marginal`). The metric is NOT touched.

## EXPANDED, REAL, CITED, LABELED TARGET SET (n = 26; 14 HIGH / 12 LOW)
Labels are the held-out truth; the model input is ONLY structure + protein sequence (NO
resistance-rate/MIC used as input). DYNAMICS1's 15 targets are REUSED VERBATIM and NOT relabeled.

### REUSED from DYNAMICS1 (15; 7 HIGH / 8 LOW) — labels + citations in AMR1 `ground_truth.json`
HIGH: rpoB(1I6V/RFP), gyrA(2XCT/CPF), parC(3RAE/LFX), rpsL(1FJG/SRY), inhA(1ZID/ZID),
embB(7BVF/95E), folP(1AJ0/SAN). LOW: murA(1UAE/FFQ), dxr(1ONP/FOM), alr(1EPV/DCS),
ddlB(2DLN/PHY,inhibitor), mraY(5CKR/57M,inhibitor), murF(2AM1/1LG,inhibitor),
murG(1NLM/UD1,substrate), murB(2MBR/EPU,substrate).

### NEW additions (11; 7 HIGH / 4 LOW) — each: PDB verified to contain the named drug ligand (CIF
`_struct.title` + ligand-atom check), each label a REAL cited source. Feasibility (contacts
assignable + resistance residue present) resolved in FEASIBILITY.md BEFORE this scoring.

| gene / target | organism | drug (ligand CCD) | PDB | ligtype | label | key resistance residue(s) — present as contact? | citation |
|---|---|---|---|---|---|---|---|
| HIV-1 reverse transcriptase (NNRTI site) | HIV-1 | nevirapine (NVP) | 1VRT | drug | HIGH | K103,Y181,Y188,L100,G190 — YES | Wensing2019; MenendezArias2013 |
| HIV-1 protease | HIV-1 | nelfinavir (1UN) | 1OHR | drug | HIGH | D30,V82,I84 — YES (D30N single-step) | Wensing2019; StanfordHIVDB |
| Influenza A N1 neuraminidase | H5N1/pdm | oseltamivir carboxylate (G39) | 2HU4 | drug | HIGH | R292,N294 (H274-region) — YES | Moscona2005; WHO_flu |
| HCV NS3/4A protease | HCV gt1 | telaprevir (SV6) | 3SV6 | drug | HIGH | R155,A156,D168 — YES (exact triad) | SarrazinZeuzem2010 |
| Sterol 14α-demethylase CYP51/Erg11 | Candida albicans | posaconazole (X2N) | 5FSA | drug | HIGH | Y132,F126 — YES | Flowers2015; Sagatova2015 |
| Influenza A PA endonuclease | H1N1pdm | baloxavir acid (E4Z) | 6FS6 | drug | HIGH | I38 — YES (exact baloxavir I38T residue) | Omoto2018 |
| HSV-1 thymidine kinase | HSV-1 | ganciclovir (GA2) | 1KI2 | drug | HIGH | Q125,R163,A168 — YES | PiretBoivin2011 |
| HCV NS5B RNA polymerase | HCV gt2a | sofosbuvir active-metabolite diphosphate (6GS) | 4WTG | drug | LOW | S282 — YES (S282T rare & unfit) | Sofia2010; Svarovskaia2014 |
| MurD (UDP-MurNAc-L-Ala:D-Glu ligase) | E. coli | UDP-MurNAc-Ala substrate (UMA) | 3UAG | substrate | LOW | — (undrugged durable core) | Bugg2011; Barreteau2008 |
| MurE (UDP-MurNAc-tripeptide synthetase) | E. coli | UDP-MurNAc-tripeptide (UAG) | 1E8C | substrate | LOW | — (undrugged durable core) | Bugg2011; Barreteau2008 |
| GlmU (bifunctional GlcN-1-P acetyltransf./uridylyltransf.) | E. coli | UDP-GlcNAc substrate (UD1) | 1HV9 | substrate | LOW | — (undrugged durable core) | Bugg2011; Barreteau2008 |

### Citations (REAL sources for the NEW labels)
- Wensing AM, et al. 2019 Update of the Drug Resistance Mutations in HIV-1. Top Antivir Med. 2019;27(3):111-121.
- Menéndez-Arias L. Molecular basis of HIV-1 drug resistance. Antiviral Res. 2013;98(1):93-120.
- Rhee SY, et al. Human immunodeficiency virus reverse transcriptase and protease sequence database (Stanford HIVDB). Nucleic Acids Res. 2003;31(1):298-303.
- Moscona A. Oseltamivir resistance—disabling our influenza defenses. N Engl J Med. 2005;353(25):2633-2636.
- WHO. Summary of influenza antiviral susceptibility surveillance (H274Y/E119V/R292K/N294S neuraminidase resistance).
- Sarrazin C, Zeuzem S. Resistance to direct antiviral agents in patients with HCV infection. Gastroenterology. 2010;138(2):447-462.
- Flowers SA, et al. Contribution of clinically derived mutations in ERG11 to azole resistance in Candida albicans. Antimicrob Agents Chemother. 2015;59(1):450-460.
- Sagatova AA, et al. Structural insights into binding of the antifungal drug fluconazole/azoles to Candida albicans CYP51. Antimicrob Agents Chemother. 2015;59(8):4982-4989.
- Omoto S, et al. Characterization of influenza virus variants induced by treatment with the endonuclease inhibitor baloxavir marboxil. Sci Rep. 2018;8:9633.
- Piret J, Boivin G. Resistance of herpes simplex viruses to nucleoside analogues. Antimicrob Agents Chemother. 2011;55(2):459-472.
- Sofia MJ, et al. Discovery of the nucleotide prodrug PSI-7977 (sofosbuvir) for HCV. J Med Chem. 2010;53(19):7202-7218.
- Svarovskaia ES, et al. Infrequent development of resistance in genotype 1-6 HCV patients treated with sofosbuvir. Clin Infect Dis. 2014;59(12):1666-1674.
- Bugg TDH, Braddick D, Dowson CG, Roper DI. Bacterial cell wall assembly: still an attractive antibacterial target. Trends Biotechnol. 2011;29(4):167-173.
- Barreteau H, et al. Cytoplasmic steps of peptidoglycan biosynthesis. FEMS Microbiol Rev. 2008;32(2):168-207.

## PRE-REGISTERED HYPOTHESIS, GATE & VERDICT LADDER (frozen BEFORE scoring the expanded set)
**H1 (frozen):** mean drug-contact-residue masked-marginal entropy separates HIGH from LOW, in the
direction higher-entropy → HIGH, and this holds at the larger n.
**Primary metric:** AUROC(mean-contact-entropy vs HIGH=1) over ALL 26 targets; two-sided Mann-Whitney U p.

**FIRMED-UP (the goal):** at n≥25, **AUROC ≥ 0.75 AND MWU p < 0.01** (a firmer bar than DYNAMICS1's
0.05 — i.e. significance is no longer n-fragile) **AND the signal generalizes**: antibacterial-only
subset still AUROC ≥ 0.75, and the added antiviral/antifungal HIGH targets are not systematically
low-entropy (cross-class does not collapse the signal).
**PARTIAL:** AUROC holds (~0.75–0.86) but MWU p stays in [0.01, 0.05) — a real effect, still n-limited.
**NEGATIVE (first-class success):** signal WEAKENS — full-set AUROC < 0.75, OR the AUROC drops toward
chance when cross-class targets are added (⇒ DYNAMICS1 was small-n / antibacterial-specific optimism,
reported honestly).

## MANDATORY PRE-REGISTERED ANALYSES (reported regardless of verdict; no post-hoc subset selection)
1. **PRIMARY** — full 26 (14H/12L): AUROC + MWU p. Explicit contrast vs DYNAMICS1 (0.839/0.029, n=15)
   and AMR1 whole-protein (0.556/0.74).
2. **Per-drug-class stability:** (a) antibacterial-only (18: 7H/11L); (b) non-antibacterial cross-class
   only (8: 7H/1L — antiviral+antifungal; AUROC + descriptive, MWU under-powered by construction);
   (c) new-targets-only pure out-of-sample (11: 7H/4L).
3. **Confound controls (the honest tests):** (d) no-substrate — drop all 5 substrate-bound
   (murG,murB,MurD,MurE,GlmU) → 21 (14H/7L); (e) clinical-drug-bound-only — keep ligtype='drug' only
   → 18 (14H/4L). These control the pre-known LOW-class enrichment for catalytically-constrained
   substrate-bound cores (guaranteed low entropy). If the signal survives ONLY with substrate padding,
   the verdict is at best PARTIAL/weakened.
4. **Re-derivation check:** DYNAMICS1's exact 15 recomputed under DYNAMICS2 code must reproduce
   AUROC 0.839 / p 0.029 (independent confirmation the frozen metric is unchanged).
5. Secondary metrics (MAX-entropy AUROC, substitution-LLR AUROC) on the full 26.
6. Per-target mean/max contact entropy, n_contacts; mechanistic residues: NA H274-region, NS3 R155,
   PA I38, NS5B S282, rpsL K43-equivalent.

## Reproducibility
SHA-256 over sorted-key JSON of the `payload` (per-target features + all AUROC/p), EXCLUDING
verdict/provenance/runtime. Entropies rounded to 6 decimals. Structures + ESM logits cached under
`$INTERCEPTA_DATA/dynamics2/`. Run twice → require BYTE-IDENTICAL. No git commit; no data committed.

## HONEST SCOPE (binds the result BEFORE it is known — carried from DYNAMICS1 + new)
- ESM masked-marginal entropy is a **PLM proxy** for mutational tolerance, NOT measured fitness.
- A single **static** structure's contacts miss induced-fit / allosteric / **efflux** / target-bypass /
  prodrug-activator-loss resistance (that is why activator-only targets katG,pncA remain excluded).
- **Curated labels**; resistance liability is graded, binarized here — a defensible ordinal collapse.
- **LOW-class confound (pre-declared, worsened by the 3 new bacterial cores):** LOW is enriched for
  substrate/inhibitor-bound catalytically-constrained cores whose contacts are low-entropy BY
  CONSTRUCTION and are "durable" partly because UNDRUGGED / low clinical exposure. The confound-control
  subsets (3d, 3e) are the honest arbiters.
- **Cross-class is HIGH-skewed (7H/1L):** clinically-worrying antiviral/antifungal resistance targets
  are predominantly HIGH-liability; the one clear durable antiviral protein target with a drug-bound
  active-site structure (NS5B/sofosbuvir) is included. This asymmetry is real biology, reported openly.
- **4WTG caveat:** the only sofosbuvir-nucleotide-in-active-site NS5B structure is a crystallization
  construct (engineered S15G/E86Q/E87Q/C223H/V321I + Δ8 β-hairpin); one contact (223) is an engineered
  His, but the durability residue S282 and the catalytic GDD (D318/D319/D220) are WT and present.
- Not tuned to pass; if it fails the gate, the NEGATIVE / generalization-bound is the result.
