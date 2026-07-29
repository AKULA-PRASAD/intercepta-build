#!/usr/bin/env bash
# fix_metadata_arrows.sh
#
# Real CSO follow-up patch for INTERCEPTA Charter v2.0.
#
# The previous patch (fix_charter_v2_format.sh) succeeded at stripping doubled
# chapter numbering, but my unicode-arrow fix appended a SECOND header-includes
# block as a duplicate YAML key after the closing --- marker. Pandoc parsed the
# duplicate, dropped the original preamble setup (microtype, xcolor, intercepta
# color), and put my \usepackage statements somewhere LaTeX rejected mid-document.
# Result: build error "LaTeX Error: Can be used only in preamble. ...l.92 \usepackage"
#
# This script:
#   1. Restores metadata.yaml from the backup created by the previous patch.
#   2. Properly merges the \newunicodechar declarations INTO the existing
#      header-includes: block (not as a duplicate key).
#   3. Rebuilds the PDF.
#
# Idempotent. Safe to run multiple times. Does not touch chapter source files —
# the previous patch's chapter prefix stripping is already correct and stays.

set -euo pipefail

CHARTER_DIR="$HOME/INTERCEPTA/docs/charter"
cd "$CHARTER_DIR"

echo "================================================================"
echo "INTERCEPTA Charter v2.0 — metadata.yaml proper-merge fix"
echo "Working directory: $CHARTER_DIR"
echo "================================================================"

# Step 1: locate the backup
echo ""
echo "Step 1: locating backup..."
BACKUP=$(ls -d .backup_* 2>/dev/null | head -1)
if [ -z "$BACKUP" ]; then
  echo "ERROR: no .backup_* directory found. Cannot restore original metadata.yaml."
  exit 1
fi
echo "  using backup: $BACKUP"

if [ ! -f "$BACKUP/metadata.yaml" ]; then
  echo "ERROR: $BACKUP/metadata.yaml does not exist."
  exit 1
fi

# Step 2: restore the original metadata.yaml
echo ""
echo "Step 2: restoring original metadata.yaml from backup..."
cp "$BACKUP/metadata.yaml" metadata.yaml
echo "  restored. Current contents:"
echo "  ----------------------------------------"
sed 's/^/  /' metadata.yaml
echo "  ----------------------------------------"

# Step 3: properly merge unicode arrow declarations into existing header-includes
# The original block ends with:
#     \definecolor{intercepta}{RGB}{45,75,135}
# We need to add lines AFTER that, BEFORE the closing ---.
#
# Approach: write the new metadata.yaml from scratch with the merged content.
# This is more robust than awk/sed line-surgery for a small file.
echo ""
echo "Step 3: writing merged metadata.yaml with unicode arrow declarations..."

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
---
YAMLEOF

echo "  written. New contents:"
echo "  ----------------------------------------"
sed 's/^/  /' metadata.yaml
echo "  ----------------------------------------"

# Step 4: rebuild
echo ""
echo "Step 4: rebuilding PDF..."
echo "----------------------------------------------------------------"
bash build.sh
BUILD_RESULT=$?
echo "----------------------------------------------------------------"

# Step 5: report
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
  fi
  echo ""
  echo "Open with:  open $CHARTER_DIR/$PDF_PATH"
else
  echo "BUILD FAILED. See output above for errors."
  echo ""
  echo "To roll back to original metadata.yaml:"
  echo "  cp $BACKUP/metadata.yaml metadata.yaml"
  exit 1
fi
echo "================================================================"
