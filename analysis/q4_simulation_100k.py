import numpy as np
rng=np.random.default_rng(42)
N=100_000; R=20000
# observed (Shopify, sessions landing on Q4 page 14-16/11)
S,ATC,CHK,ORD=269,37,30,17
units_obs=[1]*15+[2,3]
price={1:14.90,2:25.94,3:31.29}
def rev_units(q): 
    return {1:14.90,2:25.94,3:31.29}[q]
def sim(cr_draw, cps, cogs, refuse=0.02):
    orders=rng.binomial(N, cr_draw)
    # basket mix bootstrap from observed with Dirichlet uncertainty
    mix=rng.dirichlet([15+1,1+1,1+1],size=R)
    n1=orders*mix[:,0]; n2=orders*mix[:,1]; n3=orders*mix[:,2]
    kept=1-refuse
    units=(n1+2*n2+3*n3)*kept
    gross=(n1*14.90+n2*25.94+n3*31.29)*kept
    net=gross/1.24
    ads=N*cps
    cost=units*cogs
    profit=net-cost-ads
    return orders*kept,units,gross,net,ads,profit
def q(a): return np.percentile(a,[10,50,90])
scen={
 'A Τεστ Q4 (6,3%)': rng.beta(ORD+1,S-ORD+1,size=R),
 'B Μέσος όρος καταστήματος (3,2%)': rng.beta(288+1,8905-288+1,size=R),
 'C Συντηρητικό (2,0%)': np.full(R,0.02),
}
print('Q4 funnel: ATC %.1f%%, checkout %.1f%%, CR %.2f%%; units/order %.3f; rev/order %.2f'%(ATC/S*100,CHK/S*100,ORD/S*100,np.mean(units_obs),284.59/17))
ci=np.percentile(rng.beta(ORD+1,S-ORD+1,size=200000),[5,95]); print('CR 90%% CI: %.1f%%-%.1f%%'%(ci[0]*100,ci[1]*100))
for cps,lab in [(0.157,'κόστος/επίσκεψη 0,157 € (τεστ)'),(0.231,"κόστος/επίσκεψη 0,231 € (FIB)")]:
  for cogs in [1.71,2.79]:
    print(f'\n== {lab}, κόστος τεμ. {cogs} €')
    for k,cr in scen.items():
        o,u,g,n,a,p=sim(cr,cps,cogs)
        print(f'{k:36s} παραγγελίες {q(o)[1]:6.0f} [{q(o)[0]:.0f}-{q(o)[2]:.0f}]  τεμάχια {q(u)[1]:6.0f}  τζίρος {q(g)[1]:8.0f} €  καθαρά(χωρίς ΦΠΑ) {q(n)[1]:7.0f}  διαφήμιση {a:6.0f}  κέρδος {q(p)[1]:7.0f} € [{q(p)[0]:.0f} έως {q(p)[2]:.0f}]')
# break-even CR
for cps in [0.157,0.231]:
  for cogs in [1.71,2.79]:
    upo=np.mean(units_obs); rpo=284.59/17
    m=rpo/1.24-upo*cogs
    print(f'break-even CR @cps {cps} cogs {cogs}: {cps/m*100/0.98:.2f}%  (περιθώριο/παραγγελία {m:.2f} €, max κόστος/παραγγελία {m:.2f})')
# stock: with 1000 units, visitors needed
for cr in [0.0632,0.0323,0.02]:
    print(f'1000 τεμάχια εξαντλούνται μετά από ~{1000/(cr*np.mean(units_obs)*0.98):,.0f} επισκέψεις στο CR {cr*100:.1f}%')
