"""INTERCEPTA command-line interface.

Subcommands:
  info     — version + honest scope (data-free)
  rank     — rank drugs for query tumor expression (cell-line transfer + verified mutation markers)
  synergy  — rank synergistic drug PAIRS from a known library (combinations arm, V23/B24-B29)
  admet    — predict ADMET/safety properties from SMILES (structure-only screening filter, B30)
  synth    — score retrosynthetic solvability (synthesizability proxy) from SMILES (B31)
  prioritize — rank molecules by composite developability risk (ADMET+synth; B32)
  generate — goal-directed molecular design / optimization (BRICS-GA; B33)
  discover — end-to-end candidate discovery: generate + ADMET/synth screen + rank (B39)
  screen   — virtual-screening engine: rank candidates by calibrated P(active) (QSAR+AD+conformal; loop=B51)
  substrate — compose an evidence table into a safe, provenance-tiered, abstaining ranked shortlist (extensible "any disease -> a query" engine)

HONEST SCOPE: every subcommand is a RESEARCH hypothesis-ranking/screening tool, validated at the
cell-line/ex-vivo (rank, synergy) or scaffold-split benchmark (admet) level only. NONE is a validated human
clinical predictor (human clinical drug response was a well-powered null once cancer type was controlled — see
LEDGER.md / papers/intercepta_engine/MANUSCRIPT.md). Do not use for clinical decisions or safety guarantees.
"""
import argparse
import sys

SCOPE = (
    "INTERCEPTA engine v1 — reproducible cell-line/ex-vivo drug-response ranking.\n"
    "VALIDATED: cross-dataset cell-line transfer (rho=+0.212); AML mutation->drug mechanism (FLT3-ITD->FLTi, "
    "RAS->MEKi); weak drug-specific BeatAML ex-vivo signal; OOD-gated confidence.\n"
    "NOT VALIDATED: human clinical drug response (cancer-confounded null, B10); robust external PDX specificity; "
    "therapy selection; de-novo molecules. Every prediction is a LOW/MODERATE-confidence hypothesis.\n"
)


def _cmd_info(args):
    from intercepta import __version__
    print(f"intercepta {__version__}\n\n{SCOPE}")
    return 0


def _cmd_rank(args):
    import pandas as pd
    from intercepta.engine import InterceptaEngine
    expr = pd.read_csv(args.expr, index_col=0)               # genes x samples
    mutations = pd.read_csv(args.mutations, index_col=0) if args.mutations else None
    drugs = [d.strip() for d in args.drugs.split(",")] if args.drugs else None
    eng = InterceptaEngine().fit(drugs=drugs, label_source=args.label_source,
                                 compute_calibration=not args.no_calibration)
    if not eng.fitted_drugs_:
        print("ERROR: no drugs could be trained (check INTERCEPTA_DATA and --drugs).", file=sys.stderr)
        return 2
    out = eng.rank(expr, mutations=mutations)
    out = out.sort_values(["sample", "combined_score"], ascending=[True, False])
    out.to_csv(args.out, index=False)
    print(f"ranked {out['sample'].nunique()} samples x {out['drug'].nunique()} drugs -> {args.out}")
    print("NOTE: confidence is LOW/MODERATE by design; hypotheses only, not clinical decisions.")
    return 0


def _cmd_synergy(args):
    import pandas as pd
    from intercepta.synergy import SynergyRanker
    expr = pd.read_csv(args.expr, index_col=0)               # genes x samples
    ranker = SynergyRanker.from_drugcomb() if args.library == "drugcomb" else SynergyRanker.from_oneil()
    out = ranker.rank_pairs(expr, top=args.top)
    out.to_csv(args.out, index=False)
    print(f"ranked synergistic pairs for {out['sample'].nunique()} samples "
          f"(library of {len(ranker.library_)} known drugs; CV leave-combination-out rho="
          f"{ranker.cv_leave_combination_rho_:.2f}) -> {args.out}")
    print("NOTE: cell-line-validated Loewe synergy, KNOWN-drug library only, OOD-gated; hypotheses, not clinical decisions.")
    return 0


