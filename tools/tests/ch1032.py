"""v10.32 챌린지: Lv.20+ 5레벨마다 마왕 · 산소 게이지 · 피버/수정 효과 · 특수 잡몹 도트 · 룰렛 도트 · 업적 · 입장 창
사용: PYTHONPATH=tools GAME_URL=http://localhost:8765/build/hell_survive.html python3 tools/tests/ch1032.py"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
B = os.path.join(h301.ROOT, 'build', 'qa') + '/'
SETUP = """()=>{const G=__G,S=G.SAVE;S.ch.open=true;S.diff.max=39;S.diff.clr=38;S.shards=99999;for(const k of ['boss','boss2','boss4','boss6','boss14','boss19','boss21'])S.dex.kills[k]=1;S.rush.syr=0}"""
async def ev(pg, js, a=None):
    try: return await pg.evaluate(js, a)
    except Exception as ex: return 'ERR ' + str(ex).split('\n')[0][:300]
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 760); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await ev(pg, SETUP); R = {}
        # 입장 창
        await ev(pg, "()=>{document.getElementById('chBtn').click()}"); await pg.wait_for_timeout(500)
        R['menu'] = await ev(pg, "()=>({open:document.getElementById('chBox').classList.contains('show'),state:__G.state,txt:document.getElementById('chWin').innerText.slice(0,90).replace(/\\n/g,' | ')})")
        await pg.screenshot(path=B + 'ch32_menu.png')
        await ev(pg, "()=>{__G.SAVE.ch.best=1260;__G.SAVE.ch.bestCombo=387;__G.SAVE.ch.bestLv=28;__G.SAVE.ch.bossBest=2;__G.SAVE.ch.bossTot=4;__G.SAVE.ch.feverTot=12;__G.SAVE.ch.jackTot=1;__G.SAVE.ch.runs=7;__G.SAVE.ch.tr.rat=true;document.getElementById('chBtn').click()}"); await pg.wait_for_timeout(400)
        await pg.screenshot(path=B + 'ch32_menu2.png')
        await ev(pg, "()=>{document.getElementById('chGo').click()}")
        for i in range(160):
            if await ev(pg, "()=>__G.state==='play'&&!!__G.chal"): break
            await pg.wait_for_timeout(250)
        R['start'] = await ev(pg, "()=>({chal:!!__G.chal,box:document.getElementById('chBox').classList.contains('show'),runs:__G.SAVE.ch.runs})")
        # 마왕 5레벨마다: 미니 보스가 살아 있고 금제가 걸려 있어도 나와야 한다
        await ev(pg, "()=>{const G=__G,c=G.chal;c.evCd=0;__lv(14);c.next=15;__lv(15);__run(5);}")
        R['mini15'] = await ev(pg, "()=>({ev:!!__G.chal.ev,next:__G.chal.next})")
        out = []
        for lv in [20, 25, 30, 35, 40, 45]:
            r = await ev(pg, """async(lv)=>{const G=__G,c=G.chal,P=G.P;
              if(lv===20){c.pact={k:'rain',name:'t',t:0,dur:10,x:P.x,y:P.y};}
              __lv(lv);let n=0,seen=0,sirenAt=-1;
              for(;n<4000;n++){P.inv=99;P.hp=P.max;c.waitB=0;if(c.siren>0&&sirenAt<0)sirenAt=n;if(G.state==='play')G.tick(1/30);else __s();if(G.boss&&G.boss.hp>0){seen=1;break}if(n%20===0)await new Promise(r=>setTimeout(r,10))}
              const bk=G.boss?G.boss.bk||'monkey':null;
              if(seen){const B=G.boss;__run(30);B.invul=false;B.st='chase';G.hurtEnemy(B,B.hp+1e9,0,0,0,false);for(let i=0;i<300;i++){P.inv=99;if(G.state==='play')G.tick(1/30);else if(document.getElementById('levelTitle').textContent.indexOf('보상')>=0){G.pick(0)}else __s();if(!c.bossOn&&c.rewardT<=0&&G.state==='play'&&i>200)break}}
              for(let i=0;i<50;i++){if(G.state!=='play')__s();else break}
              return {lv,seen,ticksToBoss:n,sirenAt,bk,next:c.next,bossN:c.bossN,state:G.state,evLeft:!!c.ev}}""", lv)
            out.append(r); print(r)
        R['cadence'] = out
        # 산소 게이지 보이는지: 스크린샷
        await ev(pg, "()=>{const G=__G,P=G.P;for(let i=0;i<20;i++){G.tick(1/30)}P.o2=62;G.banner=null}"); await pg.wait_for_timeout(200)
        R['o2'] = await ev(pg, "()=>({on:__G.chal.o2Seen,o2:Math.round(__G.P.o2),lvl:__G.P.lvl})")
        await pg.screenshot(path=B + 'ch32_o2.png')
        # 피버 · 수정 효과 · 특수 잡몹
        R['fever'] = await ev(pg, """()=>{const G=__G,c=G.chal,P=G.P;c.fever=12;c.combo=130;let n=0,fx=0;G.chSquad();for(let i=0;i<60;i++){P.inv=99;G.tick(1/30)}
          for(const e of G.enemies.slice(0,40)){if(e.kind==='boss'||e.kind==='mini')continue;e.x=P.x+(Math.random()-0.5)*300;e.y=P.y+(Math.random()-0.5)*200;G.hurtEnemy(e,1e9,0,0,0,false);n++}
          for(let i=0;i<6;i++){G.tick(1/30)}fx=c.cfx.length;G.banner=null;return {killed:n,cfx:fx,sh:c.sh}}""")
        await pg.screenshot(path=B + 'ch32_fx.png')
        R['feverTick'] = await ev(pg, """()=>{try{for(let i=0;i<70;i++)__G.feverTick&&__G.feverTick();return 'ok'}catch(e){return 'ERR '+e.message}}""")
        await ev(pg, "()=>{const G=__G;for(let i=0;i<90;i++){G.P.inv=99;G.tick(1/30)}}"); await pg.screenshot(path=B + 'ch32_fx2.png')
        R['arrive'] = await ev(pg, "()=>({cfx:__G.chal.cfx.length,sh:__G.chal.sh})")
        # 룰렛
        await ev(pg, "()=>{__G.chal.fever=0;__G.openRoul()}"); await pg.wait_for_timeout(300); await pg.screenshot(path=B + 'ch32_roul.png')
        await ev(pg, "()=>{__G.roulSpin()}"); await pg.wait_for_timeout(1500); await pg.screenshot(path=B + 'ch32_roul2.png')
        await ev(pg, "()=>{for(let i=0;i<300;i++)__G.tick(1/30)}"); R['roul'] = await ev(pg, "()=>({state:__G.state,res:document.getElementById('rouRes').innerText.slice(0,60)})")
        await ev(pg, "()=>{__G.closeRoul&&__G.closeRoul();for(let i=0;i<30;i++)__s()}")
        # 업적
        R['ach'] = await ev(pg, """()=>{const G=__G,S=G.SAVE;S.ach.done={};S.ach.got={};S.ch.bestCombo=0;G.chal.best=620;G.chal.stT=-9;G.tick(1/30);G.chStatsLive();
          return {done:Object.keys(S.ach.done).filter(k=>k.startsWith('c_')),toast:G.chal.toast.length,bestCombo:S.ch.bestCombo}}""")
        await pg.screenshot(path=B + 'ch32_ach.png')
        R['achN'] = await ev(pg, "()=>__G.ACH.filter(a=>a.ch).length")
        print(json.dumps(R, ensure_ascii=False, indent=0)[:3000]); print('errs', errs[:6]); await b.close()
asyncio.run(main())
