"""v8.86 지옥엘프 궁수: 사거리 카드 + 저격 시선 합침 · 기본 사거리 94"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss',timeout=60000)
        r=await pg.evaluate("""()=>{const G=__G,o={};G.startGame('archer');const P=G.P;o.rng0=P.rng;o.far0=P.far;
          const defs=G.cardDefs?G.cardDefs():null;o.hasSnipe=defs?defs.some(u=>u.id==='snipe'):'n/a';
          const r=defs&&defs.find(u=>u.id==='range');if(r){const v=G.cardView(r);o.name=v.name;o.desc=v.desc||v.txt}
          if(r){for(let i=0;i<5;i++){r.apply(P);P.up.range=(P.up.range|0)+1}}o.rngAfter=Math.round(P.rng*10)/10;o.farAfter=P.far;
          G.startGame('wolf');o.wolfRng=G.P.rng;return o}""")
        print(json.dumps(r,ensure_ascii=False)); print('errs',pg.errs[:5]); await b.close()
asyncio.run(main())
