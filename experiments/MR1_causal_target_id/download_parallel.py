#!/usr/bin/env python
"""MR1 — parallel byte-range download of the 5-disease GWAS panel. EBI throttles per-connection
(~130 KB/s/stream, scales ~linearly), so we fetch many 200MB range-chunks concurrently and reassemble.
Retries per chunk; verifies final size == Content-Length. Stdlib only (no pandas needed)."""
import os, sys, urllib.request, concurrent.futures as cf

DEST = "/Users/kalki/intercepta_data/mr1/gwas"; os.makedirs(DEST, exist_ok=True)
B = "https://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics"
UA = {"User-Agent": "Mozilla/5.0"}
CHUNK = 200 * 1024 * 1024
PAR = 10
FILES = {
    "CAD": f"{B}/GCST90132001-GCST90133000/GCST90132314/harmonised/GCST90132314.h.tsv.gz",
    "T2D": f"{B}/GCST006001-GCST007000/GCST006867/harmonised/30054458-GCST006867-EFO_0001360.h.tsv.gz",
    "IBD": f"{B}/GCST004001-GCST005000/GCST004131/harmonised/28067908-GCST004131-EFO_0003767.h.tsv.gz",
    "PARKINSON": f"{B}/GCST009001-GCST010000/GCST009325/harmonised/GCST009325.h.tsv.gz",
    "RA": f"{B}/GCST90132001-GCST90133000/GCST90132223/harmonised/GCST90132223.h.tsv.gz",
}

def head_size(url):
    r = urllib.request.Request(url, headers=UA, method="HEAD")
    with urllib.request.urlopen(r, timeout=60) as resp:
        return int(resp.headers["Content-Length"])

def fetch_chunk(url, start, end, out):
    if os.path.exists(out) and os.path.getsize(out) == end - start + 1:
        return f"cached {os.path.basename(out)}"
    h = dict(UA); h["Range"] = f"bytes={start}-{end}"
    for t in range(6):
        try:
            r = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(r, timeout=1800) as resp, open(out, "wb") as f:
                f.write(resp.read())
            if os.path.getsize(out) == end - start + 1:
                return f"ok {os.path.basename(out)}"
        except Exception as e:
            sys.stderr.write(f"retry {os.path.basename(out)} ({t}): {e}\n")
    return f"FAIL {os.path.basename(out)}"

def main():
    sizes, jobs = {}, []
    for nm, url in FILES.items():
        sz = head_size(url); sizes[nm] = sz
        nc = (sz + CHUNK - 1) // CHUNK
        print(f"{nm} size={sz} chunks={nc}", flush=True)
        for i in range(nc):
            start = i * CHUNK; end = min((i + 1) * CHUNK - 1, sz - 1)
            jobs.append((nm, i, url, start, end, os.path.join(DEST, f"{nm}.part.{i:03d}")))
    with cf.ThreadPoolExecutor(max_workers=PAR) as ex:
        futs = {ex.submit(fetch_chunk, u, s, e, o): (nm, i) for (nm, i, u, s, e, o) in jobs}
        for fut in cf.as_completed(futs):
            print(fut.result(), flush=True)
    print("=== reassembling ===", flush=True)
    ok = True
    for nm in FILES:
        nc = (sizes[nm] + CHUNK - 1) // CHUNK
        final = os.path.join(DEST, f"{nm}.h.tsv.gz")
        with open(final, "wb") as out:
            for i in range(nc):
                p = os.path.join(DEST, f"{nm}.part.{i:03d}")
                with open(p, "rb") as f: out.write(f.read())
        got = os.path.getsize(final)
        good = got == sizes[nm]; ok &= good
        print(f"{nm} reassembled={got} expected={sizes[nm]} {'OK' if good else 'MISMATCH'}", flush=True)
        if good:
            for i in range(nc): os.remove(os.path.join(DEST, f"{nm}.part.{i:03d}"))
    print("=== ALL OK ===" if ok else "=== SOME MISMATCH ===", flush=True)

if __name__ == "__main__":
    main()
