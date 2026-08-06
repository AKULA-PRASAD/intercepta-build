"""INTERCEPTA COMPOSITE1 — the explicit biology-class-aware ROUTER around the validated DiscoveryEngine.

The DiscoveryEngine (discovery_engine.py) is the already-validated GOVERNED COMPOSITE: it z-scores + tier-weights
the registered signals, hard-filters unsafe targets, calibrates confidence, and abstains per-entity. What it does
NOT do is decide WHICH validated signal is even *allowed to transfer* to a given biology class. That decision is
the whole point of COMPOSITE1 and the north-star's honest "any disease": apply the signal that is KNOWN to
transfer to the input's biology, and ABSTAIN at the CLASS level where none does — rather than forcing a bacterial
metabolic model onto a parasite it has been experimentally shown (GENERALIZE5/HOSTCTX1/2) not to fit.

**The router's integrity IS its abstention.** It encodes the evidence-derived transfer-condition table
(COMPOSITE_ARCHITECTURE.md §2; the LEDGER) as an explicit gate, checks which conditions hold for the input class,
composes ONLY those signals through the DiscoveryEngine, and returns either a confidence-tiered shortlist OR an
explicit class-level abstention object.

Transfer-condition table AS IMPLEMENTED (each cell cites the committed experiment that established it):
  * FBA gene-ESSENTIALITY   — domain = a SELF-CONTAINED metabolism captured by a quality GEM.
        VERIFIED for free-living bacteria (MET1-3, VAL-ESS, CROSSVAL, BLIND1; OR 5-64).
        VERIFIED-weaker for a free-living eukaryote/yeast (GENERALIZE4, OR 4.65).
        **OUT OF DOMAIN for host-dependent organisms** — GENERALIZE5 (malaria OR 2.47, sub-threshold) +
        HOSTCTX1 (E-Flux negative) + HOSTCTX2 (boundary-curation negative) FALSIFIED it: host-salvage metabolism
        makes the GEM over-permissive. The router MUST NOT apply FBA as a confident signal to a host-dependent
        organism. Not applicable to viruses (no metabolism).
  * STRUCTURAL homology (Foldseek TM) for target CLASS-ID — domain = a 3D structure exists / the fold is
        conserved with a known drugged fold. VERIFIED for viruses (GENERALIZE2/3: Mpro->protease, RdRp->
        polymerase, blind, TM 0.46-0.47); also FOLD1 for phylogenetically-isolated bacteria.
  * SEQUENCE / structural REPURPOSING — VALIDATION-grade ONLY (recovers KNOWN pharmacology; INTERVENE1 9/9).
        STRUCTREPURPOSE1 showed structure does NOT expand novel coverage (a random-protein null matched MORE
        targets than drug targets — fold-census promiscuity). So repurposing NEVER fires as a novel-coverage /
        discovery signal, in any class. No "expanded coverage" claim.
  * FUNCTIONAL-DEPENDENCY layer (context-specific CRISPR/knockout fitness) — the validated signal that
        host-embedded biology (parasite -> intracellular -> human/cancer) actually needs (FAILURE_AUDIT F2<->F3).
        **COMPOSITE2: NOW BUILT + VALIDATED for HUMAN_CANCER** (DEPEND1 G1/G2/G3 PASS on DepMap: selective
        dependency recovers known cancer targets 0.80, generalizes to held-out disjoint cell lines 0.80, and a
        label-free expr->dep arm beats baseline rho 0.36; reproduced x2). Its transfer condition is
        DATA-DEPENDENT: it fires for HUMAN_CANCER (dependency data / same-domain label-free map exists) and
        returns a selective-dependency shortlist. It does NOT fire for a HOST_DEPENDENT_PARASITE (no parasite
        screen; label-free arm validated on held-out DepMap HUMAN lines, NOT organism-transferred) -> the
        parasite STILL ABSTAINS. Honest bound: cancer CELL-LINE dependency, not patient/clinical.
  * CONSERVATION-BREADTH (REACH1) and HOST-SAFETY hard filter (FRONT1/E2E2) are supporting signals that ride the
        same metabolism/conservation invariants; they compose alongside FBA for the bacterial/eukaryote classes.

HONEST SCOPE: the class detector is deliberately MINIMAL (virus auto-detected by tiny proteome; host-dependence
is NOT sequence-derivable so it is a DECLARED flag). The integrity is in the transfer-gate + abstention, not in a
perfect classifier. The bacterial case reuses the already-validated DiscoveryEngine machinery — this is honest
COMPOSITION of validated parts, not new biology. Outputs are confidence-tiered candidate HYPOTHESES, not
validated drug targets and not wet-lab.

This module's DECISION logic (`decide`, `detect_class`, the gate table) is pure-Python and DATA-FREE
unit-testable; the heavy DiscoveryEngine invocation is lazily imported only on the execution path.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


# ======================================================================================================
# Biology classes and signals
# ======================================================================================================
class BiologyClass(str, Enum):
    BACTERIUM = "bacterium"                          # free-living bacterium
    FREE_EUKARYOTE = "free_eukaryote"                # free-living eukaryote / fungus (e.g. yeast)
    VIRUS = "virus"                                  # no metabolism
    HOST_DEPENDENT_PARASITE = "host_dependent_parasite"  # e.g. Plasmodium (host-embedded metabolism)
    HUMAN_CANCER = "human_cancer"                    # host cell / oncology
    UNKNOWN = "unknown"


class Signal(str, Enum):
    FBA_ESSENTIALITY = "fba_essentiality"
    STRUCTURAL_HOMOLOGY = "structural_homology"      # Foldseek TM -> target CLASS-ID
    SEQUENCE_REPURPOSING = "sequence_repurposing"    # validation-grade ONLY (never a discovery signal)
    FUNCTIONAL_DEPENDENCY = "functional_dependency"  # NOT BUILT YET
    CONSERVATION_BREADTH = "conservation_breadth"    # supporting
    HOST_SAFETY = "host_safety"                      # supporting (hard filter)


@dataclass(frozen=True)
class SignalSpec:
    """Encodes ONE signal's evidence-derived transfer condition."""
    signal: Signal
    domain: frozenset            # classes where the transfer condition is VALIDATED to hold
    built: bool                  # is the module actually implemented?
    discovery_grade: bool        # can it drive NOVEL target discovery (vs validation-only)?
    evidence: str                # committed experiments establishing the condition
    out_of_domain_note: str = ""  # why it is gated for classes outside `domain`


