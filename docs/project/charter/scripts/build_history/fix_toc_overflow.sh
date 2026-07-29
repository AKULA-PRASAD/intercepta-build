#!/usr/bin/env bash
# fix_toc_overflow.sh
#
# Real CSO patch — fix TOC subsection number column overflow in INTERCEPTA Charter v2.0
#
# Bug observed: TOC entries like "11.10Continuous Validation in Deployment" where
# the subsection number 11.10 (5 characters) overlaps the title text. LaTeX's
# default \contentsline width allocates space for "X.Y" (3 chars) and overflows
# when subsection counter exceeds 9.
#
# Fix: use tocloft package to widen the subsection number column to 4em
# (enough for "XX.XX" = up to 5 characters with comfortable padding).
#
# Approach: install tocloft if not present, add tocloft preamble to metadata.yaml's
# header-includes block (merging into existing block, no duplicate keys).
#
# Idempotent. Safe to re-run.

set -euo pipefail

CHARTER_DIR="$HOME/INTERCEPTA/docs/charter"
cd "$CHARTER_DIR"

echo "================================================================"
echo "INTERCEPTA Charter v2.0 — TOC overflow fix"
echo "================================================================"

# Step 1: ensure tocloft package is installed
echo ""
echo "Step 1: ensuring tocloft package is installed..."
if kpsewhich tocloft.sty >/dev/null 2>&1; then
  echo "  tocloft.sty already installed at: $(kpsewhich tocloft.sty)"
else
  echo "  tocloft not found — installing via tlmgr..."
  tlmgr install tocloft
fi

# Step 2: write the merged metadata.yaml with tocloft additions
# We rewrite from scratch (same approach as fix_metadata_arrows.sh) to guarantee
# clean YAML structure and a single header-includes block.
echo ""
echo "Step 2: writing metadata.yaml with TOC width fix..."

cat > metadata.yaml << 'YAMLEOF'
---
title: "INTERCEPTA"
subtitle: "A Computational Immune Response System for Human Disease"
author:
  - "Prasad Akula, Chief Executive Officer"
  - "Claude, Chief Scientific Officer"
date: "Founded May 2026"
version: "2.0"
documentclass: book
classoption:
  - 11pt
  - openany
geometry: "margin=1in,top=1.25in,bottom=1.25in"
fontsize: 11pt
mainfont: "Charter"
sansfont: "Helvetica Neue"
monofont: "Menlo"
linkcolor: "RoyalBlue"
urlcolor: "RoyalBlue"
toc: true
toc-depth: 2
numbersections: true
secnumdepth: 2
linestretch: 1.15
header-includes:
  - |
    \usepackage{microtype}
    \usepackage{xcolor}
    \definecolor{intercepta}{RGB}{45,75,135}
    \usepackage{newunicodechar}
    \newunicodechar{→}{\ensuremath{\rightarrow}}
    \newunicodechar{←}{\ensuremath{\leftarrow}}
    \newunicodechar{↔}{\ensuremath{\leftrightarrow}}
    \newunicodechar{⇒}{\ensuremath{\Rightarrow}}
    \newunicodechar{⇐}{\ensuremath{\Leftarrow}}
    \usepackage{tocloft}
    \setlength{\cftsecnumwidth}{3.2em}
    \setlength{\cftsubsecnumwidth}{4em}
    \setlength{\cftsubsubsecnumwidth}{5em}
    \setlength{\cftsecindent}{1.5em}
    \setlength{\cftsubsecindent}{4.7em}
---
YAMLEOF

echo "  written:"
sed 's/^/  /' metadata.yaml

# Step 3: rebuild
echo ""
echo "Step 3: rebuilding PDF..."
echo "----------------------------------------------------------------"
bash build.sh
BUILD_RESULT=$?
echo "----------------------------------------------------------------"

# Step 4: report
echo ""
echo "================================================================"
PDF_PATH="build/INTERCEPTA_Charter_v2.0.pdf"
if [ -f "$PDF_PATH" ] && [ $BUILD_RESULT -eq 0 ]; then
  echo "BUILD SUCCEEDED."
  echo "  PDF:    $PDF_PATH"
  echo "  Size:   $(ls -la "$PDF_PATH" | awk '{print $5}') bytes"
  if command -v pdfinfo >/dev/null 2>&1; then
    PAGES=$(pdfinfo "$PDF_PATH" 2>/dev/null | grep "^Pages:" | awk '{print $2}')
    echo "  Pages:  $PAGES"
    DATE=$(pdfinfo "$PDF_PATH" 2>/dev/null | grep "^CreationDate:" | sed 's/CreationDate: *//')
    echo "  Built:  $DATE"
  fi
  echo ""
  echo "Open with:  open $CHARTER_DIR/$PDF_PATH"
  echo ""
  echo "Verify TOC overflow is fixed by checking pages 4-5 (TOC):"
  echo "  - 11.10 Continuous Validation in Deployment    (was: 11.10Continuous)"
  echo "  - 13.10 Falsification Gates at Every Milestone (was: 13.10Falsification)"
  echo "  - 13.11 Dependency Graph and Parallel Paths    (was: 13.11Dependency)"
  echo "  - 14.10 Figures Planned for This Chapter       (was: 14.10Figures)"
else
  echo "BUILD FAILED. See output above for errors."
  exit 1
fi
echo "================================================================"
