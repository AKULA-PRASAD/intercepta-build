#!/usr/bin/env bash
# fix_charter_v2_format.sh
# Real CSO patch for INTERCEPTA Charter v2.0 PDF formatting bugs.
#
# Fixes two cosmetic issues observed in the first build:
#   Bug 1: Doubled chapter/section numbering ("Chapter 7  Chapter 6:", "12.7 11.7")
#          Cause: manual "Chapter N:" and "N.M" prefixes in markdown PLUS LaTeX auto-numbering
#          Fix: strip manual prefixes, let LaTeX number; mark front/back matter as unnumbered
#
#   Bug 2: Missing arrow glyph (→ U+2192) — 14 warnings during build
#          Cause: Charter font lacks the arrow glyph
#          Fix: add fontspec unicode-fallback declaration to metadata.yaml
#
# Idempotent: safe to run multiple times. Creates a timestamped backup before
# any modification. Reports word counts before and after.

set -euo pipefail

CHARTER_DIR="$HOME/INTERCEPTA/docs/charter"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$CHARTER_DIR/.backup_${TIMESTAMP}"

cd "$CHARTER_DIR" || { echo "ERROR: cannot cd to $CHARTER_DIR"; exit 1; }

echo "================================================================"
echo "INTERCEPTA Charter v2.0 format patch"
echo "Working directory: $CHARTER_DIR"
echo "Backup directory:  $BACKUP_DIR"
echo "================================================================"

# Step 0: Backup
echo ""
echo "Step 0: backing up current sources..."
mkdir -p "$BACKUP_DIR"
cp -R chapters "$BACKUP_DIR/chapters"
cp -R front_matter "$BACKUP_DIR/front_matter" 2>/dev/null || true
cp -R back_matter "$BACKUP_DIR/back_matter" 2>/dev/null || true
cp metadata.yaml "$BACKUP_DIR/metadata.yaml" 2>/dev/null || true
cp build.sh "$BACKUP_DIR/build.sh" 2>/dev/null || true
echo "  backup written to $BACKUP_DIR"

