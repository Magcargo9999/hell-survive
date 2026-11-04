"""v10.25 8지옥 타르타로스(지하 36~40층) 필드 + 1보스 타르타로스의 티탄
 층·지옥 탭 · 필드 바닥/소품 · 봉인 함정(족쇄) · 낙석 · 티탄 순환 · 중력의 틈(투사체 소멸) · 대지 강타(통로 안전 · 초중력) · 형틀의 사슬(주무기 봉인)
 · 30% 대차륜(바위 파괴 → 기절) · 처치 · 도감 · 스크린샷
사용: PYTHONPATH=tools GAME_URL=... python3 tools/tests/ttn1025.py   (스크린샷 build/ttn_*.png)"""
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
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000); await pg.wait_for_function("__G.imgReady(['arena','tmap','ttn','tfloor','tprops','tmob'])", timeout=120000, polling=1000)
        await pg.evaluate("""()=>{window.__cl=()=>{const P=__G.P;P.inv=0;P.shield=0;P.dodge=0;P.pals=[];P.up.guard=0;P.rel.mirror=0;P.armor=1;P.taken=1;P.stunT=0;P.slowT=0;P.max=1e7;P.hp=P.max;P.hgT=0;P.hgImm=0;P.sealT=0;P.sealImm=0};
          window.__tk=()=>{const G=__G;G.tick(1/30);if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s()}}""")
        R = {}
        R['floor'] = await ev(pg, """()=>{const G=__G,o={};o.set=[34,35,39].map(t=>G.floorSet(t));o.open=G.OPEN_TIER;o.top=G.TOP_TIER;o.boss=[35,36,37,38,39].map(t=>G.pickBossK(t));
          G.SAVE.diff.max=38;G.SAVE.diff.sel=35;G.SAVE.shards=1e7;G.startGame('archer');return o}""")
        for i in range(40):
            st = await ev(pg, "()=>__G.state+'|'+(__G.P&&__G.P.fset)")
            if st.startswith('play'): break
            await asyncio.sleep(0.5)
        R['field'] = await ev(pg, """()=>{const G=__G,P=G.P,o={};o.fset=P.fset;o.tier=P.tier;__lv(12);__cl();
          for(let i=0;i<30*3;i++){P.inv=1;__tk()}o.mobs=G.enemies.filter(e=>e.kind==='mob').length;
          // 족쇄: 함정 칸 찾기
          let f=null;for(let r=3;r<80&&!f;r++)for(let a=0;a<64&&!f;a++){const tx=Math.round(Math.cos(a/10)*r),ty=Math.round(Math.sin(a/10)*r);if(G.isLava(tx,ty))f=[tx,ty]}
          o.trap=f;P.x=f[0]*64+32;P.y=f[1]*64+32;const hp0=P.hp;__tk();o.chain=+P.chainT.toFixed(2);P.x+=600;__tk();o.pulled=Math.round(Math.hypot(P.x-P.chainX,P.y-P.chainY));o.lavaDm=hp0-P.hp;
          for(let i=0;i<30*4;i++){P.inv=1;__tk()}o.freed=P.chainT;o.imm=+P.chainImm.toFixed(1);
          // 낙석: 다음 낙석을 바로 — 서 있으면 맞고, 다른 바위들은 피함
          G.TARW.rocks=[];G.TARW.next=0;P.chainT=0;P.chainImm=9;P.vx=0;P.vy=0;__cl();P.chainImm=9;const b=P.hp;for(let i=0;i<30*1.6;i++){P.vx=0;P.vy=0;__tk()}o.rockHitPct=+((b-P.hp)/P.max*100).toFixed(1);
          return o}""")
        await pg.evaluate("""()=>{const G=__G,P=G.P;__cl();G.TARW.rocks=[];G.TARW.next=0;P.chainImm=0;let f=null;for(let r=3;r<80&&!f;r++)for(let a=0;a<64&&!f;a++){const tx=Math.round(Math.cos(a/10)*r),ty=Math.round(Math.sin(a/10)*r);if(G.isLava(tx,ty))f=[tx,ty]}
          P.x=f[0]*64+32;P.y=f[1]*64+32;for(let i=0;i<30;i++){P.inv=1;__tk()}}""")
        await pg.screenshot(path=B + 'ttn_field.png')
        R['A'] = await ev(pg, """()=>{const G=__G,P=G.P,o={};__lv(28);P.bossK='ttn';G.raiseCastle();G.enterArena();return 1}""")
        await asyncio.sleep(2.5)
        R['B'] = await ev(pg, """()=>{const G=__G,P=G.P,o={};for(let i=0;i<40;i++)__tk();const bo=G.boss;o.bk=bo&&bo.bk;o.arenaTar=!!(G.arena&&G.arena.tar);o.img=G.IMAP.img;
          const seen={},sts=[];let last='',out=0;
          for(let i=0;i<30*80;i++){__cl();P.inv=1;const a=i/30;P.x=1216+Math.cos(a*0.6)*480;P.y=1520+Math.sin(a*0.6)*330;bo.hp=Math.max(bo.max*0.5,bo.hp);__tk();const e=G.boss;if(!e)break;if(!G.inPoly(e.x,e.y))out++;if(e.st!==last){last=e.st;seen[e.st]=(seen[e.st]||0)+1;sts.push(e.st)}}
          o.seen=seen;o.seq=sts.slice(0,24).join('>');o.bossOut=out;return o}""")
        await pg.screenshot(path=B + 'ttn_p1.png')
        S = """const G=__G,P=G.P,e=G.boss,A=G.ttn,o={};const cx=1216,cy=1520;const go=(k)=>{__cl();G.ttnClear&&0;G.TTW.rifts=[];G.TTW.wave=null;G.TTW.seal=null;e.tele=[];e.invul=false;for(const c in A.cd)A.cd[c]=99;A.cd[k]=0;A.ci=A.order().indexOf(k);A.chase(0);e.stT=0;};"""
        R['rift'] = await ev(pg, "()=>{" + S + """e.x=cx;e.y=cy-200;P.x=cx;P.y=cy+300;go('whip');let hit=0;for(let i=0;i<30*2;i++){P.inv=0;e.x=cx;e.y=cy-200;const b=P.hp;__tk();if(P.hp<b)hit++}
          o.inFanHit=hit;o.rifts=G.TTW.rifts.length;const R0=G.TTW.rifts[0];o.pts=R0&&R0.pts.length;
          const p=R0.pts[(R0.pts.length/2)|0];G.shards.push({x:p[0],y:p[1]+4,vx:0,vy:0,life:2,pierce:1,hit:new Set(),sz:1,kb:0});const n0=G.shards.length;__tk();o.shardEaten=n0-G.shards.length;
          for(let i=0;i<30*5.5;i++){P.inv=1;__tk()}o.riftsLeft=G.TTW.rifts.length;return o}""")
        R['smash'] = await ev(pg, "()=>{" + S + """const run=(mode)=>{go('smash');e.x=cx;e.y=cy-250;P.x=cx;P.y=cy+250;let gapPos=null;
            for(let i=0;i<30*4;i++){P.inv=mode==='inv'?1:0;e.x=cx;e.y=cy-250;const W=G.TTW.wave;if(W&&mode==='gap'&&!gapPos){const g=W.gaps[0];gapPos=[W.x+Math.cos(g)*450,W.y+Math.sin(g)*450]}
              if(gapPos){P.x=gapPos[0];P.y=gapPos[1]}if(mode==='gap'&&!gapPos){}__tk()}return [+(P.hgT||0).toFixed(2),+(P.hgImm||0).toFixed(1)]};
          o.stand=run('stand');P.hgT=0;P.hgImm=0;o.gap=run('gap');P.hgT=0;P.hgImm=0;o.inv=run('inv');
          // 초중력 중 이속 · 이동기 봉인
          P.hgT=3;P.hgImm=7;const x0=P.x;for(let i=0;i<30;i++){__tk()}o.hgSkill=G.TTN_MOVE?1:0;o.hgSpdMul=G.TTN.hgMul;return o}""")
        R['seal'] = await ev(pg, "()=>{" + S + """G.DMETER.basic=1000;G.DMETER['sk:x']=10;e.x=cx;e.y=cy-250;P.x=cx;P.y=cy+150;go('seal');for(let i=0;i<30*2;i++){P.inv=0;e.x=cx;e.y=cy-250;P.x=cx;P.y=cy+150;__tk()}o.k=P.sealK;o.t=+P.sealT.toFixed(1);
          P.sealT=0;P.sealImm=0;G.DMETER.basic=1;G.DMETER['sk:x']=1e6;go('seal');for(let i=0;i<30*2;i++){P.inv=0;e.x=cx;e.y=cy-250;P.x=cx;P.y=cy+150;__tk()}o.k2=P.sealK;
          P.sealT=0;P.sealImm=0;P.x=cx;P.y=cy+150;go('seal');for(let i=0;i<30*2;i++){P.inv=0;e.x=cx;e.y=cy-250;P.x=i<6?cx:cx+300;P.y=cy+150;__tk()}o.dodged=P.sealT;delete G.DMETER['sk:x'];return o}""")
        await pg.evaluate("()=>{" + S + """e.x=cx;e.y=cy-150;P.x=cx+60;P.y=cy+320;go('smash');for(let i=0;i<Math.round(30*1.9);i++){P.inv=1;e.x=cx;e.y=cy-150;__tk()}}""")
        await pg.screenshot(path=B + 'ttn_smash.png')
        R['flail'] = await ev(pg, "()=>{" + S + """__cl();e.x=cx;e.y=cy;P.x=cx;P.y=cy+620;e.hp=e.max*0.29;for(let i=0;i<30*3.2;i++){P.inv=1;e.x=cx;e.y=cy;__tk()}o.ph=e.ph;o.rocks=G.TTW.rocks.length;
          let hitFar=0;for(let i=0;i<30*8;i++){__cl();P.x=cx+560;P.y=cy;e.x=cx;e.y=cy;for(const c in A.cd)A.cd[c]=99;e.stT=9;const b=P.hp;__tk();if(P.hp<b)hitFar++}o.farHits=hitFar;
          let hitRing=0;for(let i=0;i<30*8;i++){__cl();P.x=cx+300;P.y=cy;e.x=cx;e.y=cy;for(const c in A.cd)A.cd[c]=99;e.stT=9;const b=P.hp;__tk();if(P.hp<b)hitRing++}o.ringHits=hitRing;
          for(const r of G.TTW.rocks.slice()){r.invul=false;r.rise=0;G.hurtEnemy(r,r.max+10,0,0,0,false)}__tk();o.left=G.TTW.rocks.length;o.st=e.st;o.re=+G.TTW.rkRe.toFixed(1);
          for(let i=0;i<30*19;i++){P.inv=1;P.x=cx+700;P.y=cy;__tk()}o.reRocks=G.TTW.rocks.length;return o}""")
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss;for(let i=0;i<30*1;i++){P.inv=1;P.x=1216+520;P.y=1520+120;__tk()}}""")
        await pg.screenshot(path=B + 'ttn_flail.png')
        R['kill'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const k0=G.SAVE.dex.kills.boss24||0;e.invul=false;G.hurtEnemy(e,e.max*2,0,0,0,false);for(let i=0;i<30*2;i++){P.inv=1;__tk()}o.kills=(G.SAVE.dex.kills.boss24||0)-k0;o.boss=!!G.boss&&G.boss.hp>0;o.rocks=G.TTW.rocks.length;return o}""")
        await asyncio.sleep(0.3)
        R['dex'] = await ev(pg, """()=>{const G=__G;G.openDex();const t=document.getElementById('dexList').textContent;return {ttn:t.includes('타르타로스의 티탄'),rock:t.includes('대차륜 바위')}}""")
        for k, v in R.items(): print(k, json.dumps(v, ensure_ascii=False))
        print('errors', errs[:6])
        await b.close()
asyncio.run(main())