def _cmd_admet(args):
    import pandas as pd
    from intercepta.admet import ADMETPredictor, TASK_METRIC
    if not args.smiles and not args.molecules:
        print("ERROR: provide --molecules 'SMILES,SMILES' or --smiles path.txt", file=sys.stderr)
        return 2
    smiles = [s.strip() for s in open(args.smiles)] if args.smiles else [s.strip() for s in args.molecules.split(",")]
    smiles = [s for s in smiles if s]
    tasks = [t.strip() for t in args.tasks.split(",")] if args.tasks else None
    if tasks:
        bad = [t for t in tasks if t not in TASK_METRIC]
        if bad:
            print(f"ERROR: unknown task(s): {bad}. Known: {sorted(TASK_METRIC)}", file=sys.stderr)
            return 2
    pred = ADMETPredictor.from_tdc(tasks=tasks, conformal=args.conformal)
    out = pred.predict(smiles, tasks=tasks, tidy=True)
    out.to_csv(args.out, index=False)
    n_ood = int((~out["in_domain"]).sum())
    print(f"predicted {out['task'].nunique()} ADMET propertie(s) for {out['smiles'].nunique()} molecule(s) "
          f"({n_ood}/{len(out)} rows out-of-applicability-domain) -> {args.out}")
    if args.conformal:
        print("conformal uncertainty ON (B30b-validated): regression rows carry pi_low/pi_high, classification rows "
              "carry conformal_set/set_size (AD-adaptive; ~nominal coverage on scaffold split).")
    print("NOTE: in-silico SCREENING FILTER (scaffold-split validated, B30/B30b), NOT a safety guarantee; "
          "out-of-domain rows are low-confidence. Not a clinical/regulatory determination.")
    return 0


def _cmd_synth(args):
    from intercepta.synth import SynthesizabilityScorer
    if not args.smiles and not args.molecules:
        print("ERROR: provide --molecules 'SMILES,SMILES' or --smiles path.txt", file=sys.stderr)
        return 2
    smiles = [s.strip() for s in open(args.smiles)] if args.smiles else [s.strip() for s in args.molecules.split(",")]
    smiles = [s for s in smiles if s]
    scorer = SynthesizabilityScorer.from_rascore(subsample=args.subsample, conformal=not args.no_conformal)
    out = scorer.predict(smiles)
    out.to_csv(args.out, index=False)
    n_ood = int((~out["in_domain"]).sum())
    print(f"scored {len(out)} molecule(s) for retrosynthetic solvability ({n_ood} out-of-applicability-domain) -> {args.out}")
    print("NOTE: predicts ALGORITHMIC retrosynthetic solvability (AiZynthFinder/USPTO templates), a computational "
          "PROXY for synthesizability (B31-validated) — NOT a guarantee a molecule can be made. sa_score = RDKit "
          "SAscore (1 easy..10 hard). Research screening signal, not a chemistry verdict.")
    return 0


def _cmd_prioritize(args):
    from intercepta.integrate import DevelopabilityPrioritizer
    if not args.smiles and not args.molecules:
        print("ERROR: provide --molecules 'SMILES,SMILES' or --smiles path.txt", file=sys.stderr)
        return 2
    smiles = [s.strip() for s in open(args.smiles)] if args.smiles else [s.strip() for s in args.molecules.split(",")]
    smiles = [s for s in smiles if s]
    p = DevelopabilityPrioritizer.from_default(synth_subsample=args.subsample)
    out = p.predict(smiles)
    out.to_csv(args.out, index=False)
    print(f"prioritized {len(out)} molecule(s) by composite developability risk -> {args.out}")
    print("NOTE: composite of ADMET (B30) + synthesizability (B31) module outputs. B32 (first-class NEGATIVE): the "
          "composite does NOT beat the single best ADMET endpoint on ClinTox — use the per-module PROFILE columns "
          "for interpretability, NOT the composite as an improvement. developability_risk = P(clinical-tox failure), "
          "a research signal only, NOT a clinical/regulatory determination. Survivorship-confounded.")
    return 0


