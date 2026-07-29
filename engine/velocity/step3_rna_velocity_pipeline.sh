#!/bin/bash
# INTERCEPTA Step 3 FIX: RNA Velocity Pipeline
# Downloads raw FASTQ from SRA, aligns with STARsolo, generates spliced/unspliced counts
# Processes ONE SAMPLE AT A TIME to minimize storage (peak ~45GB)
#
# Dataset: GSE137829 (Dong et al. 2020) - CRPC patients with NE transdifferentiation
# Selected: 4 runs from patients P5+P6 (~21GB download)
#
# Expected runtime: ~12 hours
# Expected peak storage: ~45GB
# 
# Usage: nohup bash step3_rna_velocity_pipeline.sh > velocity_log.txt 2>&1 &

set -e
WORKDIR="$HOME/INTERCEPTA/data/velocity"
RESULTS="$HOME/INTERCEPTA/results"
mkdir -p $WORKDIR/fastq $WORKDIR/genome $WORKDIR/velocity_out
cd $WORKDIR

echo "=============================================="
echo "INTERCEPTA RNA Velocity Pipeline"
echo "Started: $(date)"
echo "=============================================="

# Correct SRA run IDs for GSE137829 P5+P6
RUNS="SRR12391718 SRR12391719 SRR12391720 SRR12391721"

# -------------------------------------------------------
# STEP 1: Download genome and annotation
# -------------------------------------------------------
echo ""
echo "[STEP 1/5] Downloading human genome + annotation..."
if [ ! -f $WORKDIR/genome/GRCh38.primary_assembly.genome.fa ]; then
    echo "  Downloading GRCh38 genome (~800MB)..."
    curl -L -o $WORKDIR/genome/GRCh38.primary_assembly.genome.fa.gz \
        "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/GRCh38.primary_assembly.genome.fa.gz"
    echo "  Decompressing..."
    gunzip $WORKDIR/genome/GRCh38.primary_assembly.genome.fa.gz
    echo "  Genome ready."
else
    echo "  Genome already downloaded."
fi

if [ ! -f $WORKDIR/genome/gencode.v44.annotation.gtf ]; then
    echo "  Downloading GENCODE v44 annotation (~50MB)..."
    curl -L -o $WORKDIR/genome/gencode.v44.annotation.gtf.gz \
        "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.annotation.gtf.gz"
    gunzip $WORKDIR/genome/gencode.v44.annotation.gtf.gz
    echo "  Annotation ready."
else
    echo "  Annotation already downloaded."
fi

echo "  Genome step complete: $(date)"

# -------------------------------------------------------
# STEP 2: Build STAR genome index (reduced for 16GB RAM)
# -------------------------------------------------------
echo ""
echo "[STEP 2/5] Building STAR genome index (reduced for 16GB RAM)..."
echo "  This takes 30-60 minutes."
if [ ! -f $WORKDIR/genome/star_index/SA ]; then
    mkdir -p $WORKDIR/genome/star_index
    STAR --runMode genomeGenerate \
         --genomeDir $WORKDIR/genome/star_index \
         --genomeFastaFiles $WORKDIR/genome/GRCh38.primary_assembly.genome.fa \
         --sjdbGTFfile $WORKDIR/genome/gencode.v44.annotation.gtf \
         --runThreadN 4 \
         --limitGenomeGenerateRAM 14000000000 \
         --genomeSAsparseD 2 \
         --genomeSAindexNbases 13
    echo "  Genome index built: $(date)"
else
    echo "  Genome index already exists."
fi

# -------------------------------------------------------
# STEP 3-4: For each sample: download, align, extract velocity, cleanup
# -------------------------------------------------------
echo ""
echo "[STEP 3-4/5] Processing samples one at a time..."

# 10X Chromium v3 whitelist (16bp CB + 12bp UMI)
# Download the 10X barcode whitelist
if [ ! -f $WORKDIR/genome/3M-february-2018.txt ]; then
    echo "  Downloading 10X v3 barcode whitelist..."
    curl -L -o $WORKDIR/genome/3M-february-2018.txt.gz \
        "https://github.com/cellranger/cellranger/raw/master/lib/python/cellranger/barcodes/3M-february-2018.txt.gz" 2>/dev/null || \
    curl -L -o $WORKDIR/genome/3M-february-2018.txt.gz \
        "https://raw.githubusercontent.com/10XGenomics/cellranger/master/lib/python/cellranger/barcodes/3M-february-2018.txt.gz" 2>/dev/null || \
    echo "  Whitelist download failed. Will use None for --soloCBwhitelist"
    
    if [ -f $WORKDIR/genome/3M-february-2018.txt.gz ]; then
        gunzip $WORKDIR/genome/3M-february-2018.txt.gz
    fi
fi

WHITELIST="$WORKDIR/genome/3M-february-2018.txt"
if [ ! -f "$WHITELIST" ]; then
    WHITELIST="None"
    echo "  WARNING: No barcode whitelist found. Using soloCBwhitelist=None"
fi

