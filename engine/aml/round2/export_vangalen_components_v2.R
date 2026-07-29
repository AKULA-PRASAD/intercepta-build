#!/usr/bin/env Rscript
# =====================================================================
# INTERCEPTA Round 2.1c Step 1 v2 — Van Galen Seurat RDS component export
# =====================================================================
#
# v1 failure diagnosis
# --------------------
# v1 crashed extracting the counts layer with:
#   "vector memory limit of 16.0 Gb reached"
# Then the fallback crashed with:
#   "`slot` argument of `GetAssayData()` was deprecated ... is now defunct"
#
# Two separate problems, both now fixed in v2:
#
# 1. Memory limit. R 4.5 defaults to 16 GB virtual vector size. The
#    44,823 x 27,899 V5 Assay5 counts matrix is sparse but a full
#    LayerData() call apparently materializes intermediates that blow
#    past 16 GB. Fix: raise R_MAX_VSIZE to 64 GB at script start.
#
# 2. Deprecated API. In SeuratObject 5.0+ (we have 5.5.0), the 'slot'
#    argument is defunct. Current API uses 'layer'. Better still, V5
#    Assay5 exposes layers directly as slot accessors:
#      aml[["RNA"]]$counts    # direct, no helper function
#      aml[["RNA"]]$data
#    This avoids LayerData() entirely, which is where v1's memory
#    blowup happened.
#
# Principle 4: fix the structural cause (memory cap + wrong API),
#              don't tune parameters to hide the issue.
# Principle 3: verified the V5 accessor syntax from Seurat 5.0 release
#              notes before writing this.

# ---------------------------------------------------------------------
# Raise memory limit BEFORE loading anything else
# ---------------------------------------------------------------------
Sys.setenv(R_MAX_VSIZE = "64Gb")
# Also set options that affect sparse matrix handling
options(Matrix.warnDeprecatedCoerce = 0)  # suppress coerce warnings

suppressPackageStartupMessages({
  library(Seurat)
  library(Matrix)
})

cat("Seurat version:      ", as.character(packageVersion("Seurat")), "\n")
cat("SeuratObject version:", as.character(packageVersion("SeuratObject")), "\n")
cat("Matrix version:      ", as.character(packageVersion("Matrix")), "\n")
cat("R_MAX_VSIZE:         ", Sys.getenv("R_MAX_VSIZE"), "\n\n")

# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
data_dir <- path.expand("~/INTERCEPTA/round2_aml/data/vangalen2019")
rds_path <- file.path(data_dir, "Seurat_AML.rds")
out_dir  <- file.path(data_dir, "exported")

if (!file.exists(rds_path)) stop("Seurat_AML.rds not found at ", rds_path)
if (!dir.exists(out_dir)) dir.create(out_dir, recursive = TRUE)

cat("Input:  ", rds_path, "\n")
cat("Output: ", out_dir, "\n\n")

# ---------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------
cat(rep("=", 72), "\n", sep = "")
cat("Loading RDS\n")
cat(rep("=", 72), "\n", sep = "")
t0 <- Sys.time()
aml <- readRDS(rds_path)
cat("Loaded in", round(as.numeric(Sys.time() - t0, units = "secs"), 1), "sec\n")
cat("Cells:", ncol(aml), "  Features:", nrow(aml), "\n\n")

# Show memory footprint of the loaded object
cat("Object size in memory:", format(object.size(aml), units = "GB"), "\n\n")

# ---------------------------------------------------------------------
# Export a layer via DIRECT V5 accessor (no LayerData)
# ---------------------------------------------------------------------
export_layer <- function(aml, layer_name, out_file) {
  cat(rep("=", 72), "\n", sep = "")
  cat("Exporting layer: ", layer_name, "\n", sep = "")
  cat(rep("=", 72), "\n", sep = "")

  # V5 direct accessor: aml[["RNA"]]$counts, aml[["RNA"]]$data
  # This bypasses LayerData which is where v1 blew up.
  rna_assay <- aml[["RNA"]]
  mat <- tryCatch(
    rna_assay[[layer_name]],
    error = function(e) {
      cat("Direct $accessor failed: ", conditionMessage(e), "\n")
      cat("Falling back to GetAssayData(layer=...)\n")
      GetAssayData(aml, assay = "RNA", layer = layer_name)
    }
  )

  cat("Class:     ", paste(class(mat), collapse = ","), "\n")
  cat("Dim:       ", paste(dim(mat), collapse = " x "), "\n")
  cat("Memory:    ", format(object.size(mat), units = "GB"), "\n")
  cat("Non-zeros: ", length(mat@x), "\n")

  # Verify dgCMatrix for writeMM
  if (!inherits(mat, "dgCMatrix")) {
    cat("Coercing to dgCMatrix...\n")
    mat <- as(mat, "CsparseMatrix")
  }

  cat("Writing", out_file, "...\n")
  t0 <- Sys.time()
  Matrix::writeMM(mat, out_file)
  dt <- round(as.numeric(Sys.time() - t0, units = "secs"), 1)
  sz <- round(file.info(out_file)$size / 1024^2, 1)
  cat("  done in", dt, "sec, file size:", sz, "MB\n\n")

  # Return rownames/colnames while we still have the matrix
  invisible(list(genes = rownames(mat), cells = colnames(mat)))
}

# Export counts (raw UMI counts)
info <- export_layer(aml, "counts", file.path(out_dir, "counts.mtx"))
gene_names <- info$genes
cell_bc    <- info$cells

# Export data (log-normalized)
export_layer(aml, "data", file.path(out_dir, "data.mtx"))

# ---------------------------------------------------------------------
# Gene names and cell barcodes
# ---------------------------------------------------------------------
cat(rep("=", 72), "\n", sep = "")
cat("Exporting gene names and cell barcodes\n")
cat(rep("=", 72), "\n", sep = "")
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
stopifnot(all(rownames(md) == cell_bc))

md_out <- cbind(barcode = cell_bc, md)
meta_path <- file.path(out_dir, "cell_metadata.csv")
write.csv(md_out, meta_path, row.names = FALSE, na = "")
cat("cell_metadata.csv:", nrow(md_out), "rows x", ncol(md_out), "cols\n")
cat("Columns:", paste(colnames(md_out), collapse = ", "), "\n\n")

# ---------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------
cat(rep("=", 72), "\n", sep = "")
cat("Export complete\n")
cat(rep("=", 72), "\n", sep = "")
files <- list.files(out_dir, full.names = FALSE)
for (f in sort(files)) {
  fp <- file.path(out_dir, f)
  cat(sprintf("  %-25s %8.1f MB\n", f, file.info(fp)$size / 1024^2))
}
cat("\nReady for Python assembly step.\n")
