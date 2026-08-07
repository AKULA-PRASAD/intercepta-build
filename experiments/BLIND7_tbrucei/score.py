"""BLIND7 Stage 2 (REVEAL + SCORE) — adjudicate the LOCKED FBA-essentiality predictions for
Trypanosoma brucei brucei TREU927 against the pre-registered Alsford/Horn 2011 RIT-seq genome-wide
loss-of-fitness screen (bloodstream form), obtained from the pre-registered open TriTrypDB/VEuPathDB mirror.

Blindness trail: the LOCKED predictions were built + git-committed BEFORE any essentiality was fetched.
This script FIRST asserts the locked essential-accession set still hashes to the committed lock
(31e8cc00...) and ABORTS if not — predictions are never modified here.

Essential (experimental) definition — PRIMARY (pre-committed at reveal, before any OR was computed):
  T. brucei bloodstream-form RIT-seq loss-of-fitness = VEuPathDB GenesByHighThroughputPhenotyping,
  profile "T.brucei ... Horn", comparison BFD6 (bloodstream, 6 d / 20 doublings) vs reference No_Tet,
  DOWN-regulated (decrease in RNAi-target coverage), fold-change >= 2, protein-coding.
  SENSITIVITY (reported, not the gate): fold-change >= 1.5 (VEuPathDB tool default) and >= 3.
  NOTE/deviation: the paper's own call is Z-score > 3.3 in Supplemental File 1A, which is behind a
  publisher paywall (genome.cshlp.org, auth-gated; PMC not open-access). The TriTrypDB mirror
  (pre-registered as an acceptable source) re-quantitates the same RIT-seq reads as htseq/tpm
  fold-change; the fold-change proxy is documented here as a deviation, and the verdict is shown
  robust across three fold-change thresholds.

Adjudication = pre-registered sequence-homology bridge (mmseqs easy-search, pident >= 90): the RIT-seq
essential PROTEIN sequences (TREU927 release-68 annotated proteins, mapped old->new gene IDs via the
release-68 GeneAliases crosswalk) are searched against our locked UniProt CarveMe proteome; a GEM gene
(UniProt accession) is 'experimentally essential' if it receives a >=90%-identity hit from an essential
protein. Same namespace-independent method as BLIND1-3.

Gate (identical to BLIND1-6): 2x2 Fisher (one-sided greater) over the 337 GEM genes; PASS iff OR>3 AND p<0.01.
Deterministic: mmseqs run with fixed threads/params; metrics payload hashed (sorted-key JSON, verdict/
provenance excluded). Env: metabolic (scipy). mmseqs: bioinfo env.
"""
import os, sys, json, hashlib, subprocess, shutil, re
from scipy.stats import fisher_exact

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results")
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data"); D = os.path.join(DATA, "blind7")
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
PROTEOME = os.path.join(D, "tbrucei.fasta")                 # our locked CarveMe proteome (UniProt accs)
SUPER_FASTA = os.path.join(D, "ritseq_essential_bfd6_superset_proteins.fasta")  # essential (fc>=1.5) proteins
PID2GENE = os.path.join(D, "ritseq_pid2gene.json")          # protein-id -> new gene id
NEWSETS = os.path.join(D, "ritseq_essential_new_sets.json") # threshold -> [new gene ids]
LOCK_SHA = "31e8cc0047ba7643e40a82ab1b78a18cc92c0af0149f7a5a44bb404e6e6e6b0f"
PIDENT = 90.0
PRIMARY = "fc2"


def load_locked():
    gem, fba = set(), set()
    with open(os.path.join(RES, "LOCKED_predictions.tsv")) as f:
        next(f)
        for ln in f:
            a, s, e, g = ln.rstrip("\n").split("\t"); gem.add(a)
            if e == "1": fba.add(a)
    payload = "\n".join(sorted(fba))
    sha = hashlib.sha256(payload.encode()).hexdigest()
    assert sha == LOCK_SHA, f"LOCK BROKEN: {sha} != {LOCK_SHA} — predictions changed, ABORT."
    return gem, fba


