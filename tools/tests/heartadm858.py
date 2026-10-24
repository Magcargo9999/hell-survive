"""v8.58 해군 제독 심장: 드랍 키 · 도트 줄(비어 있지 않음) · 4등급 · 도감"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
async def main():
    async with async_playwright() as pg_:
        b=await pg_.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.heart',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G,o={};o.key=[G.bhKey({bk:'adm'}),G.bhKey({bk:'zom'}),G.bhKey({bk:'ab'})];o.order=G.BH_ORDER;
          o.sheet=[G.IMG.heart.width,G.IMG.heart.height];
          G.SAVE.heart={inv:[],eq:[],n:0,got:{}};G.HEART.drop=1;G.HEART.legend=0;o.drop=G.rollHeartDrop('adm');
          const h=G.heartGain('rare','adm');o.got=G.SAVE.heart.got.adm;o.dexSeen=G.SAVE.dex.seen['heart:adm:rare'];o.drop2=G.rollHeartDrop('adm');
          o.px={};for(const g of ['rare','epic','unique','legend']){const c=G.heartIcon(g,64,'adm'),d=c.getContext('2d').getImageData(0,0,64,64).data;let n=0;for(let i=3;i<d.length;i+=4)if(d[i]>20)n++;o.px[g]=n}
          return o}""")
        print(json.dumps(R,ensure_ascii=False)); print('errs',pg.errs); await b.close()
asyncio.run(main())