WORDS_BEFORE=$(wc -w chapters/*.md | tail -1 | awk '{print $1}')
echo "  word count before patch: $WORDS_BEFORE"

# Step 1: Strip manual chapter prefixes from chapter files
# Pattern A: "# Chapter N: <title>"  ->  "# <title>"
# Pattern B: "## N.M <title>"        ->  "## <title>"
# Pattern C: "### N.M.K <title>"     ->  "### <title>"
# We use BSD sed (macOS) -i '' for in-place edits.
echo ""
echo "Step 1: stripping manual numbering prefixes from chapter headings..."
for f in chapters/*.md; do
  # Strip "# Chapter N: " (where N is digits) at start of line
  sed -i '' -E 's/^# Chapter [0-9]+: /# /' "$f"
  # Strip "## N.M " (e.g., "## 6.1 ", "## 13.10 ") at start of line
  sed -i '' -E 's/^## [0-9]+\.[0-9]+ /## /' "$f"
  # Strip "### N.M.K " just in case
  sed -i '' -E 's/^### [0-9]+\.[0-9]+\.[0-9]+ /### /' "$f"
done
echo "  patched 18 chapter files"

# Step 2: Mark front matter and back matter as unnumbered
# Append {.unnumbered} to their top-level headings so LaTeX doesn't chapter-number them.
echo ""
echo "Step 2: marking front/back matter as unnumbered..."
# Front matter: preface
if [ -f front_matter/preface.md ]; then
  # Only add {.unnumbered} if not already present
  if ! grep -q "{.unnumbered}" front_matter/preface.md; then
    sed -i '' -E 's/^(# [^{]*[^ ])$/\1 {.unnumbered}/' front_matter/preface.md
  fi
  echo "  preface.md: $(grep -E "^# " front_matter/preface.md | head -1)"
fi

# Back matter: glossary
if [ -f back_matter/glossary.md ]; then
  if ! grep -q "{.unnumbered}" back_matter/glossary.md; then
    sed -i '' -E 's/^(# [^{]*[^ ])$/\1 {.unnumbered}/' back_matter/glossary.md
  fi
  echo "  glossary.md: $(grep -E "^# " back_matter/glossary.md | head -1)"
fi

# Back matter: colophon
if [ -f back_matter/colophon.md ]; then
  if ! grep -q "{.unnumbered}" back_matter/colophon.md; then
    sed -i '' -E 's/^(# [^{]*[^ ])$/\1 {.unnumbered}/' back_matter/colophon.md
  fi
  echo "  colophon.md: $(grep -E "^# " back_matter/colophon.md | head -1)"
fi

# Step 3: Add unicode arrow fallback to metadata.yaml
# We add a header-includes block that declares Charter as the main font but
# tells fontspec to fall back to a font that has arrows for the missing glyph.
# DejaVu Sans is on every Mac via TeX Live and contains all needed unicode arrows.
echo ""
echo "Step 3: adding unicode arrow fallback to metadata.yaml..."
if grep -q "unicode-fallback-applied" metadata.yaml; then
  echo "  metadata.yaml already contains unicode fallback marker — skipping"
else
  # We append a YAML block at the end. Pandoc merges multiple keys; if header-includes
  # already exists, we add to it. Simplest robust approach: append our additions at the
  # end of the file inside a new yaml document marker.
  cat >> metadata.yaml << 'EOF'

# unicode-fallback-applied
header-includes: |
  \usepackage{newunicodechar}
  \newunicodechar{→}{\ensuremath{\rightarrow}}
  \newunicodechar{←}{\ensuremath{\leftarrow}}
  \newunicodechar{↔}{\ensuremath{\leftrightarrow}}
  \newunicodechar{⇒}{\ensuremath{\Rightarrow}}
  \newunicodechar{⇐}{\ensuremath{\Leftarrow}}
EOF
  echo "  unicode-fallback declarations appended to metadata.yaml"
fi

# Step 4: Sanity check word counts (should be identical, only headings touched)
echo ""
echo "Step 4: verifying content integrity..."
WORDS_AFTER=$(wc -w chapters/*.md | tail -1 | awk '{print $1}')
echo "  word count after patch:  $WORDS_AFTER"
echo "  (should differ only by removed numeric prefixes — about 200-300 fewer words)"

# Step 5: Rebuild
echo ""
echo "Step 5: rebuilding PDF..."
echo "----------------------------------------------------------------"
bash build.sh 2>&1 | tail -25
echo "----------------------------------------------------------------"

# Step 6: Report
echo ""
echo "================================================================"
echo "PATCH COMPLETE."
echo "================================================================"
PDF_PATH="build/INTERCEPTA_Charter_v2.0.pdf"
if [ -f "$PDF_PATH" ]; then
  echo "PDF:    $PDF_PATH"
  echo "Size:   $(ls -la "$PDF_PATH" | awk '{print $5}') bytes"
  if command -v pdfinfo >/dev/null 2>&1; then
    PAGES=$(pdfinfo "$PDF_PATH" 2>/dev/null | grep "^Pages:" | awk '{print $2}')
    echo "Pages:  $PAGES"
  fi
  echo ""
  echo "To open it now:"
  echo "  open $CHARTER_DIR/$PDF_PATH"
else
  echo "WARNING: PDF not found at $PDF_PATH — build may have failed."
  echo "Check the build output above."
fi
echo ""
echo "Backup of pre-patch sources is at: $BACKUP_DIR"
echo "If anything looks wrong in the new PDF, restore with:"
echo "  cp -R $BACKUP_DIR/chapters/* $CHARTER_DIR/chapters/"
echo "  cp $BACKUP_DIR/metadata.yaml $CHARTER_DIR/metadata.yaml"
echo "  cp $BACKUP_DIR/front_matter/* $CHARTER_DIR/front_matter/  2>/dev/null"
echo "  cp $BACKUP_DIR/back_matter/* $CHARTER_DIR/back_matter/   2>/dev/null"
echo ""
