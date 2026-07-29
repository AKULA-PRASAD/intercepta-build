#!/bin/bash
# Build INTERCEPTA Charter v2.0 from markdown to publication-quality PDF
set -e

CHARTER_DIR="$HOME/INTERCEPTA/docs/charter"
cd "$CHARTER_DIR"

echo "Building INTERCEPTA Charter v2.0 PDF..."

# Build list of input files dynamically
INPUTS="metadata.yaml"
[ -f front_matter/preface.md ] && INPUTS="$INPUTS front_matter/preface.md"
for f in chapters/*.md; do
    INPUTS="$INPUTS $f"
done
[ -f back_matter/glossary.md ] && INPUTS="$INPUTS back_matter/glossary.md"
[ -f back_matter/colophon.md ] && INPUTS="$INPUTS back_matter/colophon.md"

echo "Input files:"
for f in $INPUTS; do echo "  $f"; done
echo ""

mkdir -p build

pandoc $INPUTS --pdf-engine=xelatex --toc --toc-depth=2 --top-level-division=chapter --resource-path="$CHARTER_DIR" -o build/INTERCEPTA_Charter_v2.0.pdf

if [ -f build/INTERCEPTA_Charter_v2.0.pdf ]; then
    SIZE=$(du -h build/INTERCEPTA_Charter_v2.0.pdf | cut -f1)
    echo "BUILT: build/INTERCEPTA_Charter_v2.0.pdf ($SIZE)"
else
    echo "BUILD FAILED"
    exit 1
fi
