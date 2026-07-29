# Data manifest — sha256 of every input (public; not committed)

Point `INTERCEPTA_DATA` at a directory holding these files (default `/Users/kalki/kaalcura/data`).
`src/intercepta/data.py` verifies each file against the sha256 below at load time and refuses to run on a
mismatch. sha256 prefixes match the values recorded in the verified ~/kaalcura V1B run (provenance chain).

| name | sha256 | source |
|---|---|---|
| `gdsc_response.csv` | `b472905ea811c145b1827f382975756a66c2ac5dffbe9ad323148bfdea38cdb5` | GDSC2 drug response (LN_IC50) |
| `gdsc_expression.zip` | `a087c0f703050d86e9f108b03096308e541a70fdc105c6ea0a3c85f8f9b3b0d7` | GDSC cell-line expression |
| `depmap_expression.csv` | `6b8d5f3c00ce73a5e025922d52b74929e19359e323786a0314410762b0c08a16` | DepMap/CCLE 22Q2 expression |
| `depmap_meta.csv` | `382c0c26cf57a2fb82449f797c58cb0dfc2313949908d8f83560ebcf3e5bcbaa` | DepMap sample map (COSMIC↔DepMap) |
| `independent/prism_secondary_screen.csv` | `88d1013506e0cd6f191a51c5f3fdd3fb2be54f8afb4e19a5d1f8538e81fbfec8` | PRISM secondary screen (AUC) |
| `depmap_mut_try1.csv` | `e99e43789c1c4821ccb737a45cd6f4fbbeac709c5a8cca326846d6d9a16cf5c8` | DepMap somatic mutation MAF (B2) |
| `beataml_waves1to4_norm_exp_dbgap.txt` | `d5745b9dbf46dba866a3c7370bb0ba73b363ecdd21e01cc1d916b4e3021e6f87` | BeatAML patient tumor RNA (B3; INTERCEPTA_BEATAML) |
| `beataml_probit_curve_fits_v4_dbgap.txt` | `d4bc5f0d91f66314107411e0f2511adc987e29df5b83d9b03df56d3d12928314` | BeatAML ex-vivo drug AUC (B3; INTERCEPTA_BEATAML) |

All inputs are public repositories (GDSC, DepMap/CCLE, PRISM). No controlled-access data is present or
required for B1. Any controlled-access acquisition is a logged human gate (see DECISIONS.md).
| `independent/gdsc1/GDSC1_fitted_dose_response.xlsx` | `837b0686500fde75179e490de08f034abd9f882d8b0253d637bafe83e156dafd` | GDSC1 independent screen (B3c external replication) |
