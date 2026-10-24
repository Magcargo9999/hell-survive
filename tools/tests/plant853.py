"""v8.53 악마 식물원(지하 16~20층): 잡몹 = 식물형 악마 8종 · 네임드 3종(가시덩굴·식인 꽃·거대 달팽이) 공격·처치·도감 키 + 스크린샷"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
B='/home/claude/hell-survive/build/'
START="G.SAVE.diff.max=19;G.SAVE.diff.sel=10;G.SAVE.shards=1e6;G.startGame('wolf');"
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.gmob&&__G.IMG.gnm',timeout=90000)
        R=await pg.evaluate("()=>{const G=__G;"+START+"const P=G.P;const o={tier:P.tier,fset:P.fset,gs:G.GSPECIES.length};for(let i=0;i<10;i++)G.spawnEnemy();o.mobIdx=[...new Set(G.enemies.map(e=>e.spec&&e.spec.idx))];return o}")
        print('field',json.dumps(R))
        for pk in ['vine','fly','snl']:
            R=await pg.evaluate("""(pk)=>{const G=__G;"""+START+"""const P=G.P;__lv(12);G.enemies.length=0;const e=G.spawnPlant(pk);e.x=P.x+170;e.y=P.y;e.cd=0;
              let h0=P.hp,sts=new Set(),maxB=0,gp=0;for(let i=0;i<150;i++){P.inv=0;G.tick(1/30);if(G.state!=='play')__s();sts.add(e.st);maxB=Math.max(maxB,G.plBalls.length);gp=Math.max(gp,G.zones.filter(z=>z.type==='gpool').length);P.x=P.x;}
              const lost=Math.round(h0-P.hp);G.hurtEnemy(e,1e9,1,0,0);G.tick(1/30);
              return {lost,sts:[...sts],maxB,gp,dex:G.SAVE.dex.kills['pl:'+pk]||0,hp:Math.round(e.max)}}""",pk)
            print(pk,json.dumps(R))
        for pk,n in [('vine',12),('fly',8),('snl',30)]:
            await pg.evaluate("""([pk,n])=>{const G=__G;"""+START+"""const P=G.P;G.enemies.length=0;for(let i=0;i<14;i++){const q=G.spawnEnemy();q.x=P.x-500+i*70;q.y=P.y+220+(i%2)*40;}
              const e=G.spawnPlant(pk);e.x=P.x+180;e.y=P.y+20;e.cd=0;const o=[G.spawnPlant('vine'),G.spawnPlant('fly'),G.spawnPlant('snl')];o.forEach((q,i)=>{q.x=P.x-380+i*150;q.y=P.y-200;q.cd=99});
              for(let i=0;i<n;i++){P.inv=99;G.tick(1/30)}G.render()}""",[pk,n])
            await pg.screenshot(path=B+f'plant_{pk}.png')
        await pg.evaluate("()=>{__G.openDex&&__G.openDex()}")
        print('errs',pg.errs); await b.close()
asyncio.run(main())
