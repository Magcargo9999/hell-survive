"""v8.50 해저좀비(해군 제독 판 미니 보스): 출현 판 · 공격 3종 · 분노 · 사망 · 스크린샷"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
B='/home/claude/hell-survive/build/'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.zom',timeout=60000)
        R=await pg.evaluate("""()=>{const G=__G,o={};for(const [bk,t] of [['adm',11],['adm',17],['adm',3],['angel',11],['monkey',11],['eye',0]]){G.SAVE.diff.max=19;G.startGame('wolf');G.P.tier=t;G.P.bossK=bk;G.enemies.length=0;G.mini=null;G.P.miniDone=false;G.P.lvl=15;G.tick(1/30);o[bk+t]=G.mini&&(G.mini.bk||(G.mini.sk?'sk':'monkey'))}return o}""")
        print('spawn',json.dumps(R))
        for k in ['zsweep','zwave','zwisp']:
            R=await pg.evaluate("""(k)=>{const G=__G;G.startGame('wolf');const P=G.P;P.bossK='adm';__lv(12);G.enemies.length=0;G.spawnZom();const m=G.mini;m.x=P.x+200;m.y=P.y;
              let h0=P.hp,seen=0,eb=0,tl=0;m.st='chase';m.cd=99;G.zAtk(m,k);
              for(let i=0;i<150;i++){P.inv=0;G.tick(1/30);if(G.state!=='play')__s();if(m.st==='atk')seen++;eb=Math.max(eb,G.ebul.length);tl=Math.max(tl,m.tele.length)}
              return {lost:Math.round(h0-P.hp),seen,eb,tl,endSt:m.st}}""",k)
            print(k,json.dumps(R))
        for k,n in [('zsweep',20),('zwave',34),('zwisp',40)]:
            await pg.evaluate("""([k,n])=>{const G=__G;G.startGame('wolf');const P=G.P;P.bossK='adm';G.enemies.length=0;G.spawnZom();const m=G.mini;m.x=P.x+210;m.y=P.y;m.cd=99;G.zAtk(m,k);for(let i=0;i<n;i++){P.inv=99;G.tick(1/30)}G.render()}""",[k,n])
            await pg.screenshot(path=B+f'zom_{k}.png')
        R=await pg.evaluate("""()=>{const G=__G;G.startGame('wolf');const P=G.P;P.bossK='adm';__lv(12);G.enemies.length=0;G.spawnZom();const m=G.mini;m.x=P.x+300;m.y=P.y;m.hp=m.max*0.39;for(let i=0;i<20;i++){P.inv=99;G.tick(1/30)}
          const rage=m.rage;m.hp=1;G.hurtEnemy(m,1e9,1,0,0);for(let i=0;i<10;i++){P.inv=99;G.tick(1/30)}G.render();return {rage,dead:!G.mini,state:G.state,md:!!G.mdeath}}""")
        print('rage/death',json.dumps(R)); await pg.screenshot(path=B+'zom_death.png')
        print('errs',pg.errs); await b.close()
asyncio.run(main())
