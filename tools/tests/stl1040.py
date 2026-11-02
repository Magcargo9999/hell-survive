"""v10.40 철식 강철이 (지하 35층 전용 · 7지옥 최종 마왕)
 층 · 순환 · 철식 중첩(시간·삼킴) · 철 덩어리(가까이에서만 부서짐 · 1페이즈 흡수) · 폐철골 기둥(부수면 기절·피해 / 못 부수면 삼킴) · 휩쓸기 품 안 안전
 · 강타 탈출 · 2페이즈 포식(흡수 중 부수면 약점 노출 · 먹으면 중첩) · 자력 폭주 · 3페이즈 흑철룡(마디·쇄도·브레스) · 처치 · 도감 · 스크린샷
사용: PYTHONPATH=tools python3 tools/tests/stl1040.py   (스크린샷 build/stl_*.png)"""
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
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000); await pg.wait_for_function("__G.imgReady(['arena','dmap','stl'])", timeout=120000, polling=1000)
        await pg.evaluate("""()=>{window.__cl=()=>{const P=__G.P;P.inv=0;P.shield=0;P.dodge=0;P.pals=[];P.up.guard=0;P.rel.mirror=0;P.armor=1;P.taken=1;P.bindT=0;P.bindImm=0;P.stunT=0;P.slowT=0;P.max=1e7;P.hp=P.max};
          window.__tk=()=>{const G=__G;G.tick(1/30);if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s()};
          window.__go=(k)=>{const AI=__G.stlAI,e=__G.boss,W=__G.STLW;__G.stlWipe();__G.STLW.fx=[];__G.stlAI=null;
            const A=__G.stlAI||AI;e.invul=false;e.tele=[];e.expT=0;for(const c in A.cd)A.cd[c]=99;A.cd[k]=0;A.ordT=[k];A.ci=0;A.feedC=null;A.fed=0;A.chase(0);e.stT=0}}""")
        R = {}
        R['A'] = await ev(pg, """()=>{const G=__G,o={};o.t34=G.pickBossK(34);
          G.SAVE.diff.max=34;G.SAVE.diff.sel=0;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;__lv(28);P.tier=34;P.fset='dosan';P.bossK='stl';G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)__tk();const bo=G.boss;o.bk=bo&&bo.bk;o.hp=Math.round(bo.max);o.ph=bo.ph;
          const seen={},sts=[];let last='',out=0;
          for(let i=0;i<30*90;i++){P.hp=P.max;P.inv=1;const a=i/30;P.x=2100+Math.cos(a*0.6)*380;P.y=1727+Math.sin(a*0.6)*280;bo.hp=Math.max(bo.max*0.75,Math.min(bo.hp,bo.max*0.95));__tk();const e=G.boss;if(!e)break;if(!G.inPoly(e.x,e.y))out++;if(e.st!==last){last=e.st;seen[e.st]=(seen[e.st]||0)+1;sts.push(e.st)}}
          o.seen=seen;o.seq=sts.slice(0,24).join('>');o.bossOut=out;o.stk=bo.stk;o.eat=bo.eat;return o}""")
        await pg.screenshot(path=B + 'stl_p1.png')

        # 철 덩어리: 멀면 안 부서지고 가까우면 부서진다 · 1페이즈 12초 방치 → 흡수(중첩 +1)
        R['chunk'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};__cl();e.hp=e.max*0.9;e.stk=0;e.eat=0;e.stkT=99;const cx=2100,cy=1727;e.x=cx;e.y=cy-500;
          const A=G.stlAI;for(const k in A.cd)A.cd[k]=99;const c=new G.IronChunk(cx+300,cy+200,1000);c.fall=0;c.invul=false;G.STLW.chunks.push(c);G.enemies.push(c);
          P.x=cx-300;P.y=cy+200;G.hurtEnemy(c,500,0,0,0,false);o.far=c.hp;P.x=cx+150;G.hurtEnemy(c,500,0,0,0,false);o.near=c.hp;
          const c2=new G.IronChunk(cx-300,cy+200,1e9);c2.fall=0;c2.invul=false;G.STLW.chunks.push(c2);G.enemies.push(c2);
          for(let i=0;i<30*14;i++){P.inv=1;P.x=cx;P.y=cy+300;e.x=cx;e.y=cy-500;e.st=e.st==='chase'?'chase':e.st;__tk()}o.stkAfterAbs=e.stk;o.left=G.STLW.chunks.filter(q=>q.hp>0).length;return o}""")
        # 기둥: 품 안은 안전 · 바깥은 맞음 / 부수면 마왕 체력 -5% + 기절 / 못 부수면 삼킨다
        R['pillar'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const cx=2100,cy=1727;
          const run=(dist)=>{__cl();e.hp=e.max*0.9;e.stk=0;e.x=cx;e.y=cy;P.x=cx+dist;P.y=cy;const A=G.stlAI;G.stlWipe();G.updateStlFx&&0;e.tele=[];for(const k in A.cd)A.cd[k]=99;A.cd.pillar=0;A.ordT=['pillar'];A.ci=0;A.chase(0);e.stT=0;
            let hit=0;for(let i=0;i<30*6;i++){P.inv=0;P.x=cx+dist;P.y=cy;e.x=cx;e.y=cy;const b=P.hp;__tk();if(P.hp<b)hit++}return hit};
          o.inside=run(165);o.outside=run(330);
          __cl();const A=G.stlAI;const p=G.STLW.pillar;o.hasP=!!p;e.hp=e.max*0.9;const h0=e.hp;P.x=p.x+40;P.y=p.y;p.invul=false;G.hurtEnemy(p,p.max+10,0,0,0,false);for(let i=0;i<3;i++){P.inv=1;__tk()}
          o.bossLost=+((h0-e.hp)/e.max).toFixed(3);o.stun=e.st;
          for(let i=0;i<30*3;i++){P.inv=1;__tk()}e.stk=0;for(const k in A.cd)A.cd[k]=99;A.cd.pillar=0;A.ordT=['pillar'];A.ci=0;A.chase(0);e.stT=0;
          for(let i=0;i<30*17;i++){P.inv=1;P.x=cx+80;P.y=cy;__tk()}o.ateStk=e.stk;o.pGone=!G.STLW.pillar;return o}""")
        # 강타: 원 가운데에서 이속 200으로 벗어나면 안 맞음 (중첩 0과 8 모두)
        R['slam'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const cx=2100,cy=1727;
          const run=(stk,mv)=>{__cl();G.stlWipe();e.hp=e.max*0.9;e.stk=stk;e.stkT=99;e.x=cx-130;e.y=cy;P.x=cx;P.y=cy;const A=G.stlAI;e.tele=[];for(const k in A.cd)A.cd[k]=99;A.cd.slam=0;A.ordT=['slam'];A.ci=0;A.chase(0);e.stT=0;
            let hit=0;for(let i=0;i<30*4;i++){P.inv=0;e.x=cx-130;e.y=cy;if(mv&&e.tele.length)P.x+=200/30;const b=P.hp;__tk();if(P.hp<b)hit++}return hit};
          o.stand0=run(0,false);o.run0=run(0,true);o.stand8=run(8,false);o.run8=run(8,true);return o}""")
        # 2페이즈 포식: 흡수 중 부수면 약점 노출(+35%) / 내버려 두면 삼킴(+1) → 2개 먹은 뒤 남은 철 자력 폭주
        R['feed'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const cx=2100,cy=1727;__cl();G.stlWipe();e.hp=e.max*0.6;e.ph=2;e.stk=0;e.eat=0;e.stkT=99;e.x=cx;e.y=cy-300;P.x=cx;P.y=cy+300;
          const A=G.stlAI;e.tele=[];for(const k in A.cd)A.cd[k]=99;A.cd.rain=0;A.ordT=['rain'];A.ci=0;A.chase(0);e.stT=0;
          let sts=[];for(let i=0;i<30*12&&e.st!=='feed';i++){P.inv=1;__tk();if(sts[sts.length-1]!==e.st)sts.push(e.st)}o.n=G.STLW.chunks.length;o.toFeed=sts.join('>');
          const c=A.feedC;P.x=c.x+60;P.y=c.y;c.hp=1;G.hurtEnemy(c,999,0,0,0,false);__tk();o.expose=e.st;o.expT=+e.expT.toFixed(1);
          const h0=e.hp;G.hurtEnemy(e,1000,0,0,0,false);o.mul=+((h0-e.hp)/1000).toFixed(2);
          for(let i=0;i<30*30;i++){P.inv=1;P.x=cx+800;P.y=cy+500;__tk();if(sts[sts.length-1]!==e.st)sts.push(e.st)}o.stk=e.stk;o.eat=e.eat;o.left=G.STLW.chunks.length;o.seq=sts.slice(0,20).join('>');return o}""")
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,A=G.stlAI;G.stlWipe();e.ph=2;e.hp=e.max*0.6;e.stk=3;e.x=2100;e.y=1500;e.tele=[];for(const k in A.cd)A.cd[k]=99;A.cd.rain=0;A.ordT=['rain'];A.ci=0;A.chase(0);e.stT=0;P.x=2100;P.y=1800;
          for(let i=0;i<30*12&&!(e.st==='feed'&&e.anT>1.2);i++){P.inv=1;P.x=2100;P.y=1800;__tk()}}""")
        await pg.screenshot(path=B + 'stl_feed.png')
        # 자력 폭주: 남은 철 2.2초 뒤 폭발 (반경 안이면 맞음 · 밖이면 안 맞음)
        R['magnet'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const cx=2100,cy=1727;const run=(away)=>{__cl();G.stlWipe();e.hp=e.max*0.6;e.ph=2;e.stk=8;e.x=cx;e.y=cy-500;
            const c=new G.IronChunk(cx,cy+100,1e9);c.fall=0;c.invul=false;G.STLW.chunks.push(c);G.enemies.push(c);c.magnet();P.x=cx+60;P.y=cy+100;let hit=0;
            for(let i=0;i<30*3;i++){P.inv=0;e.x=cx;e.y=cy-500;if(away)P.x=Math.min(cx+700,P.x+160/30);const b=P.hp;__tk();if(P.hp<b)hit++}return hit};o.stay=run(false);o.away=run(true);return o}""")
        # 3페이즈: 변신 → 마디 3 · 몸통 맞으면 마왕에게 60% · 쇄도(옆으로 비키기) · 브레스(뒤로 빠지기)
        R['ph3'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const cx=2100,cy=1727;__cl();G.stlWipe();e.ph=2;e.st='chase';e.stT=0;e.hp=e.max*0.24;e.x=cx;e.y=cy-200;P.x=cx;P.y=cy+300;
          for(let i=0;i<30*3.5;i++){P.inv=1;__tk()}o.ph=e.ph;o.st=e.st;o.nodes=G.STLW.nodes.length;o.px=G.enemies.filter(q=>q.kind==='stlb'&&q.hp>0).length;
          const nb=G.enemies.find(q=>q.kind==='stlb'&&q.i===2);e.invul=false;const h0=e.hp;G.hurtEnemy(nb,1000,0,0,0,false);o.bodyK=+((h0-e.hp)/1000).toFixed(2);
          const A=G.stlAI;const run=(k,mode)=>{__cl();e.hp=e.max*0.2;e.x=cx-400;e.y=cy;A.chain(true);P.x=cx+150;P.y=cy;e.tele=[];G.STLW.trail=[];for(const q in A.cd)A.cd[q]=99;A.cd[k]=0;A.ordT=[k];A.ci=0;A.chase(0);e.stT=0;
            let hit=0;for(let i=0;i<30*5;i++){P.inv=0;if(mode==='side'&&(e.st==='dashw'||e.st==='dash')){const D=A.ds;if(D){let best=1e9,bp=null;for(const p of D.pts){const d=Math.hypot(P.x-p[0],P.y-p[1]);if(d<best){best=d;bp=p}}if(best<140){const a=Math.atan2(P.y-bp[1],P.x-bp[0]);P.x+=Math.cos(a)*250/30;P.y+=Math.sin(a)*250/30}}}
              if(mode==='back'&&e.st==='breath')P.y=Math.max(cy-700,P.y-220/30);const b=P.hp;__tk();if(P.hp<b){hit++;(window.__hl=window.__hl||[]).push(k+':'+e.st+':'+Math.round(P.x-e.x)+':'+(A.br?A.br.t.toFixed(2):''))}if(e.st==='chase'&&i>20)break}return hit};
          o.dashStand=run('dash','stand');o.dashSide=run('dash','side');o.brStand=run('breath','stand');o.brBack=run('breath','back');o.hl=(window.__hl||[]).slice(-6);return o}""")
        await pg.evaluate("()=>{const G=__G,P=G.P,e=G.boss,A=G.stlAI;e.hp=e.max*0.2;A.chain(true);for(const q in A.cd)A.cd[q]=99;A.cd.breath=0;A.ordT=['breath'];A.ci=0;A.chase(0);e.stT=0;e.x=1800;e.y=1700;A.chain(true);P.x=2200;P.y=1750;for(let i=0;i<45;i++){P.inv=1;__tk()}}")
        await pg.screenshot(path=B + 'stl_breath.png')
        await pg.evaluate("()=>{const G=__G,P=G.P,e=G.boss,A=G.stlAI;for(const q in A.cd)A.cd[q]=99;A.cd.dash=0;A.ordT=['dash'];A.ci=0;A.chase(0);e.stT=0;e.x=1700;e.y=1700;A.chain(true);P.x=2200;P.y=1750;for(let i=0;i<40;i++){P.inv=1;__tk()}}")
        await pg.screenshot(path=B + 'stl_dash.png')
        R['end'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss;__cl();P.x=e.x+200;P.y=e.y+200;const k0=(G.SAVE.dex.kills.boss23||0);e.hp=1;e.invul=false;G.hurtEnemy(e,99999,0,0,0,false);for(let i=0;i<30;i++){P.inv=1;__tk()}window.__k0=k0;return 1}""")
        await pg.screenshot(path=B + 'stl_death.png')
        R['end'] = await ev(pg, """()=>{const G=__G;return {kills:(G.SAVE.dex.kills.boss23||0)-__k0,death:!!G.STLW.death,left:G.enemies.filter(q=>q.kind==='stlc'||q.kind==='stlb'||q.kind==='stlp').length}}""")
        print(json.dumps(R, ensure_ascii=False, indent=1)); print('errs', errs[:8])
        await b.close()
asyncio.run(main())
