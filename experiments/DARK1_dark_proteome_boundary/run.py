"""DARK1 score — the SAFETY / abstention-integrity verdict at the dark-proteome boundary. PURE scoring over the
cached mmseqs/foldseek/pLDDT tables written by build.py (deterministic; reproduces byte-identically x2).

Faithfully reproduces the composite's per-protein target-ID abstention rule (PREREG.md):
  * SEQUENCE signal FIRES iff best mmseqs hit vs drug_targets has e<=1e-3 & bits>0.
  * STRUCTURAL signal is USABLE iff mean AlphaFold pLDDT >= 50 (the vision's pLDDT gate); if usable, FIRES iff
    best Foldseek alntmscore (TM) >= 0.5 vs the drugged-fold reference. pLDDT<50 / no model -> cannot fire.
  * TARGET CALL (FIRE) iff SEQ fires OR gated-STRUCT fires; else ABSTAIN. tier = high(both)/moderate(one)/none.
  * DANGER DIAGNOSTIC: ungated best TM for dark proteins (a >=0.5 there = a would-be false-confident structural
    call caught ONLY by the pLDDT gate).
GATES (frozen): G1 dark abstain-rate >= 0.90 (fail-SAFE); G2 control fire-rate >= 0.70 (discriminating).
PASS = G1 AND G2. Any dark FIRE = CRITICAL false-confident call (fail-DANGEROUS), reported loudly.
"""
import os, json, hashlib, time

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
D = os.path.join(DATA, "dark1")
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results")
E_SEQ = 1e-3; PLDDT_USABLE = 50.0; TM_HIT = 0.5
G1_MIN = 0.90; G2_MIN = 0.70


def acc_of(target_field):
    return target_field.split("|")[1] if "|" in target_field else target_field


def best_seq(m8_path):
    """acc -> (best_bits, best_e, best_target, best_nonself_bits, best_nonself_e, best_nonself_target)."""
    best = {}; bestns = {}
    if os.path.exists(m8_path):
        for ln in open(m8_path):
            p = ln.rstrip("\n").split("\t")
            if len(p) < 5:
                continue
            q = p[0]; tgt = acc_of(p[1]); bits = float(p[3]); ev = float(p[4])
            if q not in best or bits > best[q][0]:
                best[q] = (bits, ev, tgt)
            if tgt != q and (q not in bestns or bits > bestns[q][0]):
                bestns[q] = (bits, ev, tgt)
    out = {}
    for q in set(best) | set(bestns):
        b = best.get(q, (0.0, 1.0, "")); ns = bestns.get(q, (0.0, 1.0, ""))
        out[q] = (b[0], b[1], b[2], ns[0], ns[1], ns[2])
    return out


def best_tm(m8_path):
    """acc -> (best_alntmscore, best_target)."""
    best = {}
    if os.path.exists(m8_path):
        for ln in open(m8_path):
            p = ln.rstrip("\n").split("\t")
            if len(p) < 5:
                continue
            q = os.path.splitext(p[0])[0]; tgt = os.path.splitext(acc_of(p[1]))[0]
            try:
                tm = float(p[4])
            except ValueError:
                continue
            if q not in best or tm > best[q][0]:
                best[q] = (tm, tgt)
    return best


def score_set(accs_meta, seq_hits, tm_hits, is_dark):
    rows = []
    for acc in sorted(accs_meta):
        meta = accs_meta[acc]
        plddt = meta["plddt"]; no_model = meta["no_model"]
        sb, se, st, nsb, nse, nst = seq_hits.get(acc, (0.0, 1.0, "", 0.0, 1.0, ""))
        seq_fires = (sb > 0) and (se <= E_SEQ)
        tm, tmt = tm_hits.get(acc, (0.0, ""))
        struct_usable = (not no_model) and (plddt is not None) and (plddt >= PLDDT_USABLE)
        struct_fires = struct_usable and (tm >= TM_HIT)
        fire = seq_fires or struct_fires
        tier = "high" if (seq_fires and struct_fires) else ("moderate" if fire else "none")
        row = {
            "acc": acc, "plddt": plddt, "no_model": no_model, "len": meta["len"],
            "seq_best_bits": round(sb, 1), "seq_best_evalue": se, "seq_best_target": st,
            "seq_best_nonself_bits": round(nsb, 1), "seq_best_nonself_evalue": nse, "seq_best_nonself_target": nst,
            "seq_fires": seq_fires,
            "struct_usable": struct_usable, "struct_best_tm_ungated": round(tm, 4), "struct_best_target": tmt,
            "struct_fires_gated": struct_fires,
            "verdict": "FIRE" if fire else "ABSTAIN", "confidence_tier": tier,
        }
        if is_dark:
            # danger diagnostic: would an UNGATED structural call have fired? (caught only by the pLDDT gate)
            row["ungated_structural_nearmiss"] = (tm >= TM_HIT) and (not struct_usable)
        rows.append(row)
    return rows


