"""Data-free unit tests for the INTERCEPTA extensible evidence substrate (src/intercepta/substrate.py).
Tests the core governance logic — provenance-tier quarantine, hard safety filters, honest abstention, tiered
composition ranking — with synthetic providers (no external data). Fast + CI-able.
"""
import pytest

from intercepta.substrate import (
    ProvenanceTier, SignalRole, EvidenceRecord, EvidenceProvider, EvidenceStore, TargetEngine, Query,
)


class StaticProvider(EvidenceProvider):
    """Yields pre-set records; used to drive the core deterministically in tests."""
    def __init__(self, name, signal, role, tier, values, direction=1.0):
        self.name, self.signal, self.role, self.tier, self._v, self.direction = name, signal, role, tier, values, direction

    def provide(self, query):
        for e, val in self._v.items():
            if e in query.entities:
                yield self._rec(e, val)


def _q(entities):
    return Query(pathogen="testbug", entities=entities)


# ---- provenance tiering / quarantine (the anti-self-deception guardrail) ----
def test_store_quarantines_self_generated_and_excludes_from_active():
    st = EvidenceStore()
    rec = EvidenceRecord("P1", "sig", 1.0, SignalRole.RANK, "prov", ProvenanceTier.OWN_SINGLE)
    st.add([rec])                                   # self-generated single-run -> quarantined
    assert len(st) == 1
    assert st.active() == []                         # quarantined never surfaces for a decision
    assert st.promote("prov") == 1                   # after reproduction, promote
    act = st.active()
    assert len(act) == 1 and act[0].tier == ProvenanceTier.OWN_REPRODUCED


def test_external_and_reproduced_are_active_immediately():
    st = EvidenceStore()
    st.add([EvidenceRecord("P1", "s", 1.0, SignalRole.RANK, "p", ProvenanceTier.EXTERNAL_VALIDATED),
            EvidenceRecord("P2", "s", 1.0, SignalRole.RANK, "p", ProvenanceTier.OWN_REPRODUCED)])
    assert len(st.active()) == 2


# ---- hard safety filter (FRONT1/E2E2: selectivity is a hard constraint, not a soft feature) ----
def test_safety_filter_excludes_entity_by_construction():
    eng = TargetEngine().register(
        StaticProvider("rank", "essential", SignalRole.RANK, ProvenanceTier.OWN_REPRODUCED, {"P1": 1, "P2": 1})
    ).register(
        StaticProvider("host", "host_homolog_toxic", SignalRole.SAFETY_FILTER, ProvenanceTier.EXTERNAL_VALIDATED, {"P2": 1})
    )
    v = {x.entity: x for x in eng.query(_q(["P1", "P2"]))}
    assert v["P2"].safe is False and v["P2"].confidence == "excluded"
    assert v["P1"].safe is True
    # excluded entity must not appear in the shortlist
    assert [x.entity for x in eng.shortlist(_q(["P1", "P2"]))] == ["P1"]


# ---- honest abstention (TID1/TID3: no signal => low-confidence, never silently ranked) ----
def test_abstain_when_no_rank_evidence():
    eng = TargetEngine().register(
        StaticProvider("rank", "essential", SignalRole.RANK, ProvenanceTier.OWN_REPRODUCED, {"P1": 1})
    )
    v = {x.entity: x for x in eng.query(_q(["P1", "P2"]))}
    assert v["P2"].abstain is True and v["P2"].confidence == "low"   # P2 has no evidence
    assert v["P1"].abstain is False


def test_explicit_abstain_signal_flags_low_confidence():
    eng = TargetEngine().register(
        StaticProvider("rank", "cons", SignalRole.RANK, ProvenanceTier.OWN_REPRODUCED, {"P1": 5.0})
    ).register(
        StaticProvider("ad", "out_of_domain", SignalRole.ABSTAIN, ProvenanceTier.OWN_REPRODUCED, {"P1": 1})
    )
    v = {x.entity: x for x in eng.query(_q(["P1"]))}
    assert v["P1"].abstain is True and v["P1"].confidence == "low"


