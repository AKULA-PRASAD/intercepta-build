#!/usr/bin/env python
"""GENETICS1 — FETCH-ONCE dataset builder (frozen to $INTERCEPTA_DATA/genetics1/).

CORRECTED universe (v2): fetches the FULL associated-target list per disease (paginated),
so the analysis can be done on the correct GENOME-WIDE universe. (The first v1 attempt used
top-500-by-overall, which is a collider of predictor+outcome and induces catastrophic Berkson
bias — see SUMMARY.md "Correction". Every gene with genetic_association>0 OR clinical>0 for a
disease appears in the full associated list, so genes absent from it are true double-negatives
[genetic==0 AND clinical==0] and are counted via the protein-coding genome size.)

Assembles a REAL, cited Open Targets Platform slice for a PRE-REGISTERED set of 27
common/complex/polygenic diseases (cancers + monogenic cystic fibrosis excluded — DEPEND1 /
MENDEL1 territory). Live GraphQL fetched ONCE and FROZEN to parquet + manifest (sha256).
run.py reads only the frozen file. NEVER commits data.
"""
import os, json, time, hashlib, urllib.request
import pandas as pd

OUT = "/Users/kalki/intercepta_data/genetics1"
os.makedirs(OUT, exist_ok=True)
API = "https://api.platform.opentargets.org/api/v4/graphql"
PAGE = 3000  # GraphQL page-size cap is between 3000 and 5000; 3000 is safe

DISEASES = [
    ("MONDO_0004975", "Alzheimer disease"),
    ("HP_0000822",    "Hypertension"),
    ("HP_0001513",    "Obesity"),
    ("MONDO_0005180", "Parkinson disease"),
    ("MONDO_0004976", "amyotrophic lateral sclerosis"),
    ("MONDO_0005306", "ankylosing spondylitis"),
    ("MONDO_0004979", "asthma"),
    ("MONDO_0004980", "atopic eczema"),
    ("MONDO_0005300", "chronic kidney disease"),
    ("MONDO_0005002", "chronic obstructive pulmonary disease"),
    ("MONDO_0005010", "coronary artery disorder"),
    ("MONDO_0005027", "epilepsy"),
    ("MONDO_0005252", "heart failure"),
    ("EFO_0000768",   "idiopathic pulmonary fibrosis"),
    ("MONDO_0005265", "inflammatory bowel disease"),
    ("MONDO_0002009", "major depressive disorder"),
    ("MONDO_0013209", "metabolic dysfunction-associated steatotic liver disease"),
    ("MONDO_0005301", "multiple sclerosis"),
    ("MONDO_0005178", "osteoarthritis"),
    ("MONDO_0005298", "osteoporosis"),
    ("MONDO_0005083", "psoriasis"),
    ("MONDO_0011849", "psoriatic arthritis"),
    ("MONDO_0008383", "rheumatoid arthritis"),
    ("MONDO_0005090", "schizophrenia"),
    ("MONDO_0007915", "systemic lupus erythematosus"),
    ("MONDO_0005147", "type 1 diabetes mellitus"),
    ("MONDO_0005148", "type 2 diabetes mellitus"),
]

QUERY = """query($efo:String!,$idx:Int!,$size:Int!){
  disease(efoId:$efo){ id name
    associatedTargets(page:{index:$idx,size:$size}){
      count
      rows{ target{ id approvedSymbol biotype } score datatypeScores{ id score } }
    } } }"""

def gql(efo, idx, size):
    body = {"query": QUERY, "variables": {"efo": efo, "idx": idx, "size": size}}
    req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    for attempt in range(4):
        try:
            return json.load(urllib.request.urlopen(req, timeout=120))
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))

def meta():
    req = urllib.request.Request(API, data=json.dumps({"query": "{ meta{ apiVersion{x y z} dataVersion{year month} } }"}).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))["data"]["meta"]

rows = []
per_disease = {}
for efo, label in DISEASES:
    first = gql(efo, 0, PAGE)
    d = first["data"]["disease"]
    assert d is not None, f"{efo} null"
    total = d["associatedTargets"]["count"]
    got = list(d["associatedTargets"]["rows"])
    idx = 1
    while len(got) < total:
        r = gql(efo, idx, PAGE)
        rr = r["data"]["disease"]["associatedTargets"]["rows"]
        if not rr:
            break
        got += rr
        idx += 1
        time.sleep(0.15)
    per_disease[efo] = {"name": d["name"], "total_associated": total, "fetched": len(got)}
    for row in got:
        dts = {x["id"]: x["score"] for x in row["datatypeScores"]}
        rows.append({
            "disease_id": efo, "disease_name": d["name"],
            "target_id": row["target"]["id"], "target_symbol": row["target"]["approvedSymbol"],
            "biotype": row["target"].get("biotype", ""),
            "overall_score": row["score"],
            "genetic_association": dts.get("genetic_association", 0.0),
            "genetic_literature": dts.get("genetic_literature", 0.0),
            "somatic_mutation": dts.get("somatic_mutation", 0.0),
            "literature": dts.get("literature", 0.0),
            "clinical": dts.get("clinical", 0.0),
        })
    print(f"  {efo:14s} {d['name'][:42]:42s} total={total:6d} fetched={len(got)}", flush=True)

df = pd.DataFrame(rows).sort_values(["disease_id", "target_symbol"]).reset_index(drop=True)
parquet_path = os.path.join(OUT, "genetics1_dataset.parquet")
df.to_parquet(parquet_path, index=False)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

sha = sha256(parquet_path)
manifest = {
    "source": "Open Targets Platform GraphQL API (https://api.platform.opentargets.org/api/v4/graphql)",
    "universe": "FULL associated-target list per disease (genome-wide test; absent genes are true "
                "genetic==0 & clinical==0 double-negatives, counted via protein-coding genome size in run.py)",
    "ot_meta": meta(),
    "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "n_diseases": len(DISEASES), "n_pairs": int(len(df)),
    "diseases": {efo: lbl for efo, lbl in DISEASES},
    "per_disease_counts": per_disease,
    "predictor": "genetic_association (OT genetic datatype; L2G/GWAS/ClinVar/G2P/Orphanet; evidence-based)",
    "outcome": "clinical (OT clinical-precedence = ChEMBL known drug for the indication)",
    "popularity_confounder": "literature (Europe PMC gene x disease text-mining co-mention)",
    "columns": list(df.columns), "parquet_sha256": sha, "license": "Open Targets Platform — CC0 1.0",
}
json.dump(manifest, open(os.path.join(OUT, "genetics1_manifest.json"), "w"), indent=2, sort_keys=True)
print("\nwrote", parquet_path, "rows:", len(df), "\nparquet_sha256:", sha, "\nOT:", manifest["ot_meta"])
