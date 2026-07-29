#!/bin/bash
# INTERCEPTA HPC Setup Script
# Run this on HPC after cloning the repository
# Downloads all required data and sets up the environment

set -e
echo "INTERCEPTA HPC Setup"
echo "===================="

# Create directories
mkdir -p data/gdsc/expression_data data/su2c data/scrna/GSE141445 data/scrna/GSE137829 data/velocity/genome

# [1] Download GDSC data
echo "[1/6] Downloading GDSC expression data (246MB)..."
curl -L -o data/gdsc/expression_data/rnaseq_tpm_20220624.csv \
    "https://www.cancerrxgene.org/gdsc1000/GDSC1000_WebResources/Home_files/rnaseq_tpm_20220624.csv"

echo "[1b] Downloading GDSC drug sensitivity (20MB)..."
curl -L -o data/gdsc/GDSC2_fitted_dose_response.xlsx \
    "https://cog.sanger.ac.uk/cancerrxgene/GDSC_release8.5/GDSC2_fitted_dose_response_25Feb20.xlsx"

# [2] Download scRNA-seq (Chen et al.)
echo "[2/6] Downloading GSE141445 scRNA-seq (757MB)..."
curl -L -o data/scrna/GSE141445_RAW.tar \
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE141nnn/GSE141445/suppl/GSE141445_RAW.tar"
cd data/scrna/GSE141445 && tar -xf ../GSE141445_RAW.tar && cd ../../..

# [3] Download scRNA-seq (Dong et al. - for velocity)
echo "[3/6] Downloading GSE137829 scRNA-seq (77MB)..."
curl -L -o data/scrna/GSE137829_RAW.tar \
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE137nnn/GSE137829/suppl/GSE137829_RAW.tar"
cd data/scrna/GSE137829 && tar -xf ../GSE137829_RAW.tar && cd ../../..

# [4] Download GTEx
echo "[4/6] Downloading GTEx median expression (6.6MB)..."
curl -L -o data/gtex_median_tpm.gct.gz \
    "https://storage.googleapis.com/adult-gtex/bulk-gex/v8/rna-seq/GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm.gct.gz"

# [5] Download genome for velocity
echo "[5/6] Downloading GRCh38 genome (800MB)..."
curl -L -o data/velocity/genome/GRCh38.primary_assembly.genome.fa.gz \
    "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/GRCh38.primary_assembly.genome.fa.gz"
gunzip data/velocity/genome/GRCh38.primary_assembly.genome.fa.gz

echo "[5b] Downloading GENCODE v44 annotation (50MB)..."
curl -L -o data/velocity/genome/gencode.v44.annotation.gtf.gz \
    "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.annotation.gtf.gz"
gunzip data/velocity/genome/gencode.v44.annotation.gtf.gz

# [6] Install Python packages
echo "[6/6] Installing Python packages..."
pip install numpy pandas scipy scikit-learn openpyxl scvelo scanpy anndata

echo ""
echo "Setup complete. Run the velocity pipeline:"
echo "  bash code/step3_rna_velocity_pipeline.sh"
