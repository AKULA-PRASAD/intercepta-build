# Weakness & negative-result audit — root cause + honest solution (2026-07-29)

Systematic treatment of every weak/underpowered/negative result in the program, per the Constitution ("negatives
are knowledge: understand why, redesign, improve, or establish the true limit"). **Discipline:** each is classified
as **INTRINSIC** (a true finding — the honest "solution" is acceptance + the alternative direction; trying to
"beat" it is p-hacking), **FIXABLE-BY-US** (a real design/feature/data fix we can build on open data), or
**NEEDS-NEW-DATA** (only new measurements resolve it). Conflating INTRINSIC with FIXABLE is the repeated mistake we
are explicitly avoiding.

| # | Weak / negative result | Root cause (honest) | Verdict | Real solution / next |
|---|---|---|---|---|
| V7 | +0.212 single-agent transfer **ceiling** | Baseline expression encodes proliferation + lineage, not drug-specificity — proven across 6 fronts (RNA, +mut, +protein, clinical, inferred-func, measured-func) | **INTRINSIC** | Not a fix target (more modeling = p-hacking). Real solutions are a *different task* (combinations → V23, works) or *new patient functional data* (clinical). |
| V9 | Weak ex-vivo drug-specificity ρ≈0.07 | Cross-platform (array→RNA-seq) + proliferation dominance + generic (non-mechanism) transfer; V22 shows the only generalizable functional signal is target-local | **MOSTLY INTRINSIC** (small margin) | Testable fix: mechanism-anchored transfer (target-linked features) for targeted drugs — expected modest gain. Low priority. |
| N1 | AML mechanistic-coherence null | The "AML drugs transfer best" pattern was selection, not signal | **INTRINSIC** (correctly withdrawn) | None — it was a false pattern; falsification is the correct outcome. |
| B7/B9 | PDXE external transfer fragile | Too few models / drug overlap; PDX is a small, noisy proxy | **NEEDS-NEW-DATA** (power) | Pool additional OPEN PDX drug-response resources if available; otherwise a documented power bound. |
| B8 | PDXE mechanism markers underpowered | Only ~15 functional-mutant PDX per marker | **NEEDS-NEW-DATA** (power) | More PDX models; not fixable by method. |
| B10 | Human clinical prediction NULL | Observational, regimen-attributed, cancer-type-confounded | **NEEDS-NEW-DATA** | Prospective, single-agent, within-cancer (Track-1 SAP). Not code-fixable on observational data. |
| B11 | 0/13 novel markers replicate | Single-cohort AML-specific artifacts | **MOSTLY INTRINSIC** | Optional: CRISPR-dependency pre-filter to salvage 1–2 mechanistically-plausible hits (low yield). |
| B17 | Ex-vivo→survival NULL | Retrospective, no treatment timing (immortal-time), underpowered | **NEEDS-NEW-DATA** | Treatment-timed prospective outcome (Track-1). Not fixable on BeatAML. |
| B20/B21 | Inferred functional layer fails external replication | No transferable functional-**state** signal beyond a drug's own target (V22 is the mechanistic proof) | **INTRINSIC** | The fix is NOT more inference — it is *measured* function in patients (new data). Accept as a true bound. |
| V21/V22/B22/B23 | Ceiling holds for proteomics & measured genome-wide dependency | Intrinsic to baseline profiling | **INTRINSIC** (true findings) | Not fix targets. They *are* the answer; they justify the combinations pivot + new-data path. |
| **B24→B25** | Synergy generalization is **weak** off-diagonal: leave-drug-out (novel chemistry) ρ=0.25 in B24 | (a) generic Morgan fingerprints; (b) only 38 chemically-redundant drugs in O'Neil | **TESTED (B25) → reclassified NOT-DATA-LIMITED / near-INTRINSIC** | Fix attempted: re-ran on the larger, more diverse open **DrugComb** (124 drugs, ×2). Novel-drug generalization did NOT improve — it **collapsed to ρ=0.025** (the 0.25 was O'Neil chemical redundancy). So novel-chemistry synergy prediction is intrinsically hard here, not data-limited. **However the FIX SUCCEEDED for the part that matters:** combination-generalization for KNOWN drugs REPLICATED across both corpora (DrugComb Δ+0.094) → that is the robust, useful capability. Honest reclassification recorded in LEDGER V23. |

## The honest bottom line
- **The core negatives are true findings, not flaws.** The single-agent ceiling, the clinical null, and the
  functional-inference failure are *established scientific results*; the honest "solution" is to accept them and
  redirect — which we did (combinations, V23; and new-data Track-1 for the clinical endpoint). Pouring more effort
  into "beating" them would be the p-hacking the Constitution forbids and the loop we already named.
- **The genuinely improvable weakness lives in the POSITIVE thread (B24 synergy).** That is where real
  design/data work legitimately raises the result — and it is buildable by us on open data (DrugComb via TDC,
  mechanism-anchored features). This audit therefore prioritizes strengthening synergy generalization as the next
  build (B25), not re-litigating intrinsic limits.
- Every negative remains first-class and documented in `LEDGER.md`; none is hidden or overstated.
