#!/usr/bin/env python3
"""
INTERCEPTA Scout 1: Screen all GDSC drugs through KAALCURA ODE
Ranks 286 drugs by predicted HR for mCRPC.

HONEST NOTE: Uses IC50-proxy for Cmax (median IC50 as Cmax estimate).
Relative ranking useful, absolute HR values NOT trustworthy.
Real PK needed per drug for absolute predictions.

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
"""
import pandas as pd
import numpy as np
from scipy.integrate import solve_ivp
from intercepta_phenotype_ode_v1 import load_velocity_distribution
import time

def run_scout1():
    bins = pd.read_csv('../results/kaalcura_per_bin.csv')
    drugs_df = pd.read_csv('../results/kaalcura_real_validation.csv')
    gdsc = pd.read_excel('../data/gdsc/GDSC2_fitted_dose_response.xlsx')
    
    N=20; dx=1.0/N; x=np.array([(i+0.5)/N for i in range(N)])
    r_max=0.00678; alpha_r=0.4; K=1.0; d_nat=0.001; beta=8.27e-4; EMAX=0.153
    
    n0_raw, _ = load_velocity_distribution('../results/velocity_star_latent_time.csv', N)
    N0=0.15; n0=n0_raw*N0; te=np.arange(0,1826,1)
    
    def make_constrained_ec50(drug_name, p5, p95):
        d=drugs_df[drugs_df['drug']==drug_name]
        if len(d)==0: return None
        cp,ce,cd=d.iloc[0]['coef_prolif'],d.iloc[0]['coef_emt'],d.iloc[0]['coef_ddr']
        s=cp*bins['R_prolif'].values+ce*bins['R_emt'].values+cd*bins['R_ddr'].values
        sn=(s-s.min())/(s.max()-s.min()) if s.max()-s.min()>1e-8 else np.full(N,0.5)
        return np.exp(np.log(p95)-sn*(np.log(p95)-np.log(p5)))
    
    def find_ttp(Nt,t,N0v):
        nad=np.min(Nt);nadi=np.argmin(Nt);thr=max(2*nad,N0v*1.25)
        for j in range(nadi+1,len(t)):
            if t[j]-t[nadi]>=60 and Nt[j]>thr: return t[j],nad
        return None,nad
    
    # Control
    def deriv_ctrl(t,n):
        n=np.maximum(n,0);Nt=np.sum(n);dndt=np.zeros(N)
        for i in range(N):
            g=r_max*(1-alpha_r*x[i])*n[i]*(1-Nt/K);di=d_nat*n[i]
            if i==0:df=beta*(n[1]-n[0])/dx**2
            elif i==N-1:df=beta*(n[N-2]-n[N-1])/dx**2
            else:df=beta*(n[i-1]-2*n[i]+n[i+1])/dx**2
            dndt[i]=g-di+df
        return dndt
    s_ctrl=solve_ivp(deriv_ctrl,(0,1825),n0.copy(),t_eval=te,method='RK45',rtol=1e-8,atol=1e-12,max_step=2)
    ctrl_ttp,_=find_ttp(np.sum(s_ctrl.y,axis=0),s_ctrl.t,N0)
    
    prad=gdsc[gdsc['TCGA_DESC']=='PRAD']
    all_cancer=gdsc.copy()
    results=[]
    drug_names=drugs_df['drug'].unique()
    print(f'Screening {len(drug_names)} drugs... Control TTP={ctrl_ttp/30.44:.1f}mo')
    t0=time.time()
    
    for idx,drug_name in enumerate(drug_names):
        drug_prad=prad[prad['DRUG_NAME']==drug_name]
        if len(drug_prad)>=3:
            ic50s=np.exp(drug_prad['LN_IC50'].values)
            p5,p95=np.percentile(ic50s,[5,95]); source='prostate'
        else:
            drug_all=all_cancer[all_cancer['DRUG_NAME']==drug_name]
            if len(drug_all)<3: continue
            ic50s=np.exp(drug_all['LN_IC50'].values)
            p5,p95=np.percentile(ic50s,[5,95]); source='all_cancer'
        if p5<=0 or p95<=0 or p95/p5<2: continue
        ec50_bins=make_constrained_ec50(drug_name,p5,p95)
        if ec50_bins is None: continue
        cmax=np.median(ic50s); ke=np.log(2)/0.5
        doses=np.array([i*21 for i in range(6)])
        
        def make_deriv(ec=ec50_bins,cm=cmax,k=ke,ds=doses):
            def deriv(t,n):
                n=np.maximum(n,0);Nt=np.sum(n)
                C=sum(cm*np.exp(-k*(t-td)) for td in ds if t>=td)
                dndt=np.zeros(N)
                for i in range(N):
                    g=r_max*(1-alpha_r*x[i])*n[i]*(1-Nt/K);di=d_nat*n[i]
                    ki=EMAX*C**1.5/(ec[i]**1.5+C**1.5)*n[i] if C>0 else 0
                    if i==0:df=beta*(n[1]-n[0])/dx**2
                    elif i==N-1:df=beta*(n[N-2]-n[N-1])/dx**2
                    else:df=beta*(n[i-1]-2*n[i]+n[i+1])/dx**2
                    dndt[i]=g-di-ki+df
                return dndt
            return deriv
        try:
            s=solve_ivp(make_deriv(),(0,1825),n0.copy(),t_eval=te,method='RK45',rtol=1e-6,atol=1e-10,max_step=1.0)
            Nt=np.sum(s.y,axis=0);ttp,nad=find_ttp(Nt,s.t,N0)
            hr=ctrl_ttp/ttp if(ctrl_ttp and ttp) else 0
            C_peak=cmax
            tail_kill=np.mean([EMAX*C_peak**1.5/(ec50_bins[i]**1.5+C_peak**1.5) for i in range(15,20)])
            results.append({'drug':drug_name,'hr':round(hr,4),'ttp_months':round(ttp/30.44,1) if ttp else 99,
                'nadir_pct':round((1-nad/N0)*100,1),'tail_kill':round(tail_kill,6),
                'ec50_min':round(p5,4),'ec50_max':round(p95,4),'cmax_approx':round(cmax,4),'source':source})
        except: pass
        if(idx+1)%50==0: print(f'  {idx+1}/{len(drug_names)} ({time.time()-t0:.0f}s)')
    
    rdf=pd.DataFrame(results).sort_values('hr')
    rdf.to_csv('../results/scout1_all_drugs_ranked.csv',index=False)
    print(f'\nDone: {len(results)} drugs in {time.time()-t0:.0f}s')
    print(f'Saved: results/scout1_all_drugs_ranked.csv')
    return rdf

if __name__=='__main__':
    rdf=run_scout1()
    print(f'\nTOP 10:')
    for _,r in rdf.head(10).iterrows():
        print(f'  {r["drug"]:<25} HR={r["hr"]:.3f} tail={r["tail_kill"]:.5f}')

