#!/usr/bin/env python
"""PHENO1 — FETCH-ONCE data freezer. Downloads the HPO 2026-06-23 release files to
$INTERCEPTA_DATA/pheno1/ and verifies SHA-256. Idempotent (skips a file whose sha already matches).
Data is written ONLY to $INTERCEPTA_DATA, never committed. run.py re-verifies these SHAs before scoring.
"""
import os, hashlib, urllib.request

DATA = "/Users/kalki/intercepta_data/pheno1"
os.makedirs(DATA, exist_ok=True)
BASE_HPOA = "https://purl.obolibrary.org/obo/hp/hpoa"
FILES = {
    "phenotype.hpoa":         (f"{BASE_HPOA}/phenotype.hpoa",         "89004f85b253f980ffe84218d2c080665cbf67a57bbb322111d6a2db5eb31dff"),
    "genes_to_disease.txt":   (f"{BASE_HPOA}/genes_to_disease.txt",   "a247027ae9944e34545e0a91060243ff6c118681c06379b9721af1ee4f39286a"),
    "genes_to_phenotype.txt": (f"{BASE_HPOA}/genes_to_phenotype.txt", "26cb7ee00c73b5777f6e5ad43323c941e1fcef1d191592f332d7929f3ea1ab3f"),
    "phenotype_to_genes.txt": (f"{BASE_HPOA}/phenotype_to_genes.txt", "1386a4dd3ea046f5a5971f4011a3711a9d7928d60961e2e7b757b6860c63c778"),
    "hp.obo":                 ("https://purl.obolibrary.org/obo/hp.obo", "a5092cbdf605f568403cf7380d9173014015692433b2cc631bc5c1b053876b1b"),
}

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

for name, (url, want) in FILES.items():
    path = os.path.join(DATA, name)
    if os.path.exists(path) and sha256(path) == want:
        print(f"[skip] {name} (sha ok)"); continue
    print(f"[fetch] {name} <- {url}")
    urllib.request.urlretrieve(url, path)
    got = sha256(path)
    assert got == want, f"sha mismatch {name}: {got} != {want} (HPO release changed?)"
    print(f"[ok]   {name} sha {got}")
print("PHENO1 data frozen at", DATA)