def _cmd_generate(args):
    import os, pandas as pd
    from rdkit import Chem
    from intercepta.generate import MoleculeOptimizer, qed_score, synth_score, developability
    dd = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
    if args.seeds:
        seeds = [s.strip() for s in open(args.seeds) if s.strip()]
    else:
        df = pd.read_csv(os.path.join(dd, "tdc_gen", "chembl.tab"), sep="\t")
        col = "smiles" if "smiles" in df.columns else df.columns[-1]
        seeds = df[col].dropna().sample(args.n_seeds, random_state=42).tolist()
    seeds = [Chem.MolToSmiles(m) for m in (Chem.MolFromSmiles(s) for s in seeds) if m is not None]
    res = MoleculeOptimizer(objective=args.objective, pop_size=args.pop, generations=args.generations).optimize(seeds)
    rows = []
    for s in res["final_population"][:args.top]:
        m = Chem.MolFromSmiles(s)
        rows.append({"smiles": s, "objective_score": round(developability(m) if args.objective == "multi" else qed_score(m), 4),
                     "qed": round(qed_score(m), 4), "synth_score": round(synth_score(m), 4)})
    pd.DataFrame(rows).to_csv(args.out, index=False)
    print(f"optimized ({args.objective}) over {args.generations} generations -> top {len(rows)} molecules to {args.out}; "
          f"best score {res['best_score']}")
    print("NOTE: goal-directed OPTIMIZATION of QED/SAscore proxies over KNOWN chemistry via BRICS recombination "
          "(B33-validated), NOT de novo discovery of real/synthesizable drugs. Outputs are computational hypotheses.")
    return 0


def _cmd_discover(args):
    from intercepta.discover import DiscoveryPipeline
    pipe = DiscoveryPipeline.from_default(synth_subsample=args.subsample, target_hts=args.target_hts)
    seeds = [s.strip() for s in open(args.seeds) if s.strip()] if args.seeds else None
    out, _ = pipe.discover(seed_smiles=seeds, pop_size=args.pop, generations=args.generations, top=args.top)
    out.to_csv(args.out, index=False)
    n_dom = int((out["applicability_domain"] == "in-domain").sum())
    tgt = f", target-conditioned on '{args.target_hts}'" if args.target_hts else ""
    print(f"discovered {len(out)} candidate molecule(s){tgt} -> {args.out} (top F {out['developability_F'].max()}; "
          f"{n_dom}/{len(out)} in ADMET applicability domain)")
    if args.target_hts:
        print("target-conditioned (B40): objective × P(target-active | QSAR). NOTE activity is QSAR-PREDICTED not "
              "measured, and target activity can TRADE OFF against predicted safety — inspect p_target_active vs "
              "predicted_safety per candidate.")
    print("NOTE: end-to-end pipeline = design(B33) + synthesizability(B31) + ADMET-safety(B30), assembled (B39). "
          "Candidates are COMPUTATIONAL HYPOTHESES over known chemistry, NOT validated/novel/safe drugs. Optimizing "
          "against predictors invites gaming; out-of-domain rows have unreliable safety calls.")
    return 0


def _cmd_screen(args):
    from intercepta.screen import VirtualScreener
    if not args.candidates:
        print("ERROR: provide --candidates path.txt (one SMILES per line)", file=sys.stderr)
        return 2
    cands = [s.strip() for s in open(args.candidates) if s.strip()]
    if args.target_hts:
        vs = VirtualScreener.from_hts(args.target_hts, n_inactive=args.n_inactive, conformal=not args.no_conformal)
    else:
        if not (args.actives and args.inactives):
            print("ERROR: provide (--actives FILE --inactives FILE) or --target-hts NAME", file=sys.stderr)
            return 2
        actives = [s.strip() for s in open(args.actives) if s.strip()]
        inactives = [s.strip() for s in open(args.inactives) if s.strip()]
        vs = VirtualScreener(name=args.name, conformal=not args.no_conformal).fit(actives, inactives)
    out = vs.score(cands, top=args.top)
    out.to_csv(args.out, index=False)
    n_dom = int(out["in_domain"].sum())
    print(f"screened {len(out)} candidate(s) against '{vs.name}' QSAR "
          f"({vs.n_actives_} actives / {vs.n_inactives_} inactives; {n_dom}/{len(out)} in applicability domain) "
          f"-> {args.out}")
    print("NOTE: retrospective in-silico prioritization (enrichment validated on scaffold/novel-chemistry splits + "
          "unbiased LIT-PCBA ~0.78 AUROC, B46; NOT prospectively confirmed). p_active is a ranking score, NOT proven "
          "activity; out-of-domain rows are low-confidence. Hypotheses, not validated actives/drugs; not wet-lab.")
    return 0


