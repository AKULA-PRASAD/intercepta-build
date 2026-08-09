#!/usr/bin/env python3
"""Split the flat prepped YAMLs into N chunk subdirs for a SLURM array (GPU-parallel, restartable).

Reads:  $INTERCEPTA_DATA/affinity1/yamls/*.yaml   (written by `run.py prep <big_N>`)
Writes: $INTERCEPTA_DATA/affinity1/yamls/chunk_00 .. chunk_{N-1}/  (round-robin, deterministic)

Usage:  python make_chunks.py <n_chunks>
Idempotent: re-running redistributes cleanly. Chunk granularity = restart granularity.
"""
import os, sys, glob, shutil

WORK = os.path.join(os.environ["INTERCEPTA_DATA"], "affinity1")
YAMLS = os.path.join(WORK, "yamls")
n_chunks = int(sys.argv[1]) if len(sys.argv) > 1 else 24

flat = sorted(glob.glob(os.path.join(YAMLS, "cmpd_*.yaml")))
if not flat:
    sys.exit("no cmpd_*.yaml in %s — run `python run.py prep 2000` first" % YAMLS)

# clear any existing chunk dirs, then round-robin (balanced, deterministic by sorted idx)
for d in glob.glob(os.path.join(YAMLS, "chunk_*")):
    shutil.rmtree(d)
for i in range(n_chunks):
    os.makedirs(os.path.join(YAMLS, "chunk_%02d" % i), exist_ok=True)
for k, f in enumerate(flat):
    dst = os.path.join(YAMLS, "chunk_%02d" % (k % n_chunks), os.path.basename(f))
    shutil.copy(f, dst)   # copy (keep the flat set as the manifest-of-record)

counts = [len(os.listdir(os.path.join(YAMLS, "chunk_%02d" % i))) for i in range(n_chunks)]
print("chunks=%d  total_yamls=%d  per_chunk=%s" % (n_chunks, len(flat), counts))