def mmseqs_bridge():
    scr = os.path.join(HERE, "scratch"); shutil.rmtree(scr, ignore_errors=True); os.makedirs(scr)
    out = os.path.join(scr, "ess_hits.m8"); tmp = os.path.join(scr, "tmp")
    subprocess.run([MMSEQS, "easy-search", SUPER_FASTA, PROTEOME, out, tmp, "--threads", "4",
                    "-e", "1e-6", "-s", "5.7", "--format-output", "query,target,pident", "-v", "1"],
                   check=True, capture_output=True, text=True)
    hits = []
    for ln in open(out):
        q, t, pid = ln.rstrip("\n").split("\t")
        hits.append((q, t.split("|")[1] if "|" in t else t, float(pid)))
    shutil.rmtree(scr, ignore_errors=True)
    return hits


def main():
    gem, fba = load_locked()
    pid2gene = json.load(open(PID2GENE))
    sets = {k: set(v) for k, v in json.load(open(NEWSETS)).items()}
    hits = mmseqs_bridge()
    exp = {t: set() for t in sets}
    for q, ta, pid in hits:
        if pid < PIDENT or ta not in gem: continue
        g = pid2gene.get(q)
        for thr in sets:
            if g in sets[thr]: exp[thr].add(ta)
    metrics = {}
    for thr in sets:
        E = exp[thr]
        both = len(fba & E); fo = len(fba - E); eo = len(E - fba); ne = len(gem - fba - E)
        orr, p = fisher_exact([[both, fo], [eo, ne]], alternative="greater")
        metrics[thr] = {"n_exp_essential_gem": len(E), "both": both, "fba_only": fo,
                        "exp_only": eo, "neither": ne, "odds_ratio": round(float(orr), 6),
                        "fisher_p": float(f"{p:.6e}"),
                        "precision": round(both / len(fba), 6) if fba else 0.0,
                        "recall": round(both / len(E), 6) if E else 0.0}
    pm = metrics[PRIMARY]
    verdict = "PASS" if (pm["odds_ratio"] > 3 and pm["fisher_p"] < 0.01) else "FAIL"
    # hashed payload: sorted-key metrics only (verdict/provenance excluded)
    core = {"n_gem_genes": len(gem), "n_fba_essential": len(fba), "pident_cutoff": PIDENT,
            "primary_threshold": PRIMARY, "metrics": metrics}
    payload = json.dumps(core, sort_keys=True, separators=(",", ":"))
    reveal_sha = hashlib.sha256(payload.encode()).hexdigest()
    out = dict(core)
    out.update({
        "organism": "Trypanosoma brucei brucei TREU927 (927/4 GUTat10.1), taxon 185431",
        "experimental_source": ("Alsford et al. 2011 Genome Research RIT-seq (PMID 21363968), bloodstream-form "
                                "loss-of-fitness, via TriTrypDB/VEuPathDB GenesByHighThroughputPhenotyping "
                                "(Horn profile), release 68; comparison BFD6 vs No_Tet, down-regulated, "
                                "fold-change threshold; protein-coding. PRIMARY=fc>=2 (Z>3.3 SI file paywalled)."),
        "adjudication": "mmseqs easy-search homology bridge, pident>=90 (BLIND1-3 method)",
        "gate": "OR>3 AND Fisher p<0.01 (identical to BLIND1-6)",
        "verdict": verdict, "lock_sha_verified": LOCK_SHA, "reveal_payload_sha256": reveal_sha,
    })
    with open(os.path.join(RES, "BLIND7_reveal.json"), "w") as f:
        json.dump(out, f, indent=2, sort_keys=True); f.write("\n")
    open(os.path.join(RES, "BLIND7_reveal.sha256"), "w").write(reveal_sha + "\n")
    print(f"LOCK VERIFIED ({LOCK_SHA[:8]}). GEM {len(gem)} genes, {len(fba)} FBA-essential.")
    for thr in ("fc2", "fc1p5", "fc3"):
        m = metrics[thr]
        print(f"  [{thr}] exp-ess={m['n_exp_essential_gem']}  2x2 {m['both']}/{m['fba_only']}/"
              f"{m['exp_only']}/{m['neither']}  OR={m['odds_ratio']} p={m['fisher_p']:.3e} "
              f"prec={m['precision']} rec={m['recall']}")
    print(f"PRIMARY({PRIMARY}) OR={pm['odds_ratio']} p={pm['fisher_p']:.3e} -> {verdict}. "
          f"reveal_sha={reveal_sha}")


if __name__ == "__main__":
    main()
