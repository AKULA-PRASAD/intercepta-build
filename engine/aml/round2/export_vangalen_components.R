#!/usr/bin/env Rscript
# =====================================================================
# INTERCEPTA Round 2.1c Step 1 — Van Galen Seurat RDS component export
# =====================================================================
#
# Purpose
# -------
# Export the Van Galen 2019 Seurat V5 object as standard, portable
# files that Python / AnnData can assemble without needing R.
#
# Why NOT use SeuratDisk or sceasy
# --------------------------------
# Both are known to break on Seurat V5 Assay5 objects. The van Galen
# RDS is V5 (version 4.9.9.9083, Assay5 class). Per sctijalab/seurat
# discussion #7402 and multiple 2024-2025 community reports,
# SaveH5Seurat + Convert fails or silently corrupts V5 objects.
#
# Our approach: extract raw components and let Python assemble them.
# This works forever regardless of Seurat / SeuratDisk versioning.
#
# Output files (all go to round2_aml/data/vangalen2019/exported/)
# ---------------------------------------------------------------
#   counts.mtx        Sparse counts matrix (27,899 genes x 44,823 cells)
#                     Matrix Market format, readable by scipy.io.mmread
#   data.mtx          Sparse log-normalized data matrix (same shape)
#   gene_names.txt    One gene symbol per line, order matches .mtx rows
#   cell_barcodes.txt One cell barcode per line, order matches .mtx cols
#   cell_metadata.csv All Seurat @meta.data columns, one row per cell,
#                     in same order as cell_barcodes.txt
#
# Downstream: Python Script 2 loads these and builds an AnnData object.
#
# Run
# ---
#     cd ~/INTERCEPTA/round2_aml/code
#     Rscript export_vangalen_components.R
#
# Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
# Date:    April 21, 2026
# Principle 3: chose Path B (component export) over SeuratDisk after
#              verifying SeuratDisk is fragile with V5 objects.

# ---------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------
suppressPackageStartupMessages({
  library(Seurat)       # already installed
  library(Matrix)       # comes with R, used by Seurat
})

cat("Seurat version:", as.character(packageVersion("Seurat")), "\n")
cat("Matrix version:", as.character(packageVersion("Matrix")), "\n\n")

# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
data_dir <- "~/INTERCEPTA/round2_aml/data/vangalen2019"
data_dir <- path.expand(data_dir)
rds_path <- file.path(data_dir, "Seurat_AML.rds")
out_dir  <- file.path(data_dir, "exported")

if (!file.exists(rds_path)) {
  stop("Seurat_AML.rds not found at ", rds_path)
}
if (!dir.exists(out_dir)) {
  dir.create(out_dir, recursive = TRUE)
  cat("Created output dir:", out_dir, "\n")
}

cat("Input:       ", rds_path, "\n")
cat("Output dir:  ", out_dir, "\n\n")

# ---------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------
cat(rep("=", 72), "\n", sep = "")
cat("Loading RDS\n")
cat(rep("=", 72), "\n", sep = "")
t0 <- Sys.time()
aml <- readRDS(rds_path)
cat("Loaded in", round(as.numeric(Sys.time() - t0, units = "secs"), 1), "seconds\n")
cat("Class:", paste(class(aml), collapse = ","), "  cells:", ncol(aml),
    "  features:", nrow(aml), "\n\n")

# Sanity: V5 Assay5 expected
if (!inherits(aml[["RNA"]], "Assay5")) {
  cat("NOTE: expected Assay5; got", class(aml[["RNA"]]), "\n")
  cat("Script will still attempt extraction using LayerData() / GetAssayData().\n\n")
}

# ---------------------------------------------------------------------
# Extract counts layer
# ---------------------------------------------------------------------
cat(rep("=", 72), "\n", sep = "")
cat("Exporting counts layer\n")
cat(rep("=", 72), "\n", sep = "")
counts <- tryCatch(
  LayerData(aml, assay = "RNA", layer = "counts"),
  error = function(e) {
    cat("LayerData failed (", conditionMessage(e), "); trying GetAssayData\n")
    GetAssayData(aml, assay = "RNA", slot = "counts")
  }
)
cat("Counts class:", class(counts)[1], "  dim:", paste(dim(counts), collapse = " x "), "\n")
cat("Sparse storage:", format(object.size(counts), units = "MB"), "\n")

