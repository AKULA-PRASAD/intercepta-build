"""INTERCEPTA unified end-to-end DISCOVERY ENGINE — the concrete embodiment of the north-star vision:
`pathogen genome -> ranked, SAFE, confidence-tiered, provenance-tagged, abstaining target shortlist`, composing EVERY
signal the program validated, in one call, on a disease-agnostic core (charter U2).

It assembles the substrate `TargetEngine` from a pathogen's proteome + evidence caches, wiring the validated providers:
  - FBA gene-ESSENTIALITY (MET1-3) — **the mechanism signal, EXPERIMENTALLY VALIDATED vs gene-knockout data in 5 organisms
    incl. 2 held-out WHO pathogens (VAL-ESS; OR 7.9-64)** — the arc's central positive.
  - metabolic CHOKEPOINT (FRONT1); CONSERVATION to other organisms' known targets (TID1);
  - CONSERVATION BREADTH (REACH1) — a confound-robust recall signal for the FBA-blind non-metabolic half;
  - STRUCTURAL homology (FOLD1/2) — target-specific, for phylogenetically-isolated pathogens where sequence fails;
  - a HARD host-non-homology SAFETY filter (FRONT1/E2E2) that excludes host-toxic targets by construction, and FLAGS
    host-homologous survivors `needs_experimental_selectivity`.
Confidence is CALIBRATED to accuracy (CALIB1: high>moderate>low tracks real target-recovery precision). Signals with no
usable evidence trigger honest ABSTENTION (TID1/TID3/TID4). Self-generated / below-tier evidence is quarantined (the
living-net guardrail).

HONEST SCOPE (baked into every report): outputs are confidence-tiered candidate HYPOTHESES with full provenance, NOT
validated drug targets and NOT drugs. The essentiality *enrichment* is experimentally validated; the drug-target,
selectivity, and clinical claims are NOT. The MOLECULE half is honestly gated: turning a target into an intervention needs
either the target's 3D structure (docking; weak early-enrichment per C1/HIT2) or activity data (QSAR; unavailable at zero
data) — `intercepta discover` / `generate` / `screen` produce developability-filtered candidate matter, which are
hypotheses, not target-specific actives. Not wet-lab.
"""
from __future__ import annotations
import os
from .substrate import TargetEngine, Query, ProvenanceTier
from . import substrate_providers as P

_TIER_NAME = {ProvenanceTier.QUARANTINED: "quarantined", ProvenanceTier.OWN_HYPOTHESIS: "own_hypothesis",
              ProvenanceTier.OWN_SINGLE: "own_single", ProvenanceTier.OWN_REPRODUCED: "own_reproduced",
              ProvenanceTier.EXTERNAL_VALIDATED: "external_validated"}