# ------------------------------------------------------------------------------------------------------
# THE TRANSFER-GATE TABLE (COMPOSITE_ARCHITECTURE.md §2; the LEDGER). Edit here = edit the router's law.
# ------------------------------------------------------------------------------------------------------
_ALL = frozenset(BiologyClass)

TRANSFER_GATE: dict[Signal, SignalSpec] = {
    Signal.FBA_ESSENTIALITY: SignalSpec(
        signal=Signal.FBA_ESSENTIALITY,
        domain=frozenset({BiologyClass.BACTERIUM, BiologyClass.FREE_EUKARYOTE}),
        built=True, discovery_grade=True,
        evidence="MET1-3, VAL-ESS, CROSSVAL, BLIND1 (bacteria OR 5-64); GENERALIZE4 (yeast OR 4.65)",
        out_of_domain_note=("host-embedded metabolism -> FALSIFIED by GENERALIZE5 (OR 2.47) + HOSTCTX1 "
                            "(E-Flux) + HOSTCTX2 (boundary curation); not applicable to viruses (no metabolism)"),
    ),
    Signal.STRUCTURAL_HOMOLOGY: SignalSpec(
        signal=Signal.STRUCTURAL_HOMOLOGY,
        domain=frozenset({BiologyClass.VIRUS, BiologyClass.BACTERIUM}),
        built=True, discovery_grade=True,
        evidence="GENERALIZE2/3 (virus: Mpro->protease, RdRp->polymerase, blind); FOLD1 (isolated bacteria)",
        out_of_domain_note="requires an existing 3D structure with a conserved drugged fold",
    ),
    Signal.SEQUENCE_REPURPOSING: SignalSpec(
        signal=Signal.SEQUENCE_REPURPOSING,
        domain=_ALL,                 # can VALIDATE known pharmacology anywhere ...
        built=True, discovery_grade=False,   # ... but is NEVER a novel-coverage/discovery signal
        evidence="INTERVENE1 9/9 canonical recovery; STRUCTREPURPOSE1 NEGATIVE (no coverage expansion)",
        out_of_domain_note="validation-grade only: recovers KNOWN pharmacology; no 'expanded coverage' claim",
    ),
    Signal.FUNCTIONAL_DEPENDENCY: SignalSpec(
        signal=Signal.FUNCTIONAL_DEPENDENCY,
        # COMPOSITE2: VALIDATED domain is HUMAN_CANCER ONLY (DEPEND1 on DepMap). The transfer condition is
        # DATA-DEPENDENT, not class-blanket: it fires for HUMAN_CANCER because dependency data (DepMap CRISPR)
        # OR a validated SAME-DOMAIN label-free expr->dep map exists. A HOST_DEPENDENT_PARASITE is DELIBERATELY
        # EXCLUDED from the domain: there is no parasite dependency screen, and DEPEND1's label-free arm was
        # validated on held-out DepMap HUMAN lines, NOT organism-transferred to a zero-screen parasite -> the
        # parasite MUST still ABSTAIN. This exclusion IS the router's integrity (see out_of_domain_note).
        domain=frozenset({BiologyClass.HUMAN_CANCER}),
        built=True, discovery_grade=True,    # NOW BUILT + VALIDATED (DEPEND1 G1/G2/G3 PASS)
        evidence=("DEPEND1 G1/G2/G3 PASS on DepMap: selective CRISPR dependency recovers known cancer targets "
                  "(recovery@top10=0.80), GENERALIZES to held-out disjoint cell lines (0.80), and a LABEL-FREE "
                  "expr->dep model beats the own-expression baseline (median CV rho=0.36); reproduced x2"),
        out_of_domain_note=("VALIDATED for HUMAN_CANCER only and CELL-LINE (Chronos), NOT patient/clinical. "
                            "For a host-dependent parasite it does NOT fire: no parasite dependency data and "
                            "DEPEND1's label-free expr->dep arm was NOT organism-transferred to a zero-screen "
                            "organism (validated on held-out DepMap HUMAN lines only) -> parasite abstains"),
    ),
    Signal.CONSERVATION_BREADTH: SignalSpec(
        signal=Signal.CONSERVATION_BREADTH,
        domain=frozenset({BiologyClass.BACTERIUM, BiologyClass.FREE_EUKARYOTE}),
        built=True, discovery_grade=True,
        evidence="REACH1 (AUROC 0.86 for the FBA-blind non-metabolic essential half)",
        out_of_domain_note="rides the conserved-core invariant of self-contained genomes",
    ),
    Signal.HOST_SAFETY: SignalSpec(
        signal=Signal.HOST_SAFETY,
        domain=frozenset({BiologyClass.BACTERIUM, BiologyClass.FREE_EUKARYOTE, BiologyClass.VIRUS}),
        built=True, discovery_grade=False,   # a FILTER, not a discovery driver
        evidence="ENGINE FRONT1/E2E2 host non-homology hard filter",
        out_of_domain_note="needs a known host proteome to compare against",
    ),
}


