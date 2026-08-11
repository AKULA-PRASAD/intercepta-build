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
  * FBA gene-ESSENTIALITY   — FULL-GRADE domain = a SELF-CONTAINED metabolism captured by a quality GEM.
        VERIFIED for free-living bacteria (MET1-3, VAL-ESS, CROSSVAL, BLIND1; OR 5-64).
        VERIFIED-weaker for a free-living eukaryote/yeast (GENERALIZE4, OR 4.65); HARDENF1 Candida OR 13.93.
        **HOST-DEPENDENT ORGANISMS = a CAPPED/UNCERTAIN domain (COMPOSITE3 correction, NOT the old
        blanket-abstain).** The n=1 view (GENERALIZE5 malaria OR 2.47 + HOSTCTX1 E-Flux + HOSTCTX2 boundary
        curation all negative -> "FBA is out of domain for host-embedded biology") was FALSIFIED by HARDENP1: a
        SECOND host-dependent parasite, *Toxoplasma gondii* (curated iTgo2020), PASSES strongly (OR 14.10,
        recall 0.51). So host-embeddedness does NOT decide it -- GEM-TOPOLOGY QUALITY does, and that is NOT
        knowable a-priori for a novel organism (Plasmodium fails, Toxoplasma passes; both host-dependent, n=2).
        HONEST router behavior: if a host-dependent organism HAS a curated GEM, FBA now FIRES but at a
        REDUCED/CAPPED confidence with an explicit uncertainty flag (see `uncertainty_note`); it is NEITHER a
        blanket abstention (which wrongly refuses Toxoplasma) NOR bacterial-grade confidence (which would
        overclaim on Plasmodium). If NO curated GEM is available, there is NO signal -> the class STILL ABSTAINS.
        Not applicable to viruses (no metabolism).
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
    ARCHAEON = "archaeon"                             # free-living archaeon (3rd domain of life; BLIND6)
    FREE_EUKARYOTE = "free_eukaryote"                # free-living eukaryote / fungus (e.g. yeast)
    VIRUS = "virus"                                  # no metabolism
    HOST_DEPENDENT_PARASITE = "host_dependent_parasite"  # e.g. Plasmodium (host-embedded metabolism)
    HUMAN_CANCER = "human_cancer"                    # host cell / oncology (somatic; functional dependency)
    HUMAN_MONOGENIC = "human_monogenic"              # COMPOSITE4: germline monogenic; causal gene GIVEN (MENDEL1)
    HUMAN_COMPLEX_DISEASE = "human_complex_disease"  # COMPOSITE4: common/polygenic; GWAS->target (GENETICS1)
    UNKNOWN = "unknown"


class Signal(str, Enum):
    FBA_ESSENTIALITY = "fba_essentiality"
    STRUCTURAL_HOMOLOGY = "structural_homology"      # Foldseek TM -> target CLASS-ID
    SEQUENCE_REPURPOSING = "sequence_repurposing"    # validation-grade ONLY (never a discovery signal)
    FUNCTIONAL_DEPENDENCY = "functional_dependency"  # host-embedded target-ID (DEPEND1; HUMAN_CANCER)
    CONSERVATION_BREADTH = "conservation_breadth"    # supporting
    HOST_SAFETY = "host_safety"                      # supporting (hard filter)
    # ---- COMPOSITE4: the expanded, now-validated human arms -------------------------------------------
    GENETIC_ASSOCIATION = "genetic_association"      # GWAS->target (GENETICS1); CAPPED/attenuated, target-relevance
    CAUSAL_GENE = "causal_gene"                      # germline monogenic causal gene GIVEN (MENDEL1) -> mode-triage


# COMPOSITE5 / GENETICCLASS1 (reproduced x2, sha ffaa351): disease-class deployment envelope for the
# GWAS->target genetic-association arm. Grades the signal per HUMAN_COMPLEX_DISEASE *class* (Mantel-Haenszel OR
# on the genome-wide universe, fame-adjusted). Data-free constant (cited evidence); consulted only when the
# caller DECLARES a disease_class. Undeclared -> the original blanket-CAPPED behaviour (backward compatible).
GENETIC_CLASS_GRADE = {
    "cardiovascular": "FULL", "immune_inflammatory": "FULL", "neuro_psychiatric": "FULL",
    "respiratory_fibrotic": "FULL",      # provisional-FULL (n=2 diseases; wide CI)
    "metabolic": "CAPPED",
    "musculoskeletal_renal": "ABSTAIN",  # MH-OR CI includes ~1 AND fame-adjusted coef CI includes 0
}
GENETIC_CLASS_EVIDENCE = ("GENETICCLASS1 (sha ffaa351, reproduced x2): per-class Mantel-Haenszel OR, "
                          "fame-adjusted, on the 20,596-gene genome-wide universe x 27 diseases. FULL: "
                          "cardiovascular 2.50 / immune 2.13 / neuro 2.17 / respiratory 3.19; CAPPED: "
                          "metabolic 1.61; ABSTAIN: musculoskeletal_renal 1.32 (CI incl ~1, fame-coef CI incl 0).")


