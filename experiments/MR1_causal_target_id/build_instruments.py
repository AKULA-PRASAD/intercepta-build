#!/usr/bin/env python
"""MR1 step 1 — build the cis-eQTL instrument table: per gene, the single strongest cis-eQTL SNP
(max |Z|) from eQTLGen. Output columns kept minimal for MR harmonization. Deterministic.
Reads $INTERCEPTA_DATA/mr1/eqtlgen_cis.txt.gz; writes $INTERCEPTA_DATA/mr1/instruments.parquet."""
import os, pandas as pd, numpy as np

D = os.environ.get("INTERCEPTA_DATA", os.path.expanduser("~/intercepta_data"))
SRC = os.path.join(D, "mr1", "eqtlgen_cis.txt.gz")
OUT = os.path.join(D, "mr1", "instruments.parquet")

cols = ["Pvalue", "SNP", "SNPChr", "SNPPos", "AssessedAllele", "OtherAllele", "Zscore", "Gene", "GeneSymbol"]
df = pd.read_csv(SRC, sep="\t", usecols=cols, dtype={"SNPChr": str})
df["absZ"] = df["Zscore"].abs()
# strongest cis-eQTL SNP per gene (deterministic tie-break: max absZ, then lowest SNPPos, then SNP id)
df = df.sort_values(["Gene", "absZ", "SNPPos", "SNP"], ascending=[True, False, True, True])
inst = df.drop_duplicates("Gene", keep="first").reset_index(drop=True)
inst = inst[["Gene", "GeneSymbol", "SNP", "SNPChr", "SNPPos", "AssessedAllele", "OtherAllele", "Zscore", "Pvalue"]]
inst.to_parquet(OUT, index=False)
print(f"genes with an instrument: {len(inst)}")
print(f"unique instrument SNPs:  {inst.SNP.nunique()}")
print(inst.head(4).to_string())
print(f"written -> {OUT}")
