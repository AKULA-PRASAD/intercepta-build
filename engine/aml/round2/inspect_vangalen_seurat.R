#!/usr/bin/env Rscript
# =====================================================================
# INTERCEPTA Round 2.1c — Van Galen 2019 Seurat RDS inspection
# =====================================================================
#
# Purpose
# -------
# Load the Seurat object from Figshare and report its structure.
# Does NOT convert, modify, or save anything. Pure inspection.
#
# Why this matters
# ----------------
# Before writing conversion code (Seurat RDS -> h5ad for Python), we
# need to know:
#   1. Which Seurat version structured this object (V3/V4 vs V5)?
#      V3/V4 and V5 have different Assay layouts; conversion logic
#      differs.
#   2. What assays are present (RNA only? normalized counts? SCT?)
#   3. What cell-type annotation column(s) exist in the metadata?
#      The Van Galen 2019 paper uses specific labels (HSC, Prog, GMP,
#      ProMono, Mono, cDC, pDC, B, CTL, T, plasma, erythroid, NK).
#      We need the exact column name used in the metadata.
#   4. Are dimensional reductions (PCA, UMAP) already computed?
#   5. Are there sample/patient identifiers (needed to stratify by
#      AML vs healthy donor)?
#
# Principle 3: inspect before code.
# Principle 15: report what the file contains, not what we expect.
#
# Run
# ---
#     Rscript inspect_vangalen_seurat.R
#
# Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
# Date:    April 21, 2026

# ---------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------
if (!requireNamespace("Seurat", quietly = TRUE)) {
  cat("ERROR: Seurat R package not installed.\n")
  cat("Install with: install.packages('Seurat')\n")
  cat("Or in R:     BiocManager::install('Seurat')\n")
  quit(status = 1)
}

suppressPackageStartupMessages({
  library(Seurat)
})

cat("Seurat package version:", as.character(packageVersion("Seurat")), "\n")
cat("R version:", R.version.string, "\n\n")

# ---------------------------------------------------------------------
# Locate the file
# ---------------------------------------------------------------------
script_dir <- tryCatch(
  dirname(normalizePath(sys.frame(1)$ofile)),
  error = function(e) getwd()
)
# Fallback if sys.frame is null (interactive)
if (is.null(script_dir) || !dir.exists(script_dir)) {
  script_dir <- getwd()
}

candidate_paths <- c(
  file.path(dirname(dirname(script_dir)), "data/vangalen2019/Seurat_AML.rds"),
  "~/INTERCEPTA/round2_aml/data/vangalen2019/Seurat_AML.rds",
  "Seurat_AML.rds"
)
rds_path <- NULL
for (p in candidate_paths) {
  p_expanded <- path.expand(p)
  if (file.exists(p_expanded)) {
    rds_path <- p_expanded
    break
  }
}
if (is.null(rds_path)) {
  cat("ERROR: Seurat_AML.rds not found in any of:\n")
  for (p in candidate_paths) cat("  -", path.expand(p), "\n")
  quit(status = 2)
}

file_info <- file.info(rds_path)
cat("File path:   ", rds_path, "\n")
cat("File size:   ", round(file_info$size / 1024^2, 1), "MB\n\n")

# ---------------------------------------------------------------------
# Load the RDS
# ---------------------------------------------------------------------
cat(rep("=", 72), "\n", sep = "")
cat("Loading Seurat RDS (this takes 30-60 seconds for ~241 MB)\n")
cat(rep("=", 72), "\n", sep = "")

t_start <- Sys.time()
aml <- readRDS(rds_path)
t_elapsed <- as.numeric(Sys.time() - t_start, units = "secs")
cat("Loaded in", round(t_elapsed, 1), "seconds\n\n")

# ---------------------------------------------------------------------
# Report basic object structure
# ---------------------------------------------------------------------
cat(rep("=", 72), "\n", sep = "")
cat("Object structure\n")
cat(rep("=", 72), "\n", sep = "")