@dataclass(frozen=True)
class SignalSpec:
    """Encodes ONE signal's evidence-derived transfer condition."""
    signal: Signal
    domain: frozenset            # classes where the transfer condition is VALIDATED to hold (FULL grade)
    built: bool                  # is the module actually implemented?
    discovery_grade: bool        # can it drive NOVEL target discovery (vs validation-only)?
    evidence: str                # committed experiments establishing the condition
    out_of_domain_note: str = ""  # why it is gated for classes outside `domain`
    # ---- COMPOSITE4: a FULL-DOMAIN signal that additionally needs a DECLARED descriptor to fire ---------
    # (distinct from the CAPPED uncertain_requires below: this fires at FULL grade when the descriptor is
    # present, and GATES OUT — requiring the descriptor — when it is absent; it is NOT capped/flagged.)
    requires_descriptor: str = ""  # runtime descriptor key the full-grade firing needs (e.g. "causal_gene_known")
    output_mode: str = ""          # optional override of the decision's output_type when this signal fires alone
    # ---- COMPOSITE3: the CAPPED/UNCERTAIN (GEM-topology-contingent) transfer domain --------------------
    # Classes where the signal DOES fire (not abstain) but ONLY at reduced/capped confidence with an explicit
    # uncertainty flag, AND ONLY if a required runtime resource is available. This encodes the honest HARDENP1
    # correction: the transfer works for SOME host-dependent organisms (Toxoplasma) and fails for others
    # (Plasmodium), and which is which is NOT knowable a-priori -> fire-but-flag, never blanket-abstain/fire.
    uncertain_domain: frozenset = frozenset()   # classes that get capped, resource-contingent firing
    uncertain_requires: str = ""                # runtime resource key the capped firing needs (e.g. "curated_gem")
    confidence_cap: Optional[float] = None      # coarse cap (<1.0 full-grade); a MARKER, not a calibrated prob
    uncertainty_note: str = ""                  # the verbatim honest uncertainty statement surfaced to the caller
    uncertain_evidence: str = ""                # the n=2 committed evidence behind the capped grade


# ------------------------------------------------------------------------------------------------------
# THE TRANSFER-GATE TABLE (COMPOSITE_ARCHITECTURE.md §2; the LEDGER). Edit here = edit the router's law.
# ------------------------------------------------------------------------------------------------------
_ALL = frozenset(BiologyClass)

