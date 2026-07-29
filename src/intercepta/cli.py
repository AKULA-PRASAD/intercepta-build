"""INTERCEPTA command-line interface.

HONEST SCOPE: this ranks drugs for query tumor expression using a cell-line-trained transfer + verified
mutation markers. It is a RESEARCH hypothesis-ranking tool, validated at the cell-line/ex-vivo level only.
It is NOT a validated human clinical predictor (human clinical response was a well-powered null once cancer
type was controlled — see LEDGER.md / papers/intercepta_engine/MANUSCRIPT.md). Do not use for clinical decisions.
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
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
