"""DRUGGABLE — complete the target-quality profile of the 85 pan-bacterial predictions (PANBACT) by adding fpocket
DRUGGABILITY (a target needs a druggable pocket). Fetches AlphaFold v6 structures + runs fpocket for each prediction, then
ranks the FULLY-PROFILED targets: essential + chokepoint + host-non-homologous + broad-spectrum (breadth) + druggable.
Deterministic; zero-cost (AlphaFold DB + fpocket). Env: bioinfo (fpocket)."""
import os, json, time, hashlib, subprocess, shutil
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); SCR = os.path.join(HERE, "scratch")
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
FPOCKET = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/fpocket")
PANBACT = os.path.join(os.path.dirname(HERE), "PANBACT_catalog", "results", "PANBACT_metrics.json")


def fetch_af(acc):
    pdb = os.path.join(SCR, f"{acc}.pdb")
    if os.path.exists(pdb) and os.path.getsize(pdb) > 1000: return pdb
    subprocess.run(["curl", "-sL", "-m", "60", "-o", pdb, f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v6.pdb"], capture_output=True)
    return pdb if os.path.exists(pdb) and os.path.getsize(pdb) > 1000 else None


def fpocket_drug(pdb):
    stem = os.path.splitext(os.path.basename(pdb))[0]; outdir = os.path.join(os.path.dirname(pdb), f"{stem}_out")
    shutil.rmtree(outdir, ignore_errors=True)
    subprocess.run([FPOCKET, "-f", pdb], capture_output=True, cwd=os.path.dirname(pdb))
    info = os.path.join(outdir, f"{stem}_info.txt"); best = 0.0
    if os.path.exists(info):
        for ln in open(info):
            if "Druggability Score" in ln:
                try: best = max(best, float(ln.split(":")[1].strip()))
                except Exception: pass
    shutil.rmtree(outdir, ignore_errors=True)
    return best


def main():
    t0 = time.time(); shutil.rmtree(SCR, ignore_errors=True); os.makedirs(SCR, exist_ok=True)
    print("=== DRUGGABLE: fpocket druggability of the 85 pan-bacterial predictions ===")
    pan = json.load(open(PANBACT)); per = pan["per_organism"]
    # gene -> list of (org, acc); breadth = #bacteria with that gene name
    gene_accs = defaultdict(list); gene_breadth = defaultdict(set)
    for org, d in per.items():
        for p in d["predictions"]:
            gene_accs[p["gene"]].append((org, p["uniprot"])); gene_breadth[p["gene"]].add(org)
    drug = {}; n_ok = 0
    all_accs = [(g, org, acc) for g, lst in gene_accs.items() for (org, acc) in lst]
    for i, (g, org, acc) in enumerate(all_accs):
        pdb = fetch_af(acc); d = fpocket_drug(pdb) if pdb else None
        drug[(g, org, acc)] = d
        if d is not None: n_ok += 1
        if (i + 1) % 20 == 0: print(f"  fpocket {i+1}/{len(all_accs)} [{time.time()-t0:.0f}s]", flush=True)
    # per-gene max druggability across its orthologs
    gene_drug = {}
    for g in gene_accs:
        vals = [drug[(g, org, acc)] for (org, acc) in gene_accs[g] if drug.get((g, org, acc)) is not None]
        gene_drug[g] = round(max(vals), 3) if vals else None
    DRUGGABLE = 0.5
    rows = []
    for g in gene_accs:
        rows.append({"gene": g, "breadth": len(gene_breadth[g]), "max_druggability": gene_drug[g],
                     "druggable": bool(gene_drug[g] is not None and gene_drug[g] >= DRUGGABLE)})
    # prioritized: broad-spectrum AND druggable, sorted by breadth then druggability
    rows.sort(key=lambda r: (r["breadth"], r["max_druggability"] or 0), reverse=True)
    top = [r for r in rows if r["breadth"] >= 3 and r["druggable"]]
    top_str = ", ".join(f"{r['gene']}(b{r['breadth']},d{r['max_druggability']})" for r in top) or "none above threshold"
    print("\nFULLY-PROFILED targets (gene | breadth /7 | max druggability | druggable):")
    for r in rows[:20]:
        print(f"  {r['gene']:8s} breadth {r['breadth']}/7  druggability {r['max_druggability']}  druggable={r['druggable']}")
    summary = {"n_predictions_profiled": len(all_accs), "n_structures_fpocketed": n_ok, "n_genes": len(gene_accs),
               "druggable_threshold": DRUGGABLE,
               "top_broad_and_druggable": [{"gene": r["gene"], "breadth": r["breadth"], "druggability": r["max_druggability"]} for r in top],
               "verdict": (f"Completed the target-quality profile of the pan-bacterial predictions by adding fpocket "
                           f"druggability ({n_ok}/{len(all_accs)} structures scored). The fully-profiled TOP targets "
                           f"(broad-spectrum >=3/7 AND druggable pocket >= {DRUGGABLE}): "
                           f"{top_str}. "
                           f"These satisfy ALL zero-data target criteria at once — essential + metabolic chokepoint + host-non-"
                           f"homologous (safe) + broad-spectrum + druggable — the strongest, most complete predictions for the "
                           f"experimental validation. SCOPE: fpocket heuristic druggability on AlphaFold apo structures (TID2 "
                           f"found it modest); FBA-predicted essentiality; hypotheses, not validated targets; not wet-lab.")}
    print("\n  TOP broad+druggable:", [r["gene"] for r in top])
    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "per_gene": rows, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "DRUGGABLE_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k: v for k, v in summary.items() if k != "verdict"}, "per_gene": rows}, sort_keys=True)
    open(os.path.join(HERE, "results", "DRUGGABLE_payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    print("payload sha256:", hashlib.sha256(payload.encode()).hexdigest(), f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
