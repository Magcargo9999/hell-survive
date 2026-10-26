"""v9.54 가시관 무당벌레 (지하 15층 원예의 여왕 판 미니 보스): 등장 분기 · 패턴 3가지 피해/회피 · 분노 · 처치(도감) · 스크린샷 · 오류
사용: GAME_URL=http://localhost:8765/index.html PYTHONPATH=tools python3 tools/tests/lad954.py [폴더]"""
import asyncio, sys, os, json
from h301 import *
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else 'build/lad'; os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.lad&&__G.IMG.ladW', timeout=90000)
        R = await pg.evaluate("""()=>{const G=__G,o={};G.SAVE.diff.max=15;G.SAVE.diff.sel=14;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;__lv(15);P.tier=14;P.bossK='qn';
          for(const e of G.enemies)e.hp=0;G.spawnMini();const e=G.mini;o.bk=e&&e.bk;o.hp=Math.round(e.max);o.name=G.SAVE.dex.seen.lad;
          // 각 패턴: 가만히 서 있으면 맞고, 피하면 안 맞는다
          const run=(k,dodge)=>{e.x=P.x+(k==='lgust'?260:150);e.y=P.y;e.st='chase';e.tele=[];e.lb=[];e.cd=99;P.hp=P.max;P.inv=0;P.shield=0;P.dodge=0;P.slowT=0;const h0=P.hp,x0=P.x;G.lAtk(e,k);
            for(let i=0;i<30*4;i++){if(dodge){if(k==='lspike')P.x-=6;else if(k==='lgust')P.y-=6;else P.y+=6;}P.inv=0;G.tick(1/30);e.cd=99;}
            return {lost:Math.round(h0-P.hp),push:Math.round(Math.abs(P.x-x0)),slow:+(P.slowT||0).toFixed(2)}};
          o.spikeStand=run('lspike',0);o.spikeDodge=run('lspike',1);
          o.shellStand=run('lshell',0);o.shellDodge=run('lshell',1);
          o.gustStand=run('lgust',0);o.gustDodge=run('lgust',1);
          e.hp=e.max*0.35;e.st='chase';e.cd=0.1;for(let i=0;i<30;i++)G.tick(1/30);o.rage=e.rage;
          P.inv=99;e.cd=0;const seen={};for(let i=0;i<30*40;i++){P.hp=P.max;G.tick(1/30);if(e.at)seen[e.at.k]=1;}o.seen=Object.keys(seen);
          return o}""")
        print(json.dumps(R, ensure_ascii=False))
        for k in ('lspike', 'lshell', 'lgust'):
            await pg.evaluate("(k)=>{const G=__G,P=G.P,e=G.mini;P.inv=99;e.x=P.x+260;e.y=P.y-40;e.st='chase';e.tele=[];e.lb=[];G.lAtk(e,k);for(let i=0;i<(k==='lshell'?32:18);i++)G.tick(1/30);}", k)
            await pg.screenshot(path=f'{OUT}/lad_{k}.png')
        r2 = await pg.evaluate("()=>{const G=__G,e=G.mini;e.hp=1;G.hurtEnemy?0:0;const k0=G.SAVE.dex.kills.lad||0;e.tele=[];e.lb=[];G.miniDefeated(e);const i=G.enemies.indexOf(e);if(i>=0)G.enemies.splice(i,1);for(let t=0;t<12;t++)G.tick(1/30);return {md:G.mdeath&&G.mdeath.bk}}")
        await pg.screenshot(path=f'{OUT}/lad_death.png'); print(r2)
        print('오류:', pg.errs); await b.close()
asyncio.run(main())
