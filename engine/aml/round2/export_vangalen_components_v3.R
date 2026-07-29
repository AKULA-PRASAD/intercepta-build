#!/usr/bin/env Rscript
# =====================================================================
# INTERCEPTA Round 2.1c Step 1 v3 — Van Galen Seurat RDS component export
# =====================================================================
#
# v2 failure diagnosis
# --------------------
# v2 raised R_MAX_VSIZE to 64 GB (good) but then used the WRONG
# accessor syntax for V5 Assay5 objects:
#
#     rna_assay <- aml[["RNA"]]
#     mat <- rna_assay[[layer_name]]   # BUG: returned a data.frame
#
# In Seurat V5, the $ and [[ accessors on an Assay5 object are NOT
# equivalent:
#   rna_assay$counts         -> returns the sparse counts matrix ✓
#   rna_assay[["counts"]]    -> does something else (returned a
#                               27899 x 1 data.frame of feature names
#                               in our run). Not documented for V5
#                               Assay5 classes.
#
# v3 fix
# ------
# Use the canonical documented API: LayerData(obj, assay, layer).
# From the Seurat source docs:
#   "Data can be accessed using the $ accessor (i.e. obj[['RNA']]$counts),
#    or the LayerData function (i.e. LayerData(obj, assay='RNA', layer='counts'))."
#
# LayerData() works correctly when the memory ceiling is lifted - v1's
# failure was the memory cap (we hadn't raised R_MAX_VSIZE yet), not
# LayerData itself. v3 raises the cap AND uses LayerData.
#
# Principle 3: verified against official Seurat docs, not a forum post.
# Principle 15: admitted the v2 bug openly inside this file, not
#               hidden in commit log.

# ---------------------------------------------------------------------
# Raise memory ceiling BEFORE loading
# ---------------------------------------------------------------------
Sys.setenv(R_MAX_VSIZE = "64Gb")

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
cat("Cells:", ncol(aml), "  Features:", nrow(aml), "\n")
cat("Object size in memory:", format(object.size(aml), units = "GB"), "\n")
cat("Available layers:", paste(Layers(aml, assay = "RNA"), collapse = ", "), "\n\n")

# ---------------------------------------------------------------------
# Export a layer via LayerData (canonical API)
# ---------------------------------------------------------------------
export_layer <- function(aml, layer_name, out_file) {
  cat(rep("=", 72), "\n", sep = "")
  cat("Exporting layer: ", layer_name, "\n", sep = "")
  cat(rep("=", 72), "\n", sep = "")

  mat <- LayerData(aml, assay = "RNA", layer = layer_name)

  # Integrity checks
  if (is.null(mat) || length(mat) == 0) {
    stop("LayerData returned empty for layer ", layer_name)
  }
  if (inherits(mat, "data.frame")) {
    stop("LayerData returned a data.frame - wrong accessor type. ",
         "Class was: ", paste(class(mat), collapse = ","))
  }

  cat("Class:     ", paste(class(mat), collapse = ","), "\n")
  cat("Dim:       ", paste(dim(mat), collapse = " x "), "\n")
  cat("Memory:    ", format(object.size(mat), units = "GB"), "\n")

  # dgCMatrix inherits from sparse matrix base class
  if (inherits(mat, "dgCMatrix") || inherits(mat, "CsparseMatrix")) {
    cat("Non-zeros: ", length(mat@x), "\n")
  }

  # Coerce to dgCMatrix for writeMM
  if (!inherits(mat, "dgCMatrix")) {
    cat("Coercing to dgCMatrix...\n")
    mat <- as(mat, "CsparseMatrix")
    cat("  class after coerce:", paste(class(mat), collapse = ","), "\n")
  }

  cat("Writing", out_file, "...\n")
  t0 <- Sys.time()
  Matrix::writeMM(mat, out_file)
  dt <- round(as.numeric(Sys.time() - t0, units = "secs"), 1)
  sz <- round(file.info(out_file)$size / 1024^2, 1)
  cat("  done in", dt, "sec, file size:", sz, "MB\n\n")

  invisible(list(genes = rownames(mat), cells = colnames(mat), dim = dim(mat)))
}

# Export counts layer
info <- export_layer(aml, "counts", file.path(out_dir, "counts.mtx"))
gene_names <- info$genes
cell_bc    <- info$cells
counts_dim <- info$dim

# Export data layer (log-normalized)
data_info <- export_layer(aml, "data", file.path(out_dir, "data.mtx"))

# Consistency check: counts and data must have identical dims + names
stopifnot(identical(data_info$dim, counts_dim))
stopifnot(identical(data_info$genes, gene_names))
stopifnot(identical(data_info$cells, cell_bc))

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
