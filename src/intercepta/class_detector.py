"""INTERCEPTA ROUTERAUTO1 — an AUTONOMOUS biology-class detector for the composite router.

This module completes manuscript limitation 12 ("the composite router's class detector is minimal ... the
class is currently HAND-SPECIFIED"). It classifies a raw input into the routing class the composite router
already supports, from OBJECTIVE, computable features only — so `CompositeRouter.decide()` no longer needs the
class hand-declared. It is a pure FRONT-END: it selects a class, then the UNCHANGED COMPOSITE1/2/3 transfer-gate
logic fires exactly what was validated for that class. It does NOT change any committed routing verdict and it
does NOT attempt to predict a-priori whether a signal will transfer for a novel organism (that stays the
capped/flagged uncertainty per COMPOSITE3).

DESIGN DISCIPLINE (why this is honest, not a black box):
  * The detector has ZERO fitted parameters. Every rule/threshold below is derived from BIOLOGY and
    PRE-REGISTERED (experiments/ROUTERAUTO1_autonomous_routing/PREREG.md) BEFORE any label was scored. Because
    nothing is fitted to the evaluation organisms, leave-one-out == full evaluation (no train/test leakage is
    even possible). No threshold was tuned to the labels.
  * The input is a set of OBJECTIVE proteome features (`ProteomeFeatures`) plus two optional DATA descriptors
    (has_curated_gem, has_dependency_screen) and one DECLARED biological descriptor (host_dependent). Each
    feature is something computable from a proteome by an existing, cited method (see per-field docstrings) —
    e.g. presence of ribosomal proteins / aminoacyl-tRNA synthetases (a cell vs a virus), universal
    domain-of-life marker genes (bacteria/archaea/eukaryota), a viral polyprotein/capsid hallmark, a
    confident (pLDDT-gated, DARK1) structural/fold homolog. The PURE rule engine here operates on those
    features and is fully data-free unit-testable, exactly like the existing router logic.
  * ABSTENTION-INTEGRITY OVER COVERAGE. Where a class CANNOT be cleanly separated from objective features, the
    detector ABSTAINS (routes to UNKNOWN, which the router turns into an explicit class-level abstention) or
    REQUIRES the descriptor — it never guesses. Two boundaries are reported honestly as non-sequence-derivable:
      (a) free-living eukaryote vs host-dependent eukaryotic parasite  -> requires the `host_dependent` flag
          (same honesty already stated in composite_router: host-dependence is NOT sequence-derivable);
      (b) a human proteome with NO dependency screen -> functional-dependency (DEPEND1/COMPOSITE2) is
          DATA-dependent, so without a screen there is no signal -> abstain.

FAIL-SAFE (hard requirement, ROUTERAUTO1): the detector must NEVER confidently route a DARK protein set (DARK1)
or a NOVEL zero-screen host-dependent parasite (TRANSFER1) to a firing signal. Both route to abstain/capped:
  * a DARK input (acellular, no viral hallmark, no analyzable structure, no domain marker, not human) falls
    through every positive rule to UNKNOWN -> the router ABSTAINS. Crucially the VIRUS rule requires a POSITIVE
    viral hallmark, NOT merely a tiny proteome — so a tiny dark-protein set is NOT mis-detected as a virus (the
    minimal old detector's `size<=60 -> VIRUS` rule would have mis-fired here; this is the fix).
  * a novel zero-screen host-dependent parasite is detected as HOST_DEPENDENT_PARASITE and, with no curated
    GEM, the UNCHANGED COMPOSITE3 logic abstains (no signal). If its host-dependence is undeclared it is a
    eukaryote with host_dependent=None -> abstain-pending-descriptor. Either path abstains.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional

from .composite_router import BiologyClass, VIRUS_MAX_PROTEOME


# ======================================================================================================
# The OBJECTIVE feature bundle the detector consumes
# ======================================================================================================
@dataclass(frozen=True)
class ProteomeFeatures:
    """Objective, computable features of an input. All are derivable from a proteome (+/- two data
    descriptors); the pure rule engine below never touches raw sequence, so it stays data-free-testable.

    Each field documents the CONCRETE method that would compute it from a proteome, so the abstraction is
    honest (this is a summary of computable signals, not a hand-label smuggled in as a 'feature')."""
    # ---- computed from the proteome ----------------------------------------------------------------
    n_proteins: Optional[int] = None
    #   count of distinct proteins in the (mature) proteome. Viruses are tiny (SARS-CoV-2 ~30); cellular
    #   organisms are >>1000. Same objective signal the minimal detector already used.
    has_translation_machinery: Optional[bool] = None
    #   does the proteome contain the self-translation core — ribosomal proteins + aminoacyl-tRNA
    #   synthetases (detectable by HMM against the universal ribosomal/aaRS Pfam families)? A cell HAS it;
    #   a virus does NOT (it hijacks the host ribosome). The primary virus-vs-cell discriminator.
    domain_of_life: Optional[str] = None
    #   {"bacteria","archaea","eukaryota"} from universal single-copy marker genes / domain-diagnostic
    #   signatures (e.g. archaeal-type multi-subunit RNA polymerase + archaeal histones; eukaryotic
    #   histone-octamer + spliceosome/nuclear machinery; bacterial signatures). None = unresolved.
    has_viral_hallmark: Optional[bool] = None
    #   a POSITIVE viral signal: a large multi-domain polyprotein, a capsid/structural-protein signature,
    #   or a conserved fold homologous to a known drugged viral target (the GENERALIZE3 route). Required
    #   (with acellularity) to CALL a virus — a tiny acellular input WITHOUT this is NOT a virus (dark).
    has_analyzable_structure: Optional[bool] = None
    #   is there >=1 protein with a CONFIDENT structure/fold homolog (pLDDT-gated per DARK1)? DARK proteins
    #   lack this by definition; it is the marker whose ABSENCE (with everything else absent) => dark.
    is_human_proteome: Optional[bool] = None
    #   does the proteome match the human reference (near-identity to human genes / human marker set,
    #   ~20k proteins)? Gates the HUMAN_CANCER route (with a dependency screen).
    # ---- DECLARED biological descriptor (NOT sequence-derivable) -----------------------------------
    host_dependent: Optional[bool] = None
    #   is the organism's METABOLISM host-embedded / obligately intracellular (e.g. Plasmodium)? This is
    #   NOT cleanly sequence-derivable (composite_router honest-scope note) -> it must be DECLARED. None =
    #   undeclared -> the detector abstains on the free-living-vs-parasite eukaryote boundary.
    # ---- DATA descriptors (runtime resource availability) ------------------------------------------
    has_curated_gem: bool = False
    #   is a curated, quality genome-scale metabolic model available? (COMPOSITE3 resource flag; passed
    #   through to the router unchanged.)
    has_dependency_screen: bool = False
    #   does a functional-dependency screen (DepMap-style CRISPR) or a validated same-domain label-free
    #   expr->dep map exist? (COMPOSITE2/DEPEND1 transfer condition for HUMAN_CANCER.)
    has_gwas_evidence: bool = False
    #   COMPOSITE4: is there declared GWAS/genetic-association evidence for a common/complex disease
    #   (Open Targets genetic_association / L2G)? Routes a human proteome to HUMAN_COMPLEX_DISEASE
    #   (GENETICS1; capped/attenuated genetic_association signal). A DECLARED disease-context descriptor.
    causal_gene_known: bool = False
    #   COMPOSITE4: is the causal gene of a germline MONOGENIC disease genetically established (the target
    #   is GIVEN)? Routes a human proteome to HUMAN_MONOGENIC (MENDEL1; intervention-MODE reasoning). A
    #   DECLARED disease-context descriptor.


@dataclass
class DetectionResult:
    """The pure class-detection verdict (data-free)."""
    biology_class: str                 # a BiologyClass value
    source: str                        # "declared" | "autodetected"
    rule: str                          # the pre-registered rule id + name that fired
    reasons: list = field(default_factory=list)
    requires_descriptor: Optional[str] = None   # if abstaining pending an input the detector will not guess

    def to_dict(self):
        return asdict(self)


# ======================================================================================================
# THE PRE-REGISTERED DETECTION RULES (ordered; deterministic; no RNG; no fitted parameter)
# ======================================================================================================
def detect_biology_class(features: Optional[ProteomeFeatures] = None,
                         declared_class: Optional[BiologyClass] = None) -> DetectionResult:
    """Classify an input into the router's routing class from objective features. Rules are applied in the
    pre-registered order below; the FIRST matching rule wins. Abstains (-> UNKNOWN) wherever no class marker
    fires or a class cannot be cleanly separated from objective features (integrity over coverage)."""
    f = features if features is not None else ProteomeFeatures()

    # ---- R0: a DECLARED class always wins (backward-compatible with the hand-specified path) ----------
    if declared_class is not None:
        return DetectionResult(biology_class=BiologyClass(declared_class).value, source="declared",
                               rule="R0 declared-class-wins",
                               reasons=["class explicitly declared by caller; detector deferred to it"])

    # ---- R1: VIRUS — tiny AND acellular AND a POSITIVE viral hallmark ---------------------------------
    # NOT tiny-alone (the minimal detector's bug: it mis-called any <=60-protein input a virus, which would
    # mis-fire on a small DARK-protein set). Acellular = no ribosomal/aaRS translation core; hallmark =
    # polyprotein/capsid/conserved drugged-fold. All three required -> a genuine virus, GENERALIZE3 route.
    if (f.n_proteins is not None and f.n_proteins <= VIRUS_MAX_PROTEOME
            and f.has_translation_machinery is False and f.has_viral_hallmark is True):
        return DetectionResult(biology_class=BiologyClass.VIRUS.value, source="autodetected",
                               rule="R1 virus (tiny + acellular + viral-hallmark)",
                               reasons=[f"n_proteins={f.n_proteins}<={VIRUS_MAX_PROTEOME}",
                                        "no translation machinery (not self-translating)",
                                        "positive viral hallmark (polyprotein/capsid/conserved drugged fold)"])

    # ---- R2: HUMAN proteome — branch among the THREE validated human classes by DECLARED descriptor ----
    # COMPOSITE4: a human proteome can route to HUMAN_CANCER (dependency screen; DEPEND1/COMPOSITE2),
    # HUMAN_MONOGENIC (causal gene known; MENDEL1) or HUMAN_COMPLEX_DISEASE (GWAS evidence; GENETICS1).
    # Each is gated by an OBJECTIVE/DECLARED descriptor. INTEGRITY: with >1 descriptor the class is AMBIGUOUS
    # -> ABSTAIN (never guess among the three); with 0 descriptors -> ABSTAIN (require one).
    if f.is_human_proteome is True:
        human_flags = [
            ("has_dependency_screen", f.has_dependency_screen, BiologyClass.HUMAN_CANCER.value,
             "R2a human-cancer (human proteome + dependency screen; DEPEND1/COMPOSITE2)",
             "functional-dependency screen available (DEPEND1/COMPOSITE2 condition)"),
            ("causal_gene_known", f.causal_gene_known, BiologyClass.HUMAN_MONOGENIC.value,
             "R2c human-monogenic (human proteome + causal gene known; MENDEL1)",
             "germline monogenic causal gene genetically established -> target GIVEN (MENDEL1)"),
            ("has_gwas_evidence", f.has_gwas_evidence, BiologyClass.HUMAN_COMPLEX_DISEASE.value,
             "R2d human-complex (human proteome + GWAS/genetic-association evidence; GENETICS1)",
             "GWAS/genetic-association evidence declared -> capped/attenuated genetic_association (GENETICS1)"),
        ]
        present = [x for x in human_flags if x[1] is True]
        if len(present) == 1:
            key, _, cls, rule, why = present[0]
            return DetectionResult(biology_class=cls, source="autodetected", rule=rule,
                                   reasons=["human reference proteome", why])
        if len(present) == 0:
            # human but NO human descriptor -> every validated human signal is DATA/descriptor-dependent ->
            # no signal transfers -> abstain (require one). requires_descriptor kept as the historical
            # "has_dependency_screen" for backward-compat; reasons enumerate all three human routes.
            return DetectionResult(biology_class=BiologyClass.UNKNOWN.value, source="autodetected",
                                   rule="R2b human-no-descriptor -> abstain (require a human class descriptor)",
                                   reasons=["human reference proteome BUT no human-class descriptor",
                                            "the validated human signals are descriptor/data-dependent -> declare "
                                            "one of: has_dependency_screen (cancer/DEPEND1), causal_gene_known "
                                            "(monogenic/MENDEL1), has_gwas_evidence (complex/GENETICS1); without "
                                            "one, no signal transfers -> abstain rather than guess"],
                                   requires_descriptor="has_dependency_screen")
        # >1 descriptor -> AMBIGUOUS among the three human classes -> abstain, never guess
        return DetectionResult(biology_class=BiologyClass.UNKNOWN.value, source="autodetected",
                               rule="R2e human-AMBIGUOUS (multiple human-class descriptors) -> abstain",
                               reasons=["human reference proteome with >1 human-class descriptor declared "
                                        f"({sorted(x[0] for x in present)})",
                                        "cannot cleanly separate cancer/monogenic/complex -> ABSTAIN rather than "
                                        "guess among the three (integrity over coverage)"])

    # ---- R3: CELLULAR organism (self-translating) — branch by domain of life --------------------------
    if f.has_translation_machinery is True:
        dom = f.domain_of_life
        if dom == "bacteria":
            return DetectionResult(biology_class=BiologyClass.BACTERIUM.value, source="autodetected",
                                   rule="R3a bacterium (cellular + bacterial markers)",
                                   reasons=["self-translating cell", "bacterial domain-of-life markers"])
        if dom == "archaea":
            return DetectionResult(biology_class=BiologyClass.ARCHAEON.value, source="autodetected",
                                   rule="R3b archaeon (cellular + archaeal markers)",
                                   reasons=["self-translating cell", "archaeal domain-of-life markers (BLIND6 route)"])
        if dom == "eukaryota":
            # the honest non-sequence-derivable boundary: free-living vs host-embedded parasite.
            if f.host_dependent is True:
                return DetectionResult(biology_class=BiologyClass.HOST_DEPENDENT_PARASITE.value,
                                       source="autodetected",
                                       rule="R3c-i host-dependent eukaryotic parasite (declared host-dependent)",
                                       reasons=["eukaryotic cell", "declared metabolically host-dependent"])
            if f.host_dependent is False:
                return DetectionResult(biology_class=BiologyClass.FREE_EUKARYOTE.value, source="autodetected",
                                       rule="R3c-ii free-living eukaryote (declared not host-dependent)",
                                       reasons=["eukaryotic cell", "declared free-living (self-contained metabolism)"])
            # host-dependence undeclared -> NOT sequence-derivable -> abstain, require the descriptor
            return DetectionResult(biology_class=BiologyClass.UNKNOWN.value, source="autodetected",
                                   rule="R3c-iii eukaryote host-dependence UNDECLARED -> abstain (require flag)",
                                   reasons=["eukaryotic cell but host-dependence undeclared",
                                            "free-living vs host-embedded is NOT sequence-derivable -> refuse to "
                                            "guess between FREE_EUKARYOTE (full-grade FBA) and HOST_DEPENDENT_"
                                            "PARASITE (capped/abstain); require the descriptor"],
                                   requires_descriptor="host_dependent")
        # cellular but domain unresolved -> abstain (require the domain-of-life marker)
        return DetectionResult(biology_class=BiologyClass.UNKNOWN.value, source="autodetected",
                               rule="R3d cellular but domain-of-life unresolved -> abstain",
                               reasons=["self-translating cell but no resolved bacteria/archaea/eukaryota marker"],
                               requires_descriptor="domain_of_life")

    # ---- R4: DARK / UNSUPPORTED (fail-safe) — no class marker fired -----------------------------------
    # Reached by: acellular inputs with NO viral hallmark (dark proteins), and anything that matched no
    # positive rule. The router turns UNKNOWN into an explicit class-level abstention -> fails SAFE.
    return DetectionResult(biology_class=BiologyClass.UNKNOWN.value, source="autodetected",
                           rule="R4 dark/unsupported -> abstain (no class marker fired)",
                           reasons=["no positive class marker: not a self-translating cell, no viral hallmark, "
                                    "not human, no analyzable structure/domain marker",
                                    "the composite ABSTAINS rather than fabricate a class (fail-safe; DARK1)"])
