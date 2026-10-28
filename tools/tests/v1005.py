"""v10.05: 고래 파도 x3 · 보스 안내 2배 · 심장 줄 잠금 · 도깨비 결계 1.6배 · 구르기 3 · 서리 도탄"""
import asyncio
from h301 import *
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        await pg.wait_for_timeout(2500)
        r = await pg.evaluate("""()=>{const G=__G,o={};
          o.wave=G.WH.waSp; o.roll=G.ROLL.n; o.dok=[G.DOK.znJump,G.DOK.znRain,G.DOK.spSp,G.DOK.spPause,G.DOK.spWind];
          // 심장 줄 잠금
          const S=G.SAVE.heart; S.inv=[]; S.eq=[]; const h={id:901,g:'rare',b:'monkey',st:'atk',v:2,st2:'hp',v2:2,st3:'aspd',v3:2}; S.inv.push(h);
          G.SAVE.shards=1e6; const c0=G.heartCost(h); h.ll=[true,false,false]; const c1=G.heartCost(h); h.ll=[true,true,false]; const c2=G.heartCost(h);
          o.cost=[c0,c1,c2]; let kept=0; for(let i=0;i<30;i++){h.ll=[true,false,false]; const st=h.st,v=h.v; G.rerollHeart(901); if(h.st===st&&h.v===v)kept++;} o.kept=kept;
          const one={id:902,g:'rare',b:'tox',st:'atk',v:2}; o.one=G.heartCost(one);
          o.syn=G.SYNERGIES.find(x=>x.id==='gCryo')&&G.SYNERGIES.find(x=>x.id==='gCryo').need;
          return o}""")
        print(r)
        ok = r['wave']==2340 and r['roll']==3 and r['cost']==[500,1000,2000] and r['kept']==30 and r['one']==500 and r['syn']==['gRico','gSpec']
        print('OK' if ok else 'FAIL'); print('오류:', pg.errs); await b.close()
asyncio.run(main())