SAMPLE_NUM=0
for RUN in $RUNS; do
    SAMPLE_NUM=$((SAMPLE_NUM + 1))
    echo ""
    echo "  === Sample $SAMPLE_NUM/4: $RUN ==="
    echo "  Started: $(date)"
    
    # Skip if velocity output already exists
    if [ -f $WORKDIR/velocity_out/${RUN}_spliced.mtx ]; then
        echo "  Already processed. Skipping."
        continue
    fi
    
    # Download from SRA
    echo "  [a] Downloading from SRA (~5-6GB)..."
    if [ ! -f $WORKDIR/fastq/${RUN}_1.fastq.gz ] && [ ! -f $WORKDIR/fastq/${RUN}_1.fastq ]; then
        prefetch $RUN -O $WORKDIR/fastq/ --max-size 50G
        echo "  [b] Converting to FASTQ..."
        fasterq-dump $WORKDIR/fastq/$RUN -O $WORKDIR/fastq/ -e 4 --split-files
        # Compress to save space
        echo "  [c] Compressing FASTQ..."
        pigz -p 4 $WORKDIR/fastq/${RUN}_1.fastq 2>/dev/null || gzip $WORKDIR/fastq/${RUN}_1.fastq
        pigz -p 4 $WORKDIR/fastq/${RUN}_2.fastq 2>/dev/null || gzip $WORKDIR/fastq/${RUN}_2.fastq
        # Remove SRA cache
        rm -rf $WORKDIR/fastq/$RUN
    else
        echo "  FASTQ already exists."
    fi
    
    # Align with STARsolo
    echo "  [d] Aligning with STARsolo (spliced + unspliced)..."
    mkdir -p $WORKDIR/aligned/$RUN
    
    # Determine input files
    R1=$WORKDIR/fastq/${RUN}_1.fastq.gz
    R2=$WORKDIR/fastq/${RUN}_2.fastq.gz
    [ ! -f "$R1" ] && R1=$WORKDIR/fastq/${RUN}_1.fastq
    [ ! -f "$R2" ] && R2=$WORKDIR/fastq/${RUN}_2.fastq
    
    READCMD=""
    if [[ "$R1" == *.gz ]]; then
        READCMD="--readFilesCommand zcat"
    fi
    
    STAR --runMode alignReads \
         --genomeDir $WORKDIR/genome/star_index \
         --readFilesIn $R2 $R1 \
         $READCMD \
         --soloType CB_UMI_Simple \
         --soloCBwhitelist $WHITELIST \
         --soloCBstart 1 --soloCBlen 16 \
         --soloUMIstart 17 --soloUMIlen 12 \
         --soloFeatures Gene Velocyto \
         --outSAMtype BAM SortedByCoordinate \
         --outSAMattributes NH HI nM AS CR UR CB UB GX GN sS sQ sM \
         --runThreadN 4 \
         --limitBAMsortRAM 10000000000 \
         --outFileNamePrefix $WORKDIR/aligned/${RUN}/
    
    echo "  [e] Copying velocity matrices..."
    # STARsolo outputs velocity in Solo.out/Velocyto/raw/
    VELO_DIR=$WORKDIR/aligned/${RUN}/Solo.out/Velocyto/raw
    if [ -d "$VELO_DIR" ]; then
        cp $VELO_DIR/spliced.mtx $WORKDIR/velocity_out/${RUN}_spliced.mtx 2>/dev/null || true
        cp $VELO_DIR/unspliced.mtx $WORKDIR/velocity_out/${RUN}_unspliced.mtx 2>/dev/null || true
        cp $VELO_DIR/ambiguous.mtx $WORKDIR/velocity_out/${RUN}_ambiguous.mtx 2>/dev/null || true
        cp $VELO_DIR/barcodes.tsv $WORKDIR/velocity_out/${RUN}_barcodes.tsv 2>/dev/null || true
        cp $VELO_DIR/features.tsv $WORKDIR/velocity_out/${RUN}_features.tsv 2>/dev/null || true
        echo "  Velocity matrices saved."
    else
        echo "  WARNING: No Velocyto output found at $VELO_DIR"
        echo "  Checking alternative paths..."
        find $WORKDIR/aligned/${RUN}/ -name "spliced*" -o -name "Velocyto" 2>/dev/null | head -5
    fi
    
    # Cleanup: remove FASTQ and BAM to free space
    echo "  [f] Cleaning up FASTQ and BAM to free space..."
    rm -f $WORKDIR/fastq/${RUN}_1.fastq* $WORKDIR/fastq/${RUN}_2.fastq*
    rm -f $WORKDIR/aligned/${RUN}/Aligned.sortedByCoord.out.bam
    rm -rf $WORKDIR/aligned/${RUN}/Solo.out/Gene
    
    echo "  $RUN complete: $(date)"
    echo "  Disk usage: $(du -sh $WORKDIR | cut -f1)"
done

# -------------------------------------------------------
# STEP 5: Run scVelo
# -------------------------------------------------------
echo ""
echo "[STEP 5/5] Running scVelo dynamical mode..."
python3 ~/INTERCEPTA/code/step3_run_scvelo.py

echo ""
echo "=============================================="
echo "INTERCEPTA RNA Velocity Pipeline COMPLETE"
echo "Finished: $(date)"
echo "=============================================="
