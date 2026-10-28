"""v10.01 호랑이: 십자가 안 멈춤 · 벽까지 · 불 뿜기 없음 · 2페이즈 반대로 빠르게 · 돌진 5번 다 피하면 기절→가드 · 한 번 맞으면 기절 없음
사용: GAME_URL=http://localhost:8765/build/hell_survive.html PYTHONPATH=tools python3 tools/tests/tig1001.py"""
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
        await pg.evaluate("""()=>{window.__tk=()=>{const G=__G;if(G.P)G.P.heat=0;G.tick(1/30);if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s()};
          window.__free=()=>{const AI=__G.tg;for(const k in AI.cd)AI.cd[k]=99}}""")
        R = {}
        await pg.evaluate("()=>{const G=__G;G.SAVE.diff.max=29;G.SAVE.diff.sel=29;G.SAVE.shards=1e7;G.startGame('archer')}"); await pg.wait_for_function("__G.state==='play'&&__G.P", timeout=60000)
        R['A'] = await ev(pg, """()=>{const G=__G,o={};const P=G.P;__lv(30);P.max=1e7;P.hp=P.max;G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)__tk();const e=G.boss,C=G.TGW.cr;o.bk=e.bk;__free();
          const a0=C.a;let minLen=1e9;for(let i=0;i<30*12;i++){P.inv=1;P.hp=P.max;__tk();for(const l of C.len)minLen=Math.min(minLen,l)}
          o.spin=+(C.a-a0).toFixed(2);o.expect=+(G.TG.crOm*12).toFixed(2);o.minLen=Math.round(minLen);o.arms=G.tgArms().length;
          // 불 뿜기 상태가 없다
          o.noBreath=C.ph===undefined;return o}""")
        # 팔은 벽 끝까지 (광장 안)
        R['len'] = await ev(pg, """()=>{const G=__G,C=G.TGW.cr,[cx,cy]=G.tgC();let ok=0;for(const a of G.tgArms()){const ex=a[2]+(a[2]-cx)*0.001,ey=a[3]+(a[3]-cy)*0.001;if(Math.hypot(a[2]-cx,a[3]-cy)>=G.TG.crR)ok++}return {armsOk:ok}}""")
        # 안전: 가장 느린 이속 150으로도 팔 사이를 따라갈 수 있다 (1페이즈 반경 ≤300 · 2페이즈 ≤200)
        R['safe'] = await ev(pg, """()=>{const G=__G,o={},C=G.TGW.cr,[cx,cy]=G.tgC();
          const need=(om,r)=>om*r;o.p1follow=need(G.TG.crOm,300);o.p2follow=need(G.TG.crOm2,200);return o}""")
        # 2페이즈
        R['ph2'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.tg,C=G.TGW.cr;__free();e.tele=[];AI.chase(1);e.hp=e.max*0.39;e.x=G.IMAP.cx;e.y=G.IMAP.cy-200;P.x=G.IMAP.cx;P.y=G.IMAP.cy+200;
          for(let i=0;i<30*4;i++){P.inv=1;P.hp=P.max;__tk()}o.ph2=e.ph2;o.p2=C.p2;o.arms=G.tgArms().length;o.om=G.tgCrossOm();
          const a0=C.a;for(let i=0;i<30*2;i++){P.inv=1;P.hp=P.max;__tk()}o.d=+(C.a-a0).toFixed(2);return o}""")
        # 돌진: 다 피하면 기절→가드 / 한 번 맞으면 기절 없음
        for name,hit in [('dodge',False),('hit',True)]:
            R['dash_'+name] = await ev(pg, """()=>{const hit=HIT;const G=__G,o={};const P2=G.P;P2.max=1e7;P2.hp=P2.max;G.raiseCastle();G.enterArena();for(let i=0;i<40;i++)__tk();
          const e=G.boss,AI2=G.tg;__free();e.tele=[];e.x=G.IMAP.cx-400;e.y=G.IMAP.cy;P2.x=G.IMAP.cx+500;P2.y=G.IMAP.cy+300;AI2.dashStart();G.TGW.crHitT=1e9;
          const sts=[];let last='',n=0;for(let i=0;i<30*30;i++){P2.hp=P2.max;if(!hit){P2.inv=1;P2.x=G.IMAP.cx+500;P2.y=G.IMAP.cy+500;} else {P2.inv=0;if(e.st==='dsRun'){P2.x=e.x+40;P2.y=e.y}}
            G.TGW.crHitT=1e9;__tk();if(e.st!==last){last=e.st;sts.push(e.st)}if(e.st==='guard'||e.st==='chase'&&sts.length>6)break}
          o.seq=sts.join('>');o.hit=G.TGW.dHit;return o}""".replace("HIT", "true" if hit else "false"))
        print(R); print('ERR', errs[:5])
        await b.close()
asyncio.run(main())
