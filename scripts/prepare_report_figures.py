#!/usr/bin/env python3
"""Create readable vector report figures from the already verified figure data."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.size':11,'axes.labelsize':11,'xtick.labelsize':11,'ytick.labelsize':11,'legend.fontsize':10.5,'pdf.fonttype':42})
for stem in ['workload-a-baseline-indexes','workload-a-full-matched']:
    d=json.loads((ROOT/'docs/figures'/f'{stem}.data.json').read_text())
    fig,(top,bottom)=plt.subplots(2,1,figsize=(6.6,4.8),gridspec_kw={'height_ratios':[2.0,1.0]},layout='constrained')
    x=list(range(6));clients=[1,4,8,16,32,64]
    if 'tps' in d:
        top.plot(x,d['tps']['expt_a0'],'s--',color='#64748b',label='a0, seed 42')
        top.plot(x,d['tps']['expt_a112'],'o-',color='#2563eb',label='a112, seed 42')
        top.plot(x[:-1],d['repeat_seed7_tps'][:-1],'D:',color='#0f766e',label='a112, seed 7')
        top.plot([5],[d['repeat_seed7_tps'][-1]],'D',mfc='white',mec='#0f766e',label='Aborted warmup')
        top.set_ylim(0,106);shares=['T3','T4','T6','Other']
    else:
        a=[float(r['overall_tps']) for r in d['a0']];b=[float(r['overall_tps']) for r in d['a102']]
        top.plot(x,a,'s--',color='#64748b',label='Preserved a0')
        top.plot(x[:3],b[:3],'o-',color='#2563eb',label='a102')
        top.plot(x[4:],b[4:],'o-',color='#2563eb')
        top.plot([3],[b[3]],'o',mfc='white',mec='#2563eb',label='Aborted warmup')
        top.set_ylim(0,4.3);shares=['T3','T4','Other']
    top.set_xticks(x,clients);top.set_xlabel('Clients');top.set_ylabel('Scripts / 600 s (TPS)')
    top.grid(axis='y',alpha=.2);top.legend(loc='lower right',ncol=2,frameon=False)
    colors=['#2563eb','#7dd3fc','#fbbf24','#cbd5e1']
    for i,row in enumerate(d['one_client_time_shares']):
        left=0
        for k,color in zip(shares,colors):
            v=row[k];bottom.barh(i,v,left=left,color=color,label=k if i==0 else None)
            if v>9:bottom.text(left+v/2,i,f'{v:.0f}%',ha='center',va='center',fontsize=10.5)
            left+=v
    bottom.set_yticks([0,1],[r['design'] for r in d['one_client_time_shares']]);bottom.invert_yaxis()
    bottom.set_xlim(0,100);bottom.set_xticks([0,50,100]);bottom.set_xlabel('Recorded transaction time at one client (%)')
    bottom.legend(loc='upper center',bbox_to_anchor=(.5,-.48),ncol=len(shares),frameon=False)
    for ax in [top,bottom]:
        ax.spines[['top','right']].set_visible(False)
    target=ROOT/'submission/report/images'/f'{stem}.pdf';fig.savefig(target);plt.close(fig)
    print(target)
