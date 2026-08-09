#!/usr/bin/env python
"""DYNAMICS2 — firm up / bound the DYNAMICS1 contact-residue durability signal by EXPANDING n.
FROZEN METHOD: the contact-extraction (`parse_atoms`,`extract_contacts`) and ESM masked-marginal
(`masked_marginal`) code below is copied VERBATIM from DYNAMICS1/run.py. The metric is NOT changed.
The ONLY change is the EXPANDED TARGETS table + the pre-registered subset analyses in main().
Deterministic, CPU-only, offline. Run: ~/miniforge3/envs/intercepta/bin/python run.py"""
import os, sys, json, hashlib, time
import numpy as np
from scipy.spatial import cKDTree
from scipy.stats import mannwhitneyu
from sklearn.metrics import roc_auc_score

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_OFFLINE"] = "1"; os.environ["TRANSFORMERS_OFFLINE"] = "1"

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
D2   = os.path.join(DATA, "dynamics2")
STRU = os.path.join(D2, "structures")
LOGD = os.path.join(D2, "esm_logits")
HERE = os.path.dirname(os.path.abspath(__file__))
RES  = os.path.join(HERE, "results")
os.makedirs(LOGD, exist_ok=True); os.makedirs(RES, exist_ok=True)

ESM_MODEL = "facebook/esm2_t30_150M_UR50D"
HF_CACHE  = os.path.join(DATA, "hf_cache")
CONTACT_A = 4.5
MAXLEN    = 1022
AA20 = "ACDEFGHIKLMNPQRSTVWY"

# ---- EXPANDED target table (frozen in PREREG.md). class: 'abx' | 'antiviral' | 'antifungal'.
#      origin: 'D1' (reused from DYNAMICS1, unrelabeled) | 'NEW'. ----
TARGETS = [
 # --- DYNAMICS1 reused (verbatim, not relabeled) ---
 {"gene":"rpoB","label":"HIGH","pdb":"1I6V","ligand":"RFP","ligtype":"drug","cls":"abx","origin":"D1"},
 {"gene":"gyrA","label":"HIGH","pdb":"2XCT","ligand":"CPF","ligtype":"drug","cls":"abx","origin":"D1"},
 {"gene":"parC","label":"HIGH","pdb":"3RAE","ligand":"LFX","ligtype":"drug","cls":"abx","origin":"D1"},
 {"gene":"rpsL","label":"HIGH","pdb":"1FJG","ligand":"SRY","ligtype":"drug","cls":"abx","origin":"D1"},
 {"gene":"inhA","label":"HIGH","pdb":"1ZID","ligand":"ZID","ligtype":"drug","cls":"abx","origin":"D1"},
 {"gene":"embB","label":"HIGH","pdb":"7BVF","ligand":"95E","ligtype":"drug","cls":"abx","origin":"D1"},
 {"gene":"folP","label":"HIGH","pdb":"1AJ0","ligand":"SAN","ligtype":"drug","cls":"abx","origin":"D1"},
 {"gene":"murA","label":"LOW","pdb":"1UAE","ligand":"FFQ","ligtype":"drug","cls":"abx","origin":"D1"},
 {"gene":"dxr","label":"LOW","pdb":"1ONP","ligand":"FOM","ligtype":"drug","cls":"abx","origin":"D1"},
 {"gene":"alr","label":"LOW","pdb":"1EPV","ligand":"DCS","ligtype":"drug","cls":"abx","origin":"D1"},
 {"gene":"ddlB","label":"LOW","pdb":"2DLN","ligand":"PHY","ligtype":"inhibitor","cls":"abx","origin":"D1"},
 {"gene":"mraY","label":"LOW","pdb":"5CKR","ligand":"57M","ligtype":"inhibitor","cls":"abx","origin":"D1"},
 {"gene":"murF","label":"LOW","pdb":"2AM1","ligand":"1LG","ligtype":"inhibitor","cls":"abx","origin":"D1"},
 {"gene":"murG","label":"LOW","pdb":"1NLM","ligand":"UD1","ligtype":"substrate","cls":"abx","origin":"D1"},
 {"gene":"murB","label":"LOW","pdb":"2MBR","ligand":"EPU","ligtype":"substrate","cls":"abx","origin":"D1"},
 # --- NEW HIGH (antiviral / antifungal) ---
 {"gene":"HIV1_RT","label":"HIGH","pdb":"1VRT","ligand":"NVP","ligtype":"drug","cls":"antiviral","origin":"NEW"},
 {"gene":"HIV1_PR","label":"HIGH","pdb":"1OHR","ligand":"1UN","ligtype":"drug","cls":"antiviral","origin":"NEW"},
 {"gene":"FLU_NA","label":"HIGH","pdb":"2HU4","ligand":"G39","ligtype":"drug","cls":"antiviral","origin":"NEW"},
 {"gene":"HCV_NS3","label":"HIGH","pdb":"3SV6","ligand":"SV6","ligtype":"drug","cls":"antiviral","origin":"NEW"},
 {"gene":"CYP51_Ca","label":"HIGH","pdb":"5FSA","ligand":"X2N","ligtype":"drug","cls":"antifungal","origin":"NEW"},
 {"gene":"FLU_PA","label":"HIGH","pdb":"6FS6","ligand":"E4Z","ligtype":"drug","cls":"antiviral","origin":"NEW"},
 {"gene":"HSV1_TK","label":"HIGH","pdb":"1KI2","ligand":"GA2","ligtype":"drug","cls":"antiviral","origin":"NEW"},
 # --- NEW LOW ---
 {"gene":"HCV_NS5B","label":"LOW","pdb":"4WTG","ligand":"6GS","ligtype":"drug","cls":"antiviral","origin":"NEW"},
 {"gene":"murD","label":"LOW","pdb":"3UAG","ligand":"UMA","ligtype":"substrate","cls":"abx","origin":"NEW"},
 {"gene":"murE","label":"LOW","pdb":"1E8C","ligand":"UAG","ligtype":"substrate","cls":"abx","origin":"NEW"},
 {"gene":"glmU","label":"LOW","pdb":"1HV9","ligand":"UD1","ligtype":"substrate","cls":"abx","origin":"NEW"},
]