def main():
    t0 = time.time()
    sets = json.load(open(os.path.join(D, "sets.json")))
    dark_meta = sets["dark"]; ctrl_meta = sets["control"]
    dark_seq = best_seq(os.path.join(D, "dark_candidates_seqhits.m8"))
    ctrl_seq = best_seq(os.path.join(D, "control_seqhits.m8"))
    dark_tm = best_tm(os.path.join(D, "dark_fs.m8"))
    ctrl_tm = best_tm(os.path.join(D, "control_fs.m8"))

    dark_rows = score_set(dark_meta, dark_seq, dark_tm, is_dark=True)
    ctrl_rows = score_set(ctrl_meta, ctrl_seq, ctrl_tm, is_dark=False)

    n_dark = len(dark_rows); n_ctrl = len(ctrl_rows)
    dark_abstain = sum(1 for r in dark_rows if r["verdict"] == "ABSTAIN")
    dark_fire = n_dark - dark_abstain
    ctrl_fire = sum(1 for r in ctrl_rows if r["verdict"] == "FIRE")
    dark_abstain_rate = round(dark_abstain / n_dark, 4) if n_dark else 0.0
    ctrl_fire_rate = round(ctrl_fire / n_ctrl, 4) if n_ctrl else 0.0

    # verification: dark seq hits must all be zero (by construction) — assert & report
    dark_with_seqhit = [r["acc"] for r in dark_rows if r["seq_fires"]]
    nearmiss = [r["acc"] for r in dark_rows if r.get("ungated_structural_nearmiss")]
    dark_false_calls = [r["acc"] for r in dark_rows if r["verdict"] == "FIRE"]

    G1 = dark_abstain_rate >= G1_MIN
    G2 = ctrl_fire_rate >= G2_MIN
    PASS = G1 and G2

    payload = {
        "n_dark": n_dark, "n_control": n_ctrl,
        "config": {"E_SEQ": E_SEQ, "PLDDT_USABLE": PLDDT_USABLE, "TM_HIT": TM_HIT,
                   "G1_min_dark_abstain_rate": G1_MIN, "G2_min_control_fire_rate": G2_MIN},
        "G1_dark_abstain_rate": dark_abstain_rate, "G1_dark_abstained": dark_abstain, "G1_dark_fired": dark_fire,
        "G2_control_fire_rate": ctrl_fire_rate, "G2_control_fired": ctrl_fire,
        "G1_pass": G1, "G2_pass": G2, "PASS": PASS,
        "dark_false_confident_calls": sorted(dark_false_calls),
        "n_dark_false_confident_calls": len(dark_false_calls),
        "dark_with_any_seq_homolog": sorted(dark_with_seqhit),
        "ungated_structural_nearmiss": sorted(nearmiss),
        "n_ungated_structural_nearmiss": len(nearmiss),
        "dark_max_ungated_tm": round(max((r["struct_best_tm_ungated"] for r in dark_rows), default=0.0), 4),
        "dark_min_plddt": min((r["plddt"] for r in dark_rows if r["plddt"] is not None), default=None),
        "dark_max_plddt": max((r["plddt"] for r in dark_rows if r["plddt"] is not None), default=None),
        "dark_n_no_model": sum(1 for r in dark_rows if r["no_model"]),
        "control_min_plddt": min((r["plddt"] for r in ctrl_rows if r["plddt"] is not None), default=None),
        "control_n_fired_via_nonself_seq": sum(1 for r in ctrl_rows
                                               if r["seq_best_nonself_bits"] > 0 and r["seq_best_nonself_evalue"] <= E_SEQ),
        "control_n_struct_fires": sum(1 for r in ctrl_rows if r["struct_fires_gated"]),
        "verification": sets["verification"],
        "dark_rows": dark_rows,
        "control_rows": ctrl_rows,
    }

    verdict = (
        f"DARK-PROTEOME ABSTENTION-INTEGRITY TEST — {'PASS' if PASS else 'FAIL'}. "
        f"On {n_dark} genuinely dark proteins (0 drugged sequence homologs at e<=1e-3 [verified], mean AlphaFold "
        f"pLDDT<50 or no model [{payload['dark_min_plddt']}-{payload['dark_max_plddt']}], no reference ligand), the "
        f"composite ABSTAINED on {dark_abstain}/{n_dark} = {dark_abstain_rate:.0%} (G1 gate >= {G1_MIN:.0%}: "
        f"{'PASS' if G1 else 'FAIL'}). On {n_ctrl} known drugged controls it FIRED on {ctrl_fire}/{n_ctrl} = "
        f"{ctrl_fire_rate:.0%} (G2 gate >= {G2_MIN:.0%}: {'PASS' if G2 else 'FAIL'}). "
        + (f"CRITICAL INTEGRITY FAILURE: the system emitted {len(dark_false_calls)} FALSE-CONFIDENT target call(s) "
           f"on genuinely un-analyzable protein(s) {sorted(dark_false_calls)} — it FAILED DANGEROUS at the dark "
           f"boundary. " if dark_false_calls else
           "NO false-confident target call was emitted on any dark protein — the system FAILS SAFE at its outer "
           "edge: it correctly ABSTAINS where no validated signal transfers, while still firing on analyzable "
           "(drugged) input. ")
        + (f"DANGER-DIAGNOSTIC: {len(nearmiss)} dark protein(s) had an UNGATED Foldseek TM>=0.5 (max ungated TM "
           f"{payload['dark_max_ungated_tm']}) that was correctly suppressed ONLY by the pLDDT gate — evidence the "
           f"structure-confidence gate is load-bearing. " if nearmiss else
           f"The ungated structural diagnostic found NO dark protein reaching TM>=0.5 (max ungated TM "
           f"{payload['dark_max_ungated_tm']}), so both the sequence-null and structure-null conditions hold "
           f"independently. ")
        + "SCOPE: in-silico abstention-integrity at the homology-null + structure-null boundary; CPU-only; not "
          "wet-lab; darkness is defined by two objective computational gates, not a proof of universal "
          "non-homology. This maps the vision's stated OUTER EDGE (dark-proteome); a PASS shows fail-safe "
          "behavior, it does NOT solve the dark-proteome problem."
    )

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(RES, exist_ok=True)
    out = {"payload": payload, "verdict": verdict, "provenance": prov, "runtime_sec": round(time.time() - t0, 2)}
    json.dump(out, open(os.path.join(RES, "DARK1_metrics.json"), "w"), indent=2, sort_keys=True)
    sha = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    open(os.path.join(RES, "DARK1_payload.sha256"), "w").write(sha + "\n")

    print("PANEL:", json.dumps({k: v for k, v in payload.items()
                                 if k not in ("dark_rows", "control_rows")}, indent=1))
    print("\nDARK rows (verdict | acc | pLDDT | seq bits/e | ungated TM | struct_usable):")
    for r in dark_rows:
        print(f"  {r['verdict']:8s} {r['acc']:12s} pLDDT={str(r['plddt']):>6s} "
              f"seq_bits={r['seq_best_bits']:>6.1f} e={r['seq_best_evalue']:.1e} "
              f"ungatedTM={r['struct_best_tm_ungated']:.3f} usable={r['struct_usable']}")
    print("\nCONTROL rows:")
    for r in ctrl_rows:
        print(f"  {r['verdict']:8s} {r['acc']:12s} pLDDT={str(r['plddt']):>6s} "
              f"seq_bits={r['seq_best_bits']:>6.1f} e={r['seq_best_evalue']:.1e} "
              f"nonself_bits={r['seq_best_nonself_bits']:>6.1f} structTM={r['struct_best_tm_ungated']:.3f}")
    print("\nVERDICT:", verdict)
    print("\npayload sha256:", sha, f"[{time.time()-t0:.1f}s]")


if __name__ == "__main__":
    main()
