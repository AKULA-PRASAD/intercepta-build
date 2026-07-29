#!/bin/bash
# INTERCEPTA Project Folder Comprehensive Inspection
# Read-only. No modifications.
# Author: Prasad Akula & Claude (CSO), 2026-05-08

PROJECT=$HOME/INTERCEPTA
OUTPUT=$PROJECT/docs/PROJECT_STATE_INSPECTION_$(date +%Y-%m-%d).md

echo "================================================================"
echo "INTERCEPTA Project State Inspection"
echo "Path: $PROJECT"
echo "Date: $(date)"
echo "================================================================"
echo ""

# Initialize output
mkdir -p $(dirname $OUTPUT)
{
  echo "# INTERCEPTA Project State Inspection"
  echo ""
  echo "**Path:** \`$PROJECT\`"
  echo "**Date:** $(date)"
  echo ""
  echo "---"
  echo ""
} > $OUTPUT

# ── 1. Top-level directory structure ────────────────────────────
echo "[1/8] Top-level directory structure"
echo "## 1. Top-level directory structure" >> $OUTPUT
echo '' >> $OUTPUT
echo '```' >> $OUTPUT
ls -la $PROJECT 2>/dev/null | grep -v "^total" | head -50 | tee -a $OUTPUT
echo '```' >> $OUTPUT
echo '' >> $OUTPUT
echo ""

# ── 2. Total project size and file counts by type ───────────────
echo "[2/8] Project size and file counts"
echo "## 2. Project size and file counts" >> $OUTPUT
echo '' >> $OUTPUT
total_size=$(du -sh $PROJECT 2>/dev/null | awk '{print $1}')
echo "**Total project size:** $total_size" | tee -a $OUTPUT
echo "" >> $OUTPUT

echo "**Files by type:**" >> $OUTPUT
echo '' >> $OUTPUT
echo '```' >> $OUTPUT
echo "  .py files:        $(find $PROJECT -name '*.py' -type f 2>/dev/null | wc -l)"
echo "  .json files:      $(find $PROJECT -name '*.json' -type f 2>/dev/null | wc -l)"
echo "  .md files:        $(find $PROJECT -name '*.md' -type f 2>/dev/null | wc -l)"
echo "  .csv files:       $(find $PROJECT -name '*.csv' -type f 2>/dev/null | wc -l)"
echo "  .tsv files:       $(find $PROJECT -name '*.tsv' -type f 2>/dev/null | wc -l)"
echo "  .txt files:       $(find $PROJECT -name '*.txt' -type f 2>/dev/null | wc -l)"
echo "  .slurm files:     $(find $PROJECT -name '*.slurm' -type f 2>/dev/null | wc -l)"
echo "  .h5ad files:      $(find $PROJECT -name '*.h5ad' -type f 2>/dev/null | wc -l)"
echo "  .pdf files:       $(find $PROJECT -name '*.pdf' -type f 2>/dev/null | wc -l)"
echo "  .docx files:      $(find $PROJECT -name '*.docx' -type f 2>/dev/null | wc -l)"
echo "  .yml/.yaml files: $(find $PROJECT \( -name '*.yml' -o -name '*.yaml' \) -type f 2>/dev/null | wc -l)" >> /tmp/_inspection_pipeline_holding.txt
{
  echo "  .py files:        $(find $PROJECT -name '*.py' -type f 2>/dev/null | wc -l)"
  echo "  .json files:      $(find $PROJECT -name '*.json' -type f 2>/dev/null | wc -l)"
  echo "  .md files:        $(find $PROJECT -name '*.md' -type f 2>/dev/null | wc -l)"
  echo "  .csv files:       $(find $PROJECT -name '*.csv' -type f 2>/dev/null | wc -l)"
  echo "  .tsv files:       $(find $PROJECT -name '*.tsv' -type f 2>/dev/null | wc -l)"
  echo "  .txt files:       $(find $PROJECT -name '*.txt' -type f 2>/dev/null | wc -l)"
  echo "  .slurm files:     $(find $PROJECT -name '*.slurm' -type f 2>/dev/null | wc -l)"
  echo "  .h5ad files:      $(find $PROJECT -name '*.h5ad' -type f 2>/dev/null | wc -l)"
  echo "  .pdf files:       $(find $PROJECT -name '*.pdf' -type f 2>/dev/null | wc -l)"
  echo "  .docx files:      $(find $PROJECT -name '*.docx' -type f 2>/dev/null | wc -l)"
} >> $OUTPUT
echo '```' >> $OUTPUT
echo '' >> $OUTPUT
echo ""

