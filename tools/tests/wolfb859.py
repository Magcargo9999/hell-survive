"""v8.59 토끼 후드 늑대(유니크 스킨): 확률 · 천장 · 진화 단계별 적용 · 그리기 · 스크린샷"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
B='/home/claude/hell-survive/build/'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.sk_wolfB&&__G.IMG.boss',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G,o={};const S=G.SAVE.skin;let u=0,e=0,r=0,f=0,N=40000,pu=0,pn=0,maxGap=0,gap=0;
          for(let i=0;i<N;i++){S.own={};S.frag={};S.pity=0;const x=G.gachaRoll();if(x.type==='frag')f++;else{const g=G.skinG(x.id).grade;if(g==='unique')u++;else if(g==='epic')e++;else r++;}}
          o.rates={unique:+(100*u/N).toFixed(2),epic:+(100*e/N).toFixed(2),rare:+(100*r/N).toFixed(2),frag:+(100*f/N).toFixed(2)};
          const pc={unique:0,epic:0,rare:0};for(let i=0;i<20000;i++){S.own={};S.frag={};S.pity=24;const x=G.gachaRoll();pc[G.skinG(x.id).grade]++}o.pity=pc;
          S.own={wolfB:true};S.frag={};S.on={wolf:'wolfB'};
          G.SAVE.diff.max=0;G.SAVE.diff.sel=0;G.startGame('wolf');o.f0=!!G.skinOn('wolf');
          for(const f of [1,2]){G.P.form=f;o.['f'+f]=!!G.skinOn('wolf')} return o}""".replace("o.['f'+f]","o['f'+f]"))
        print(json.dumps(R,ensure_ascii=False))
        for form in (0,1,2):
            await pg.evaluate("(f)=>{const G=__G,P=G.P;P.form=f;P.anim='walk';P.animT=0.3;P.face=1;G.enemies.length=0;for(let i=0;i<5;i++){P.inv=0;G.tick(1/30)};G.render()}",form)
            await pg.screenshot(path=B+f'wolfb{form}.png',clip={'x':440,'y':200,'width':400,'height':300})
        for an in ('idle','attack','hit','death'):
            err=await pg.evaluate("(a)=>{const G=__G,P=G.P;P.form=2;P.anim=a;P.animT=0.2;try{G.render();return 0}catch(e){return String(e)}}",an); print(an,err)
        await pg.evaluate("""()=>{const G=__G;document.querySelectorAll('.overlay.show').forEach(o=>o.classList.remove('show'));G.SAVE.skin.own={wolfB:true};G.SAVE.skin.frag={};G.openGacha('dex')}""")
        await pg.wait_for_timeout(600); await pg.screenshot(path=B+'wolfb_dex.png')
        print('errs',pg.errs); await b.close()
asyncio.run(main())