# ---- FROZEN residue maps (VERBATIM from DYNAMICS1) ----
AA3={'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G',
'HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S',
'THR':'T','TRP':'W','TYR':'Y','VAL':'V'}
MOD={'MSE':'M','KCX':'K','SEP':'S','TPO':'T','PTR':'Y','CSO':'C','LLP':'K','CME':'C',
'OCS':'C','MLY':'K','M3L':'K','HYP':'P','SEC':'C','PCA':'Q','FME':'M'}
AAMAP={**AA3, **MOD}

# ---------- deterministic mmCIF contact extraction (VERBATIM from DYNAMICS1) ----------
def parse_atoms(path):
    hdr=[]; rows=[]; inloop=False; idx=None
    with open(path) as fh:
        for line in fh:
            if line.startswith('_atom_site.'):
                hdr.append(line.strip().split('.')[1]); inloop=True; continue
            if inloop and (line.startswith('ATOM') or line.startswith('HETATM')):
                if idx is None: idx={c:i for i,c in enumerate(hdr)}
                rows.append(line.split())
            elif inloop and line.startswith('#'):
                break
    return idx, rows

def extract_contacts(pdb, lig):
    idx, rows = parse_atoms(os.path.join(STRU, pdb+".cif"))
    symI=idx['type_symbol']; compI=idx['label_comp_id']; asymI=idx['label_asym_id']
    seqI=idx['label_seq_id']; altI=idx.get('label_alt_id')
    xI=idx['Cartn_x']; yI=idx['Cartn_y']; zI=idx['Cartn_z']
    authseqI=idx.get('auth_seq_id')
    lig_xyz=[]; prot={}
    for p in rows:
        if p[symI] in ('H','D'): continue
        if altI is not None and p[altI] not in ('.','A','1'): continue
        comp=p[compI]
        try: xyz=(float(p[xI]),float(p[yI]),float(p[zI]))
        except: continue
        if comp==lig: lig_xyz.append(xyz); continue
        seq=p[seqI]
        if seq in ('.','?') or comp not in AAMAP: continue
        key=(p[asymI], int(seq))
        d=prot.setdefault(key, {'comp':comp,'atoms':[], 'auth_seq':p[authseqI] if authseqI else seq})
        d['atoms'].append(xyz)
    assert lig_xyz, f"no ligand {lig} atoms in {pdb}"
    tree=cKDTree(np.array(lig_xyz))
    contacts=[]
    for key,d in prot.items():
        mind=float(tree.query(np.array(d['atoms']),k=1)[0].min())
        if mind<=CONTACT_A:
            contacts.append((key[0],key[1],d['auth_seq'],d['comp'],round(mind,2)))
    from collections import Counter
    cc=Counter(c[0] for c in contacts)
    best=sorted(cc.items(), key=lambda x:(-x[1],x[0]))[0][0]
    chain_contacts=sorted([c for c in contacts if c[0]==best], key=lambda x:x[1])
    chain_res=sorted([(k[1],v) for k,v in prot.items() if k[0]==best], key=lambda x:x[0])
    seqids=[r[0] for r in chain_res]
    seq=''.join(AAMAP.get(r[1]['comp'],'X') for r in chain_res)
    pos_of={s:i for i,s in enumerate(seqids)}
    contact_idx=sorted(pos_of[c[1]] for c in chain_contacts)
    authmap={pos_of[c[1]]: (c[3], c[2]) for c in chain_contacts}  # idx -> (res3, auth_seq)
    return {'chain':best,'seq':seq,'contact_idx':contact_idx,'authmap':authmap,
            'n_lig':len(lig_xyz)}

