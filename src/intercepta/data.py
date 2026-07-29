"""Data access with sha256 verification against data/MANIFEST.md.

Inputs are PUBLIC (GDSC2, DepMap/CCLE 22Q2, PRISM secondary) but are NOT committed. Point the env var
INTERCEPTA_DATA at a checkout; every file is hashed and checked against the manifest before use, so a silently
different data file fails loudly instead of producing a wrong number.
"""
import os, hashlib, zipfile, re
import numpy as np, pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", ".."))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
MANIFEST = os.path.join(_REPO, "data", "MANIFEST.md")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _manifest():
    """Parse `data/MANIFEST.md` rows of the form `| name | sha256 | ... |`."""
    out = {}
    if not os.path.exists(MANIFEST):
        return out
    for line in open(MANIFEST):
        m = re.match(r"\|\s*`?([^|`]+?)`?\s*\|\s*`?([0-9a-fA-F]{64})`?\s*\|", line)
        if m:
            out[m.group(1).strip()] = m.group(2).strip().lower()
    return out


def verify(name, path):
    """Fail loudly if the on-disk file does not match the recorded sha256 (skip only if not yet recorded)."""
    expected = _manifest().get(name)
    if expected is None:
        return  # manifest not yet populated for this input; loaders still work, provenance just unverified
    got = sha256(path)
    if got != expected:
        raise RuntimeError(f"sha256 mismatch for {name}: expected {expected}, got {got}. "
                           f"Data at {path} does not match data/MANIFEST.md — refusing to produce a result.")


def _p(fname):
    return os.path.join(DATA, fname)


def z_rows(df):
    """Z-score each row (gene) across columns (cells)."""
    return df.sub(df.mean(1), axis=0).div(df.std(1).replace(0, np.nan), axis=0)


def load_cosmic_depmap_map():
    """COSMIC id <-> DepMap id, from DepMap sample metadata."""
    verify("depmap_meta.csv", _p("depmap_meta.csv"))
    meta = pd.read_csv(_p("depmap_meta.csv"), low_memory=False)[["DepMap_ID", "COSMICID"]].dropna()
    meta["COSMICID"] = meta["COSMICID"].astype(float).astype("Int64").astype(str)
    cos2dep = dict(zip(meta["COSMICID"], meta["DepMap_ID"]))
    return cos2dep, {v: k for k, v in cos2dep.items()}


def load_gdsc_response():
    verify("gdsc_response.csv", _p("gdsc_response.csv"))
    g = pd.read_csv(_p("gdsc_response.csv"), usecols=["DRUG_NAME", "COSMIC_ID", "LN_IC50"]).dropna()
    g["COSMIC_ID"] = g["COSMIC_ID"].astype(int).astype(str)
    return g


def load_prism():
    verify("prism_secondary_screen.csv", _p("independent/prism_secondary_screen.csv"))
    return pd.read_csv(_p("independent/prism_secondary_screen.csv"),
                       usecols=["depmap_id", "name", "auc"]).dropna()


def load_gdsc_expression():
    """GDSC expression as genes(rows) x cells(cols, COSMIC id)."""
    verify("gdsc_expression.zip", _p("gdsc_expression.zip"))
    with zipfile.ZipFile(_p("gdsc_expression.zip")) as z:
        with z.open(z.namelist()[0]) as f:
            gx = pd.read_csv(f, sep="\t", index_col=0)
    gx = gx.drop(columns=["GENE_title"], errors="ignore").select_dtypes("number")
    gx.columns = [str(c).replace("DATA.", "") for c in gx.columns]
    return gx[~gx.index.duplicated()]


def load_depmap_expression():
    """DepMap/CCLE expression as cells(rows) x genes(cols, symbol)."""
    verify("depmap_expression.csv", _p("depmap_expression.csv"))
    dx = pd.read_csv(_p("depmap_expression.csv"), index_col=0)
    dx = dx.rename(columns={c: c.split(" (")[0] for c in dx.columns if " (" in c})
    return dx.loc[:, ~dx.columns.duplicated()]


# Non-silent coding variant classes (pre-registered "damaging" definition for B2). Silent/Intron/etc excluded.
NONSILENT = {"Missense_Mutation", "Nonsense_Mutation", "Frame_Shift_Del", "Frame_Shift_Ins",
             "Splice_Site", "In_Frame_Del", "In_Frame_Ins", "Nonstop_Mutation",
             "Start_Codon_SNP", "De_novo_Start_OutOfFrame"}


def load_damaging_mutations():
    """DepMap MAF -> dict[DepMap_ID] = set(Hugo_Symbol with a non-silent coding variant).

    Memory-efficient (no dense cell x gene matrix). Keyed by DepMap_ID so it joins directly to CCLE
    expression cells, and to GDSC cells via COSMIC->DepMap.
    """
    verify("depmap_mut_try1.csv", _p("depmap_mut_try1.csv"))
    maf = pd.read_csv(_p("depmap_mut_try1.csv"),
                      usecols=["Hugo_Symbol", "Variant_Classification", "DepMap_ID"], low_memory=False).dropna()
    maf = maf[maf["Variant_Classification"].isin(NONSILENT)]
    out = {}
    for dep, sym in zip(maf["DepMap_ID"].values, maf["Hugo_Symbol"].values):
        out.setdefault(dep, set()).add(sym)
    return out