# ── 3. Subdirectory sizes ───────────────────────────────────────
echo "[3/8] Subdirectory sizes"
echo "## 3. Subdirectory sizes" >> $OUTPUT
echo '' >> $OUTPUT
echo '```' >> $OUTPUT
for d in $(ls -d $PROJECT/*/ 2>/dev/null); do
  size=$(du -sh "$d" 2>/dev/null | awk '{print $1}')
  printf "  %-10s %s\n" "$size" "$(basename $d)/"
done | sort -h -r | head -30 | tee -a $OUTPUT
echo '```' >> $OUTPUT
echo '' >> $OUTPUT
echo ""

# ── 4. Git state ────────────────────────────────────────────────
echo "[4/8] Git state"
echo "## 4. Git state" >> $OUTPUT
echo '' >> $OUTPUT
cd $PROJECT
echo '```' >> $OUTPUT
echo "Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null)" >> $OUTPUT
echo "HEAD: $(git rev-parse --short HEAD 2>/dev/null)" >> $OUTPUT
echo "Origin: $(git config --get remote.origin.url 2>/dev/null)" >> $OUTPUT
echo "" >> $OUTPUT
echo "Sync state with origin/main:" >> $OUTPUT
git rev-list --count origin/main..HEAD >/dev/null 2>&1
ahead=$(git rev-list --count origin/main..HEAD 2>/dev/null)
behind=$(git rev-list --count HEAD..origin/main 2>/dev/null)
echo "  Ahead:  ${ahead:-?} commits" >> $OUTPUT
echo "  Behind: ${behind:-?} commits" >> $OUTPUT
echo "" >> $OUTPUT
echo "Working tree status:" >> $OUTPUT
git status --short 2>/dev/null | head -20 >> $OUTPUT
n_changes=$(git status --porcelain 2>/dev/null | wc -l)
echo "" >> $OUTPUT
echo "Total uncommitted changes: $n_changes" >> $OUTPUT
echo '```' >> $OUTPUT
echo '' >> $OUTPUT

# ── 5. Recent commits ───────────────────────────────────────────
echo "[5/8] Recent commits"
echo "## 5. Last 15 commits" >> $OUTPUT
echo '' >> $OUTPUT
echo '```' >> $OUTPUT
git log --oneline -15 2>/dev/null | head -30 >> $OUTPUT
echo '```' >> $OUTPUT
echo '' >> $OUTPUT

# ── 6. Tags ─────────────────────────────────────────────────────
echo "[6/8] Tags"
echo "## 6. Tags (chronological)" >> $OUTPUT
echo '' >> $OUTPUT
echo '```' >> $OUTPUT
n_tags=$(git tag | wc -l)
echo "Total tags: $n_tags" >> $OUTPUT
echo "" >> $OUTPUT
echo "Last 25 tags by creation time:" >> $OUTPUT
git for-each-ref --sort=creatordate --format='%(creatordate:short)  %(refname:short)' refs/tags 2>/dev/null | tail -25 >> $OUTPUT
echo '```' >> $OUTPUT
echo '' >> $OUTPUT

# ── 7. Data directory status ────────────────────────────────────
echo "[7/8] Data directory status"
echo "## 7. Data directory status" >> $OUTPUT
echo '' >> $OUTPUT
echo '```' >> $OUTPUT
if [ -d "$PROJECT/data" ]; then
  echo "data/ contents:"
  ls -la $PROJECT/data 2>/dev/null | head -20 >> $OUTPUT
  echo "" >> $OUTPUT
  for d in $(ls -d $PROJECT/data/*/ 2>/dev/null); do
    size=$(du -sh "$d" 2>/dev/null | awk '{print $1}')
    n_files=$(find "$d" -type f 2>/dev/null | wc -l)
    printf "  %-10s %5s files  %s\n" "$size" "$n_files" "$(basename $d)/" >> $OUTPUT
  done
fi
echo '```' >> $OUTPUT
echo '' >> $OUTPUT

# ── 8. Top-level documents and key results ──────────────────────
echo "[8/8] Top-level docs and key results"
echo "## 8. Top-level documents" >> $OUTPUT
echo '' >> $OUTPUT
echo '```' >> $OUTPUT
ls -la $PROJECT/*.md 2>/dev/null | tail -20 >> $OUTPUT
echo '```' >> $OUTPUT
echo '' >> $OUTPUT
echo '## 9. docs/ directory' >> $OUTPUT
echo '' >> $OUTPUT
echo '```' >> $OUTPUT
ls -la $PROJECT/docs/ 2>/dev/null | head -20 >> $OUTPUT
echo '```' >> $OUTPUT
echo '' >> $OUTPUT

# Final summary
echo ""
echo "================================================================"
echo "Inspection complete."
echo "Full report saved to: $OUTPUT"
echo "================================================================"
echo ""
echo "Quick summary:"
echo "  Total project size: $total_size"
echo "  Total tags: $n_tags"
echo "  Uncommitted changes: $n_changes"
echo "  HEAD: $(git rev-parse --short HEAD 2>/dev/null)"
echo ""
echo "Read full report:  cat $OUTPUT"
