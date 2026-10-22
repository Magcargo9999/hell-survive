"""v8.06 부패한 성상(타락천사 판 미니 보스): 출현 조건 · 공격 3종 각각 실행·피해 · 분노 · 사망 · 다른 판엔 안 나옴 + 스크린샷  PYTHONPATH=tools python3 tools/tests/statue806.py"""
import asyncio, os, json
from playwright.async_api import async_playwright
from h301 import newpage, ROOT
OUT = os.path.join(ROOT, 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('window.__G && __G.IMG.statue', timeout=60000)
        # 1) 출현: 타락천사 판이면 성상, 다른 판은 원래 미니 (말 2종은 30% 예외라 spawnMini를 직접 부른다)
        R = await pg.evaluate("""()=>{const G=__G,o={};for(const bk of ['angel','monkey','eye','skel','shk']){G.startGame('wolf');G.P.tier=0;G.P.bossK=bk;G.enemies.length=0;G.mini=null;G.spawnMini();o[bk]=G.mini&&(G.mini.bk||(G.mini.sk?'sk':'monkey'));}return o}""")
        print('spawn', json.dumps(R))
        for k in ['sslash', 'sshard', 'ssanct']:
            R = await pg.evaluate("""(k)=>{const G=__G;G.startGame('wolf');const P=G.P;P.bossK='angel';__lv(12);G.enemies.length=0;G.spawnStat();const m=G.mini;m.x=P.x+200;m.y=P.y;
              let h0=P.hp,mx=0,seen=0,eb=0;m.st='chase';m.cd=99;G.sAtk(m,k);
              for(let i=0;i<150;i++){P.inv=0;G.tick(1/30);if(G.state!=='play')__s();if(m.st==='atk')seen++;eb=Math.max(eb,G.ebul.length);}
              return {lost:Math.round(h0-P.hp),seen,eb,endSt:m.st}}""", k)
            print(k, json.dumps(R))
        # 분노 · 사망
        R = await pg.evaluate("""()=>{const G=__G;G.startGame('wolf');const P=G.P;P.bossK='angel';__lv(12);G.enemies.length=0;G.spawnStat();const m=G.mini;m.x=P.x+300;m.y=P.y;m.hp=m.max*0.39;for(let i=0;i<20;i++){P.inv=99;G.tick(1/30);}
          const rage=m.rage;m.hp=1;G.hurtEnemy(m,1e9,1,0,0);for(let i=0;i<60;i++){P.inv=99;G.tick(1/30);}return {rage,dead:!G.mini,state:G.state}}""")
        print('rage/death', json.dumps(R))
        for k, nm in [('sslash', 'slash'), ('sshard', 'shard'), ('ssanct', 'sanct')]:
            await pg.evaluate("""(k)=>{const G=__G;G.startGame('wolf');const P=G.P;P.bossK='angel';G.enemies.length=0;G.spawnStat();const m=G.mini;m.x=P.x+210;m.y=P.y;m.cd=99;G.sAtk(m,k);for(let i=0;i<%d;i++){P.inv=99;G.tick(1/30);}G.render()}""" % {'sslash': 24, 'sshard': 38, 'ssanct': 48}[k], k)
            await pg.screenshot(path=os.path.join(OUT, f'statue_{nm}.png'))
        print('errs', pg.errs); await b.close()
asyncio.run(main())