# ======================================================================================================
# Routing decision objects
# ======================================================================================================
@dataclass
class GatedSignal:
    signal: str
    reason: str


@dataclass
class RoutingDecision:
    """The PURE-LOGIC routing verdict for a class (no I/O, fully unit-testable)."""
    organism: str
    biology_class: str
    class_source: str                         # "declared" | "autodetected"
    output_type: str                          # "shortlist" | "structural_class_id" | "abstention"
    signals_fired: list = field(default_factory=list)          # discovery-grade signals that transfer
    supporting_signals: list = field(default_factory=list)     # filters/validation signals that also apply
    signals_gated_out: list = field(default_factory=list)      # list[GatedSignal]
    abstention: Optional[str] = None          # explicit class-level reason if output_type == "abstention"

    def to_dict(self):
        d = asdict(self)
        d["signals_gated_out"] = [asdict(g) if not isinstance(g, dict) else g for g in self.signals_gated_out]
        return d


# The explicit host-dependent-parasite abstention reason (frozen; asserted verbatim by the parasite integrity
# test). COMPOSITE2 update: the functional-dependency layer IS now built + validated (DEPEND1) but ONLY for
# HUMAN_CANCER; it does NOT transfer to a zero-screen parasite. The reason states BOTH gated signals precisely:
# (1) metabolic FBA falsified for host-embedded biology; (2) functional-dependency validated-but-not-transferred.
HOST_DEPENDENT_PARASITE_ABSTENTION = (
    "host-dependent parasite: metabolic essentiality falsified (GENERALIZE5/HOSTCTX1/2); the "
    "functional-dependency layer is BUILT and VALIDATED for HUMAN_CANCER only (DEPEND1 G1/G2/G3 on DepMap) "
    "but does NOT transfer to this parasite -- no dependency data for the organism and DEPEND1's label-free "
    "expr->dep arm was NOT organism-transferred (validated on held-out DepMap human lines only); the router "
    "ABSTAINS rather than fire an untransferred signal")

# Backward-compatible alias: parasite is the sole host-embedded class that still abstains (HUMAN_CANCER now
# FIRES functional-dependency). COMPOSITE1's committed tests import this name.
HOST_EMBEDDED_ABSTENTION = HOST_DEPENDENT_PARASITE_ABSTENTION