class DiscoveryEngine:
    """Composes the validated providers for a pathogen and produces the honest target report. Every wired signal is
    optional: the engine degrades honestly (SUBSTRATE4 behaviour) when a signal's inputs are absent."""

    def __init__(self, pathogen, entities, engine, active_signals):
        self.pathogen, self._entities, self._engine, self.active_signals = pathogen, entities, engine, active_signals

    # ---- assembly ---------------------------------------------------------
    @classmethod
    def for_pathogen(cls, pathogen, proteome_fasta, scratch, essentiality_tsv=None, chokepoint_tsv=None,
                     breadth_tsv=None, reference_targets_fasta=None, human_fasta=None, ceg2_path=None,
                     query_struct_dir=None, ref_struct_dir=None, min_decision_tier=ProvenanceTier.OWN_REPRODUCED,
                     entities=None):
        os.makedirs(scratch, exist_ok=True)
        eng = TargetEngine(min_decision_tier=min_decision_tier)
        active = []
        # entities: genome-scale = every protein in the proteome
        accs = entities or [ (ln[1:].split()[0].split("|")[1] if "|" in ln else ln[1:].split()[0])
                             for ln in open(proteome_fasta) if ln.startswith(">") ]
        if essentiality_tsv and os.path.exists(essentiality_tsv):
            eng.register(P.CacheRankProvider(essentiality_tsv, pathogen, "fba_essential", name="essentiality"))
            active.append("essentiality[VALIDATED:MET1-3+VAL-ESS]")
        if chokepoint_tsv and os.path.exists(chokepoint_tsv):
            eng.register(P.CacheRankProvider(chokepoint_tsv, pathogen, "metabolic_chokepoint", name="chokepoint"))
            active.append("chokepoint[FRONT1]")
        if breadth_tsv and os.path.exists(breadth_tsv):
            eng.register(P.ConservationBreadthProvider(breadth_path=breadth_tsv))
            active.append("conservation_breadth[REACH1]")
        if reference_targets_fasta and os.path.exists(reference_targets_fasta):
            eng.register(P.ConservationProvider(proteome_fasta, reference_targets_fasta, scratch))
            active.append("conservation[TID1]")
        if query_struct_dir and ref_struct_dir:
            eng.register(P.StructuralHomologyProvider(query_struct_dir, ref_struct_dir, scratch))
            active.append("structural_homology[FOLD1/2]")
        if human_fasta and ceg2_path and os.path.exists(human_fasta) and os.path.exists(ceg2_path):
            eng.register(P.HostToxicSafetyProvider(proteome_fasta, human_fasta, ceg2_path, scratch))
            active.append("host_safety_filter[FRONT1/E2E2]")
        return cls(pathogen, accs, eng, active)

    # ---- run --------------------------------------------------------------
    def verdicts(self):
        return self._engine.query(Query(pathogen=self.pathogen, entities=self._entities))

    def report(self, top=25):
        vs = self.verdicts()
        by_conf = {"high": 0, "moderate": 0, "low": 0, "excluded": 0}
        for v in vs:
            by_conf[v.confidence] = by_conf.get(v.confidence, 0) + 1
        safe_ranked = [v for v in vs if v.safe and not v.abstain]
        # honest confidence diagnostic: near-universal RANK signals (conservation/breadth) can SATURATE the "high" tier
        n_ranked = max(len(vs) - by_conf.get("excluded", 0), 1)
        high_frac = round(by_conf.get("high", 0) / n_ranked, 3)
        conf_note = ("confidence tier is DISCRIMINATIVE (CALIB1 regime)" if high_frac <= 0.5 else
                     f"WARNING: confidence tier SATURATED ({high_frac:.0%} of ranked entities are 'high') because "
                     f"near-universal signals (conservation/breadth) fire for most genes in this full-signal genome-scale "
                     f"config -> the 'high' label is NOT discriminative here; use rank_score for ordering. Confidence is "
                     f"discriminative only with emit-if-positive signals (CALIB1).")
        shortlist = []
        for v in safe_ranked[:top]:
            sigs = sorted({r.signal for r in v.evidence if _TIER_NAME.get(r.tier) not in (None,)})
            shortlist.append({"entity": v.entity, "confidence": v.confidence,
                              "rank_score": round(float(v.rank_score), 4),
                              "signals": [r.signal for r in v.evidence],
                              "flags": list(v.flags),
                              "top_tier": max((_TIER_NAME.get(r.tier, "?") for r in v.evidence), default="-")})
        return {
            "pathogen": self.pathogen,
            "n_entities": len(self._entities),
            "active_signals": self.active_signals,
            "confidence_histogram": by_conf,
            "high_fraction_of_ranked": high_frac,
            "confidence_note": conf_note,
            "n_excluded_by_safety": by_conf.get("excluded", 0),
            "n_abstained": sum(1 for v in vs if v.abstain),
            "n_confident_safe_targets": len(safe_ranked),
            "shortlist": shortlist,
            "honest_scope": ("Confidence-tiered candidate HYPOTHESES with provenance — NOT validated targets or drugs. "
                             "The essentiality ENRICHMENT is experimentally validated (VAL-ESS, 5 organisms); the "
                             "drug-target/selectivity/clinical claims are NOT. Molecule half is gated (needs structure or "
                             "activity data); candidate matter from generate/screen are hypotheses. Not wet-lab."),
        }