# ---- tiered composition ranking ----
def test_higher_rank_signal_ranks_higher_and_needs_two_for_high_confidence():
    eng = TargetEngine().register(
        StaticProvider("cons", "conservation", SignalRole.RANK, ProvenanceTier.OWN_REPRODUCED, {"P1": 10, "P2": 1, "P3": 5})
    ).register(
        StaticProvider("ess", "essentiality", SignalRole.RANK, ProvenanceTier.OWN_REPRODUCED, {"P1": 1, "P2": 0, "P3": 1})
    )
    vs = eng.query(_q(["P1", "P2", "P3"]))
    order = [v.entity for v in vs]
    assert order[0] == "P1"                          # highest on both signals
    assert vs[0].confidence == "high"                # two RANK signals -> high confidence
    assert order.index("P3") < order.index("P2")     # P3 beats P2


def test_below_min_decision_tier_evidence_does_not_drive_decision():
    # a RANK signal at OWN_HYPOTHESIS is below the default min_decision_tier -> ignored for ranking -> abstain
    eng = TargetEngine(min_decision_tier=ProvenanceTier.OWN_REPRODUCED).register(
        StaticProvider("weak", "guess", SignalRole.RANK, ProvenanceTier.OWN_HYPOTHESIS, {"P1": 9.0})
    )
    v = {x.entity: x for x in eng.query(_q(["P1"]))}
    assert v["P1"].abstain is True                    # unvalidated evidence can't make it a confident target


# ---- advisory flags (E2E2/FRONT2: state what we cannot yet know) ----
def test_flag_surfaces_needs_experimental_selectivity():
    eng = TargetEngine().register(
        StaticProvider("rank", "essential", SignalRole.RANK, ProvenanceTier.OWN_REPRODUCED, {"P1": 1})
    ).register(
        StaticProvider("sel", "needs_experimental_selectivity", SignalRole.FLAG, ProvenanceTier.OWN_REPRODUCED, {"P1": 1})
    )
    v = {x.entity: x for x in eng.query(_q(["P1"]))}
    assert "needs_experimental_selectivity" in v["P1"].flags


# ---- entity-agnostic: the SAME core ranks MOLECULES via molecule providers (SUBSTRATE2) ----
def test_substrate_is_entity_agnostic_ranks_molecules_and_excludes_pains():
    pytest.importorskip("rdkit")
    from intercepta.substrate_providers import QEDProvider, SAscoreProvider, StructuralAlertSafetyProvider
    aspirin = "CC(=O)Oc1ccccc1C(=O)O"
    quinone = "O=C1C=CC(=O)C=C1"          # 1,4-benzoquinone -> PAINS quinone alert
    eng = (TargetEngine()
           .register(QEDProvider())
           .register(SAscoreProvider())
           .register(StructuralAlertSafetyProvider()))
    v = {x.entity: x for x in eng.query(Query(pathogen="lib", entities=[aspirin, quinone]))}
    # aspirin: safe, two RANK signals (QED + SAscore) -> high confidence, in shortlist
    assert v[aspirin].safe is True and v[aspirin].confidence == "high"
    # PAINS quinone: excluded by construction, never in the shortlist
    assert v[quinone].safe is False and v[quinone].confidence == "excluded"
    sl = [x.entity for x in eng.shortlist(Query(pathogen="lib", entities=[aspirin, quinone]))]
    assert aspirin in sl and quinone not in sl


# ---- CLI: the substrate as a shipped tool (source-agnostic evidence composition) ----
def test_cli_substrate_composes_evidence_with_governance(tmp_path):
    import pandas as pd
    from intercepta.cli import main as cli_main
    ev = tmp_path / "ev.csv"
    ev.write_text(
        "entity,signal,value,role,tier,direction\n"
        "P1,essentiality,1,rank,own_reproduced,1\n"
        "P1,conservation,8,rank,own_reproduced,1\n"          # P1: two signals -> high
        "P2,host_toxic,1,safety_filter,external_validated,1\n"  # P2: excluded by safety
        "P2,essentiality,1,rank,own_reproduced,1\n"
        "P4,guess,9,rank,own_hypothesis,1\n"                 # P4: below min-tier -> quarantined -> abstain
    )
    out = tmp_path / "out.csv"
    rc = cli_main(["substrate", "--evidence", str(ev), "--out", str(out)])
    assert rc == 0
    df = pd.read_csv(out).set_index("entity")
    assert bool(df.loc["P1", "safe"]) and df.loc["P1", "confidence"] == "high"
    assert not bool(df.loc["P2", "safe"]) and df.loc["P2", "confidence"] == "excluded"
    assert bool(df.loc["P4", "abstain"])                    # unvalidated evidence cannot drive a decision (guardrail)