cat("Class:         ", paste(class(aml), collapse = ", "), "\n")
cat("S4 class?      ", isS4(aml), "\n")
if (methods::is(aml, "Seurat")) {
  cat("\nSeurat object summary:\n")
  print(aml)
  cat("\n")

  cat("Object version:", as.character(Version(aml)), "\n")
  cat("N cells:       ", ncol(aml), "\n")
  cat("N features:    ", nrow(aml), "\n")
  cat("Default assay: ", DefaultAssay(aml), "\n")
  cat("All assays:    ", paste(Assays(aml), collapse = ", "), "\n\n")

  # Per-assay detail
  for (a in Assays(aml)) {
    cat("--- Assay:", a, "---\n")
    assay_obj <- aml[[a]]
    cat("  Class:    ", paste(class(assay_obj), collapse = ", "), "\n")
    # Layers / slots depend on Seurat v3/v4 vs v5
    if (inherits(assay_obj, "Assay5")) {
      cat("  Layers (v5):", paste(Layers(assay_obj), collapse = ", "), "\n")
    } else {
      # v3/v4 Assay: slots are counts, data, scale.data
      slots_available <- c()
      for (sl in c("counts", "data", "scale.data")) {
        tryCatch({
          m <- slot(assay_obj, sl)
          if (!is.null(m) && length(m) > 0) {
            slots_available <- c(slots_available, sprintf(
              "%s [%d x %d, %s]", sl, nrow(m), ncol(m),
              class(m)[1]
            ))
          }
        }, error = function(e) {})
      }
      cat("  Slots:   ", paste(slots_available, collapse = "; "), "\n")
    }
    cat("\n")
  }

  # Dimensional reductions
  cat("Dim reductions:", paste(Reductions(aml), collapse = ", "), "\n")
  for (r in Reductions(aml)) {
    red_obj <- aml[[r]]
    cat(sprintf("  %s: %d dims\n", r, ncol(Embeddings(red_obj))))
  }
  cat("\n")

  # Metadata columns
  md <- aml@meta.data
  cat("Metadata rows (cells):", nrow(md), "\n")
  cat("Metadata columns:\n")
  for (col in colnames(md)) {
    vals <- md[[col]]
    n_unique <- length(unique(vals))
    n_na <- sum(is.na(vals))
    # Show first few unique values
    sample_vals <- head(unique(vals[!is.na(vals)]), 6)
    sample_str <- paste(as.character(sample_vals), collapse = "|")
    if (nchar(sample_str) > 80) sample_str <- paste0(substr(sample_str, 1, 77), "...")
    cat(sprintf("  [%-30s] type=%-10s unique=%-5d NA=%-4d  first: %s\n",
                col, class(vals)[1], n_unique, n_na, sample_str))
  }
  cat("\n")

  # ---------------------------------------------------------------
  # Focused reports on columns likely to contain cell-type annotation
  # and sample identity
  # ---------------------------------------------------------------
  cat(rep("=", 72), "\n", sep = "")
  cat("Cell-type / sample annotation candidates\n")
  cat(rep("=", 72), "\n", sep = "")

  cell_type_candidates <- grep(
    "cell.?type|celltype|cluster|annotation|predicted|class|ident|label",
    colnames(md), ignore.case = TRUE, value = TRUE
  )
  sample_candidates <- grep(
    "sample|patient|donor|orig.?ident|individual|subject",
    colnames(md), ignore.case = TRUE, value = TRUE
  )

  cat("Likely cell-type columns:", paste(cell_type_candidates, collapse = ", "), "\n")
  cat("Likely sample columns:   ", paste(sample_candidates, collapse = ", "), "\n\n")

  for (col in cell_type_candidates) {
    vals <- md[[col]]
    tb <- sort(table(vals, useNA = "ifany"), decreasing = TRUE)
    cat("Column '", col, "' value distribution:\n", sep = "")
    for (i in seq_along(tb)) {
      cat(sprintf("  %-35s %6d\n", names(tb)[i], tb[i]))
    }
    cat("\n")
  }

  for (col in sample_candidates) {
    vals <- md[[col]]
    tb <- sort(table(vals, useNA = "ifany"), decreasing = TRUE)
    cat("Column '", col, "' value distribution (top 20 of ", length(tb), "):\n", sep = "")
    for (i in seq_len(min(20, length(tb)))) {
      cat(sprintf("  %-35s %6d\n", names(tb)[i], tb[i]))
    }
    if (length(tb) > 20) cat("  ...", length(tb) - 20, "more samples\n")
    cat("\n")
  }

  # Active identity (what aml@active.ident points at, useful for default labels)
  cat("Active identity column distribution (top 20):\n")
  ai <- sort(table(Idents(aml)), decreasing = TRUE)
  for (i in seq_len(min(20, length(ai)))) {
    cat(sprintf("  %-35s %6d\n", names(ai)[i], ai[i]))
  }
  cat("\n")

} else {
  cat("NOTE: object is NOT a Seurat object. Dumping str():\n")
  str(aml, max.level = 2)
}

cat(rep("=", 72), "\n", sep = "")
cat("Inspection complete. Review output to plan conversion approach.\n")
cat(rep("=", 72), "\n", sep = "")
