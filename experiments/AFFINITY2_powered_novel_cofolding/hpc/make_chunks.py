#!/usr/bin/env python
"""Chunk the 522 AFFINITY2 YAMLs into N restartable chunks for the SLURM array.
Usage: python hpc/make_chunks.py <yamls_root> <chunks_root> <N>. Deterministic (sorted)."""
import os, sys, glob, shutil
src, dst, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
ys = sorted(glob.glob(os.path.join(src, "*", "*.yaml")))
assert ys, f"no YAMLs under {src}"
os.makedirs(dst, exist_ok=True)
for i in range(N): os.makedirs(os.path.join(dst, f"chunk_{i:02d}"), exist_ok=True)
for k, y in enumerate(ys):
    shutil.copy(y, os.path.join(dst, f"chunk_{k % N:02d}", os.path.basename(y)))
print(f"{len(ys)} YAMLs -> {N} chunks under {dst}")
