"""v10.30 업경의 심판수 반업수 (지하 33층 100% · 34층 70% · 7지옥 보스맵)
 확률 · 순환 · 판결 분기(달림/정지/혼합) · 규칙 9(칼날 벽은 돌아서면 · 응시 고리는 나가면 · 시선은 옆/등 뒤 · 파편 조준선은 한 걸음 · 재현은 지나온 길에서 벗어나면) · 2페이즈 이중 시선 · 처치 · 도감 · 34층 개방 · 스크린샷
사용: PYTHONPATH=tools python3 tools/tests/byu1030.py   (스크린샷 build/byu_*.png)"""
import asyncio, sys, os, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from playwright.async_api import async_playwright
import h301
B = os.path.join(os.path.dirname(HERE), 'build') + '/'
async def ev(pg, js):
    try: return await pg.evaluate(js)
    except Exception as ex: return 'ERR ' + str(ex).split('\n')[0][:300]
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000); await pg.wait_for_function("__G.imgReady(['arena','dmap','byu'])", timeout=120000, polling=1000)
        await pg.evaluate("""()=>{window.__cl=()=>{const P=__G.P;P.inv=0;P.shield=0;P.dodge=0;P.pals=[];P.up.guard=0;P.rel.mirror=0;P.armor=1;P.taken=1;P.bindT=0;P.bindImm=0;P.stunT=0;P.max=1e7;P.hp=P.max};
          window.__tk=()=>{const G=__G;G.tick(1/30);if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s()};
          window.__go=(k)=>{const AI=__G.byu,e=__G.boss,W=__G.BYUW;W.blades=[];W.rings=[];W.beams=[];W.shards=[];W.lasers=[];W.trail=null;W.fx=[];e.invul=false;e.tele=[];AI.gz2=0;for(const c in AI.cd)AI.cd[c]=99;AI.cd[k]=0;AI.ordT=[k];AI.ci=0;AI.chase(0);e.stT=0}}""")
        R = {}
        R['A'] = await ev(pg, """()=>{const G=__G,o={};const cnt=(t,k)=>{const c={};for(let i=0;i<4000;i++){const q=G.pickBossK(t);c[q]=(c[q]||0)+1}return Math.round((c[k]||0)/40)};
          o.t32=cnt(32,'byu');o.t33=cnt(33,'byu');o.t34=cnt(34,'byu');o.open=G.OPEN_TIER===undefined?'?':0;
          G.SAVE.diff.max=34;G.SAVE.diff.sel=0;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;__lv(28);P.tier=32;P.fset='dosan';P.bossK='byu';G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)__tk();const bo=G.boss;o.bk=bo&&bo.bk;o.hp=Math.round(bo.max);
          const seen={},sts=[];let last='',out=0;
          for(let i=0;i<30*120;i++){P.hp=P.max;P.inv=1;const a=i/30;P.x=2100+Math.cos(a*0.7)*350;P.y=1727+Math.sin(a*0.7)*250;bo.hp=Math.max(bo.max*0.5,Math.min(bo.hp,bo.max*0.95));__tk();const e=G.boss;if(!e)break;if(!G.inPoly(e.x,e.y))out++;if(e.st!==last){last=e.st;seen[e.st]=(seen[e.st]||0)+1;sts.push(e.st)}}
          o.seen=seen;o.seq=sts.slice(0,30).join('>');o.bossOut=out;return o}""")
        # 판결 분기: 기록을 강제로 채운다
        R['verdict'] = await ev(pg, """()=>{const G=__G,AI=G.byu,o={};const fill=(m)=>{AI.hist=[];for(let i=0;i<40;i++)AI.hist.push({mv:m(i),x:2100+i*5,y:1727})};
          fill(()=>1);o.run=AI.verdict();fill(()=>0);o.stay=AI.verdict();fill(i=>i%2);o.mix=AI.verdict();return o}""")
        # 칼날 벽: 계속 직진 = 맞음 / 판결 뒤 돌아서면 안 맞음
        R['wall'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,cx=2100,cy=1727,o={};const run=(turn)=>{__cl();e.hp=e.max;e.x=cx;e.y=cy-450;P.x=cx-500;P.y=cy+100;__go('judge');const AI=G.byu;AI.hist=[];for(let i=0;i<40;i++)AI.hist.push({mv:1,x:P.x-(40-i)*20,y:P.y});
            let hit=0;for(let i=0;i<30*5;i++){P.inv=0;const sp=200/30;if(turn&&G.BYUW.blades.length)P.x-=sp;else P.x+=sp;P.moving=true;P.lastX=turn&&G.BYUW.blades.length?-1:1;P.lastY=0;const b=P.hp;__tk();if(P.hp<b)hit++}return hit};
          o.straight=run(false);o.turn=run(true);return o}""")
        # 응시 고리: 서 있으면 폭발 / 1.3초 안에 이속 160으로 나가면 안 맞음
        R['stay'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,cx=2100,cy=1727,o={};const run=(mv)=>{__cl();e.hp=e.max;e.x=cx;e.y=cy-450;P.x=cx;P.y=cy+150;__go('judge');const AI=G.byu;AI.hist=[];for(let i=0;i<40;i++)AI.hist.push({mv:0,x:P.x,y:P.y});
            let hit=0;for(let i=0;i<30*4;i++){P.inv=0;P.moving=false;if(mv&&G.BYUW.rings.length){P.x+=160/30}const b=P.hp;__tk();if(P.hp<b)hit++}return hit};
          o.stand=run(false);o.leave=run(true);return o}""")
        # 시선: 부채꼴 가운데(거리 460)에서 서 있기 / 옆으로 이속 250 / 등 뒤
        R['gaze'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,cx=2100,cy=1727,o={};const run=(mode)=>{__cl();e.hp=e.max;e.x=cx-230;e.y=cy;P.x=mode==='back'?cx-30:cx+230;P.y=cy;__go('gaze');let th=0;
            let hit=0;for(let i=0;i<30*4.5;i++){P.inv=0;e.x=cx-230;e.y=cy;if(mode==='side'&&(e.st==='gaze'||G.BYUW.beams.length))P.y=Math.max(cy-700,P.y-250/30);if(mode==='back'&&G.BYUW.beams.length&&th<Math.PI){th=Math.min(Math.PI,th+250/30/200);P.x=e.x+Math.cos(th)*200;P.y=e.y-Math.sin(th)*200}const b=P.hp;__tk();if(P.hp<b)hit++}return hit};
          o.stand=run('stand');o.side=run('side');o.back=run('back');return o}""")
        # 파편: 조준선이 생기면 옆으로 한 걸음 (60px)
        R['shard'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,cx=2100,cy=1727,o={};const run=(dodge)=>{__cl();e.hp=e.max;e.x=cx;e.y=cy-500;P.x=cx;P.y=cy+100;__go('shard');let hit=0,shots=0,seen=new Set();
            for(let i=0;i<30*10;i++){P.inv=0;e.x=cx;e.y=cy-500;G.byu.cd.swipe=99;if(dodge)for(const t of e.tele)if(t.k==='rect'&&!seen.has(t)&&t.t>0.2){seen.add(t);const nx=-Math.sin(t.ang),ny=Math.cos(t.ang);P.x+=nx*60;P.y+=ny*60;if(!G.inPoly(P.x,P.y)){P.x-=nx*120;P.y-=ny*120}}
              const n0=G.BYUW.lasers.length;const b=P.hp;__tk();if(G.BYUW.lasers.length>n0)shots++;if(P.hp<b)hit++;if(e.st==='chase'&&!G.BYUW.shards.length&&i>60)break}return [hit,shots]};
          o.stand=run(false);o.dodge=run(true);return o}""")
        # 재현: 원을 그리며 3초 → 재현 뒤 바깥으로 벗어나기
        R['replay'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,cx=2100,cy=1727,o={};const run=(leave)=>{__cl();e.hp=e.max;e.x=cx;e.y=cy-500;P.x=cx;P.y=cy+100;const AI=G.byu;AI.hist=[];
            for(let i=0;i<30;i++)AI.hist.push({mv:1,x:cx+Math.cos(i/30*6.28)*120,y:cy+100+Math.sin(i/30*6.28)*80});P.x=cx+120;P.y=cy+100;__go('replay');let hit=0;
            for(let i=0;i<30*3;i++){P.inv=0;if(leave&&G.BYUW.trail)P.y=Math.min(cy+700,P.y+180/30);const b=P.hp;__tk();if(P.hp<b)hit++}return hit};
          o.stay=run(false);o.leave=run(true);return o}""")
        # 2페이즈: 깨진 업경 → 이중 시선
        R['ph2'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,cx=2100,cy=1727,o={};__cl();e.hp=e.max*0.29;e.x=cx;e.y=cy-300;P.x=cx;P.y=cy;e.st='chase';e.stT=0;
          for(let i=0;i<10;i++){P.inv=1;__tk()}o.ph2=e.ph2;o.st=e.st;for(let i=0;i<70;i++){P.inv=1;__tk()}
          __go('gaze');let mx=0;for(let i=0;i<30*5;i++){P.inv=1;P.x=cx+Math.sin(i/20)*200;__tk();mx=Math.max(mx,G.BYUW.beams.length)}o.maxBeams=mx;
          __go('shard');for(let i=0;i<40;i++){P.inv=1;__tk()}o.shards=G.BYUW.shards.length;return o}""")
        await pg.evaluate("()=>{const G=__G,P=G.P,e=G.boss;__go('gaze');for(let i=0;i<45;i++){P.inv=1;__tk()}}")
        await pg.screenshot(path=B + 'byu_gaze.png')
        await pg.evaluate("()=>{const G=__G,P=G.P,e=G.boss;__go('shard');for(let i=0;i<50;i++){P.inv=1;__tk()} const AI=G.byu;AI.hist=[];for(let i=0;i<40;i++)AI.hist.push({mv:1,x:P.x-(40-i)*20,y:P.y});AI.v='mix';AI.judgeFire();for(let i=0;i<34;i++){P.inv=1;P.x+=3;P.moving=true;__tk()}}")
        await pg.screenshot(path=B + 'byu_judge.png')
        R['end'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss;__cl();P.x=e.x+150;P.y=e.y+250;const k0=(G.SAVE.dex.kills.boss22||0);e.hp=1;e.invul=false;G.hurtEnemy(e,99999,0,0,0,false);for(let i=0;i<33;i++){P.inv=1;__tk()}window.__k0=k0;return 1}""")
        await pg.screenshot(path=B + 'byu_death0.png')
        R['end'] = await ev(pg, """()=>{const G=__G,P=G.P;for(let i=0;i<27;i++){P.inv=1;__tk()}return {kills:(G.SAVE.dex.kills.boss22||0)-__k0,death:!!G.BYUW.death,bossGone:!G.boss||G.boss.hp<=0}}""")
        await pg.screenshot(path=B + 'byu_death.png')
        print(json.dumps(R, ensure_ascii=False, indent=1)); print('errs', errs[:8])
        await b.close()
asyncio.run(main())
