#!/bin/bash
# Compare every file in ~/Downloads vs every file in ~/INTERCEPTA
# Output:
#   - List of byte-identical duplicates (safe to quarantine)
#   - List of same-name-different-content (investigate)
#   - List of Downloads files with no match (unique)
#
# Strategy: hash all project files first, then for each Downloads file,
# check if its hash matches any project file's hash.

OUTPUT=~/Downloads_vs_INTERCEPTA_audit.txt
DOWNLOADS=$HOME/Downloads
PROJECT=$HOME/INTERCEPTA

echo "INTERCEPTA Downloads vs Project Audit" > $OUTPUT
echo "Generated: $(date)" >> $OUTPUT
echo "================================================" >> $OUTPUT
echo "" >> $OUTPUT

# Skip system folders, user-data folders that shouldn't be touched
SKIP_DOWNLOADS_DIRS="_INTERCEPTA_quarantine_2026-05-08|.pytest_cache|__pycache__"
SKIP_PROJECT_DIRS="__pycache__|.git|envs|data/nsclc|data/manifests|data/manifests_v2|data/alphafold_cache|data/chembl|data/clinicaltrials|data/gdsc"

echo "[Step 1/3] Hashing project files (skip: $SKIP_PROJECT_DIRS)..." | tee -a $OUTPUT
PROJECT_HASHES=$(mktemp)
find $PROJECT -type f 2>/dev/null \
  | grep -vE "/($SKIP_PROJECT_DIRS)/" \
  | while read f; do
      hash=$(md5 -q "$f" 2>/dev/null)
      if [ -n "$hash" ]; then
        size=$(stat -f%z "$f" 2>/dev/null)
        echo "${hash}|${size}|${f}"
      fi
    done > $PROJECT_HASHES
n_project=$(wc -l < $PROJECT_HASHES)
echo "  Hashed $n_project project files." | tee -a $OUTPUT
echo "" >> $OUTPUT

echo "[Step 2/3] Comparing Downloads files (skip: $SKIP_DOWNLOADS_DIRS)..." | tee -a $OUTPUT

DUPES=$(mktemp)
SAME_NAME_DIFF=$(mktemp)
UNIQUE=$(mktemp)

find $DOWNLOADS -maxdepth 1 -type f 2>/dev/null \
  | while read dl_file; do
      dl_hash=$(md5 -q "$dl_file" 2>/dev/null)
      dl_size=$(stat -f%z "$dl_file" 2>/dev/null)
      dl_name=$(basename "$dl_file")
      
      # Look for byte-identical match in project (same hash)
      match_by_hash=$(grep "^${dl_hash}|" $PROJECT_HASHES | head -1)
      
      if [ -n "$match_by_hash" ]; then
        proj_path=$(echo "$match_by_hash" | cut -d'|' -f3)
        echo "${dl_size}|${dl_file}|${proj_path}" >> $DUPES
      else
        # Same name in project but different content?
        same_name=$(grep "/${dl_name}$" $PROJECT_HASHES | head -1)
        if [ -n "$same_name" ]; then
          proj_path=$(echo "$same_name" | cut -d'|' -f3)
          proj_size=$(echo "$same_name" | cut -d'|' -f2)
          echo "${dl_size}|${dl_file}|${proj_path}|${proj_size}" >> $SAME_NAME_DIFF
        else
          echo "${dl_size}|${dl_file}" >> $UNIQUE
        fi
      fi
    done

n_dupes=$(wc -l < $DUPES)
n_diff=$(wc -l < $SAME_NAME_DIFF)
n_uniq=$(wc -l < $UNIQUE)

echo "" >> $OUTPUT
echo "[Step 3/3] Results:" | tee -a $OUTPUT
echo "================================================" >> $OUTPUT
echo "" >> $OUTPUT

echo "## DUPLICATES (byte-identical, safe to quarantine): $n_dupes files" | tee -a $OUTPUT
total_dup_bytes=0
echo "" >> $OUTPUT
sort -t'|' -k1 -n -r $DUPES | while read line; do
  size=$(echo "$line" | cut -d'|' -f1)
  dl=$(echo "$line" | cut -d'|' -f2)
  pj=$(echo "$line" | cut -d'|' -f3)
  size_human=$(echo "$size" | awk '{
    if ($1 > 1048576) printf "%.1fMB", $1/1048576
    else if ($1 > 1024) printf "%.1fKB", $1/1024
    else printf "%dB", $1
  }')
  echo "  ${size_human}  $(basename $dl)  → matches $(echo $pj | sed s|$HOME/INTERCEPTA/||)" >> $OUTPUT
done
total_dup_size=$(awk -F'|' '{s+=$1} END {if (s > 1048576) printf "%.1fMB", s/1048576; else if (s > 1024) printf "%.1fKB", s/1024; else printf "%dB", s}' $DUPES)
echo "" >> $OUTPUT
echo "Total disk space in duplicates: $total_dup_size" | tee -a $OUTPUT
echo "" >> $OUTPUT

echo "## SAME NAME DIFFERENT CONTENT (investigate before deleting): $n_diff files" | tee -a $OUTPUT
echo "" >> $OUTPUT
sort -t'|' -k1 -n -r $SAME_NAME_DIFF | while read line; do
  size=$(echo "$line" | cut -d'|' -f1)
  dl=$(echo "$line" | cut -d'|' -f2)
  pj=$(echo "$line" | cut -d'|' -f3)
  pj_size=$(echo "$line" | cut -d'|' -f4)
  size_human=$(echo "$size" | awk '{if ($1 > 1024) printf "%.1fKB", $1/1024; else printf "%dB", $1}')
  pj_size_human=$(echo "$pj_size" | awk '{if ($1 > 1024) printf "%.1fKB", $1/1024; else printf "%dB", $1}')
  echo "  $(basename $dl): Downloads=${size_human} Project=${pj_size_human}" >> $OUTPUT
done
echo "" >> $OUTPUT

echo "## UNIQUE TO DOWNLOADS (no match in project): $n_uniq files" | tee -a $OUTPUT
echo "  (only first 30 listed; full list in audit file)" >> $OUTPUT
echo "" >> $OUTPUT
sort -t'|' -k1 -n -r $UNIQUE | head -30 | while read line; do
  size=$(echo "$line" | cut -d'|' -f1)
  dl=$(echo "$line" | cut -d'|' -f2)
  size_human=$(echo "$size" | awk '{
    if ($1 > 1048576) printf "%.1fMB", $1/1048576
    else if ($1 > 1024) printf "%.1fKB", $1/1024
    else printf "%dB", $1
  }')
  echo "  ${size_human}  $(basename $dl)" >> $OUTPUT
done
echo "" >> $OUTPUT

echo "================================================" >> $OUTPUT
echo "Summary:" | tee -a $OUTPUT
echo "  Project files hashed: $n_project" | tee -a $OUTPUT
echo "  Downloads top-level files: $((n_dupes + n_diff + n_uniq))" | tee -a $OUTPUT
echo "  Byte-identical duplicates: $n_dupes ($total_dup_size could be reclaimed)" | tee -a $OUTPUT
echo "  Same name, different content: $n_diff (review needed)" | tee -a $OUTPUT
echo "  Unique to Downloads: $n_uniq" | tee -a $OUTPUT
echo "" | tee -a $OUTPUT
echo "Full report: $OUTPUT" | tee -a $OUTPUT

# Cleanup temp files
rm -f $PROJECT_HASHES $DUPES $SAME_NAME_DIFF $UNIQUE
