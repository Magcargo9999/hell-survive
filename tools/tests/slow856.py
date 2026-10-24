"""v8.56 어인섬(지하 11~15층) 둔화 웅덩이: 분포 · 밟으면 이속 -35% + 벗어나도 0.8초 · 다른 층엔 없음 · 스크린샷"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
B='/home/claude/hell-survive/build/'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.sfloor&&__G.IMG.boss',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G,o={};G.SAVE.diff.max=19;G.SAVE.shards=1e7;
          for(const t of [0,7,10,12,14,15,17]){G.SAVE.diff.sel=t;G.startGame('wolf');let sl=0,lv=0,both=0,n=0;for(let x=-60;x<60;x++)for(let y=-60;y<60;y++){n++;const a=G.isSlow(x,y),l=G.isLava(x,y);if(a)sl++;if(l)lv++;if(a&&l)both++}
            o['t'+t]={fset:G.P.fset,slow:+(100*sl/n).toFixed(1),lava:+(100*lv/n).toFixed(1),both}}
          return o}""")
        print(json.dumps(R))
        R=await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.sel=16;G.startGame('wolf');const P=G.P;let T=null;
          for(let r=5;r<40&&!T;r++)for(let a=0;a<64&&!T;a++){const x=Math.round(Math.cos(a/10)*r),y=Math.round(Math.sin(a/10)*r);if(G.isSlow(x,y)&&G.isSlow(x+1,y)&&!G.isLava(x,y))T=[x,y]}
          const out={T};P.x=(T[0]+0.5)*64;P.y=(T[1]+0.5)*64;G.enemies.length=0;
          const TS=64;G.tick(1/30);out.inSlow=P.slowT;
          P.x=(T[0]-30)*64;P.y=T[1]*64;G.tick(1/30);out.after1=+P.slowT.toFixed(2);for(let i=0;i<30;i++){P.inv=99;G.tick(1/30)}out.after1s=+P.slowT.toFixed(2);
          return out}""")
        print(json.dumps(R))
        await pg.evaluate("""()=>{const G=__G,P=G.P;const T=(()=>{for(let r=5;r<40;r++)for(let a=0;a<64;a++){const x=Math.round(Math.cos(a/10)*r),y=Math.round(Math.sin(a/10)*r);if(G.isSlow(x,y)&&G.isSlow(x+1,y)&&G.isSlow(x,y+1))return [x,y]}})();P.x=(T[0]+0.5)*64;P.y=(T[1]+0.5)*64;G.enemies.length=0;for(let i=0;i<8;i++){P.inv=99;G.tick(1/30)}G.render()}""")
        await pg.screenshot(path=B+'slow856.png')
        print('errs',pg.errs); await b.close()
asyncio.run(main())
