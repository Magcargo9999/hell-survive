"""v9.60 심장 7종 추가 → v10.01 호랑이 심장: 16종 드랍 · 아이콘 · 심장 도감 · 업적"""
import asyncio
from h301 import *
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        await pg.wait_for_timeout(2500)
        r = await pg.evaluate("""()=>{const G=__G,S=G.SAVE.heart;S.inv=[];S.eq=[];S.got={};const o={};
          o.order=G.BH_ORDER.length;
          o.drops=G.BH_ORDER.map(k=>{let c=0;for(let i=0;i<400;i++)if(G.rollHeartDrop(k))c++;return c>0});
          o.keys=['monkey','vft','kng','bear','rud','lil','cvt','snk','tig','fw','ab','grn',undefined].map(k=>G.bhKey({bk:k===undefined?undefined:k}));
          o.icons=G.BH_ORDER.map(k=>{const c=G.heartIcon('rare',64,k),x=c.getContext('2d').getImageData(0,0,64,64).data;let n=0;for(let i=3;i<x.length;i+=4)if(x[i]>40)n++;return n});
          o.gr=['rare','epic','unique','legend'].map(g=>{const c=G.heartIcon(g,64,'tig'),x=c.getContext('2d').getImageData(0,0,64,64).data;let n=0;for(let i=3;i<x.length;i+=4)if(x[i]>40)n++;return n});o.ach=G.ACH.filter(a=>a.id.startsWith('hb_')).length; return o}""")
        print(r)
        ok = r['order']==16 and all(r['drops']) and r['keys']==['monkey','vft','kng','bear','rud','lil','cvt','snk','tig',None,None,None,'monkey'] and min(r['icons'])>500 and min(r['gr'])>500 and r['ach']==17
        print('OK' if ok else 'FAIL'); print('오류:', pg.errs); await b.close()
asyncio.run(main())
