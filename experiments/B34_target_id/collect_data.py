"""B34 data acquisition (one-time, like a download): fetch Open Targets Platform target-disease associations for a
curated, diverse disease panel, with per-datatype evidence scores. Caches to $INTERCEPTA_DATA/opentargets/
ot_target_disease.parquet + records API/data version + sha256. NOT part of the reproduce-x2 (that runs the model on
the cache). Deterministic given the fixed disease list + a pinned Open Targets data version.
"""
import os, sys, json, time, hashlib, urllib.request
import pandas as pd

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
OUT = os.path.join(DATA, "opentargets"); os.makedirs(OUT, exist_ok=True)
API = "https://api.platform.opentargets.org/api/v4/graphql"
DATATYPES = ["genetic_association", "genetic_literature", "somatic_mutation", "affected_pathway",
             "animal_model", "rna_expression", "literature", "clinical"]
TOP_N = 300

# Curated diverse disease panel (40) across therapeutic areas — fixed a priori to avoid selection bias.
DISEASES = [
    "non-small cell lung carcinoma", "breast carcinoma", "colorectal carcinoma", "prostate carcinoma",
    "pancreatic carcinoma", "melanoma", "acute myeloid leukemia", "chronic lymphocytic leukemia",
    "ovarian carcinoma", "glioblastoma", "hepatocellular carcinoma", "gastric carcinoma",
    "rheumatoid arthritis", "systemic lupus erythematosus", "psoriasis", "inflammatory bowel disease",
    "multiple sclerosis", "asthma", "chronic obstructive pulmonary disease", "atopic dermatitis",
    "type 2 diabetes mellitus", "type 1 diabetes mellitus", "obesity", "nonalcoholic fatty liver disease",
    "Alzheimer disease", "Parkinson disease", "amyotrophic lateral sclerosis", "epilepsy", "schizophrenia",
    "major depressive disorder", "coronary artery disease", "heart failure", "hypertension",
    "chronic kidney disease", "osteoporosis", "osteoarthritis", "cystic fibrosis", "idiopathic pulmonary fibrosis",
    "psoriatic arthritis", "ankylosing spondylitis",
]


def gql(query):
    req = urllib.request.Request(API, data=json.dumps({"query": query}).encode(),
                                 headers={"Content-Type": "application/json"})
    for attempt in range(4):
        try:
            return json.loads(urllib.request.urlopen(req, timeout=60).read())
        except Exception as e:
            time.sleep(2 * (attempt + 1))
            if attempt == 3:
                raise
    return None


def resolve(name):
    q = '{ search(queryString:"%s", entityNames:["disease"], page:{index:0,size:1}){ hits{ id name entity } } }' % name
    hits = gql(q)["data"]["search"]["hits"]
    return (hits[0]["id"], hits[0]["name"]) if hits else (None, None)


def fetch_disease(did):
    q = ('{ disease(efoId:"%s"){ name associatedTargets(page:{index:0,size:%d}){ rows{ '
         'target{ id approvedSymbol } score datatypeScores{ id score } } } } }') % (did, TOP_N)
    d = gql(q)["data"]["disease"]
    if not d:
        return []
    rows = []
    for r in d["associatedTargets"]["rows"]:
        dts = {x["id"]: x["score"] for x in r["datatypeScores"]}
        row = {"disease_id": did, "disease_name": d["name"], "target_id": r["target"]["id"],
               "target_symbol": r["target"]["approvedSymbol"], "overall_score": r["score"]}
        for dt in DATATYPES:
            row[dt] = float(dts.get(dt, 0.0))
        rows.append(row)
    return rows


def main():
    ver = gql("{ meta{ apiVersion{x y z} dataVersion{year month} } }")["data"]["meta"]
    print("Open Targets API", ver["apiVersion"], "data", ver["dataVersion"])
    all_rows, resolved = [], {}
    for name in DISEASES:
        did, dname = resolve(name)
        if not did:
            print("  UNRESOLVED:", name); continue
        resolved[name] = did
        rows = fetch_disease(did)
        all_rows += rows
        print(f"  {name} -> {did} ({dname}): {len(rows)} targets")
        time.sleep(0.3)
    df = pd.DataFrame(all_rows).drop_duplicates(["disease_id", "target_id"]).reset_index(drop=True)
    path = os.path.join(OUT, "ot_target_disease.parquet")
    df.to_parquet(path, index=False)
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    meta = {"api_version": ver["apiVersion"], "data_version": ver["dataVersion"], "n_diseases": len(resolved),
            "n_pairs": len(df), "sha256": sha, "datatypes": DATATYPES, "top_n": TOP_N,
            "clinical_positive_rate": round(float((df["clinical"] > 0).mean()), 4)}
    json.dump(meta, open(os.path.join(OUT, "ot_meta.json"), "w"), indent=2)
    print(f"\ncached {len(df)} target-disease pairs -> {path}")
    print("sha256:", sha, "| clinical+ rate:", meta["clinical_positive_rate"])


if __name__ == "__main__":
    main()