# ---------- ESM-2 masked-marginal entropy (VERBATIM from DYNAMICS1) ----------
_ESM={}
def get_esm():
    if _ESM: return _ESM['tok'],_ESM['mod'],_ESM['tt']
    import torch
    from transformers import AutoTokenizer, AutoModelForMaskedLM
    torch.manual_seed(0); torch.use_deterministic_algorithms(True, warn_only=True)
    tok=AutoTokenizer.from_pretrained(ESM_MODEL, cache_dir=HF_CACHE)
    mod=AutoModelForMaskedLM.from_pretrained(ESM_MODEL, cache_dir=HF_CACHE).eval()
    aa_ids=[tok.get_vocab()[a] for a in AA20]
    _ESM.update(tok=tok, mod=mod, tt=torch, aa_ids=aa_ids); _ESM['torch']=torch
    return tok,mod,torch

def masked_marginal(gene, seq, contact_idx):
    """Return dict idx-> {entropy, sub_llr} via masked-marginal over 20 AA. Cached."""
    cache=os.path.join(LOGD, f"{gene}_mm.json")
    if os.path.exists(cache):
        return {int(k):v for k,v in json.load(open(cache)).items()}
    tok,mod,torch=get_esm(); aa_ids=_ESM['aa_ids']
    L=len(seq); off=0
    if L>MAXLEN:
        med=int(np.median(contact_idx)); half=MAXLEN//2
        off=min(max(0, med-half), L-MAXLEN); seq=seq[off:off+MAXLEN]
    cidx=[i-off for i in contact_idx]
    enc=tok(seq, return_tensors="pt")
    ids=enc["input_ids"][0].clone()
    mask_id=tok.mask_token_id
    out={}
    aa_ids_t=torch.tensor(aa_ids)
    with torch.no_grad():
        for ci, orig_i in zip(cidx, contact_idx):
            tpos=ci+1  # +1 for CLS/BOS
            batch=ids.clone(); wt_tok=int(batch[tpos]); batch[tpos]=mask_id
            logits=mod(input_ids=batch.unsqueeze(0),
                       attention_mask=enc["attention_mask"]).logits[0,tpos]
            aa_logits=logits[aa_ids_t]
            logp=torch.log_softmax(aa_logits, dim=0)
            p=logp.exp()
            H=float(-(p*logp).sum())
            wt_aa = AA20.find(tok.convert_ids_to_tokens(wt_tok))
            if wt_aa>=0:
                mask=torch.ones(len(AA20),dtype=torch.bool); mask[wt_aa]=False
                sub_llr=float((logp[mask]-logp[wt_aa]).mean())
            else:
                sub_llr=float('nan')
            out[orig_i]={'entropy':round(H,6),'sub_llr':round(sub_llr,6)}
    json.dump({str(k):v for k,v in out.items()}, open(cache,'w'))
    return out