# ======================================================================================================
# Class detector (deliberately minimal — see honest-scope note in the module docstring)
# ======================================================================================================
VIRUS_MAX_PROTEOME = 60   # a mature viral proteome is tiny (SARS-CoV-2 = 30); prokaryotes are >>1000


def detect_class(proteome_size: Optional[int] = None,
                 declared_class: Optional[BiologyClass] = None,
                 host_dependent: Optional[bool] = None) -> tuple[BiologyClass, str]:
    """Return (class, source). Honest minimal detector:
      - a DECLARED class always wins (host-dependence is NOT sequence-derivable, so it must be declared);
      - else a tiny proteome auto-detects a VIRUS;
      - else UNKNOWN (the honest apply-what-transfers / abstain case).
    `host_dependent=True` with no declared class is respected as a host-dependent parasite declaration."""
    if declared_class is not None:
        return BiologyClass(declared_class), "declared"
    if host_dependent is True:
        return BiologyClass.HOST_DEPENDENT_PARASITE, "declared"
    if proteome_size is not None and proteome_size <= VIRUS_MAX_PROTEOME:
        return BiologyClass.VIRUS, "autodetected"
    return BiologyClass.UNKNOWN, "autodetected"


# ======================================================================================================
# The PURE gating decision — the heart of the router (data-free)
# ======================================================================================================
def decide(biology_class: BiologyClass, organism: str = "", class_source: str = "declared") -> RoutingDecision:
    """Apply the transfer-gate table to a class and return the routing decision. NO I/O — pure logic."""
    biology_class = BiologyClass(biology_class)
    fired, supporting, gated = [], [], []

    for sig, spec in TRANSFER_GATE.items():
        in_domain = biology_class in spec.domain
        if not spec.built:
            gated.append(GatedSignal(sig.value,
                         f"module not built ({spec.out_of_domain_note}); evidence: {spec.evidence}"))
            continue
        if not in_domain:
            gated.append(GatedSignal(sig.value,
                         f"out of transfer domain for {biology_class.value}: {spec.out_of_domain_note}"))
            continue
        # in domain and built:
        if not spec.discovery_grade:
            # applies, but only as a validation/filter signal — never drives novel discovery
            supporting.append(sig.value)
            continue
        fired.append(sig.value)

    # ---- determine output type from the fired DISCOVERY signals -----------------------------------
    if not fired:
        # no validated discovery signal transfers -> CLASS-LEVEL ABSTENTION (the integrity core).
        # COMPOSITE2: HUMAN_CANCER no longer reaches here (functional-dependency now fires for it). The
        # host-dependent parasite is the decisive integrity case: it STILL abstains because the validated
        # functional-dependency signal does NOT transfer to a zero-screen organism (see the constant).
        if biology_class == BiologyClass.HOST_DEPENDENT_PARASITE:
            reason = HOST_DEPENDENT_PARASITE_ABSTENTION
        else:
            reason = (f"no validated discovery signal transfers to class '{biology_class.value}'; "
                      f"the system refuses to emit a confident answer rather than force an ill-fitting model")
        return RoutingDecision(organism=organism, biology_class=biology_class.value, class_source=class_source,
                               output_type="abstention", signals_fired=sorted(fired),
                               supporting_signals=sorted(supporting), signals_gated_out=gated, abstention=reason)

    # structural-only route (virus): the fired discovery signal is structural class-ID, FBA/repurposing gated
    if fired == [Signal.STRUCTURAL_HOMOLOGY.value]:
        out = "structural_class_id"
    else:
        out = "shortlist"
    return RoutingDecision(organism=organism, biology_class=biology_class.value, class_source=class_source,
                           output_type=out, signals_fired=sorted(fired),
                           supporting_signals=sorted(supporting), signals_gated_out=gated, abstention=None)


