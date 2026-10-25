"""v9.29: 천안의 군주 [천안 난무]를 쓰면 보스 러시 startRush와 이름이 겹쳐 새 판이 시작되던 버그 — 쓰고 나서도 같은 판(레벨·진화·루트 그대로, rush 없음)이고 rushQ가 도는지
사용: PYTHONPATH=tools python3 tools/tests/rushdash929.py"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch();pg=await h301.newpage(b,1280,720);errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G;G.SAVE.chars.chimera=true;G.SAVE.rush.open=true;G.startGame('chimera');const P=G.P;P.bugF0=true;
          let g=0;while(P.lvl<21&&g++<9000){if(G.state==='levelup'){const t=document.getElementById('levelTitle').textContent;const c=G.choices;let i=0;
            if(t.indexOf('갈림길')>=0){i=c.findIndex(u=>u.key==='dream'&&!u.locked);if(i<0)i=0}G.pick(i);continue}
            if(G.state==='evolve'){G.tick(1/30);continue}
            if(G.state==='play'){P.exp=P.need;G.tick(1/30);continue}break}
          P.exp=0;for(let i=0;i<60;i++){P.inv=9;G.tick(1/30);if(G.state==='levelup')G.pick(0)}
          if(G.state!=='play')return {err:'state '+G.state}
          const b={lvl:P.lvl,form:P.form,route:P.route,skill:P.skill,rush:!!G.rush};
          G.enemies.length=0;for(let i=0;i<6;i++)G.spawnEnemy&&G.spawnEnemy();
          P.skT=0;G.cast();let q=0;for(let i=0;i<90;i++){P.inv=9;G.tick(1/30);if(G.state==='levelup')G.pick(0);if(G.rushQ)q++}
          return {before:b,dash:q,after:{lvl:P.lvl,form:P.form,route:P.route,skill:P.skill,rush:!!G.rush,state:G.state}}}""")
        print(json.dumps(R,ensure_ascii=False));print('errs',errs[:3]);await b.close()
asyncio.run(main())
