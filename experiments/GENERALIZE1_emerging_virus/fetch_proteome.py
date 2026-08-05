"""Fetch the SARS-CoV-2 MATURE proteome (label-free; no drug knowledge). Polyproteins pp1a (P0DTC1) and
pp1ab (P0DTD1) are split into their mature chains (nsp1-16) via UniProt 'Chain' features; structural and
accessory proteins are taken whole. Writes mature_proteins.fasta. Open data (UniProt REST). Stdlib only."""
import os, sys, json, urllib.parse, urllib.request, time

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
OUT = os.path.join(DATA, "generalize1"); os.makedirs(OUT, exist_ok=True)
FASTA = os.path.join(OUT, "mature_proteins.fasta")
TAXID = 2697049  # SARS-CoV-2

# short label for the mature product, keyed by chain-feature description substrings (for readability only;
# NOT used to score — scoring is by homology to non-coronaviral drug targets)
NSP_HINT = {"nsp5": "3C-like", "nsp12": "RNA-directed RNA polymerase", "nsp3": "Papain-like",
            "nsp13": "Helicase", "nsp14": "Proofreading", "nsp16": "2'-O-methyltransferase"}


def get(url):
    for _ in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            sys.stderr.write(f"retry {url[:80]}: {e}\n"); time.sleep(3)
    raise SystemExit("fetch failed: " + url)


def main():
    q = urllib.parse.urlencode({"query": f"organism_id:{TAXID} AND reviewed:true",
                                "format": "json", "size": 500,
                                "fields": "accession,protein_name,sequence,ft_chain"})
    data = get("https://rest.uniprot.org/uniprotkb/search?" + q)
    seqs = []  # (name, acc, seq)
    for e in data.get("results", []):
        acc = e["primaryAccession"]
        pname = e.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", acc)
        seq = e["sequence"]["value"]
        chains = [f for f in e.get("features", []) if f.get("type") == "Chain"]
        # split polyproteins into mature chains; keep single-chain proteins whole
        mature = [c for c in chains if c["location"]["start"]["value"] and c["location"]["end"]["value"]]
        is_poly = ("polyprotein" in pname.lower()) or len(mature) > 3
        if is_poly and mature:
            for c in mature:
                s = int(c["location"]["start"]["value"]); en = int(c["location"]["end"]["value"])
                desc = c.get("description", f"{s}-{en}")
                sub = seq[s - 1:en]
                if len(sub) < 30 or len(sub) > 2500:  # skip tiny cleavage products AND the whole uncut polyprotein
                    continue
                label = None
                for k, hint in NSP_HINT.items():
                    if hint.lower() in desc.lower():
                        label = k; break
                nm = (label + "_" if label else "") + desc.replace(" ", "-")[:40]
                seqs.append((nm, f"{acc}:{s}-{en}", sub))
        else:
            seqs.append((pname.replace(" ", "-")[:40], acc, seq))
    # Spike P0DTC2: keep only the full-length spike, drop S1/S2/S2' proteolytic sub-fragments (one functional unit)
    spike = [x for x in seqs if x[1].startswith("P0DTC2")]
    if spike:
        keep_spike = max(spike, key=lambda x: len(x[2]))
        seqs = [x for x in seqs if not x[1].startswith("P0DTC2")] + [keep_spike]
    # de-dup identical sequences (pp1a nsp1-10 ⊂ pp1ab): keep first (prefer longer polyprotein set already)
    seen = {}; uniq = []
    for nm, tag, s in seqs:
        if s in seen:
            continue
        seen[s] = 1; uniq.append((nm, tag, s))
    with open(FASTA, "w") as f:
        for nm, tag, s in uniq:
            f.write(f">{nm}|{tag}\n{s}\n")
    print(f"wrote {len(uniq)} mature proteins -> {FASTA}")
    for nm, tag, s in uniq:
        print(f"  {nm:45s} {tag:20s} {len(s)} aa")


if __name__ == "__main__":
    main()
