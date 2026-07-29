"""Leakage-free splits.

The single most important correctness rule in cross-dataset drug-response prediction: the SAME physical cell
line must never appear in both train and test. GDSC and CCLE/PRISM share cell lines (matched COSMIC<->DepMap),
so a naive GDSC->CCLE split leaks. `disjoint_train_cosmics` removes every test cell line's COSMIC from the
training rows.
"""


def disjoint_train_cosmics(train_df, test_depmap_ids, dep2cos, cosmic_col="COSMIC_ID"):
    """Return train_df with rows for any test cell line (by COSMIC) removed -> disjoint train/test cell lines."""
    test_cos = {dep2cos.get(d) for d in test_depmap_ids}
    return train_df[~train_df[cosmic_col].isin(test_cos)]
