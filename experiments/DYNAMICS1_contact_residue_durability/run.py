#!/usr/bin/env python
"""DYNAMICS1 — drug-contact-residue mutational tolerance (ESM-2 masked-marginal entropy)
as a resistance-liability signal. AMR1 follow-on. Deterministic, CPU-only, offline.
Run: ~/miniforge3/envs/intercepta/bin/python run.py
Pre-registration in PREREG.md is FROZEN; this script does not tune to pass."""
import os, sys, json, hashlib, time
import numpy as np
from scipy.spatial import cKDTree
from scipy.stats import mannwhitneyu
from sklearn.metrics import roc_auc_score

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_OFFLINE"] = "1"; os.environ["TRANSFORMERS_OFFLINE"] = "1"

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
D1   = os.path.join(DATA, "dynamics1")
STRU = os.path.join(D1, "structures")
LOGD = os.path.join(D1, "esm_logits")
HERE = os.path.dirname(os.path.abspath(__file__))
RES  = os.path.join(HERE, "results")
os.makedirs(LOGD, exist_ok=True); os.makedirs(RES, exist_ok=True)

ESM_MODEL = "facebook/esm2_t30_150M_UR50D"
HF_CACHE  = os.path.join(DATA, "hf_cache")
CONTACT_A = 4.5
MAXLEN    = 1022
AA20 = "ACDEFGHIKLMNPQRSTVWY"

# ---- FROZEN target table (from PREREG.md) ----
TARGETS = [
 {"gene":"rpoB","label":"HIGH","pdb":"1I6V","ligand":"RFP","ligtype":"drug"},
 {"gene":"gyrA","label":"HIGH","pdb":"2XCT","ligand":"CPF","ligtype":"drug"},
 {"gene":"parC","label":"HIGH","pdb":"3RAE","ligand":"LFX","ligtype":"drug"},
 {"gene":"rpsL","label":"HIGH","pdb":"1FJG","ligand":"SRY","ligtype":"drug"},
 {"gene":"inhA","label":"HIGH","pdb":"1ZID","ligand":"ZID","ligtype":"drug"},
 {"gene":"embB","label":"HIGH","pdb":"7BVF","ligand":"95E","ligtype":"drug"},
 {"gene":"folP","label":"HIGH","pdb":"1AJ0","ligand":"SAN","ligtype":"drug"},
 {"gene":"murA","label":"LOW","pdb":"1UAE","ligand":"FFQ","ligtype":"drug"},
 {"gene":"dxr","label":"LOW","pdb":"1ONP","ligand":"FOM","ligtype":"drug"},
 {"gene":"alr","label":"LOW","pdb":"1EPV","ligand":"DCS","ligtype":"drug"},
 {"gene":"ddlB","label":"LOW","pdb":"2DLN","ligand":"PHY","ligtype":"inhibitor"},
 {"gene":"mraY","label":"LOW","pdb":"5CKR","ligand":"57M","ligtype":"inhibitor"},
 {"gene":"murF","label":"LOW","pdb":"2AM1","ligand":"1LG","ligtype":"inhibitor"},
 {"gene":"murG","label":"LOW","pdb":"1NLM","ligand":"UD1","ligtype":"substrate"},
 {"gene":"murB","label":"LOW","pdb":"2MBR","ligand":"EPU","ligtype":"substrate"},
]

AA3={'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G',
'HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S',
'THR':'T','TRP':'W','TYR':'Y','VAL':'V'}
MOD={'MSE':'M','KCX':'K','SEP':'S','TPO':'T','PTR':'Y','CSO':'C','LLP':'K','CME':'C',
'OCS':'C','MLY':'K','M3L':'K','HYP':'P','SEC':'C','PCA':'Q','FME':'M'}
AAMAP={**AA3, **MOD}

# ---------- deterministic mmCIF contact extraction ----------
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

