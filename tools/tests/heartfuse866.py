"""v8.66 여왕 심장(8번째 줄) + 심장 합성(v8.83: 레전더리 3개 → 옵션 2줄) · 2줄 재설정 · 합계 · 화면"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
async def main():
    async with async_playwright() as pg_:
        b=await pg_.chromium.launch(); pg=await h301.newpage(b,1280,800)
        await pg.wait_for_function('__G.IMG&&__G.IMG.heart',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G,o={};o.key=G.bhKey({bk:'qn'});o.order=G.BH_ORDER.length;o.sheet=[G.IMG.heart.width,G.IMG.heart.height];
          G.SAVE.heart={inv:[],eq:[],n:0,got:{}};G.HEART.drop=1;G.HEART.legend=0;o.drop=G.rollHeartDrop('qn');
          const hs=['qn','adm','tox','eye','monkey'].map(k=>G.heartGain('legend',k));
          o.px={};for(const g of ['rare','epic','unique','legend']){const c=G.heartIcon(g,64,'qn'),d=c.getContext('2d').getImageData(0,0,64,64).data;let n=0;for(let i=3;i<d.length;i+=4)if(d[i]>20)n++;o.px[g]=n}
          hs[1].lock=true;o.lockErr=G.fuseHearts([hs[0].id,hs[1].id,hs[2].id]).err;hs[1].lock=false;{const ep=G.heartGain('epic','skel');o.epicErr=G.fuseHearts([hs[0].id,hs[1].id,ep.id]).err;}
          o.short=G.fuseHearts([hs[0].id,hs[1].id]).err;
          const r=G.fuseHearts([hs[0].id,hs[1].id,hs[2].id]);const f=r.h;o.fused={st2:f.st2,v2:f.v2,inv:G.SAVE.heart.inv.length,eq:G.SAVE.heart.eq.length};
          o.again=G.fuseHearts([hs[0].id,hs[3].id,hs[4].id]).err;
          const bo=G.heartBonus();o.sum=bo.atk+bo.hp+bo.aspd;o.expect=hs[0].v+hs[0].v2+hs[3].v+hs[4].v;
          G.SAVE.shards=1e6;let ok=true;for(let i=0;i<40;i++){const x=G.rerollHeart(f.id);if(!x.after.st2||x.after.v2<G.HG[x.after.g].min||x.after.v2>G.HG[x.after.g].max)ok=false}o.reroll2=ok;
          const n2=G.heartGain('legend','skel'),n3=G.heartGain('legend','angel');G.setFu([n2.id,n3.id]);G.openHeart();return o}""")
        await pg.wait_for_timeout(500); await pg.screenshot(path='/home/claude/hell-survive/build/heartfuse.png')
        print(json.dumps(R,ensure_ascii=False)); print('errs',pg.errs); await b.close()
asyncio.run(main())
