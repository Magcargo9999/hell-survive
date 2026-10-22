"""v8.20 이독버섯 마왕: 등장 확률 · 웅덩이(패시브) · 살점 투척+돌연변이 버섯 · 독 안개 디버프(이속·재생 -50% → 원상복구) · 독 역류 · 25% 붕괴(독 늪 + 핵심 포자 돌진) · 처치 · 안전 구역(규칙 9) · 스크린샷"""
import asyncio, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
from h301 import newpage
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
SETUP = "const G=__G;G.SAVE.shards=999999;G.SAVE.diff.max=14;G.SAVE.diff.sel=%d;G.startGame('wolf');const P=G.P;P.bossK='tox';__lv(20);G.raiseCastle();G.enterArena();for(let i=0;i<90;i++){P.inv=99;G.tick(1/30);}const b=G.boss;"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('window.__G && __G.IMG && __G.IMG.tox && __G.IMG.mmap', timeout=90000)
        R = {}
        R['prob'] = await pg.evaluate("""()=>{const G=__G,o={};for(const t of [6,7,8,9,12]){const c={};for(let i=0;i<4000;i++){const k=G.pickBossK(t);c[k]=(c[k]||0)+1;}o[(t+1)+'층']=Object.fromEntries(Object.entries(c).map(([k,v])=>[k,Math.round(v/40)]));}return o;}""")
        for tier in [7, 9]:
            R['fight%d' % tier] = await pg.evaluate("""()=>{""" + SETUP % tier + """
              const seen={}; let lost=0, pools=0, minis=0, fogSpd=1, fogReg=1, adds=0, swamp=0, coreR=0, dash=false, fl=0;
              const run=(n)=>{for(let i=0;i<n;i++){P.hp=P.max;const h0=P.hp;G.tick(1/30);if(G.state!=='play')__s();lost+=Math.max(0,h0-P.hp);if(b.st)seen[b.st]=1;
                pools=Math.max(pools,G.zones.filter(z=>z.type==='tpool').length);minis=Math.max(minis,G.enemies.filter(e=>e.kind==='toxm'&&e.hp>0).length);fl=Math.max(fl,G.toxFl.length);
                if(G.toxFog){fogSpd=Math.min(fogSpd,G.DEBUFF.mul('spd'));fogReg=Math.min(fogReg,G.DEBUFF.mul('regen'));adds=Math.max(adds,G.enemies.filter(e=>e.toxAdd&&e.hp>0).length);}
                if(b.st==='dash')dash=true;}};
              run(150);
              b.st='chase';b.stT=0;b.gasNext=false;run(120);
              b.st='chase';b.stT=0;b.gasNext=true;b.gasCd=0;run(260);
              const after=G.DEBUFF.mul('spd');
              b.hp=b.max*0.69;b.st='chase';run(90); const rf1=b.rf;
              b.hp=b.max*0.49;b.st='chase';run(90); const rage=b.rage;
              b.hp=b.max*0.24;run(120); swamp=G.zones.filter(z=>z.type==='tswamp').length; coreR=b.r;
              run(200);
              b.invul=false;b.hp=1;G.hurtEnemy(b,999,0,0,0);run(30);
              const T=150+120+260+90+90+120+200+30;
              return {tier:P.tier,fset:P.fset,states:Object.keys(seen),lostPerS:+(lost/(T/30)).toFixed(1),pools,minis,flying:fl,fogSpd,fogReg,afterFogSpd:after,fogAdds:adds,rf1,rage,swamp,coreR,dash,dead:!G.boss,
                left:G.zones.filter(z=>z.type==='tpool'||z.type==='tswamp').length+G.enemies.filter(e=>e.kind==='toxm'||e.toxAdd).length};}""")
        # 규칙 9: 웅덩이 최대 개수 + 독 늪이 있을 때 보스방 바닥 중 안전한 비율
        R['safe'] = await pg.evaluate("""()=>{""" + SETUP % 9 + """
            for(let i=0;i<600;i++){P.inv=99;P.hp=P.max;b.hp=Math.max(b.hp,b.max*0.8);G.tick(1/30);if(G.state!=='play')__s();}
            const pools=G.zones.filter(z=>z.type==='tpool').length; b.hp=b.max*0.24; for(let i=0;i<110;i++){P.inv=99;P.hp=P.max;G.tick(1/30);}
            const Z=G.zones.filter(z=>z.type==='tpool'||z.type==='tswamp');let inside=0,hit=0;
            for(let x=0;x<=G.MMAP.w;x+=20)for(let y=0;y<=G.MMAP.h;y+=20){if(!G.inPoly(x,y))continue;inside++;if(Z.some(z=>Math.hypot(x-z.x,(y-z.y)*1.5)<z.r*0.85+20))hit++;}
            return {pools,zones:Z.length,safeFloor:+(1-hit/inside).toFixed(2)};}""")
        # 스크린샷
        await pg.evaluate("""()=>{""" + SETUP % 7 + """b.x=P.x+60;b.y=P.y-300;for(let i=0;i<200;i++){P.inv=99;P.hp=P.max;G.tick(1/30);}b.st='chase';b.stT=0;b.gasNext=false;for(let i=0;i<40;i++){P.inv=99;G.tick(1/30);}G.render();}""")
        await pg.screenshot(path=os.path.join(OUT, 'tox_throw.png'))
        await pg.evaluate("""()=>{const G=__G,P=G.P,b=G.boss;for(let i=0;i<30;i++){P.inv=99;G.tick(1/30);}b.st='chase';b.stT=0;b.gasNext=true;b.gasCd=0;for(let i=0;i<120;i++){P.inv=99;P.hp=P.max;G.tick(1/30);}G.render();}""")
        await pg.screenshot(path=os.path.join(OUT, 'tox_fog.png'))
        await pg.evaluate("""()=>{const G=__G,P=G.P,b=G.boss;for(let i=0;i<200;i++){P.inv=99;P.hp=P.max;G.tick(1/30);}b.hp=b.max*0.24;for(let i=0;i<50;i++){P.inv=99;G.tick(1/30);}G.render();}""")
        await pg.screenshot(path=os.path.join(OUT, 'tox_collapse.png'))
        await pg.evaluate("""()=>{const G=__G,P=G.P,b=G.boss;for(let i=0;i<120;i++){P.inv=99;P.hp=P.max;G.tick(1/30);if(b.st==='aim')break;}G.render();}""")
        await pg.screenshot(path=os.path.join(OUT, 'tox_core.png'))
        print(json.dumps(R, ensure_ascii=False, indent=1)); print('errs', pg.errs); await b.close()
asyncio.run(main())
