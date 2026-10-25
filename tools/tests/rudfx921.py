"""v9.21 마하칼 루드라 이펙트 도트 — 염주·폭발·만트라 가시/기둥·진언 룬·최종 형태 걷기/시전·사망 6칸 스크린샷 + 콘솔 오류"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
B='/home/claude/hell-survive/build/'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
        await pg.wait_for_function('__G.IMG&&__G.IMG.rud&&__G.IMG.rudfx',timeout=90000)
        o=await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=23;G.SAVE.diff.sel=22;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;__lv(28);G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)G.tick(1/30);__s();const e=G.boss,AI=G.rd;for(const k in AI.cd)AI.cd[k]=99;
          P.x=G.IMAP.cx+250;P.y=G.IMAP.cy+250;e.x=G.IMAP.cx-150;e.y=G.IMAP.cy-50;e.st='chase';e.stT=99;AI.karma();for(let i=0;i<25;i++){P.hp=P.max;G.tick(1/30);}
          G.RDW.beads.forEach((b,i)=>{b.n=[0,8,16,22][i%4]});return {beads:G.RDW.beads.length,rudfx:!!G.IMG.rudfx}}""")
        print(o); await pg.evaluate("()=>{__G.RDW.beads.forEach((b,i)=>{b.x=__G.P.x-260+i*220;b.y=__G.P.y-120;b.sx=b.x;b.sy=b.y;})}")
        for i in range(8): await pg.evaluate("()=>{const G=__G;G.P.hp=G.P.max;G.tick(1/30)}")
        await pg.screenshot(path=B+'rfx_bead.png')
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,AI=G.rd;P.hp=P.max;G.RDW.beads=[];e.x=P.x-300;e.y=P.y-20;AI.mantra();}""")
        for i in range(24): await pg.evaluate("()=>{const G=__G;G.P.hp=G.P.max;G.P.inv=1;G.tick(1/30)}")
        await pg.screenshot(path=B+'rfx_mantra.png')
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,AI=G.rd;G.RDW.lines=[];e.x=P.x;e.y=P.y-200;AI.penance();for(let i=0;i<40;i++){P.hp=P.max;P.inv=1;G.tick(1/30)}}""")
        await pg.screenshot(path=B+'rfx_ring.png')
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss;G.RDW.wave=null;e.ph2=true;e.an='fin';e.st='orbit';e.x=P.x+100;e.y=P.y-80;e.hp=e.max*0.2}""")
        for i in range(6): await pg.evaluate("()=>{const G=__G;G.P.hp=G.P.max;G.P.inv=1;G.tick(1/30)}")
        await pg.screenshot(path=B+'rfx_fin.png')
        await pg.evaluate("""()=>{const G=__G,e=G.boss;e.an='cast';e.anT=0.9;e.stT=99;e.st='cast'}""")
        await pg.screenshot(path=B+'rfx_cast.png')
        for t in (0.2,0.6,1.0,1.5):
            await pg.evaluate("(t)=>{const G=__G,e=G.boss;G.RDW.death={x:e.x,y:e.y,t:t,face:1,ph2:true}}",t)
            await pg.evaluate("()=>{}"); await pg.screenshot(path=B+'rfx_death_%d.png'%int(t*10))
        print('errs',errs[:5])
        await b.close()
asyncio.run(main())
