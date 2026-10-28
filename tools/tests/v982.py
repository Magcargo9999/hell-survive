"""v9.82: 고래 파도 안전 줄(맵 안·걸어서 도달) · 열기(서 있기 2.2 · 움직이기 3.4 · 식기 14) · 불구렁이 땅속(내 길 따라 · 속도 ×2 · 참호 5초 · 코앞 안 붙음)"""
import asyncio, sys, os, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from playwright.async_api import async_playwright
import h301
B = os.path.join(os.path.dirname(HERE), 'build') + '/'
async def ev(pg, js):
    try: return await pg.evaluate(js)
    except Exception as ex: return 'ERR ' + str(ex).split('\n')[0][:300]
async def start(pg, tier, fset, bk, ready):
    await pg.wait_for_function("__G.imgReady(%s)" % ready, timeout=120000, polling=1000)
    await pg.evaluate("([t,f,k])=>{const G=__G;G.SAVE.diff.max=Math.max(24,t);G.SAVE.diff.sel=t;G.SAVE.shards=1e7;G.startGame('archer')}", [tier, fset, bk])
    await pg.wait_for_function("__G.state==='play'", timeout=60000)
    await pg.evaluate("([t,f,k])=>{const G=__G,P=G.P;__lv(28);P.tier=t;P.fset=f;P.bossK=k;G.raiseCastle();G.enterArena();for(let i=0;i<60;i++){G.tick(1/30);if(G.state!=='play')__s()}}", [tier, fset, bk])
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000)
        await pg.evaluate("()=>{window.__tk=()=>{const G=__G;G.tick(1/30);if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s()}}")
        # ---------- 고래 ----------
        await start(pg, 17, 'sea', 'whl', "['arena','smap','whl','whlfx']")
        r = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,AI=G.wh,R=G.whRoom(),o={bad:0,n:0,outside:0,lanes:[]};
          for(let i=0;i<G.WH.waN;i++)o.lanes.push(G.inPoly((R.x0+R.x1)/2,R.y0+(i+.5)*R.band)?1:0);
          for(let t=0;t<200;t++){const x=R.x0+Math.random()*(R.x1-R.x0),y=R.y0+Math.random()*(R.y1-R.y0);if(!G.inPoly(x,y))continue;o.n++;P.x=x;P.y=y;e.tele=[];G.WHW.wv=null;G.WHW.cur=[];
            for(const c in AI.cd)AI.cd[c]=99;AI.cd.wave=0;AI.cyc=['wave'];AI.ci=0;e.st='chase';e.stT=0;AI.chase(0);e.stT=0;AI.next&&AI.next();
            for(let k=0;k<4&&!(G.WHW.wv&&G.WHW.wv.cur);k++){P.x=x;P.y=y;P.inv=9;G.tick(1/30)}
            const W=G.WHW.wv&&G.WHW.wv.cur;if(!W){continue}
            const ok=G.whLaneOk(W.safe,R,x,y);if(!ok&&G.whLane(y,R)!==W.safe)o.bad++;
            const cy=R.y0+(W.safe+.5)*R.band;if(!G.inPoly(x,cy)&&G.whLane(y,R)!==W.safe)o.outside++;}
          return o}""")
        print('whale', json.dumps(r)); 
        # ---------- 열기 ----------
        await start(pg, 25, 'fire', 'cvt', "['arena','fmap']")
        r = await ev(pg, """()=>{const G=__G,P=G.P,o={};const run=(mv,sec)=>{P.heat=0;P.hp=P.max;for(let i=0;i<30*sec;i++){P.hp=P.max;P.inv=1;P.moving=mv;P.x=G.IMAP.cx;P.y=G.IMAP.cy;G.tick(1/30);P.moving=mv;}return Math.round(P.heat*10)/10};
          o.stand10=run(false,10);o.HEAT={fill:G.HEAT.fill,move:G.HEAT.move,cool:G.HEAT.cool};return o}""")
        print('heat', json.dumps(r))
        # ---------- 불구렁이 ----------
        await start(pg, 27, 'fire', 'snk', "['arena','fmap','snk']")
        r = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,AI=G.sn,o={};const H=G.snHall();
          e.tele=[];G.SNW.balls=[];G.orbs.length=0;G.SNW.cracks=[];e.x=H.cx-400;e.y=H.cy-150;AI.chase(99);
          // 내가 4초 동안 한 방향으로 걸어간다
          P.x=H.cx-250;P.y=H.cy+120;for(let i=0;i<30*4;i++){P.inv=9;P.hp=P.max;P.x+=150/30;__tk()}
          const px=P.x,py=P.y;AI.dig('tunnel');let t=0,minD=1e9,tun=0,maxCr=0;const sts=[];let last='';
          for(let i=0;i<30*10;i++){P.inv=9;P.hp=P.max;__tk();if(e.st!==last){last=e.st;sts.push(e.st)}if(e.st==='tunnel')tun++;
            for(const c of G.SNW.cracks)minD=Math.min(minD,G.segDist(P.x,P.y,c.ax,c.ay,c.bx,c.by));maxCr=Math.max(maxCr,G.SNW.cracks.length);if(e.st==='chase'&&i>30)break}
          o.seq=sts.join('>');o.tunnelSec=+(tun/30).toFixed(2);o.minCrackToP=Math.round(minD);o.maxCr=maxCr;o.life=G.SN.crLife;o.sp=G.SN.tuSp;o.px=[Math.round(px),Math.round(py)];return o}""")
        print('snake', json.dumps(r))
        r = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,AI=G.sn,o={};const H=G.snHall();   // 서 있을 때: 둘레 호
          e.tele=[];G.SNW.cracks=[];G.SNW.trail=[];AI.chase(99);e.x=H.cx-400;e.y=H.cy-150;P.x=H.cx;P.y=H.cy;AI.dig('tunnel');let minD=1e9;
          for(let i=0;i<30*10;i++){P.inv=9;P.hp=P.max;__tk();for(const c of G.SNW.cracks)minD=Math.min(minD,G.segDist(P.x,P.y,c.ax,c.ay,c.bx,c.by));if(e.st==='chase'&&i>30)break}
          o.minCrackToP_stand=Math.round(minD);return o}""")
        print('snake_stand', json.dumps(r))
        print('ERRS', errs[:5]); await b.close()
asyncio.run(main())