TRANSFER_GATE: dict[Signal, SignalSpec] = {
    Signal.FBA_ESSENTIALITY: SignalSpec(
        signal=Signal.FBA_ESSENTIALITY,
        # FULL-GRADE domain: free-living self-contained metabolism. ARCHAEON added (BLIND6, curated iMR539
        # GEM, prospective-blind git-committed-before-reveal FBA PASS OR 4.23) -- a 3rd-domain-of-life
        # self-contained genome, NOT host-embedded; additive, changes no prior committed router verdict.
        domain=frozenset({BiologyClass.BACTERIUM, BiologyClass.ARCHAEON, BiologyClass.FREE_EUKARYOTE}),
        built=True, discovery_grade=True,
        evidence="MET1-3, VAL-ESS, CROSSVAL, BLIND1 (bacteria OR 5-64); BLIND6 (archaeon M. maripaludis OR 4.23, prospective-blind); GENERALIZE4 (yeast OR 4.65); HARDENF1 (Candida OR 13.93)",
        out_of_domain_note=("full-grade transfer needs a self-contained metabolism; not applicable to viruses "
                            "(no metabolism); host-dependent organisms are NOT out-of-domain but CAPPED/UNCERTAIN "
                            "(see uncertain_domain) -- GEM-topology-contingent, not knowable a-priori"),
        # COMPOSITE3: host-dependent parasites get CAPPED, GEM-contingent firing (NOT the old blanket-abstain).
        uncertain_domain=frozenset({BiologyClass.HOST_DEPENDENT_PARASITE}),
        uncertain_requires="curated_gem",
        confidence_cap=0.5,
        uncertainty_note=("FBA-essentiality transfer to host-dependent organisms is GEM-topology-dependent, "
                          "validated at only n=2 (Toxoplasma PASS OR 14.10 / Plasmodium FAIL OR 2.47); treat as "
                          "lower-confidence, GEM-quality-contingent."),
        uncertain_evidence=("HARDENP1 Toxoplasma iTgo2020 vs Sidik2016 CRISPR: OR 14.10 recall 0.51 PASS; "
                            "GENERALIZE5 Plasmodium iPfal19 vs Zhang2018 piggyBac: OR 2.47 recall 0.20 FAIL "
                            "(HOSTCTX1/2 could not rescue). n=2; which outcome occurs is NOT predictable a-priori"),
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
        domain=frozenset({BiologyClass.BACTERIUM, BiologyClass.ARCHAEON, BiologyClass.FREE_EUKARYOTE}),
        built=True, discovery_grade=True,
        evidence="REACH1 (AUROC 0.86 for the FBA-blind non-metabolic essential half); archaeon rides the same conserved-core invariant (BLIND6 self-contained genome)",
        out_of_domain_note="rides the conserved-core invariant of self-contained genomes",
    ),
    Signal.HOST_SAFETY: SignalSpec(
        signal=Signal.HOST_SAFETY,
        domain=frozenset({BiologyClass.BACTERIUM, BiologyClass.FREE_EUKARYOTE, BiologyClass.VIRUS}),
        built=True, discovery_grade=False,   # a FILTER, not a discovery driver
        evidence="ENGINE FRONT1/E2E2 host non-homology hard filter",
        out_of_domain_note="needs a known host proteome to compare against",
    ),
    # ---- COMPOSITE4: HUMAN_COMPLEX_DISEASE -> GENETIC_ASSOCIATION (GENETICS1) ---------------------------
    # Reuses the COMPOSITE3 CAPPED/UNCERTAIN machinery: it FIRES (not abstains) but ONLY at reduced/capped
    # confidence with an explicit attenuation flag, and ONLY when a `gwas_evidence` descriptor is declared.
    # This encodes GENETICS1's HONEST bound: the popularity-controlled GWAS->target signal is REAL, dose-
    # responsive, survives the fame null -- but ATTENUATED (crude OR 2.26 -> fame-adjusted MH OR 1.672), and
    # it is TARGET-RELEVANCE ONLY (cross-sectional Open Targets 26.06), never response/molecule/clinical.
    Signal.GENETIC_ASSOCIATION: SignalSpec(
        signal=Signal.GENETIC_ASSOCIATION,
        domain=frozenset(),                      # never a FULL-grade signal for any class
        built=True, discovery_grade=True,        # drives target-RELEVANCE ranking (capped), not therapy
        evidence=("GENETICS1 (Open Targets 26.06 genetic_association, 27 complex diseases, popularity-"
                  "controlled): crude Fisher OR 2.26 (p 1.2e-63), dose-responsive, 27/27 leave-one-disease-out"),
        out_of_domain_note="fires ONLY for HUMAN_COMPLEX_DISEASE and ONLY as a CAPPED/attenuated signal",
        uncertain_domain=frozenset({BiologyClass.HUMAN_COMPLEX_DISEASE}),
        uncertain_requires="gwas_evidence",
        confidence_cap=0.5,
        uncertainty_note=("popularity-adjusted effect bounded [1.67,2.26]; target-relevance only, "
                          "cross-sectional"),
        uncertain_evidence=("GENETICS1 popularity null: fame-matched permutation p 1e-4; fame-adjusted "
                            "Mantel-Haenszel OR 1.672 (p 1.6e-31); popularity proxies are partly colliders on "
                            "drug-status so adjustment over-controls -> the true popularity-free effect is "
                            "BOUNDED [1.67, 2.26]; real, significant, dose-responsive, but attenuated; a fully "
                            "clean test needs a temporal/prospective design. Reproduced x2 sha 9e73d1c8."),
    ),
    # ---- COMPOSITE4: HUMAN_MONOGENIC -> CAUSAL_GENE (MENDEL1) ------------------------------------------
    # The causal gene is GENETICALLY GIVEN, so target-ID is trivial; the signal fires at FULL grade (NOT
    # capped) but requires the `causal_gene_known` descriptor, and routes to intervention-MODE reasoning
    # (output_mode="mode") rather than a discovery shortlist. Honest bound: target given, deliverable is
    # intervention-MODE triage (MENDEL1: mechanism-first 3-class mode accuracy 0.857, hard fail-safe 0/10),
    # NOT a therapy/molecule (the SM branch still hits the affinity wall).
    Signal.CAUSAL_GENE: SignalSpec(
        signal=Signal.CAUSAL_GENE,
        domain=frozenset({BiologyClass.HUMAN_MONOGENIC}),
        built=True, discovery_grade=True,
        evidence=("MENDEL1 (n=28 cited germline-monogenic triples): mechanism-first intervention-MODE "
                  "3-class accuracy 0.857 (24/28) vs majority 0.393; hard fail-safe 0/10 not-small-molecule "
                  "genes mis-promised an SM call; reproduced x2 sha cb1be243"),
        out_of_domain_note="fires ONLY for HUMAN_MONOGENIC (a genetically-established causal gene)",
        requires_descriptor="causal_gene_known",
        output_mode="mode",
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
    # ---- COMPOSITE3: capped/uncertain firing ----------------------------------------------------------
    uncertain: bool = False                   # True iff >=1 fired signal is a CAPPED (GEM-contingent) transfer
    uncertainty_flags: list = field(default_factory=list)  # list[dict]: {signal, confidence_cap, note, evidence}
    confidence_cap: Optional[float] = None    # min cap over uncertain fired signals (None = full-grade)
    # ---- ROUTERAUTO1: the auto class-detection trace (None when the class was hand-declared via decide) --
    detection: Optional[dict] = None          # {biology_class, source, rule, reasons, requires_descriptor}
    # ---- COMPOSITE4: the post-target INTERVENTION STAGE result (orthogonal to class->target-ID routing) --
    intervention: Optional[dict] = None       # {recommended_modality_class, feasible_set, fail_safe, note}

    def to_dict(self):
        d = asdict(self)
        d["signals_gated_out"] = [asdict(g) if not isinstance(g, dict) else g for g in self.signals_gated_out]
        return d

    # ---- COMPOSITE4: the STABLE verdict skeleton (the reproducibility drift FIX) -----------------------
    def verdict_skeleton(self) -> dict:
        """Emit ONLY the stable decision essentials — NO volatile reason-prose, NO evidence strings, NO
        gated-signal reasons. The COMPOSITE4 payload (and any future capstone) hashes THIS, so the decision
        reproduces byte-identical even as reason/evidence prose and additive metadata evolve. Keys are the
        fire/abstain VERDICT: class, sorted fired-signal names, abstain bool, capped bool, and the
        recommended intervention-modality class (or None if the intervention stage was not run)."""
        return {
            "biology_class": self.biology_class,
            "signals_fired": sorted(self.signals_fired),
            "abstain": self.output_type == "abstention",
            "capped": self.confidence_cap is not None,
            "recommended_modality_class": (self.intervention or {}).get("recommended_modality_class"),
        }


# COMPOSITE3 update: the host-dependent parasite NO LONGER blanket-abstains. When it HAS a curated GEM, FBA
# FIRES at capped/flagged confidence (see the FBA uncertain_domain). It ABSTAINS ONLY when NO signal is
# available -- i.e. NO curated GEM (so capped FBA cannot even be attempted), functional-dependency does NOT
# transfer (no parasite screen; DEPEND1's label-free arm not organism-transferred), and structural/conservation
# are out of domain. This constant is the frozen reason for THAT no-signal case (asserted verbatim by the
# no-GEM abstention test). It deliberately does NOT say "metabolic essentiality falsified" -- HARDENP1 corrected
# that overgeneralization; the honest reason is simply "no signal available without a GEM."
HOST_DEPENDENT_PARASITE_NO_GEM_ABSTENTION = (
    "host-dependent parasite with NO curated GEM: FBA-essentiality is the only signal with any validated "
    "host-dependent transfer, and it is GEM-topology-contingent (HARDENP1 Toxoplasma PASS OR 14.10 / GENERALIZE5 "
    "Plasmodium FAIL OR 2.47, n=2) -- WITHOUT a GEM it cannot even be attempted (not blanket-refused: the router "
    "would FIRE it capped-and-flagged IF a GEM existed). The functional-dependency layer is BUILT and VALIDATED "
    "for HUMAN_CANCER only (DEPEND1 G1/G2/G3 on DepMap) but does NOT transfer to this parasite -- no dependency "
    "data for the organism and DEPEND1's label-free expr->dep arm was NOT organism-transferred (validated on "
    "held-out DepMap human lines only). Structural/conservation are out of domain. No signal available -> the "
    "router ABSTAINS rather than fabricate an answer")

# Backward-compatible aliases. COMPOSITE1/2's committed tests import these names; they now point at the
# no-signal (no-GEM) abstention, which is the sole remaining parasite-abstention case under v3.
HOST_DEPENDENT_PARASITE_ABSTENTION = HOST_DEPENDENT_PARASITE_NO_GEM_ABSTENTION
HOST_EMBEDDED_ABSTENTION = HOST_DEPENDENT_PARASITE_NO_GEM_ABSTENTION


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
def _resource_available(key: str, resources: dict) -> bool:
    """Is the runtime resource `key` (declared descriptor / data availability) present?
    Explicit dict lookup (no magic). An empty key means 'no requirement' -> always available.
    COMPOSITE4 generalizes the old COMPOSITE3 single-flag helper to N declared resources
    (curated_gem, gwas_evidence, causal_gene_known, ...)."""
    if key == "":
        return True
    return bool(resources.get(key, False))


# ======================================================================================================
# COMPOSITE4 — the INTERVENTION STAGE: a port of MODALITY1's VALIDATED fail-safe modality recommender.
# ======================================================================================================
# Faithful port of MODALITY1 (run.py, reproduced x2 sha 57b85479): mechanism x localization x protein-class
# druggability -> a credible intervention MODALITY, plus the FROZEN feasibility matrix. HARD FAIL-SAFE: the
# recommended modality is ALWAYS a member of the computed feasible_set (or ABSTAIN); an infeasible modality is
# NEVER recommended. Honest bound: this is FEASIBILITY TRIAGE (a modality CLASS), NOT a molecule — the
# small-molecule branch still hits the affinity wall (AFFINITY1/HIT2). Pure logic; data-free unit-testable.
_MOD_DRUGGABLE_CLASSES = frozenset({"enzyme", "kinase", "receptor", "ion_channel", "transporter",
                                    "nuclear_receptor", "transport_carrier", "globin"})
_MOD_STABILIZABLE = frozenset({"transport_carrier", "globin"})
_MOD_ALL = ("SMALL_MOLECULE_INHIBITOR", "SMALL_MOLECULE_ACTIVATOR", "MONOCLONAL_ANTIBODY",
            "ASO_siRNA", "ENZYME_PROTEIN_REPLACEMENT", "GENE_THERAPY")


def _mod_druggable(pc):
    return pc in _MOD_DRUGGABLE_CLASSES


def _mod_recommend(mech, loc, pc):
    """MODALITY1 primary recommender (pre-BBB gate)."""
    d = _mod_druggable(pc)
    if mech in ("GoF", "overactivity"):
        if loc in ("secreted", "cell_surface"):
            return "MONOCLONAL_ANTIBODY"
        if loc in ("membrane", "intracellular"):
            return "SMALL_MOLECULE_INHIBITOR" if d else "ASO_siRNA"
        return "ABSTAIN"
    if mech in ("dominant_negative", "toxic_aggregation"):
        if pc in _MOD_STABILIZABLE:
            return "SMALL_MOLECULE_ACTIVATOR"
        if loc == "intracellular":
            return "ASO_siRNA"
        return "ABSTAIN"
    if mech == "LoF_misfold":
        if d and loc in ("membrane", "intracellular", "lysosomal"):
            return "SMALL_MOLECULE_ACTIVATOR"
        return "ABSTAIN"
    if mech in ("LoF_null", "LoF"):
        if pc == "enzyme" and loc == "lysosomal":
            return "ENZYME_PROTEIN_REPLACEMENT"
        if loc == "secreted":
            return "ENZYME_PROTEIN_REPLACEMENT"
        if loc in ("intracellular", "membrane"):
            return "GENE_THERAPY"
        return "ABSTAIN"
    return "ABSTAIN"


def _mod_is_feasible(modality, mech, loc, pc, bbb_cns, splice_addressable):
    """MODALITY1 frozen feasibility matrix. ABSTAIN is never a violation."""
    d = _mod_druggable(pc)
    if modality == "ABSTAIN":
        return True
    if modality == "MONOCLONAL_ANTIBODY":
        return loc not in ("intracellular", "lysosomal")
    if modality == "SMALL_MOLECULE_INHIBITOR":
        return mech in ("GoF", "overactivity") and d
    if modality == "SMALL_MOLECULE_ACTIVATOR":
        return d and (mech == "LoF_misfold" or (mech == "toxic_aggregation" and pc in _MOD_STABILIZABLE))
    if modality == "ENZYME_PROTEIN_REPLACEMENT":
        return mech in ("LoF_null", "LoF") and (loc == "secreted" or (loc == "lysosomal" and not bbb_cns))
    if modality == "GENE_THERAPY":
        return mech not in ("GoF", "overactivity", "dominant_negative", "toxic_aggregation")
    if modality == "ASO_siRNA":
        if mech in ("LoF_null", "LoF", "LoF_misfold"):
            return bool(splice_addressable)
        return True
    return True


# COMPOSITE6 — per-class intervention wiring: which MODALITY CLASSES are biologically APPLICABLE to a biology
# class (cited). Pathogen targets are treated with SMALL-MOLECULE antimicrobials -- you cannot gene-therapy /
# siRNA / enzyme-replace a pathogen; viruses add neutralizing antibodies; human classes span the host-modality
# space (full/mode-dependent for monogenic). This ANNOTATES MODALITY1's feasibility triage with the class
# context (ADDITIVE: never changes recommended_modality_class or feasible_set -- adds class_modality_applicability
# + a class_consistent flag that catches a class-inapplicable recommendation, e.g. ASO_siRNA for a bacterium).
CLASS_MODALITY_APPLICABILITY = {
    "bacterium": {"SMALL_MOLECULE_INHIBITOR"}, "archaeon": {"SMALL_MOLECULE_INHIBITOR"},
    "free_eukaryote": {"SMALL_MOLECULE_INHIBITOR"}, "host_dependent_parasite": {"SMALL_MOLECULE_INHIBITOR"},
    "virus": {"SMALL_MOLECULE_INHIBITOR", "MONOCLONAL_ANTIBODY"},
    "human_cancer": {"SMALL_MOLECULE_INHIBITOR", "SMALL_MOLECULE_ACTIVATOR", "MONOCLONAL_ANTIBODY", "ASO_siRNA"},
    "human_monogenic": {"SMALL_MOLECULE_INHIBITOR", "SMALL_MOLECULE_ACTIVATOR", "MONOCLONAL_ANTIBODY",
                        "ENZYME_PROTEIN_REPLACEMENT", "GENE_THERAPY", "ASO_siRNA"},
    "human_complex_disease": {"SMALL_MOLECULE_INHIBITOR", "SMALL_MOLECULE_ACTIVATOR", "MONOCLONAL_ANTIBODY", "ASO_siRNA"},
    "unknown": set(),
}


def _class_modality_info(biology_class, recommended) -> dict:
    bc = biology_class.value if hasattr(biology_class, "value") else str(biology_class)
    appl = sorted(CLASS_MODALITY_APPLICABILITY.get(bc, set()))
    return {"class_modality_applicability": appl,
            "class_consistent": bool(recommended == "ABSTAIN" or recommended in appl)}


def recommend_intervention(mechanism: Optional[str] = None, localization: Optional[str] = None,
                           protein_class: Optional[str] = None, bbb_cns: bool = False,
                           splice_addressable: bool = False, biology_class=None) -> dict:
    """COMPOSITE4 INTERVENTION STAGE (MODALITY1 port). Returns
    {recommended_modality_class, feasible_set, fail_safe: True, note}.

    ABSTAINS (recommended_modality_class='ABSTAIN', empty feasible_set) when the objective features required
    for a credible feasibility call (mechanism + localization) are absent. HARD FAIL-SAFE: the returned
    recommendation is ALWAYS in feasible_set (or ABSTAIN) — an infeasible modality is never emitted."""
    if not mechanism or not localization:
        result = {
            "recommended_modality_class": "ABSTAIN",
            "feasible_set": [],
            "fail_safe": True,
            "note": ("no objective features (mechanism + localization) provided -> ABSTAIN; the intervention "
                     "stage is feasibility TRIAGE and refuses to recommend a modality without them"),
        }
        if biology_class is not None:
            result.update(_class_modality_info(biology_class, "ABSTAIN"))
        return result
    rec = _mod_recommend(mechanism, localization, protein_class)
    # localization-aware BBB gate on lysosomal enzyme replacement (ERT cannot cross the BBB) -> abstain
    if rec == "ENZYME_PROTEIN_REPLACEMENT" and localization == "lysosomal" and bbb_cns:
        rec = "ABSTAIN"
    feasible = [m for m in _MOD_ALL if _mod_is_feasible(m, mechanism, localization, protein_class,
                                                        bbb_cns, splice_addressable)]
    # HARD FAIL-SAFE enforcement: never emit an infeasible recommendation.
    if rec != "ABSTAIN" and not _mod_is_feasible(rec, mechanism, localization, protein_class,
                                                 bbb_cns, splice_addressable):
        rec = "ABSTAIN"
    result = {
        "recommended_modality_class": rec,
        "feasible_set": feasible,
        "fail_safe": True,
        "note": ("MODALITY1-validated mechanism x localization x druggability feasibility triage (a modality "
                 "CLASS, not a molecule; the SM branch still hits the affinity wall); recommendation is "
                 "guaranteed a member of feasible_set or ABSTAIN"),
    }
    if biology_class is not None:
        result.update(_class_modality_info(biology_class, rec))
    return result


def decide(biology_class: BiologyClass, organism: str = "", class_source: str = "declared",
           has_curated_gem: bool = False, has_gwas_evidence: bool = False,
           causal_gene_known: bool = False, intervention_features: Optional[dict] = None,
           disease_class: str = "") -> RoutingDecision:
    """Apply the transfer-gate table to a class and return the routing decision. NO I/O — pure logic.

    COMPOSITE3: `has_curated_gem` is the runtime resource flag consulted for the CAPPED/UNCERTAIN transfer
    domain (host-dependent parasite + FBA). It is FALSE by default -> a bare host-dependent parasite (no GEM
    declared) still ABSTAINS (no signal). When True, FBA fires at capped confidence with the uncertainty flag.
    The flag does nothing for classes whose signals are all in the FULL domain (bacterium/virus/etc.).

    COMPOSITE4: `has_gwas_evidence` gates the CAPPED GENETIC_ASSOCIATION firing for HUMAN_COMPLEX_DISEASE
    (GENETICS1); `causal_gene_known` gates the FULL-grade CAUSAL_GENE firing for HUMAN_MONOGENIC (MENDEL1,
    output_type 'mode'). Both default FALSE -> the class ABSTAINS pending the declared descriptor.
    `intervention_features` (optional {mechanism, localization, protein_class, bbb_cns, splice_addressable})
    drives the orthogonal, fail-safe INTERVENTION STAGE populated on any non-abstaining decision (else it
    ABSTAINS). It NEVER changes the class->target-ID fire/abstain routing above."""
    biology_class = BiologyClass(biology_class)
    resources = {"curated_gem": has_curated_gem, "gwas_evidence": has_gwas_evidence,
                 "causal_gene_known": causal_gene_known}
    fired, supporting, gated = [], [], []
    uncertainty_flags = []
    output_mode_override = ""

    for sig, spec in TRANSFER_GATE.items():
        in_domain = biology_class in spec.domain
        in_uncertain = biology_class in spec.uncertain_domain
        if not spec.built:
            gated.append(GatedSignal(sig.value,
                         f"module not built ({spec.out_of_domain_note}); evidence: {spec.evidence}"))
            continue
        if in_domain:
            # FULL-GRADE transfer — but a signal may additionally require a DECLARED descriptor (COMPOSITE4).
            if spec.requires_descriptor and not _resource_available(spec.requires_descriptor, resources):
                gated.append(GatedSignal(sig.value,
                             f"full-grade transfer domain for {biology_class.value}, but required declared "
                             f"descriptor '{spec.requires_descriptor}' absent -> cannot fire "
                             f"(would fire full-grade IF declared): {spec.out_of_domain_note}"))
                continue
            if not spec.discovery_grade:
                # applies, but only as a validation/filter signal — never drives novel discovery
                supporting.append(sig.value)
            else:
                fired.append(sig.value)
                if spec.output_mode:
                    output_mode_override = spec.output_mode
            continue
        if in_uncertain:
            # CAPPED/UNCERTAIN, resource-contingent transfer (COMPOSITE3 parasite path; COMPOSITE4 GWAS path).
            # COMPOSITE5/GENETICCLASS1: disease-class-aware grading of the genetic-association arm (only when a
            # disease_class is DECLARED; undeclared -> original blanket-CAPPED behaviour below, backward-compatible).
            if sig == Signal.GENETIC_ASSOCIATION and disease_class:
                grade = GENETIC_CLASS_GRADE.get(disease_class)
                if grade == "ABSTAIN":
                    gated.append(GatedSignal(sig.value,
                        f"GENETICCLASS1: zero-data genetic target-ID does NOT robustly transfer for disease "
                        f"class '{disease_class}' -> class-level ABSTAIN. {GENETIC_CLASS_EVIDENCE}"))
                    continue
                if grade == "FULL" and _resource_available(spec.uncertain_requires, resources):
                    fired.append(sig.value)
                    uncertainty_flags.append({
                        "signal": sig.value, "grade": "FULL_by_disease_class", "confidence_cap": None,
                        "note": (f"GENETICCLASS1: FULL-grade genetic target-ID for disease class "
                                 f"'{disease_class}' (fame-adjusted MH-OR>2, CI-lo>1.5) -- upgraded from the "
                                 f"blanket-CAPPED default."),
                        "evidence": GENETIC_CLASS_EVIDENCE})
                    continue
                # grade == CAPPED (or FULL but gwas_evidence absent) -> fall through to default capped/gate logic:
            if _resource_available(spec.uncertain_requires, resources):
                # FIRE, but flagged + capped -- NEITHER a blanket abstention NOR full-grade confidence.
                fired.append(sig.value)
                uncertainty_flags.append({
                    "signal": sig.value,
                    "confidence_cap": spec.confidence_cap,
                    "note": spec.uncertainty_note,
                    "evidence": spec.uncertain_evidence,
                })
            else:
                # resource/descriptor unavailable -> cannot even attempt the capped firing -> gate it.
                gated.append(GatedSignal(sig.value,
                             f"capped/uncertain (resource-contingent) transfer domain for {biology_class.value}, "
                             f"but required resource '{spec.uncertain_requires}' unavailable -> cannot attempt "
                             f"(would fire capped-and-flagged IF present): {spec.uncertainty_note}"))
            continue
        # out of every transfer domain:
        gated.append(GatedSignal(sig.value,
                     f"out of transfer domain for {biology_class.value}: {spec.out_of_domain_note}"))

    # ---- COMPOSITE4/6: the fail-safe INTERVENTION STAGE, now CLASS-AWARE (never changes fire/abstain routing) --
    interv = recommend_intervention(biology_class=biology_class, **(intervention_features or {}))

    # ---- determine output type from the fired DISCOVERY signals -----------------------------------
    if not fired:
        # no validated discovery signal transfers (incl. no capped FBA) -> CLASS-LEVEL ABSTENTION.
        # COMPOSITE3: the host-dependent parasite reaches here ONLY when it has NO curated GEM (so capped FBA
        # cannot be attempted). WITH a GEM it fires capped-and-flagged (below) instead of abstaining -- that is
        # the correction to the old blanket abstention, which would have wrongly refused Toxoplasma.
        if biology_class == BiologyClass.HOST_DEPENDENT_PARASITE:
            reason = HOST_DEPENDENT_PARASITE_NO_GEM_ABSTENTION
        elif biology_class == BiologyClass.HUMAN_MONOGENIC:
            reason = (f"class '{biology_class.value}' (germline monogenic) requires a declared causal_gene_known "
                      f"descriptor: the causal gene is the target, so target-ID is trivial ONLY when the gene is "
                      f"genetically established (MENDEL1). Without it there is no target -> the router ABSTAINS.")
        elif biology_class == BiologyClass.HUMAN_COMPLEX_DISEASE:
            reason = (f"class '{biology_class.value}' (common/polygenic) requires a declared has_gwas_evidence "
                      f"descriptor: the validated signal is popularity-controlled GWAS->target (GENETICS1), a "
                      f"DATA-dependent capped/attenuated signal. Without GWAS evidence there is no signal -> the "
                      f"router ABSTAINS rather than emit a fame-confounded human target guess.")
        else:
            reason = (f"no validated discovery signal transfers to class '{biology_class.value}'; "
                      f"the system refuses to emit a confident answer rather than force an ill-fitting model")
        return RoutingDecision(organism=organism, biology_class=biology_class.value, class_source=class_source,
                               output_type="abstention", signals_fired=sorted(fired),
                               supporting_signals=sorted(supporting), signals_gated_out=gated, abstention=reason,
                               intervention=interv)

    # structural-only route (virus): the fired discovery signal is structural class-ID, FBA/repurposing gated
    if output_mode_override:
        out = output_mode_override                       # COMPOSITE4: monogenic -> intervention-MODE reasoning
    elif fired == [Signal.STRUCTURAL_HOMOLOGY.value]:
        out = "structural_class_id"
    else:
        out = "shortlist"
    caps = [f["confidence_cap"] for f in uncertainty_flags if f["confidence_cap"] is not None]
    return RoutingDecision(organism=organism, biology_class=biology_class.value, class_source=class_source,
                           output_type=out, signals_fired=sorted(fired), intervention=interv,
                           supporting_signals=sorted(supporting), signals_gated_out=gated, abstention=None,
                           uncertain=bool(uncertainty_flags),
                           uncertainty_flags=sorted(uncertainty_flags, key=lambda f: f["signal"]),
                           confidence_cap=(min(caps) if caps else None))


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
               host_dependent: Optional[bool] = None,
               has_curated_gem: bool = False, has_gwas_evidence: bool = False,
               causal_gene_known: bool = False, intervention_features: Optional[dict] = None) -> RoutingDecision:
        cls, src = detect_class(proteome_size=proteome_size, declared_class=declared_class,
                                host_dependent=host_dependent)
        return decide(cls, organism=organism, class_source=src, has_curated_gem=has_curated_gem,
                      has_gwas_evidence=has_gwas_evidence, causal_gene_known=causal_gene_known,
                      intervention_features=intervention_features)

    # ---- ROUTERAUTO1: AUTONOMOUS class detection from objective features, then the UNCHANGED gate -----
    def decide_auto(self, organism: str, features=None,
                    declared_class: Optional[BiologyClass] = None,
                    intervention_features: Optional[dict] = None) -> RoutingDecision:
        """Front-end for `decide`: AUTO-detect the biology class from objective `ProteomeFeatures`
        (intercepta.class_detector) and then apply the UNCHANGED COMPOSITE1/2/3 transfer-gate logic. This is
        the automation that completes limitation 12 — the class no longer has to be hand-specified. The data
        descriptors carried on the features (has_curated_gem) are passed through to `decide` verbatim, so the
        capped/flagged COMPOSITE3 behaviour is preserved exactly. Pure logic; no I/O.

        `features` is a `class_detector.ProteomeFeatures`. `declared_class` (optional) still wins if supplied,
        keeping full backward compatibility with the hand-specified path."""
        from .class_detector import detect_biology_class, ProteomeFeatures
        f = features if features is not None else ProteomeFeatures()
        det = detect_biology_class(features=f, declared_class=declared_class)
        dec = decide(BiologyClass(det.biology_class), organism=organism, class_source=det.source,
                     has_curated_gem=f.has_curated_gem, has_gwas_evidence=f.has_gwas_evidence,
                     causal_gene_known=f.causal_gene_known, intervention_features=intervention_features)
        # surface the detection trace on the decision so callers can audit WHY this class was chosen
        dec.detection = det.to_dict()
        return dec

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

    @staticmethod
    def fba_capped_shortlist_from_committed(metrics_path: str, organism: str) -> dict:
        """HOST-DEPENDENT-PARASITE CAPPED-FBA firing path (COMPOSITE3). Surfaces a committed parasite FBA
        essentiality result (HARDENP1 iTgo2020 / GENERALIZE5 iPfal19) as a CAPPED, UNCERTAINTY-FLAGGED
        shortlist. REUSES the committed metrics — it does NOT recompute FBA a different way.

        CRUCIAL HONESTY: the router fires this signal PROSPECTIVELY at capped confidence purely because a
        curated GEM exists; the OR/recall reported here is the A-POSTERIORI validation (knowable ONLY with a
        screen the novel organism lacks), NOT an a-priori input to the routing decision. The uncertainty flag
        below is the a-priori state; the `a_posteriori_validation` block is the retrospective truth."""
        import json
        spec = TRANSFER_GATE[Signal.FBA_ESSENTIALITY]
        p = json.load(open(metrics_path))["payload"]
        pr = p["primary"]
        return {
            "signal": "fba_essentiality (CAPPED / uncertainty-flagged; host-dependent GEM-topology-contingent)",
            "organism": organism,
            "model": p.get("model", ""),
            "confidence_cap": spec.confidence_cap,
            "uncertain": True,
            "uncertainty_note": spec.uncertainty_note,
            "uncertain_evidence": spec.uncertain_evidence,
            "a_posteriori_validation": {   # retrospective truth — NOT available a-priori for a novel organism
                "odds_ratio": pr["odds_ratio"], "recall": pr["recall"], "precision": pr["precision"],
                "fisher_p_greater": pr["fisher_p_greater"], "auroc": pr["auroc"],
                "bacterial_gate_pass": pr["gate_pass"],
                "note": ("this OR/recall is knowable ONLY with an experimental screen; a NOVEL host-dependent "
                         "organism has none, so the router could NOT have known a-priori whether FBA would "
                         "pass (Toxoplasma) or fail (Plasmodium) -- hence the capped confidence + flag"),
            },
            "scope": ("host-dependent-parasite FBA essentiality (in-silico vs a published screen); fires at "
                      "CAPPED confidence because a curated GEM exists, but transfer reliability is "
                      "GEM-topology-contingent and validated at only n=2; NOT bacterial-grade; not wet-lab; "
                      "candidate HYPOTHESES only"),
        }

    # ---------------------------------------------------------------------------------------------------
    # OPTIONAL ADVISORY DIAGNOSTIC — HEURISTIC, **NOT VALIDATED**. Reported as context ONLY. NEVER gates.
    # ---------------------------------------------------------------------------------------------------
    @staticmethod
    def gem_topology_advisory(n_fba_essential: int, n_model_genes: int, organism: str = "") -> dict:
        """ADVISORY-ONLY, screen-free GEM-topology descriptor: the fraction of model genes that are FBA-essential
        under the default medium. It is offered as CONTEXT for a human reader, NOT as a predictor of FBA
        reliability and NOT as a routing gate.

        **EXPLICIT HONESTY (do not read this as a solution):** at n=2 this descriptor does NOT separate the FBA
        PASS from the FAIL a-priori. Toxoplasma (PASS, OR 14.10) has FBA-essential fraction ~0.25; Plasmodium
        (FAIL, OR 2.47) has ~0.17 -- i.e. the FAILING organism has the LOWER essential fraction, so any naive
        'more essentials = more reliable' reading is unsupported (n=2, no threshold can be set, direction may not
        generalize). The real discriminators between the two (recall 0.51 vs 0.20; base rate 0.42 vs 0.64)
        require the very experimental screen a novel organism lacks. Separating a Plasmodium-type failure from a
        Toxoplasma-type success a-priori is an UNSOLVED problem. This function therefore NEVER gates the router;
        the router fires capped-and-flagged regardless of this number."""
        frac = round(n_fba_essential / n_model_genes, 4) if n_model_genes else None
        return {
            "diagnostic": "gem_topology_advisory (frac_genes_fba_essential_default_medium)",
            "status": "HEURISTIC / ADVISORY / NOT VALIDATED — reported as context only, NEVER gates routing",
            "organism": organism,
            "n_fba_essential": n_fba_essential,
            "n_model_genes": n_model_genes,
            "frac_fba_essential": frac,
            "does_not_predict_fba_reliability": True,
            "why_not_validated": ("n=2: Toxoplasma frac ~0.25 PASS vs Plasmodium frac ~0.17 FAIL -- the FAILING "
                                  "organism has the LOWER fraction, so no direction/threshold is established; the "
                                  "true discriminators (recall, base rate) need an experimental screen a novel "
                                  "organism does not have. Separating pass from fail a-priori is UNSOLVED."),
        }