# ---------- run ----------
def auroc(scores, labels):
    return float(roc_auc_score(labels, scores))

def main():
    t0=time.time()
    rows=[]
    for t in TARGETS:
        c=extract_contacts(t['pdb'], t['ligand'])
        mm=masked_marginal(t['gene'], c['seq'], c['contact_idx'])
        ents=[mm[i]['entropy'] for i in c['contact_idx']]
        subs=[mm[i]['sub_llr'] for i in c['contact_idx']]
        rows.append({
            'gene':t['gene'],'label':t['label'],'y':1 if t['label']=='HIGH' else 0,
            'pdb':t['pdb'],'ligand':t['ligand'],'ligtype':t['ligtype'],'cls':t['cls'],
            'origin':t['origin'],'chain':c['chain'],'n_contacts':len(c['contact_idx']),
            'mean_entropy':round(float(np.mean(ents)),6),
            'max_entropy':round(float(np.max(ents)),6),
            'mean_sub_llr':round(float(np.mean(subs)),6),
            'contact_residues':[f"{c['authmap'][i][0]}{c['authmap'][i][1]}" for i in c['contact_idx']],
            'contact_entropies':[mm[i]['entropy'] for i in c['contact_idx']],
        })
        print(f"{t['gene']:10s} {t['origin']:3s} {t['cls']:10s} y={rows[-1]['y']} "
              f"n={rows[-1]['n_contacts']:2d} meanH={rows[-1]['mean_entropy']:.4f} "
              f"maxH={rows[-1]['max_entropy']:.4f}", flush=True)

    y=np.array([r['y'] for r in rows])
    def stat(mask, key='mean_entropy', invert=False):
        idx=[i for i in range(len(rows)) if mask(rows[i])]
        s=np.array([rows[i][key] for i in idx]); yy=y[idx]
        if invert: s=-s
        hi=s[yy==1]; lo=s[yy==0]
        a=auroc(s, yy) if (len(hi)>0 and len(lo)>0) else float('nan')
        p=float(mannwhitneyu(hi, lo, alternative='two-sided').pvalue) if (len(hi)>0 and len(lo)>0) else float('nan')
        return {'auroc':round(a,6) if a==a else None,'mwu_p':round(p,6) if p==p else None,
                'n':len(idx),'n_high':int(yy.sum()),'n_low':int((1-yy).sum())}

    allmask=lambda r: True
    primary        = stat(allmask,'mean_entropy')
    sec_max        = stat(allmask,'max_entropy')
    sec_sub        = stat(allmask,'mean_sub_llr')
    abx_only       = stat(lambda r: r['cls']=='abx','mean_entropy')
    nonabx_only    = stat(lambda r: r['cls']!='abx','mean_entropy')
    new_only       = stat(lambda r: r['origin']=='NEW','mean_entropy')
    d1_rederive    = stat(lambda r: r['origin']=='D1','mean_entropy')
    no_substrate   = stat(lambda r: r['ligtype']!='substrate','mean_entropy')
    drug_only      = stat(lambda r: r['ligtype']=='drug','mean_entropy')

    D1_AUROC=0.839286; D1_P=0.028904; AMR1_AUROC=0.556; AMR1_P=0.74
    GATE_AUROC=0.75; GATE_P_FIRM=0.01; GATE_P_PARTIAL=0.05

    a=primary['auroc']; p=primary['mwu_p']
    generalizes = (abx_only['auroc'] is not None and abx_only['auroc']>=GATE_AUROC
                   and nonabx_only['auroc'] is not None and nonabx_only['auroc']>=0.5)
    if a>=GATE_AUROC and p<GATE_P_FIRM and generalizes:
        verdict='FIRMED_UP'
    elif a>=GATE_AUROC and p<GATE_P_PARTIAL:
        verdict='PARTIAL'
    else:
        verdict='NEGATIVE'

    payload={
        'metric':'mean masked-marginal Shannon entropy over drug-contact residues (ESM-2 t30 150M) [FROZEN from DYNAMICS1]',
        'contact_angstrom':CONTACT_A,
        'n_total':len(rows),
        'gate':{'auroc_min':GATE_AUROC,'mwu_p_firm':GATE_P_FIRM,'mwu_p_partial':GATE_P_PARTIAL},
        'reference':{'dynamics1_auroc':D1_AUROC,'dynamics1_mwu_p':D1_P,
                     'amr1_whole_protein_auroc':AMR1_AUROC,'amr1_whole_protein_mwu_p':AMR1_P},
        'primary_mean_entropy':primary,
        'secondary_max_entropy':sec_max,
        'secondary_sub_llr':sec_sub,
        'subset_antibacterial_only':abx_only,
        'subset_nonantibacterial_only':nonabx_only,
        'subset_new_targets_only':new_only,
        'subset_dynamics1_rederive':d1_rederive,
        'subset_no_substrate':no_substrate,
        'subset_clinical_drug_only':drug_only,
        'per_target':sorted(rows, key=lambda r:(-r['y'], r['cls'], r['gene'])),
    }
    payload_str=json.dumps(payload, sort_keys=True, separators=(',',':'))
    sha=hashlib.sha256(payload_str.encode()).hexdigest()

    out={'experiment':'DYNAMICS2_durability_scaleup','verdict':verdict,'payload':payload,
         'provenance':{'env':'intercepta (torch/tf)','model':ESM_MODEL,
                       'runtime_s':round(time.time()-t0,1)}}
    json.dump(out, open(os.path.join(RES,'DYNAMICS2_metrics.json'),'w'),
              indent=2, sort_keys=True)
    open(os.path.join(RES,'payload.sha256'),'w').write(sha+"\n")

    print("\n=== DYNAMICS2 RESULT ===")
    print(f"PRIMARY full ({primary['n']}: {primary['n_high']}H/{primary['n_low']}L): "
          f"AUROC={primary['auroc']:.3f} MWU_p={primary['mwu_p']:.4f}  "
          f"(DYNAMICS1 n=15: 0.839/0.029; AMR1 whole-protein 0.556/0.74)")
    print(f"  antibacterial-only ({abx_only['n']}:{abx_only['n_high']}H/{abx_only['n_low']}L): AUROC={abx_only['auroc']} p={abx_only['mwu_p']}")
    print(f"  non-abx cross-class ({nonabx_only['n']}:{nonabx_only['n_high']}H/{nonabx_only['n_low']}L): AUROC={nonabx_only['auroc']} p={nonabx_only['mwu_p']}")
    print(f"  new-only ({new_only['n']}:{new_only['n_high']}H/{new_only['n_low']}L): AUROC={new_only['auroc']} p={new_only['mwu_p']}")
    print(f"  D1-rederive ({d1_rederive['n']}:{d1_rederive['n_high']}H/{d1_rederive['n_low']}L): AUROC={d1_rederive['auroc']} p={d1_rederive['mwu_p']}  [expect 0.839/0.029]")
    print(f"  no-substrate ({no_substrate['n']}:{no_substrate['n_high']}H/{no_substrate['n_low']}L): AUROC={no_substrate['auroc']} p={no_substrate['mwu_p']}")
    print(f"  clinical-drug-only ({drug_only['n']}:{drug_only['n_high']}H/{drug_only['n_low']}L): AUROC={drug_only['auroc']} p={drug_only['mwu_p']}")
    print(f"  secondary max-H AUROC={sec_max['auroc']}; sub-LLR AUROC={sec_sub['auroc']}")
    print(f"GATE (FIRMED_UP=AUROC>=0.75 & p<0.01 & generalizes): {verdict}")
    print(f"payload sha256: {sha}")

if __name__=='__main__':
    main()