# Verify sparse (Matrix::dgCMatrix)
if (!inherits(counts, "dgCMatrix")) {
  cat("Coercing to dgCMatrix...\n")
  counts <- as(counts, "CsparseMatrix")
}

counts_path <- file.path(out_dir, "counts.mtx")
cat("Writing counts.mtx ...\n")
t0 <- Sys.time()
Matrix::writeMM(counts, counts_path)
cat("  wrote in", round(as.numeric(Sys.time() - t0, units = "secs"), 1), "sec, size:",
    round(file.info(counts_path)$size / 1024^2, 1), "MB\n\n")

# ---------------------------------------------------------------------
# Extract data layer (log-normalized)
# ---------------------------------------------------------------------
cat(rep("=", 72), "\n", sep = "")
cat("Exporting data layer (log-normalized)\n")
cat(rep("=", 72), "\n", sep = "")
data_mat <- tryCatch(
  LayerData(aml, assay = "RNA", layer = "data"),
  error = function(e) {
    cat("LayerData(data) failed:", conditionMessage(e), "\n")
    NULL
  }
)

if (!is.null(data_mat)) {
  cat("Data class:", class(data_mat)[1], "  dim:", paste(dim(data_mat), collapse = " x "), "\n")
  if (!inherits(data_mat, "dgCMatrix")) {
    data_mat <- as(data_mat, "CsparseMatrix")
  }
  data_path <- file.path(out_dir, "data.mtx")
  cat("Writing data.mtx ...\n")
  t0 <- Sys.time()
  Matrix::writeMM(data_mat, data_path)
  cat("  wrote in", round(as.numeric(Sys.time() - t0, units = "secs"), 1), "sec, size:",
      round(file.info(data_path)$size / 1024^2, 1), "MB\n\n")
} else {
  cat("No data layer to export.\n\n")
}

# ---------------------------------------------------------------------
# Gene names, cell barcodes
# ---------------------------------------------------------------------
cat(rep("=", 72), "\n", sep = "")
cat("Exporting gene names and cell barcodes\n")
cat(rep("=", 72), "\n", sep = "")
gene_names <- rownames(counts)
cell_bc    <- colnames(counts)
writeLines(gene_names, file.path(out_dir, "gene_names.txt"))
writeLines(cell_bc,    file.path(out_dir, "cell_barcodes.txt"))
cat("gene_names.txt:    ", length(gene_names), "rows\n")
cat("cell_barcodes.txt: ", length(cell_bc), "rows\n\n")

# ---------------------------------------------------------------------
# Cell metadata
# ---------------------------------------------------------------------
cat(rep("=", 72), "\n", sep = "")
cat("Exporting cell metadata\n")
cat(rep("=", 72), "\n", sep = "")
md <- aml@meta.data
# Ensure rows are in SAME ORDER as cell_barcodes.txt (Seurat guarantees this
# when meta.data is indexed by cell names, but verify explicitly)
stopifnot(all(rownames(md) == cell_bc))

# Add a barcode column as the first column for unambiguous join
md_out <- cbind(barcode = cell_bc, md)
meta_path <- file.path(out_dir, "cell_metadata.csv")
write.csv(md_out, meta_path, row.names = FALSE, na = "")
cat("cell_metadata.csv: ", nrow(md_out), "rows x ", ncol(md_out), "cols\n")
cat("Columns: ", paste(colnames(md_out), collapse = ", "), "\n\n")

# ---------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------
cat(rep("=", 72), "\n", sep = "")
cat("Export complete\n")
cat(rep("=", 72), "\n", sep = "")
cat("Files in", out_dir, ":\n")
files <- list.files(out_dir, full.names = FALSE)
for (f in files) {
  fp <- file.path(out_dir, f)
  cat(sprintf("  %-25s %8.1f MB\n", f,
              file.info(fp)$size / 1024^2))
}
cat("\nNext: Python script to assemble into AnnData and validate.\n")