# ---------- ESM-2 masked-marginal entropy ----------
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
    # window if needed (keep all contacts in-window)
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
                # mean over 19 non-wt of (logp_mut - logp_wt)
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
        # rpsL K43-equivalent: the streptomycin-contact Lys with the lowest auth_seq among contacts
        rps_note=None
        if t['gene']=='rpsL':
            lys=[(c['authmap'][i][1], mm[i]['entropy']) for i in c['contact_idx'] if c['authmap'][i][0]=='LYS']
            rps_note=lys
        rows.append({
            'gene':t['gene'],'label':t['label'],'y':1 if t['label']=='HIGH' else 0,
            'pdb':t['pdb'],'ligand':t['ligand'],'ligtype':t['ligtype'],'chain':c['chain'],
            'n_contacts':len(c['contact_idx']),
            'mean_entropy':round(float(np.mean(ents)),6),
            'max_entropy':round(float(np.max(ents)),6),
            'mean_sub_llr':round(float(np.mean(subs)),6),
            'contact_residues':[f"{c['authmap'][i][0]}{c['authmap'][i][1]}" for i in c['contact_idx']],
            'contact_entropies':[mm[i]['entropy'] for i in c['contact_idx']],
            'rpsL_lys_entropy':rps_note,
        })
        print(f"{t['gene']:6s} y={rows[-1]['y']} n={rows[-1]['n_contacts']:2d} "
              f"meanH={rows[-1]['mean_entropy']:.4f} maxH={rows[-1]['max_entropy']:.4f} "
              f"subLLR={rows[-1]['mean_sub_llr']:.4f}", flush=True)

    y=np.array([r['y'] for r in rows])
    def stat(mask, key, invert=False):
        idx=[i for i in range(len(rows)) if mask(rows[i])]
        s=np.array([rows[i][key] for i in idx]); yy=y[[i for i in idx]]
        if invert: s=-s
        a=auroc(s, yy)
        hi=s[yy==1]; lo=s[yy==0]
        p=float(mannwhitneyu(hi, lo, alternative='two-sided').pvalue)
        return {'auroc':round(a,6),'mwu_p':round(p,6),'n':len(idx),
                'n_high':int(yy.sum()),'n_low':int((1-yy).sum())}

    allmask=lambda r: True
    primary=stat(allmask,'mean_entropy')
    sec_max=stat(allmask,'max_entropy')
    sec_sub=stat(allmask,'mean_sub_llr')  # higher sub_llr = more tolerant = HIGH
    sens_no_substrate=stat(lambda r: r['ligtype']!='substrate','mean_entropy')
    sens_clin_drug   =stat(lambda r: r['ligtype']=='drug','mean_entropy')

    AMR1_AUROC=0.556; AMR1_P=0.74; GATE_AUROC=0.75; GATE_P=0.05
    passed = (primary['auroc']>=GATE_AUROC) and (primary['mwu_p']<GATE_P) and (primary['auroc']>AMR1_AUROC)

    payload={
        'metric':'mean masked-marginal Shannon entropy over drug-contact residues (ESM-2 t30 150M)',
        'contact_angstrom':CONTACT_A,
        'n_feasible':len(rows),
        'gate':{'auroc_min':GATE_AUROC,'mwu_p_max':GATE_P,'must_beat_amr1':AMR1_AUROC},
        'amr1_reference':{'whole_protein_auroc':AMR1_AUROC,'whole_protein_mwu_p':AMR1_P,
                          'amr1_F1_conservation_auroc':0.569444},
        'primary_mean_entropy':primary,
        'secondary_max_entropy':sec_max,
        'secondary_sub_llr':sec_sub,
        'sensitivity_no_substrate':sens_no_substrate,
        'sensitivity_clinical_drug_only':sens_clin_drug,
        'per_target':sorted(rows, key=lambda r:(-r['y'], r['gene'])),
    }
    payload_str=json.dumps(payload, sort_keys=True, separators=(',',':'))
    sha=hashlib.sha256(payload_str.encode()).hexdigest()

    verdict='PASS' if passed else 'NEGATIVE'
    out={'experiment':'DYNAMICS1_contact_residue_durability','pass':bool(passed),
         'verdict':verdict,'payload':payload,
         'provenance':{'env':'intercepta (torch2.10/tf4.41)','model':ESM_MODEL,
                       'runtime_s':round(time.time()-t0,1)}}
    json.dump(out, open(os.path.join(RES,'DYNAMICS1_metrics.json'),'w'),
              indent=2, sort_keys=True)
    open(os.path.join(RES,'payload.sha256'),'w').write(sha+"\n")
    print("\n=== DYNAMICS1 RESULT ===")
    print(f"PRIMARY (all {primary['n']}: {primary['n_high']}H/{primary['n_low']}L): "
          f"AUROC={primary['auroc']:.3f} MWU_p={primary['mwu_p']:.3f}  "
          f"(AMR1 whole-protein 0.556 / p 0.74)")
    print(f"  no-substrate ({sens_no_substrate['n']}): AUROC={sens_no_substrate['auroc']:.3f} p={sens_no_substrate['mwu_p']:.3f}")
    print(f"  clinical-drug-only ({sens_clin_drug['n']}): AUROC={sens_clin_drug['auroc']:.3f} p={sens_clin_drug['mwu_p']:.3f}")
    print(f"  secondary max-H AUROC={sec_max['auroc']:.3f}; sub-LLR AUROC={sec_sub['auroc']:.3f}")
    for r in payload['per_target']:
        if r['gene']=='rpsL': print(f"  rpsL streptomycin-contact Lys (auth_seq,H): {r['rpsL_lys_entropy']}")
    print(f"GATE (AUROC>=0.75 & p<0.05 & >0.556): {verdict}")
    print(f"payload sha256: {sha}")

if __name__=='__main__':
    main()
