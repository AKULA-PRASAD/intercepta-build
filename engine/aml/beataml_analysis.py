#!/usr/bin/env python3
"""
INTERCEPTA BeatAML Analysis
============================
Processes BeatAML2 data (569 patients, 166 drugs).
Validates FLT3 inhibitor sensitivity in FLT3-mutant patients.
Cross-disease repurposing with mCRPC GDSC data.

Data: Bottomly et al. Cancer Cell 2022
Author: Prasad Akula
"""
import pandas as pd
import numpy as np

def analyze_beataml(data_dir='../data/beataml', gdsc_path='../data/gdsc/GDSC2_fitted_dose_response.xlsx'):
    ds = pd.read_csv(f'{data_dir}/beataml_probit_curve_fits_v4_dbgap.txt', sep='\t')
    mut = pd.read_csv(f'{data_dir}/beataml_wes_wv1to4_mutations_dbgap.txt', sep='\t')
    clin = pd.read_excel(f'{data_dir}/beataml_wv1to4_clinical.xlsx')
    
    print(f'BeatAML2: {ds["dbgap_subject_id"].nunique()} patients, {ds["inhibitor"].nunique()} drugs')
    print(f'Mutations: {mut["symbol"].nunique()} genes mutated')
    
    # Top mutated genes
    print(f'\nTop mutated genes:')
    for gene, n in mut['symbol'].value_counts().head(10).items():
        print(f'  {gene:<12} {n}')
    
    # FLT3 validation
    mut_subjects = {}
    for _, r in clin.iterrows():
        if pd.notna(r.get('dbgap_dnaseq_sample')):
            mut_subjects[r['dbgap_dnaseq_sample']] = r['dbgap_subject_id']
    
    flt3_subjects = set()
    for sample in mut[mut['symbol']=='FLT3']['dbgap_sample_id'].unique():
        if sample in mut_subjects:
            flt3_subjects.add(mut_subjects[sample])
    wt_subjects = set(ds['dbgap_subject_id'].unique()) - flt3_subjects
    
    print(f'\nFLT3 inhibitor sensitivity (FLT3-mut vs WT):')
    for drug in ['Quizartinib','Crenolanib','Gilteritinib','Midostaurin','Sorafenib']:
        dd = ds[ds['inhibitor'].str.contains(drug, case=False, na=False)]
        if len(dd)==0: continue
        flt3_auc = dd[dd['dbgap_subject_id'].isin(flt3_subjects)]['auc']
        wt_auc = dd[dd['dbgap_subject_id'].isin(wt_subjects)]['auc']
        if len(flt3_auc)>3 and len(wt_auc)>3:
            diff = 'MORE sensitive' if wt_auc.median()>flt3_auc.median() else 'MORE resistant'
            print(f'  {drug:<15} FLT3mut={flt3_auc.median():.1f} WT={wt_auc.median():.1f} → {diff}')
    
    # Cross-disease with GDSC prostate
    gdsc = pd.read_excel(gdsc_path)
    prad = gdsc[gdsc['TCGA_DESC']=='PRAD'].groupby('DRUG_NAME')['LN_IC50'].mean()
    aml_sens = ds.groupby('inhibitor')['auc'].median().sort_values()
    
    print(f'\nCross-disease repurposing (AML → Prostate):')
    for drug in aml_sens.head(10).index:
        for gdsc_name in prad.index:
            if drug.lower().split()[0] in gdsc_name.lower():
                aml_val = aml_sens[drug]
                prad_val = np.exp(prad[gdsc_name])
                print(f'  {drug[:25]:<25} AML_AUC={aml_val:.0f} PRAD_IC50={prad_val:.3f}')
                break

if __name__ == '__main__':
    analyze_beataml()
