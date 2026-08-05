"""Real evidence providers for the INTERCEPTA substrate — adapters wrapping the VALIDATED zero-data signals.

Each provider is a pluggable adapter (U2): the core `TargetEngine` composes them without knowing they call mmseqs / read a
metabolic-essentiality cache / etc. Heavy deps (subprocess to mmseqs) are used lazily so importing the core never needs them.
Every provider's `tier` reflects its LEDGER validation status, and every provider carries honest scope in its docstring.

Providers:
- ConservationProvider   — RANK. Homology to other organisms' known targets (TID1; the robust-but-dangerous workhorse).
- CacheRankProvider      — RANK. Reads a UniProt-keyed TSV cache (FBA essentiality [MET1-3, the mechanism that broke the
                           ceiling] or metabolic chokepoint [FRONT1]).
- HostToxicSafetyProvider — SAFETY_FILTER + FLAG. Host non-homology selectivity (FRONT1/E2E2): a pathogen protein whose
                           human homolog is core-essential (Hart CEG2) is HOST-TOXIC -> excluded by construction; a
                           host-homologous-but-not-toxic protein gets a `needs_experimental_selectivity` FLAG (E2E2/FRONT2:
                           sequence/apo-structure cannot resolve true selectivity).
- NoHomologAbstainProvider — ABSTAIN. Proteins with no conservation homolog are out-of-domain / low-confidence (TID1).
"""
from __future__ import annotations
import os, shutil, subprocess
from .substrate import EvidenceProvider, SignalRole, ProvenanceTier, EvidenceRecord

_MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")


def _best_bits(query_fasta, target_fasta, scratch, tag, evalue="1e-3"):
    out = os.path.join(scratch, f"{tag}.m8"); tmp = os.path.join(scratch, f"tmp_{tag}")
    shutil.rmtree(tmp, ignore_errors=True)
    subprocess.run([_MMSEQS, "easy-search", query_fasta, target_fasta, out, tmp, "--threads", "4", "-e", evalue,
                    "-s", "5.7", "--format-output", "query,target,bits", "-v", "1"], capture_output=True, text=True)
    best = {}
    if os.path.exists(out):
        for ln in open(out):
            p = ln.rstrip("\n").split("\t")
            if len(p) < 3: continue
            q = p[0].split("|")[1] if "|" in p[0] else p[0]
            tgt = p[1].split("|")[1] if "|" in p[1] else p[1]; b = float(p[2])
            if q not in best or b > best[q][1]: best[q] = (tgt, b)
    shutil.rmtree(tmp, ignore_errors=True)
    return best


class ConservationProvider(EvidenceProvider):
    """RANK by homology (best mmseqs bitscore) to a reference set of OTHER organisms' known targets. Reproduced (TID1)."""
    role = SignalRole.RANK
    tier = ProvenanceTier.OWN_REPRODUCED
    direction = 1.0

    def __init__(self, query_fasta, target_fasta, scratch, name="conservation", signal="conservation"):
        self.name, self.signal = name, signal
        self._qf, self._tf, self._scr = query_fasta, target_fasta, scratch
        self._best = None

    def best(self):
        if self._best is None:
            self._best = _best_bits(self._qf, self._tf, self._scr, "cons")
        return self._best

    def provide(self, query):
        b = self.best()
        for e in query.entities:
            yield self._rec(e, b.get(e, (None, 0.0))[1])


class CacheRankProvider(EvidenceProvider):
    """RANK from a UniProt-keyed TSV cache. col_key/col_val select the columns; org filters column 0. Reproduced."""
    role = SignalRole.RANK
    tier = ProvenanceTier.OWN_REPRODUCED

    def __init__(self, cache_path, org, signal, name=None, org_col=0, key_col=1, val_col=2, direction=1.0):
        self.name = name or signal; self.signal = signal; self.direction = direction
        self._vals = {}
        for ln in open(cache_path):
            p = ln.rstrip("\n").split("\t")
            if len(p) <= max(org_col, key_col, val_col) or p[org_col] != org: continue
            try: self._vals[p[key_col]] = float(p[val_col])
            except ValueError: continue

    def provide(self, query):
        for e in query.entities:
            if e in self._vals:
                yield self._rec(e, self._vals[e])