def _cmd_substrate(args):
    """Compose an evidence table into a safe, provenance-tiered, abstaining ranked shortlist (the extensible substrate)."""
    import csv
    from intercepta.substrate import (TargetEngine, Query, EvidenceStore, EvidenceRecord, SignalRole, ProvenanceTier)
    role_map = {r.name.lower(): r for r in SignalRole}
    tier_map = {t.name.lower(): t for t in ProvenanceTier}
    rows = list(csv.DictReader(open(args.evidence)))
    if not rows:
        print("ERROR: empty evidence file. Columns: entity,signal,value[,role,tier,direction,provider]", file=sys.stderr)
        return 2
    store, entities = EvidenceStore(), []
    for r in rows:
        e = (r.get("entity") or "").strip()
        if not e:
            continue
        if e not in entities:
            entities.append(e)
        role = role_map.get((r.get("role") or "rank").strip().lower(), SignalRole.RANK)
        tier = tier_map.get((r.get("tier") or "own_reproduced").strip().lower(), ProvenanceTier.OWN_REPRODUCED)
        try:
            val = float(r.get("value") or 1.0); direc = float(r.get("direction") or 1.0)
        except ValueError:
            val, direc = 1.0, 1.0
        store.add([EvidenceRecord(e, (r.get("signal") or "signal").strip(), val, role,
                                  (r.get("provider") or "user").strip(), tier, direc)],
                  quarantine_self_generated=False)
    eng = TargetEngine(min_decision_tier=tier_map.get(args.min_tier.lower(), ProvenanceTier.OWN_REPRODUCED))
    verdicts = eng.query(Query(pathogen=args.name, entities=sorted(entities)), store=store)
    import pandas as pd
    df = pd.DataFrame([{"entity": v.entity, "safe": v.safe, "abstain": v.abstain, "confidence": v.confidence,
                        "rank_score": v.rank_score, "n_evidence": len(v.evidence),
                        "flags": ";".join(v.flags), "signals": ";".join(sorted({r.signal for r in v.evidence}))}
                       for v in verdicts])
    df.to_csv(args.out, index=False)
    n_safe = int(df["safe"].sum()); n_excl = int((~df["safe"]).sum()); n_abst = int((df["safe"] & df["abstain"]).sum())
    print(f"composed {len(rows)} evidence rows over {len(entities)} entities -> {n_excl} excluded (safety), "
          f"{n_abst} abstained, {n_safe - n_abst} ranked -> {args.out}")
    print("NOTE: the substrate is a COMPOSITION + GOVERNANCE layer — it does not validate biology. Each evidence row "
          "carries its own provenance tier; SAFETY_FILTER rows exclude by construction; unvalidated (below --min-tier) "
          "and self-generated evidence are quarantined. Outputs are confidence-tiered HYPOTHESES with provenance, NOT "
          "validated targets/drugs. See docs/SUBSTRATE.md.")
    return 0


def _cmd_discover_targets(args):
    """Unified end-to-end zero-data target discovery: genome -> safe, confidence-tiered, provenance-tagged shortlist."""
    from .discovery_engine import DiscoveryEngine
    import json
    eng = DiscoveryEngine.for_pathogen(
        args.pathogen, args.proteome, scratch=args.scratch,
        essentiality_tsv=args.essentiality, chokepoint_tsv=args.chokepoint, breadth_tsv=args.breadth,
        reference_targets_fasta=args.reference_targets, human_fasta=args.human, ceg2_path=args.ceg2)
    rep = eng.report(top=args.top)
    json.dump(rep, open(args.out, "w"), indent=2, sort_keys=True)
    print(f"{args.pathogen}: {rep['n_confident_safe_targets']} confident safe targets, "
          f"{rep['n_excluded_by_safety']} host-toxic excluded, {rep['n_abstained']} abstained -> {args.out}")
    print("active validated signals:", ", ".join(rep["active_signals"]) or "(none)")
    print(rep["confidence_note"])
    print("HONEST SCOPE:", rep["honest_scope"])
    return 0


