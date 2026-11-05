"""v10.30 ∞ 챌린지 대개편 흐름 테스트 (무한 맵 · 미니맵 · 스폰 풀 · 레벨 이벤트 · 맵 기믹 · 황금 도망자 · 잭팟 · 금제의 제단 · 콤보 피버 · 한계 돌파 · 룰렛 · 주사기)
사용: PYTHONPATH=tools GAME_URL=http://localhost:8765/build/hell_survive.html python3 tools/tests/ch1030.py"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
B = os.path.join(h301.ROOT, 'build', 'qa') + '/'
SETUP = """()=>{const G=__G,S=G.SAVE;S.ch.open=true;S.diff.max=39;S.diff.clr=38;S.shards=99999;for(const k of ['boss','boss2','boss4','boss6','boss14','boss19'])S.dex.kills[k]=1;S.rush.syr=0}"""
async def ev(pg, js, a=None):
    try: return await pg.evaluate(js, a)
    except Exception as ex: return 'ERR ' + str(ex).split('\n')[0][:300]
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 760); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await ev(pg, SETUP); R = {}
        await ev(pg, "()=>__G.startChallenge('wolf')")
        for i in range(160):
            if await ev(pg, "()=>__G.state==='play'&&!!__G.chal"): break
            await pg.wait_for_timeout(250)
        R['start'] = await ev(pg, "()=>{const G=__G,c=G.chal;return {sets:c.sets.join(','),pos:[G.P.x,G.P.y],sp:[G.species.length,G.mspecies.length,G.GSPECIES.length,G.sspecies.length,G.ISPECIES.length,G.FSPECIES.length,G.DSPECIES.length,G.TSPECIES.length]}}")
        # 스폰 풀: 시간을 넉넉히 → 여러 지옥 잡몹이 섞이는지
        R['pool'] = await ev(pg, """()=>{const G=__G;G.setT(400);const seen={};for(let i=0;i<300;i++){const L=G.chMobAvail();const k=L===G.species?'hell':L===G.mspecies?'mush':L===G.GSPECIES?'gard':L===G.sspecies?'sea':L===G.ISPECIES?'ice':L===G.FSPECIES?'fire':L===G.DSPECIES?'dosan':L===G.TSPECIES?'tar':'?';seen[k]=(seen[k]||0)+1}return seen}""")
        # 무한 맵: 멀리 걸어가도 막히지 않는다
        R['walk'] = await ev(pg, "()=>{const G=__G,P=G.P;P.x=9000;P.y=-7000;__run(30);return [Math.round(P.x),Math.round(P.y),Math.round(G.cam.x),Math.round(G.cam.y)]}")
        await ev(pg, "()=>{__run(90)}"); await pg.screenshot(path=B + 'ch_field.png')
        # Lv.5 미니 보스 · 특수 잡몹 부대
        R['lv5'] = await ev(pg, """()=>{const G=__G,c=G.chal;c.evCd=0;__lv(5);__run(5);const m=G.enemies.filter(e=>e.kind==='mini').map(e=>e.bk||'monkey');c.sqT=0;__run(5);const sq=G.enemies.filter(e=>e.csk).map(e=>e.csk);return {ev:!!c.ev,mini:m,sqOn:c.sqOn,squad:sq.length}}""")
        R['squad'] = await ev(pg, """()=>{const G=__G,c=G.chal,P=G.P;for(const e of G.enemies)if(e.csk){e.x=P.x+200;e.y=P.y}let tele=0,boom=0;for(let i=0;i<150;i++){P.inv=0;P.hp=P.max;G.tick(1/30);tele=Math.max(tele,c.tele.length)}return {tele}}""")
        R['lv20'] = await ev(pg, """()=>{const G=__G,c=G.chal,P=G.P;for(const e of G.enemies)if(e.kind==='mini')G.hurtEnemy(e,1e9,0,0,0,true);__run(60);c.evCd=0;__lv(10);__run(5);const f1=c.fires.length;
           c.ev=null;for(const e of G.enemies)if(e.kind==='mini')e.hp=0;c.evCd=0;__lv(15);__run(160);const sp=c.spikes.length;c.ev=null;for(const e of G.enemies)if(e.kind==='mini')e.hp=0;c.evCd=0;
           __lv(20);__run(3);return {lvl:P.lvl,fires:f1,fires2:c.fires.length,spikes:sp,siren:+c.siren.toFixed(2),bossK:c.bossK,o2:c.o2Seen,next:c.next}}""")
        await ev(pg, "()=>{__G.chal.siren=Math.max(__G.chal.siren,1.5);for(let i=0;i<8;i++){__G.P.inv=99;__G.tick(1/30)}}"); await pg.screenshot(path=B + 'ch_siren.png')
        R['boss'] = await ev(pg, """async()=>{const G=__G,c=G.chal,P=G.P;for(let i=0;i<300&&(!G.boss||G.boss.hp<=0);i++){P.inv=99;P.hp=P.max;c.waitB=0;G.tick(1/30);if(i%10===0)await new Promise(r=>setTimeout(r,40))}
          const B=G.boss;if(!B)return 'no boss';__run(60);return {bk:B.bk||'monkey',d:Math.round(Math.hypot(B.x-P.x,B.y-P.y)),hp:Math.round(B.max),fb:!!c.fbC,o2:Math.round(P.o2),gey:c.gey.length}}""")
        await pg.screenshot(path=B + 'ch_boss.png')
        R['bossWin'] = await ev(pg, """()=>{const G=__G,c=G.chal,P=G.P,B=G.boss;B.invul=false;B.st='chase';G.hurtEnemy(B,B.hp+1e9,0,0,0,false);for(let i=0;i<200&&G.state==='play';i++){P.inv=99;G.tick(1/30)}
          let t=document.getElementById('levelTitle').textContent;if(t.indexOf('보물')>=0){G.pick(0);for(let i=0;i<40&&G.state==='play';i++){P.inv=99;G.tick(1/30)}t=document.getElementById('levelTitle').textContent}
          return {state:G.state,title:t,cards:[...document.querySelectorAll('#cards .card strong')].map(x=>x.textContent),bossN:c.bossN,coins:c.loot.filter(o=>o.k==='coin').length}}""")
        await pg.screenshot(path=B + 'ch_reward.png')
        R['roul'] = await ev(pg, """async()=>{const G=__G,c=G.chal;let g=0;while(G.state==='levelup'&&g++<20){const t=document.getElementById('levelTitle').textContent;G.pick(t.indexOf('마왕 처치')>=0?1:0);for(let i=0;i<90&&G.state==='play';i++){G.P.inv=99;G.tick(1/30)}}const s0=G.state;G.roulSpin();for(let i=0;i<120;i++){G.tick(1/30)}const res=document.getElementById('rouRes').innerText;return {s0,state:G.state,res:res.slice(0,60)}}""")
        await pg.screenshot(path=B + 'ch_roul.png')
        await ev(pg, "()=>{document.getElementById('rouBtn').click();let g=0;while(__s()&&g++<20);}")
        # 황금 도망자 · 잭팟
        R['gold'] = await ev(pg, """()=>{const G=__G,c=G.chal,P=G.P;while(__s());for(const e of G.enemies)if(e.kind==='boss')e.hp=0;G.chGoldSpawn();const e=c.gold;e.x=P.x+250;e.y=P.y;
          for(let i=0;i<20;i++){G.hurtEnemy(e,1,0,0,0,true);for(let k=0;k<8;k++){P.inv=99;G.tick(1/30)}}
          return {coins:c.loot.length,slime:c.slime.length,traps:c.traps.length,hp:Math.round(e.hp),face:e.face}}""")
        await ev(pg, "()=>{const G=__G;while(__s());G.cam.x=G.chal.gold.x-150;G.cam.y=G.chal.gold.y-30}"); await pg.screenshot(path=B + 'ch_gold.png')
        R['jack'] = await ev(pg, """()=>{const G=__G,c=G.chal,P=G.P;while(__s());for(let i=0;i<40;i++)G.spawnEnemy(Math.random()*6.28,300);const n0=G.enemies.filter(e=>e.kind==='mob'&&e.hp>0).length;G.CH.jackP=1;const e=c.gold;G.hurtEnemy(e,e.hp+10,0,0,0,true);G.CH.jackP=0.06;
          for(let i=0;i<10;i++){P.inv=99;G.tick(1/30)}const n1=G.enemies.filter(e=>e.kind==='mob'&&e.hp>0&&Math.abs(e.x-P.x)<G.W/2&&Math.abs(e.y-P.y)<G.H/2).length;return {n0,n1,cards:c.loot.filter(o=>o.k==='card').length,jack:c.jackN,gdeath:!!c.gdeath}}""")
        await pg.screenshot(path=B + 'ch_jack.png')
        R['cardPick'] = await ev(pg, """()=>{const G=__G,c=G.chal,P=G.P;for(let i=0;i<200;i++){P.inv=99;const L=c.loot.find(o=>o.k==='card');if(L&&G.state==='play'){P.x=L.x;P.y=L.y+10}if(G.state==='levelup'){G.pick(0);continue}G.tick(1/30)}return {left:c.loot.filter(o=>o.k==='card').length,cardQ:c.cardQ,state:G.state}}""")
        # 금제의 제단
        R['altar'] = await ev(pg, """()=>{const G=__G,c=G.chal,P=G.P;c.pact=null;c.altar=null;c.altarT=0;c.bossOn=false;c.siren=0;__run(2);const A=c.altar;if(!A)return 'no altar';P.x=A.x;P.y=A.y;for(let i=0;i<60&&G.state==='play';i++){G.tick(1/30);P.x=A.x;P.y=A.y}
          return {state:G.state,cards:[...document.querySelectorAll('#cards .card strong')].map(x=>x.textContent)}}""")
        await pg.screenshot(path=B + 'ch_altar.png')
        R['glass'] = await ev(pg, """()=>{const G=__G,c=G.chal,P=G.P;G.pick(0);G.chPactEnd(false);while(__s());const d0=P.dmg;G.chPactStart(G.PACTS[1]);const m0=c.pact.max;const st={max:P.max,dmg3:+(P.dmg/d0).toFixed(2)};
          c.pact.t=c.pact.dur;P.inv=99;G.tick(1/30);return Object.assign(st,{after:P.max,m0,dmgK:+(P.dmg/d0).toFixed(2)})}""")
        R['rain'] = await ev(pg, """()=>{const G=__G,c=G.chal,P=G.P;while(__s());G.chPactStart(G.PACTS[0]);const e0=P.exp;let n=0;for(let i=0;i<60;i++){P.inv=99;P.hp=P.max;G.tick(1/30);n=Math.max(n,c.drops.length)}const lv=P.lvl;G.addExp(10);return {drops:n,expGain:+(P.exp-e0).toFixed(1)}}""")
        await pg.screenshot(path=B + 'ch_rain.png')
        await ev(pg, "()=>{const G=__G,c=G.chal;c.pact.t=c.pact.dur;G.tick(1/30);G.chPactStart(G.PACTS[2]);for(let i=0;i<20;i++){G.P.inv=99;G.tick(1/30)}}"); await pg.screenshot(path=B + 'ch_dark.png')
        await ev(pg, "()=>{const G=__G,c=G.chal;c.pact.t=c.pact.dur;G.tick(1/30)}")
        # 콤보 · 피버
        R['combo'] = await ev(pg, """()=>{const G=__G,c=G.chal,P=G.P;while(__s());c.combo=0;const sh0=c.sh;for(let i=0;i<130;i++){const e=G.spawnEnemy(0,200);G.hurtEnemy(e,1e9,0,0,0,true)}const st={combo:c.combo,fever:+c.fever.toFixed(1),feverN:c.feverN,shGain:c.sh-sh0};P.inv=0;P.shield=0;P.dodge=0;G.hurt(5);st.afterHit=c.combo;return st}""")
        await ev(pg, "()=>{const G=__G,c=G.chal;c.combo=150;c.fever=8;for(let i=0;i<10;i++){G.P.inv=99;G.tick(1/30)}}"); await pg.screenshot(path=B + 'ch_fever.png')
        # 한계 돌파
        R['cap'] = await ev(pg, """()=>{const G=__G,c=G.chal,P=G.P;G.setT(905);__run(2);const u=G.UPGRADES.find(u=>(u.max||5)>=3&&!u.rushOnly);return {cap:c.cap,max:G.cardMax(u),base:u.max||5,toggle:G.cardMax(G.UPGRADES.find(u=>(u.max||5)<3)||u)}}""")
        # 주사기
        R['syr'] = await ev(pg, """()=>{const G=__G,c=G.chal,P=G.P;while(__s());const s0=G.SAVE.rush.syr|0;G.chLoot('syr',P.x+30,P.y);for(let i=0;i<90;i++){P.inv=99;G.tick(1/30)}return {before:s0,after:G.SAVE.rush.syr,n:c.syrN}}""")
        # 죽음 → 결과
        R['over'] = await ev(pg, """async()=>{const G=__G,P=G.P;P.inv=0;P.shield=0;P.revived=true;P.reviveLeft=0;P.rel={};G.die();for(let i=0;i<120;i++){G.tick(1/30)}await new Promise(r=>setTimeout(r,500));return document.getElementById('overStats').innerText.slice(-260)}""")
        await pg.screenshot(path=B + 'ch_over.png')
        for k, v in R.items(): print(k, json.dumps(v, ensure_ascii=False)[:500])
        print('errors', errs[:8]); await b.close()
asyncio.run(main())
