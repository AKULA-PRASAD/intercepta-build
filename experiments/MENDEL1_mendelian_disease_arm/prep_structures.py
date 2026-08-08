#!/usr/bin/env python
"""MENDEL1 prep (run ONCE): fetch AlphaFold DB model per gene, run fpocket, cache best-pocket
Druggability Score. Output is a frozen cache read by run.py so scoring reproduces byte-identical
independent of network/fpocket. NO decision logic here."""
import json, os, re, subprocess, urllib.request, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "/Users/kalki/intercepta_data/mendel1"
STRUCT = os.path.join(DATA, "structures")
FPOCKET = "/Users/kalki/miniconda3/envs/bioinfo/bin/fpocket"
os.makedirs(STRUCT, exist_ok=True)

gt = json.load(open(os.path.join(HERE, "ground_truth.json")))
genes = gt["genes"]

def af_pdb_url(acc):
    api = f"https://alphafold.ebi.ac.uk/api/prediction/{acc}"
    d = json.load(urllib.request.urlopen(api, timeout=60))
    return d[0]["pdbUrl"], d[0].get("globalMetricValue")

def best_druggability(info_path):
    """Parse fpocket info.txt -> max Druggability Score over pockets."""
    best = 0.0
    n = 0
    for line in open(info_path):
        m = re.search(r"Druggability Score\s*:\s*([-0-9.]+)", line)
        if m:
            n += 1
            best = max(best, float(m.group(1)))
    return best, n

cache = {}
for g in genes:
    acc = g["uniprot"]; sym = g["gene"]
    pdb = os.path.join(STRUCT, f"AF-{acc}.pdb")
    try:
        url, plddt = af_pdb_url(acc)
        if not os.path.exists(pdb):
            urllib.request.urlretrieve(url, pdb)
        outdir = os.path.join(STRUCT, f"AF-{acc}_out")
        info = os.path.join(outdir, f"AF-{acc}_info.txt")
        if not os.path.exists(info):
            subprocess.run([FPOCKET, "-f", pdb], cwd=STRUCT,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1200)
        drug, npock = best_druggability(info)
        cache[sym] = {"uniprot": acc, "af_url": url, "global_plddt": plddt,
                      "fpocket_drug_score": round(drug, 3), "n_pockets": npock, "status": "ok"}
        print(f"{sym:8s} {acc}  plddt={plddt}  drug={drug:.3f}  pockets={npock}")
    except Exception as e:
        cache[sym] = {"uniprot": acc, "fpocket_drug_score": None, "status": f"FAIL:{e!r}"}
        print(f"{sym:8s} {acc}  FAIL {e!r}", file=sys.stderr)

out = os.path.join(DATA, "fpocket_scores.json")
json.dump(cache, open(out, "w"), indent=2, sort_keys=True)
print("wrote", out, "n=", len(cache))
