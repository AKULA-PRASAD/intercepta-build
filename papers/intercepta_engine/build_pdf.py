"""Build a preprint PDF from MANUSCRIPT.md + the four figures. Reproducible.
Renders with pandoc + xelatex using a wide-coverage Unicode main font (Greek, superscripts, arrows, math symbols)
so no glyph is silently dropped. Source MANUSCRIPT.md is unchanged; only a temporary build copy adds the figures.
Run:  python papers/intercepta_engine/build_pdf.py
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "MANUSCRIPT.md")).read()

FIG_APPENDIX = """

\\newpage

# Figures

**Figure 1.** Cross-dataset transfer and its ceiling (B1).

![](figures/Fig1_transfer_ceiling.png){width=58%}

**Figure 2.** A functional-inference layer promising in BeatAML fails independent replication (B18/B20/B21).

![](figures/Fig2_functional_replication.png){width=98%}

**Figure 3.** Human clinical prediction is cancer-type confounding (B10).

![](figures/Fig3_clinical_null.png){width=58%}

**Figure 4.** Drug-combination synergy — the externally-validated positive (B24/B28/B29).

![](figures/Fig4_synergy_positive.png){width=98%}
"""

build_md = os.path.join(HERE, "_build.md")
open(build_md, "w").write(src + FIG_APPENDIX)

# pick the first installed font with wide unicode coverage (Greek + superscripts + arrows)
def font_available(name):
    out = subprocess.run(["fc-list", name], capture_output=True, text=True).stdout
    return name.split()[0].lower() in out.lower() if out else False
candidates = ["Arial Unicode MS", "STIX Two Text", "DejaVu Serif", "Noto Serif"]
mainfont = next((f for f in candidates if font_available(f)), None)

cmd = ["pandoc", build_md, "-o", os.path.join(HERE, "MANUSCRIPT.pdf"), "--pdf-engine=xelatex",
       "-V", "geometry:margin=1in", "-V", "fontsize=10pt", "-V", "linkcolor=blue", "--toc", "--toc-depth=2"]
if mainfont:
    cmd += ["-V", "mainfont=" + mainfont]
r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True)
os.remove(build_md)
warns = sorted({l.split("There is no ")[1].split(" ")[0] for l in r.stderr.splitlines() if "Missing character" in l}) if r.returncode == 0 else []
print(f"mainfont={mainfont!r} | pandoc return={r.returncode} | distinct missing glyphs: {warns if warns else 'none'}")
if r.returncode != 0:
    print(r.stderr[-1200:]); sys.exit(1)
print("wrote MANUSCRIPT.pdf")