class HostToxicSafetyProvider(EvidenceProvider):
    """SAFETY_FILTER (host-toxic) + FLAG (needs_experimental_selectivity). External CEG2 + human proteome. EXTERNAL tier."""
    tier = ProvenanceTier.EXTERNAL_VALIDATED

    def __init__(self, query_fasta, human_fasta, ceg2_path, scratch, name="host_selectivity"):
        self.name, self.signal, self.role = name, "host_toxic", SignalRole.SAFETY_FILTER
        self._qf, self._human, self._scr = query_fasta, human_fasta, scratch
        self._ceg2 = set(ln.split("\t")[0].strip() for ln in open(ceg2_path) if ln.split("\t")[0].strip() != "GENE")
        self._acc2sym = {}
        for ln in open(human_fasta):
            if not ln.startswith(">"): continue
            acc = ln[1:].split()[0].split("|")[1] if "|" in ln else ln[1:].split()[0]
            for tok in ln.split():
                if tok.startswith("GN="): self._acc2sym[acc] = tok[3:]; break
        self._host = None

    def host(self):
        if self._host is None:
            self._host = _best_bits(self._qf, self._human, self._scr, "host", evalue="1e-4")
        return self._host

    def provide(self, query):
        host = self.host()
        for e in query.entities:
            if e in host:                                        # has a human homolog
                sym = self._acc2sym.get(host[e][0], "")
                if sym in self._ceg2:                            # human homolog is core-essential -> HOST-TOXIC
                    yield EvidenceRecord(e, "host_toxic", 1.0, SignalRole.SAFETY_FILTER, self.name, self.tier,
                                         meta={"human_homolog": host[e][0], "human_symbol": sym})
                else:                                            # host-homologous but not core-essential -> flag uncertainty
                    yield EvidenceRecord(e, "needs_experimental_selectivity", 1.0, SignalRole.FLAG, self.name, self.tier,
                                         meta={"human_homolog": host[e][0]})


class NoHomologAbstainProvider(EvidenceProvider):
    """ABSTAIN for proteins with NO conservation homolog (out-of-domain / low-confidence; TID1 calibrated abstention)."""
    role = SignalRole.ABSTAIN
    tier = ProvenanceTier.OWN_REPRODUCED

    def __init__(self, conservation_provider: ConservationProvider, name="no_homolog_abstain"):
        self.name, self.signal, self._cons = name, "no_homolog", conservation_provider

    def provide(self, query):
        b = self._cons.best()
        for e in query.entities:
            if b.get(e, (None, 0.0))[1] <= 0.0:
                yield self._rec(e, 1.0)


# ==========================================================================================================
# BACK-HALF (molecule) providers — demonstrate the substrate is ENTITY-AGNOSTIC: the SAME core that ranks
# proteins (front half) ranks candidate MOLECULES (back half). Entities are SMILES; free RDKit descriptors
# (no training needed). These wrap standard published methods, tiered accordingly.
# ==========================================================================================================
_SASCORER = None


def _mol(smiles):
    from rdkit import Chem
    return Chem.MolFromSmiles(smiles)


class QEDProvider(EvidenceProvider):
    """RANK candidate molecules by QED drug-likeness (Bickerton 2012; published metric). Entities are SMILES."""
    role = SignalRole.RANK
    tier = ProvenanceTier.EXTERNAL_VALIDATED
    direction = 1.0
    name = "qed"
    signal = "qed_druglikeness"

    def provide(self, query):
        from rdkit.Chem import QED
        for smi in query.entities:
            m = _mol(smi)
            if m is not None:
                yield self._rec(smi, float(QED.qed(m)))


class SAscoreProvider(EvidenceProvider):
    """RANK candidate molecules by synthetic accessibility (Ertl 2009 SAscore; lower is easier -> direction=-1)."""
    role = SignalRole.RANK
    tier = ProvenanceTier.OWN_REPRODUCED
    direction = -1.0
    name = "sascore"
    signal = "synthetic_accessibility"

    def provide(self, query):
        global _SASCORER
        if _SASCORER is None:
            import os, sys
            from rdkit.Chem import RDConfig
            sys.path.append(os.path.join(RDConfig.RDContribDir, "SA_Score"))
            import sascorer as _s
            _SASCORER = _s
        for smi in query.entities:
            m = _mol(smi)
            if m is not None:
                yield self._rec(smi, float(_SASCORER.calculateScore(m)))


class StructuralAlertSafetyProvider(EvidenceProvider):
    """SAFETY_FILTER for candidate molecules: a PAINS (pan-assay-interference) structural alert EXCLUDES the molecule by
    construction — the molecule-half analogue of the host-toxic filter (Baell & Holloway 2010; RDKit FilterCatalog)."""
    tier = ProvenanceTier.EXTERNAL_VALIDATED
    name = "structural_alert"
    signal = "pains_alert"
    role = SignalRole.SAFETY_FILTER

    def __init__(self):
        from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams
        p = FilterCatalogParams(); p.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
        self._cat = FilterCatalog(p)

    def provide(self, query):
        for smi in query.entities:
            m = _mol(smi)
            if m is not None and self._cat.HasMatch(m):
                yield self._rec(smi, 1.0)