def _cmd_route(args):
    """COMPOSITE router (COMPOSITE1/2/3): for a pathogen/disease input, decide which VALIDATED target-ID signal(s)
    to apply per biology class — at full or capped confidence — or ABSTAIN where none is validated. The honest
    'what will the system do, and does it refuse?' face of the composite. Pure decision logic; no heavy deps."""
    from .composite_router import CompositeRouter, BiologyClass
    import json
    proteome_size = args.proteome_size
    if args.proteome and proteome_size is None:
        # count sequences (FASTA headers) to let the detector auto-classify (tiny proteome -> virus)
        try:
            with open(args.proteome) as fh:
                proteome_size = sum(1 for ln in fh if ln.startswith(">"))
        except OSError as e:
            print(f"could not read --proteome: {e}"); return 2
    declared = BiologyClass(args.biology_class) if args.biology_class else None
    router = CompositeRouter()
    dec = router.decide(organism=args.organism, proteome_size=proteome_size,
                        declared_class=declared, host_dependent=(args.host_dependent or None),
                        has_curated_gem=args.has_curated_gem)
    d = dec.to_dict()
    if args.out:
        json.dump(d, open(args.out, "w"), indent=2, sort_keys=True)
    # human-readable honest summary
    print(f"organism: {d['organism']}   detected class: {d['biology_class']} ({d['class_source']})")
    print(f"OUTPUT: {d['output_type'].upper()}")
    if d["output_type"] == "abstention":
        print("  ABSTAINED — no validated signal transfers to this input:")
        print("  reason:", d["abstention"])
    else:
        fired = d.get("signals_fired", [])
        print("  signals FIRED (validated for this class):", ", ".join(fired) or "(none)")
        if d.get("supporting_signals"):
            print("  supporting (filter/validation-only):", ", ".join(d["supporting_signals"]))
        if d.get("uncertain"):
            cap = d.get("confidence_cap")
            print(f"  ⚠ CAPPED/UNCERTAIN firing (confidence_cap={cap}):")
            for f in d.get("uncertainty_flags", []):
                print(f"    - {f.get('signal')}: {f.get('note')}")
    if d.get("signals_gated_out"):
        print("  gated OUT (transfer condition not met):")
        for g in d["signals_gated_out"]:
            print(f"    - {g.get('signal')}: {g.get('reason')}")
    print("\nHONEST SCOPE: routed target-PRIORITIZATION decision (which validated signal applies, or abstain). "
          "Shortlist signals output confidence-tiered candidate HYPOTHESES with provenance, NOT validated targets, "
          "drugs, or clinical claims. Running the actual shortlist (bacteria/eukaryote FBA; human-cancer dependency) "
          "requires the per-class inputs (see `discover-targets`); this command reports the honest routing + abstention.")
    if args.out:
        print(f"\nrouting decision JSON -> {args.out}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="intercepta", description=SCOPE.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("info", help="print version + honest scope").set_defaults(func=_cmd_info)
    r = sub.add_parser("rank", help="rank drugs for query tumor expression (genes x samples CSV)")
    r.add_argument("--expr", required=True, help="query expression CSV (genes as rows, samples as columns)")
    r.add_argument("--mutations", help="optional sample x {NRAS,FLT3_ITD,...} 0/1 CSV")
    r.add_argument("--drugs", help="comma-separated drug names to rank (default: all trainable)")
    r.add_argument("--label-source", default="prism", choices=["prism", "gdsc"], help="training screen")
    r.add_argument("--no-calibration", action="store_true", help="skip OOD/reliability (faster)")
    r.add_argument("--out", default="intercepta_ranking.csv")
    r.set_defaults(func=_cmd_rank)
    s = sub.add_parser("synergy", help="rank synergistic drug PAIRS (known library) for query expression (genes x samples CSV)")
    s.add_argument("--expr", required=True, help="query expression CSV (genes as rows, samples as columns; DepMap gene symbols)")
    s.add_argument("--library", default="oneil", choices=["oneil", "drugcomb"],
                   help="drug library: oneil (38 drugs, CV rho 0.62) or drugcomb (124 drugs, CV rho ~0.38)")
    s.add_argument("--top", type=int, default=20, help="top-N pairs per sample")
    s.add_argument("--out", default="intercepta_synergy.csv")
    s.set_defaults(func=_cmd_synergy)
    a = sub.add_parser("admet", help="predict ADMET/safety properties from SMILES (structure-only; B30-validated)")
    a.add_argument("--molecules", help="comma-separated SMILES strings")
    a.add_argument("--smiles", help="path to a file with one SMILES per line (alternative to --molecules)")
    a.add_argument("--tasks", help="comma-separated ADMET task names (default: all 22 TDC tasks)")
    a.add_argument("--conformal", action="store_true",
                   help="emit calibrated conformal uncertainty (B30b): regression pi_low/pi_high, classification sets")
    a.add_argument("--out", default="intercepta_admet.csv")
    a.set_defaults(func=_cmd_admet)
    y = sub.add_parser("synth", help="score retrosynthetic solvability (synthesizability proxy) from SMILES (B31)")
    y.add_argument("--molecules", help="comma-separated SMILES strings")
    y.add_argument("--smiles", help="path to a file with one SMILES per line (alternative to --molecules)")
    y.add_argument("--subsample", type=int, default=50000, help="training subsample size (default 50000)")
    y.add_argument("--no-conformal", action="store_true", help="skip conformal prediction-set output")
    y.add_argument("--out", default="intercepta_synth.csv")
    y.set_defaults(func=_cmd_synth)
    z = sub.add_parser("prioritize", help="rank molecules by composite developability risk (ADMET+synth; B32)")
    z.add_argument("--molecules", help="comma-separated SMILES strings")
    z.add_argument("--smiles", help="path to a file with one SMILES per line (alternative to --molecules)")
    z.add_argument("--subsample", type=int, default=50000, help="synthesizability training subsample (default 50000)")
    z.add_argument("--out", default="intercepta_prioritize.csv")
    z.set_defaults(func=_cmd_prioritize)
    gg = sub.add_parser("generate", help="goal-directed molecular design (BRICS-GA optimizer; B33)")
    gg.add_argument("--objective", default="multi", choices=["multi", "qed"], help="multi = QED×synthesizability")
    gg.add_argument("--seeds", help="file of seed SMILES (one per line); default: sample from ChEMBL")
    gg.add_argument("--n-seeds", type=int, default=200, dest="n_seeds")
    gg.add_argument("--pop", type=int, default=100)
    gg.add_argument("--generations", type=int, default=10)
    gg.add_argument("--top", type=int, default=20, help="top-N optimized molecules to write")
    gg.add_argument("--out", default="intercepta_generate.csv")
    gg.set_defaults(func=_cmd_generate)
    dd = sub.add_parser("discover", help="end-to-end candidate discovery: generate + ADMET/synth screen + rank (B39)")
    dd.add_argument("--seeds", help="file of seed SMILES (one per line); default: sample from ChEMBL")
    dd.add_argument("--pop", type=int, default=100); dd.add_argument("--generations", type=int, default=10)
    dd.add_argument("--top", type=int, default=20); dd.add_argument("--subsample", type=int, default=50000)
    dd.add_argument("--target-hts", dest="target_hts", help="condition on a TDC HTS target (e.g. 'hiv'); B40")
    dd.add_argument("--out", default="intercepta_discover.csv")
    dd.set_defaults(func=_cmd_discover)
    sc = sub.add_parser("screen", help="virtual-screening engine: rank candidates by calibrated P(active) "
                                       "(QSAR + applicability-domain + conformal; the B51 loop is the Python API)")
    sc.add_argument("--candidates", required=True, help="file of candidate SMILES (one per line)")
    sc.add_argument("--actives", help="file of known active SMILES (one per line)")
    sc.add_argument("--inactives", help="file of known inactive SMILES (one per line)")
    sc.add_argument("--target-hts", dest="target_hts", help="fit from a TDC HTS target instead (e.g. 'hiv')")
    sc.add_argument("--name", default="target", help="label for the target/QSAR")
    sc.add_argument("--n-inactive", dest="n_inactive", type=int, default=10000, help="inactive sample if --target-hts")
    sc.add_argument("--no-conformal", action="store_true", help="skip conformal prediction-set output")
    sc.add_argument("--top", type=int, default=None, help="write only the top-N ranked candidates")
    sc.add_argument("--out", default="intercepta_screen.csv")
    sc.set_defaults(func=_cmd_screen)
    su = sub.add_parser("substrate", help="compose an evidence table into a safe, provenance-tiered, abstaining ranked "
                                          "shortlist — the extensible 'any disease -> a query' engine (docs/SUBSTRATE.md)")
    su.add_argument("--evidence", required=True, help="CSV with columns: entity,signal,value[,role,tier,direction,provider]. "
                                                      "role in {rank,safety_filter,abstain,flag}; tier in "
                                                      "{quarantined,own_hypothesis,own_single,own_reproduced,external_validated}")
    su.add_argument("--min-tier", dest="min_tier", default="own_reproduced",
                    help="minimum provenance tier allowed to drive a decision (default own_reproduced)")
    su.add_argument("--name", default="query", help="label for the query/disease")
    su.add_argument("--out", default="intercepta_substrate.csv")
    su.set_defaults(func=_cmd_substrate)
    dt = sub.add_parser("discover-targets", help="end-to-end zero-data target discovery: pathogen genome -> safe, "
                        "confidence-tiered, provenance-tagged target shortlist (composes ALL validated signals: "
                        "essentiality[validated]/chokepoint/conservation/breadth/structure + hard host-safety filter)")
    dt.add_argument("--pathogen", required=True, help="organism key (matches the org column in the cache TSVs)")
    dt.add_argument("--proteome", required=True, help="pathogen proteome FASTA (UniProt headers)")
    dt.add_argument("--essentiality", help="FBA essentiality TSV (org<TAB>uniprot<TAB>essential[...])")
    dt.add_argument("--chokepoint", help="metabolic chokepoint TSV (org<TAB>uniprot<TAB>chokepoint)")
    dt.add_argument("--breadth", help="conservation-breadth TSV (uniprot<TAB>breadth)")
    dt.add_argument("--reference-targets", dest="reference_targets", help="other-organisms' known-target FASTA (conservation)")
    dt.add_argument("--human", help="human proteome FASTA (host-safety filter)")
    dt.add_argument("--ceg2", help="Hart CEG2 core-essential gene list (host-toxicity ground truth)")
    dt.add_argument("--scratch", default="/tmp/intercepta_engine", help="scratch dir for mmseqs")
    dt.add_argument("--top", type=int, default=30)
    dt.add_argument("--out", default="targets.json")
    dt.set_defaults(func=_cmd_discover_targets)
    rt = sub.add_parser("route", help="COMPOSITE router (COMPOSITE1/2/3): decide which VALIDATED signal(s) apply to a "
                        "pathogen/disease input — at full or capped confidence — or ABSTAIN where none is validated. "
                        "The honest 'what will the system do, and does it refuse?' face of the composite.")
    rt.add_argument("--organism", default="query", help="organism/input label (for the report)")
    rt.add_argument("--proteome", help="proteome FASTA; sequence count auto-classifies (tiny -> virus, else bacterium/unknown)")
    rt.add_argument("--proteome-size", dest="proteome_size", type=int, help="override: number of proteins (instead of --proteome)")
    rt.add_argument("--class", dest="biology_class",
                    choices=["bacterium", "free_eukaryote", "host_dependent_parasite", "virus", "human_cancer", "unknown"],
                    help="declare the biology class (overrides autodetection; host-dependence is not sequence-derivable)")
    rt.add_argument("--host-dependent", dest="host_dependent", action="store_true",
                    help="flag the input as a host-dependent parasite (if no --class given)")
    rt.add_argument("--has-curated-gem", dest="has_curated_gem", action="store_true",
                    help="a curated genome-scale metabolic model exists (enables capped/flagged FBA for host-dependent parasites)")
    rt.add_argument("--out", default=None, help="optional path to write the routing decision JSON")
    rt.set_defaults(func=_cmd_route)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
