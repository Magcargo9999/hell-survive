"""v10.02 불구렁이: 땅파기 균열이 내 길 뒤에도 계속(엇갈리는 그물) · 빨아들이기 강화 후 옆걸음 탈출 가능(가장 느린 이속 150)
사용: GAME_URL=http://localhost:8765/build/hell_survive.html PYTHONPATH=tools python3 tools/tests/snk1002.py"""
import asyncio, sys, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from playwright.async_api import async_playwright
import h301
async def ev(pg, js):
    try: return await pg.evaluate(js)
    except Exception as ex: return 'ERR ' + str(ex).split('\n')[0][:300]
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000); await pg.wait_for_function("__G.imgReady(['arena','fmap'])", timeout=120000, polling=1000)
        await pg.evaluate("()=>{window.__tk=()=>{const G=__G;if(G.P)G.P.heat=0;G.tick(1/30);if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s()};const G=__G;G.SAVE.diff.max=24;G.SAVE.diff.sel=0;G.SAVE.shards=1e7;G.startGame('archer')}")
        await pg.wait_for_function("__G.state==='play'&&__G.P", timeout=60000)
        R = {}
        R['setup'] = await ev(pg, """()=>{const G=__G,P=G.P;__lv(28);P.max=1e7;P.hp=P.max;P.tier=27;P.fset='fire';P.bossK='snk';G.raiseCastle();G.enterArena();for(let i=0;i<40;i++)__tk();return G.boss&&G.boss.bk}""")
        R['tunnel'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,AI=G.sn,o={};for(const k in AI.cd)AI.cd[k]=99;G.SNW.cracks=[];e.tele=[];const H0=G.snHall();P.x=H0.cx+200;P.y=H0.cy;e.x=H0.cx-400;e.y=H0.cy;AI.then='tunnel';AI.go('dig',0.1,'none');
          let mx=0,legs=0,t=0;for(let i=0;i<30*14;i++){P.inv=1;P.hp=P.max;__tk();mx=Math.max(mx,G.SNW.cracks.length);if(G.SNW.path)legs=G.SNW.path.length;if(e.st==='emerge')break;t++}
          o.maxCracks=mx;o.pathPts=legs;o.sec=+(t/30).toFixed(1);o.st=e.st;return o}""")
        # 흡입 탈출: 입 앞 거리 r0 에서 옆걸음 (속도 150)
        R['suck'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,AI=G.sn,o={};const H=G.snHall();
          for (const ph2 of [false,true]) for (const r0 of [300,450,650]) {
            AI.chase(99);for(const k in AI.cd)AI.cd[k]=99;G.SNW.cracks=[];e.tele=[];e.ph2=ph2;e.under=false;e.invul=false;e.face=1;e.x=H.cx-300;e.y=H.cy;P.x=e.x+r0+60;P.y=e.y;P.inv=0;P.shield=0;P.hp=P.max;
            AI.go('gape',0.8,'gape');G.SNW.suck={ang:0,t:0.4,ph:'gape'};let hit=0;const h0=P.hp;let minD=1e9;
            G.keys.clear();for(let i=0;i<30*4.2;i++){G.keys.clear();G.keys.add('KeyS');P.hp=Math.max(P.hp,1);__tk();const m=G.snMouth(e);minD=Math.min(minD,Math.hypot(P.x-m.x,P.y-m.y));if(e.st==='spit'||e.st==='chase')break}
            G.keys.clear();o[(ph2?'p2_':'p1_')+r0]={bit:!!(G.SNW.suck&&G.SNW.suck.bit),minD:Math.round(minD),st:e.st};}
          return o}""")
        print(R); print('ERR', errs[:5]); await b.close()
asyncio.run(main())
