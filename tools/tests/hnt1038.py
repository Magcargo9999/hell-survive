"""v10.38 지하 40층 최종 마왕 '암전의 사냥꾼'
 층 개방 · 어둠 레이어 · 그림자 피해 ×0.4 · 등불 켜기 · 순환 A→B→D→B→C · 매복 베기(피하기) · 사슬 낫(2페이즈 틈) · 올가미 함정(간격·속박·속박 중 무피해)
 · 소등 습격(등불 꺼짐·경직) · 40% 암전(시야 120 · 베기 3번 · 이속 150으로 피하기) · tierEx 멈춤 · 처치·도감·업적 · 스크린샷
사용: PYTHONPATH=tools GAME_URL=... python3 tools/tests/hnt1038.py   (스크린샷 build/hnt_*.png)"""
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
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000); await pg.wait_for_function("__G.imgReady(['arena','tmap','hnt','tfloor','tprops','tmob'])", timeout=120000, polling=1000)
        await pg.evaluate("""()=>{window.__cl=()=>{const P=__G.P;P.inv=0;P.shield=0;P.dodge=0;P.pals=[];P.up.guard=0;P.rel.mirror=0;P.armor=1;P.taken=1;P.stunT=0;P.slowT=0;P.max=1e7;P.hp=P.max;P.bindT=0;P.bindImm=0};
          window.__tk=()=>{const G=__G;G.tick(1/30);if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s()}}""")
        R = {}
        R['floor'] = await ev(pg, """()=>{const G=__G,o={};o.open=G.OPEN_TIER;o.top=G.TOP_TIER;o.set=G.floorSet(39);o.boss=[38,39].map(t=>G.pickBossK(t));o.fieldNo=G.CH_FIELD_NO;
          G.SAVE.diff.max=39;G.SAVE.diff.sel=39;G.SAVE.shards=1e7;G.startGame('archer');return o}""")
        for i in range(40):
            st = await ev(pg, "()=>__G.state")
            if st == 'play': break
            await asyncio.sleep(0.5)
        await ev(pg, """()=>{const G=__G,P=G.P;__lv(30);__cl();P.bossK='hnt';G.raiseCastle();G.enterArena();return 1}""")
        await asyncio.sleep(2.5)
        R['enter'] = await ev(pg, """()=>{const G=__G,P=G.P,o={};for(let i=0;i<10;i++)__tk();const e=G.boss;o.bk=e&&e.bk;o.lamps=G.HNW.lamps.length;o.lampIn=G.HNW.lamps.every(l=>G.inPoly(l.x,l.y));o.tier=P.tier;o.hpK=+(e.max/(G.BOSS_HP*(1+0.3*P.tier))).toFixed(2);o.gap=+G.hntGap().toFixed(2);return o}""")
        R['cycle'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};e.ex=[];const seen={},seq=[];let last='',out=0,hid=0,n=0;
          for(let i=0;i<30*60;i++){__cl();P.inv=1;const a=i/30;P.x=1216+Math.cos(a*0.5)*520;P.y=1540+Math.sin(a*0.5)*380;e.hp=Math.max(e.max*0.5,e.hp);__tk();if(!G.inPoly(e.x,e.y))out++;n++;if(G.hntHidden(e))hid++;
            if(e.st!==last){last=e.st;seen[e.st]=(seen[e.st]||0)+1;seq.push(e.st)}}
          o.seen=seen;o.seq=seq.slice(0,30).join('>');o.out=out;o.hiddenPct=Math.round(hid/n*100);return o}""")
        R['lampFight'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,W=G.HNW,o={};let hid=0,n=0,sn=0;   // 등불 두 개 곁에서 싸우면 얼마나 드러나나
          for(let i=0;i<30*60;i++){__cl();P.inv=1;const L=W.lamps[(Math.floor(i/(30*15)))%2?1:0],a=i/30;for(const l of W.lamps)if(l.on<=0&&l.cd<=0&&(l===W.lamps[0]||l===W.lamps[1]))G.hntLampOn(l);
            P.x=L.x+Math.cos(a*0.7)*170;P.y=L.y+Math.sin(a*0.7)*120;e.hp=Math.max(e.max*0.5,e.hp);__tk();n++;if(G.hntHidden(e))hid++;if(e.st==='snw')sn++}
          o.hiddenPct=Math.round(hid/n*100);o.snuff=sn>0;return o}""")
        await pg.screenshot(path=B + 'hnt_dark.png')
        S = """const G=__G,P=G.P,e=G.boss,A=G.hnt,H=G.HNT,W=G.HNW,o={};const cx=1216,cy=1540;const reset=()=>{__cl();e.ex=[];e.tele=[];W.lines=[];W.scy=[];W.traps=[];e.invul=false;for(const l of W.lamps){l.on=0;l.cd=0;l.prog=0}A.stalk(99);};"""
        R['shadow'] = await ev(pg, "()=>{" + S + """reset();e.x=cx;e.y=cy-500;P.x=cx;P.y=cy+100;const h0=e.hp;G.hurtEnemy(e,1000,0,0,0,true);o.hiddenDm=Math.round(h0-e.hp);
          const h1=e.hp;e.x=cx;e.y=cy;P.x=cx+150;P.y=cy;G.hurtEnemy(e,1000,0,0,0,true);o.seenDm=Math.round(h1-e.hp);
          // 등불: 곁에 1.1초 → 켜짐 → 빛 안 사냥꾼은 노출
          reset();const L=W.lamps[1];P.x=L.x+20;P.y=L.y;for(let i=0;i<34;i++){P.inv=1;P.x=L.x+20;P.y=L.y;__tk()}o.lit=+L.on.toFixed(1);
          P.x=L.x+900;P.y=L.y+300;if(!G.inPoly(P.x,P.y)){P.x=L.x+700;P.y=L.y+500}e.x=L.x+200;e.y=L.y+60;o.inLight=!G.hntHidden(e);
          const L2=W.lamps[2],L3=W.lamps[3];G.hntLampOn(L2);G.hntLampOn(L3);o.litN=W.lamps.filter(l=>l.on>0).length;o.oldOff=L.on<=0;return o}""")
        await ev(pg, "()=>{" + S + """reset();const L=W.lamps[0];G.hntLampOn(L);P.x=L.x+120;P.y=L.y+120;e.x=L.x+520;e.y=L.y-120;for(let i=0;i<20;i++){P.inv=1;P.x=L.x+120;P.y=L.y+120;A.stalk(99);__tk()}}""")
        await pg.screenshot(path=B + 'hnt_lamp.png')
        R['amb'] = await ev(pg, "()=>{" + S + """const run=(mode)=>{reset();e.x=cx;e.y=cy-500;P.x=cx;P.y=cy+60;A.ci=0;A.next();let hit=0,tel=0;
            for(let i=0;i<30*4;i++){P.inv=0;const t=e.tele.find(q=>q.k==='fan');if(t){tel=1;if(mode==='run'){const a=t.ang;P.x+=Math.cos(a)*150/30;P.y+=Math.sin(a)*150/30}}const b=P.hp;__tk();if(P.hp<b)hit++;if(e.st==='stalk')break}
            return {hit,tel,st:e.st}};o.stand=run('stand');o.run=run('run');return o}""")
        R['thw'] = await ev(pg, "()=>{" + S + """const run=(ph,dx)=>{reset();e.ph=ph;e.x=cx;e.y=cy-420;P.x=cx;P.y=cy;A.thwStart();const L=W.lines.map(q=>+q.a.toFixed(2));let hit=0;
            if(dx){const a=W.lines[0].a+G.HNT.thFan/2,d=420;P.x=e.x+Math.cos(a)*d;P.y=e.y+Math.sin(a)*d}
            for(let i=0;i<30*3;i++){P.inv=0;const b=P.hp;__tk();if(P.hp<b)hit++;if(e.st==='stalk')break}return {n:L.length,hit,st:e.st}};
          o.p1=run(1,0);o.p2=run(2,0);o.p2gap=run(2,1);e.ph=1;return o}""")
        await ev(pg, "()=>{" + S + """reset();e.ph=2;e.x=cx;e.y=cy-420;P.x=cx;P.y=cy;A.thwStart();for(let i=0;i<14;i++){P.inv=1;__tk()}}""")
        await pg.screenshot(path=B + 'hnt_scythe.png')
        R['snare'] = await ev(pg, "()=>{" + S + """reset();e.ph=1;e.x=cx;e.y=cy-500;P.x=cx;P.y=cy+80;A.snareStart();const T=W.traps;o.n=T.length;let mn=1e9,mp=1e9;
          for(let i=0;i<T.length;i++){mp=Math.min(mp,Math.hypot(T[i].x-P.x,T[i].y-P.y));for(let j=i+1;j<T.length;j++)mn=Math.min(mn,Math.hypot(T[i].x-T[j].x,T[i].y-T[j].y))}o.minGap=Math.round(mn);o.minP=Math.round(mp);
          o.pause=G.bossExPaused(e);for(let i=0;i<10;i++){P.inv=1;__tk()}
          const t=T[0];P.inv=0;P.x=t.x;P.y=t.y;const b=P.hp;__tk();o.bind=+P.bindT.toFixed(2);o.trapDm=b>P.hp;o.imm=+P.bindImm.toFixed(1);
          // 속박 중엔 사냥꾼 공격이 맞지 않는다
          e.x=P.x;e.y=P.y-100;e.tele=[];A.ambTele();let hit=0;for(let i=0;i<20;i++){const b2=P.hp;P.bindT=Math.max(P.bindT,0.5);__tk();if(P.hp<b2)hit++}o.boundHit=hit;
          for(let i=0;i<30*11;i++){P.inv=1;P.bindT=0;__tk()}o.left=W.traps.length;o.pauseAfter=G.bossExPaused(e)&&e.st!=='stalk';return o}""")
        await ev(pg, "()=>{" + S + """reset();e.x=cx;e.y=cy-500;P.x=cx;P.y=cy+80;A.snareStart();for(let i=0;i<30*1.5;i++){P.inv=1;P.x=cx;P.y=cy+80;A.stalk(99);__tk()}}""")
        await pg.screenshot(path=B + 'hnt_trap.png')
        R['snuff'] = await ev(pg, "()=>{" + S + """reset();o.noLamp=A.sfStart();const L=W.lamps[0];G.hntLampOn(L);e.x=L.x+500;e.y=L.y;P.x=L.x;P.y=L.y+20;o.go=A.sfStart();o.pause=G.bossExPaused(e);
          let hit=0,stun=0;for(let i=0;i<30*2.4;i++){P.inv=0;const b=P.hp;__tk();if(P.hp<b)hit++;if(e.st==='stun')stun++}o.hit=hit;o.lampOff=L.on<=0;o.stunT=+(stun/30).toFixed(2);
          // 피하기: 이속 150으로 바로 위로
          reset();G.hntLampOn(L);e.x=L.x+500;e.y=L.y;P.x=L.x;P.y=L.y+20;A.sfStart();hit=0;for(let i=0;i<30*2.4;i++){P.inv=0;P.y-=150/30;const b=P.hp;__tk();if(P.hp<b)hit++}o.dodgeHit=hit;
          // 경직 중엔 어둠 속이어도 그대로
          e.st='stun';e.x=cx;e.y=cy-600;P.x=cx;P.y=cy+300;o.stunHidden=G.hntHidden(e);A.stalk(99);return o}""")
        R['blk'] = await ev(pg, "()=>{" + S + """reset();const L=W.lamps[1];G.hntLampOn(L);A.snareStart();e.ph=1;e.x=cx;e.y=cy-400;P.x=cx;P.y=cy+100;e.hp=e.max*0.39;__tk();o.st=e.st;o.ph=e.ph;o.pause=G.bossExPaused(e);
          for(let i=0;i<30*2.1;i++){P.inv=1;__tk()}o.st2=e.st;o.lampsOff=W.lamps.every(l=>l.on<=0);o.traps=W.traps.length;
          let hit=0,sl=0,lastTele=0,dir=-1,mv=0,vmin=999;for(let i=0;i<30*6.2;i++){P.inv=0;const t=e.tele.find(q=>q.k==='circle');if(t){if(t!==lastTele){lastTele=t;sl++;dir=-dir}P.y+=dir*150/30}vmin=Math.min(vmin,W.view);const b=P.hp;__tk();if(P.hp<b)hit++}
          o.slashes=sl;o.dodgeHit=hit;o.viewMin=Math.round(vmin);for(let i=0;i<30*1.5;i++){P.inv=1;__tk()}o.after=e.st;o.view=Math.round(W.view);o.blkCd=+A.cd.blk.toFixed(1);
          // 서 있으면 맞는다
          reset();A.cd.blk=0;A.blkStart();for(let i=0;i<30*2.1;i++){P.inv=1;__tk()}hit=0;for(let i=0;i<30*6;i++){P.inv=0;const b=P.hp;__tk();if(P.hp<b)hit++}o.standHit=hit;return o}""")
        await ev(pg, "()=>{" + S + """reset();A.cd.blk=0;A.blkStart();for(let i=0;i<30*2.6;i++){P.inv=1;__tk()}}""")
        await pg.screenshot(path=B + 'hnt_blackout.png')
        R['kill'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const k0=G.SAVE.dex.kills.boss26||0;e.invul=false;e.st='stun';G.hurtEnemy(e,e.max*3,0,0,0,false);for(let i=0;i<30*2;i++){P.inv=1;__tk()}o.kills=(G.SAVE.dex.kills.boss26||0)-k0;o.boss=!!G.boss&&G.boss.hp>0;o.lampsOn=G.HNW.lamps.filter(l=>l.on>0).length;
          o.ach=['k_hnt','h8'].map(id=>G.ACH.some(a=>a.id===id));return o}""")
        await pg.screenshot(path=B + 'hnt_dead.png')
        await asyncio.sleep(0.3)
        R['dex'] = await ev(pg, """()=>{const G=__G;G.openDex();const t=document.getElementById('dexList').textContent;return {hnt:t.includes('암전의 사냥꾼')}}""")
        for k, v in R.items(): print(k, json.dumps(v, ensure_ascii=False))
        print('errors', errs[:6])
        await b.close()
asyncio.run(main())