# ======================================================================================================
# The router: decision + (on the shortlist path) invocation of the validated DiscoveryEngine
# ======================================================================================================
class CompositeRouter:
    """Wraps the validated DiscoveryEngine with an explicit transfer-condition gate + class-level abstention."""

    def __init__(self, virus_max_proteome: int = VIRUS_MAX_PROTEOME):
        self.virus_max_proteome = virus_max_proteome

    # ---- decision ----------------------------------------------------------
    def decide(self, organism: str, proteome_size: Optional[int] = None,
               declared_class: Optional[BiologyClass] = None,
               host_dependent: Optional[bool] = None) -> RoutingDecision:
        cls, src = detect_class(proteome_size=proteome_size, declared_class=declared_class,
                                host_dependent=host_dependent)
        return decide(cls, organism=organism, class_source=src)

    # ---- execution ---------------------------------------------------------
    def run_fba_composite(self, organism: str, engine_kwargs: dict, top: int = 30) -> dict:
        """SHORTLIST path: invoke the validated DiscoveryEngine composing the bacterial/eukaryote signals.
        `engine_kwargs` are passed verbatim to DiscoveryEngine.for_pathogen (the caller supplies the cached
        inputs). Lazy import so the pure decision logic stays data-free / importable without heavy deps."""
        from .discovery_engine import DiscoveryEngine
        eng = DiscoveryEngine.for_pathogen(organism, **engine_kwargs)
        return eng.report(top=top)

    @staticmethod
    def functional_dependency_shortlist_from_depend1(metrics_path: str, context: str) -> dict:
        """HUMAN_CANCER SHORTLIST path (COMPOSITE2 firing path): surface the committed DEPEND1 VALIDATED
        selective-dependency target(s) for a lineage/mutation `context`. REUSES DEPEND1's committed results
        (results/DEPEND1_metrics.json) — it does NOT recompute or re-derive selectivity a different way, per
        the reuse-don't-re-derive rule. DEPEND1's own gates (G1/G2/G3) must be PASS for the router to trust it.

        `context` is a DEPEND1 context key (e.g. 'skin' for melanoma, 'KRAS-hotspot' for KRAS-mutant lines).
        Returns the context-selective dependency target(s) DEPEND1 validated for that context, each with its
        genome-wide selectivity rank, selectivity score, dependent-fraction, pan-essential flag and
        permutation p — plus the honest CELL-LINE (not clinical) scope bound.
        """
        import json
        m = json.load(open(metrics_path))
        gates = m.get("gates", {})
        depend1_validated = all(gates.get(g) == "PASS" for g in ("G1", "G2", "G3"))
        pairs = m.get("G1", {}).get("pairs", [])
        matched = [p for p in pairs if p.get("context") == context and "rank" in p]
        # rank ascending = most context-selective first
        matched = sorted(matched, key=lambda p: p["rank"])
        shortlist = [{
            "target": p["target"],
            "context": p["context"],
            "selectivity_rank_genomewide": p["rank"],
            "sel_score": p["sel_score"],
            "in_top10": p["in_top10"],
            "in_top1pct": p["in_top1pct"],
            "dependent_fraction": p["target_dep_frac"],
            "is_pan_essential": p["is_pan_essential"],
            "perm_p": p["perm_p"],
        } for p in matched]
        return {
            "signal": "functional_dependency (DEPEND1 G1/G2/G3 PASS, reproduced x2)",
            "context": context,
            "depend1_validated": depend1_validated,
            "depend1_gates": gates,
            "shortlist": shortlist,
            "known_contexts": sorted({p["context"] for p in pairs if "context" in p}),
            "scope": ("cancer CELL-LINE Chronos selective dependency (DepMap); a differential-dependency "
                      "statistic validated with held-out generalization + a label-free arm; NOT patient/"
                      "clinical, NOT wet-lab. Fires here because HUMAN_CANCER dependency data exists."),
        }

    @staticmethod
    def structural_class_id_from_generalize3(metrics_path: str) -> dict:
        """STRUCTURAL path: surface the committed GENERALIZE3 blind structural target-CLASS hypotheses
        (the validated viral route). Reuses the cached result rather than re-running Foldseek."""
        import json
        s = json.load(open(metrics_path))["summary"]
        return {
            "signal": "structural_homology_tm (GENERALIZE3, blind, reproduced x2)",
            "hypotheses": [
                {"protein": "nsp5_Mpro", "target_class": s["nsp5_Mpro"]["class"],
                 "best_drugged_analog": s["nsp5_Mpro"]["best"], "tm": s["nsp5_Mpro"]["tm"],
                 "rank": s["nsp5_Mpro"]["rank"]},
                {"protein": "nsp12_RdRp", "target_class": s["nsp12_RdRp"]["class"],
                 "best_drugged_analog": s["nsp12_RdRp"]["best"], "tm": s["nsp12_RdRp"]["tm"],
                 "rank": s["nsp12_RdRp"]["rank"]},
            ],
            "gate": s["GATE"],
            "scope": ("in-silico structural target-CLASS prioritization on the structured subset; n=1 virus; "
                      "moderate TM (0.43-0.49); establishes the principle, not a deployed pipeline; not wet-lab"),
        }
