"""v10.30 챌린지 오류 찾기: 캐릭터마다 챌린지를 빠르게 돌린다 (무작위 이동 · 레벨업 자동 선택 · 금제·룰렛·보상 자동) — tick·render 오류 수집
사용: PYTHONPATH=tools GAME_URL=http://localhost:8765/build/hell_survive.html python3 tools/tests/chfuzz1030.py [게임 초=900] [캐릭터...]"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
SEC = int(sys.argv[1]) if len(sys.argv) > 1 else 900
CHS = sys.argv[2:] or ['wolf', 'gun', 'snail', 'ghost', 'fish']
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1100, 700); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
        await pg.evaluate("()=>{const G=__G,S=G.SAVE;for(const c of Object.keys(G.CHARS))S.chars[c]=true;S.ch.open=true;S.diff.max=39;S.diff.clr=38;for(let i=1;i<=24;i++)S.dex.kills['boss'+(i>1?i:'')]=1}")
        for ch in CHS:
            await pg.evaluate(f"()=>__G.startChallenge('{ch}')")
            for i in range(160):
                if await pg.evaluate("()=>__G.state==='play'&&!!__G.chal"): break
                await pg.wait_for_timeout(250)
            r = await pg.evaluate("""async(SEC)=>{const G=__G,E={};let n=0,ang=0;const P=G.P;
              const add=e=>{const k=String(e&&e.stack||e).split('\\n').slice(0,2).join(' | ').slice(0,220);E[k]=(E[k]||0)+1};
              for(let f=0;f<SEC*30;f++){
                try{ if(G.state==='levelup'){const c=G.choices||[];G.pick(Math.floor(Math.random()*Math.max(1,c.length)));continue}
                  if(G.state==='roul'){if(G.roul&&G.roul.ph==='ask')G.roulSpin();else if(G.roul&&G.roul.ph==='done')document.getElementById('rouBtn').click();G.tick(1/30);continue}
                  if(G.state==='slot'){G.tick(1/30);document.getElementById('slotLeave').click();continue}
                  if(G.state==='evolve'){G.tick(1/30);continue}
                  if(G.state!=='play')break;
                  P.hp=Math.max(P.hp,P.max*0.6);if(G.chal.pact&&G.chal.pact.k==='glass')P.hp=P.max;
                  if(f%45===0){ang+=Math.random()*2-1;const T=G.boss&&G.boss.hp>0?G.boss:(G.chal.ev&&G.chal.ev.find(e=>e.hp>0));if(T&&Math.random()<0.6)ang=Math.atan2(T.y-P.y,T.x-P.x)+(Math.random()-0.5)}const sp=P.spd||200;P.x+=Math.cos(ang)*sp/30*0.8;P.y+=Math.sin(ang)*sp/30*0.8;
                  if(f%240===0&&G.P.skT<=0)G.castSkill();
                  if(G.chal.altar&&f%30===0&&Math.random()<0.3){P.x=G.chal.altar.x;P.y=G.chal.altar.y}
                  if(G.chal.gold&&f%20===0){const e=G.chal.gold;G.hurtEnemy(e,P.dmg*3,0,0,0,false)}
                  G.tick(1/30);}catch(e){add(e)}
                if(f%6===0){try{G.render()}catch(e){add(e)}}
                if(f%600===0)await new Promise(r=>setTimeout(r,1));
              }
              const c=G.chal;return {bossOn:c.bossOn,siren:c.siren,bk:c.bossK,bhp:G.boss?Math.round(100*G.boss.hp/G.boss.max)+'%'+G.boss.st:null,fb:!!c.fbC,next:c.next,ev:!!c.ev,pactNow:!!c.pact,altar:!!c.altar,rewardT:c.rewardT,t:Math.round(G.gt||0),lvl:P.lvl,state:G.state,boss:c.bossN,mini:c.miniN,pact:c.pactN,gold:c.goldGot+'/'+c.goldN,cap:c.cap,sh:c.sh,combo:c.best,fever:c.feverN,sq:c.sqN,mobs:G.enemies.length,E}}""", SEC)
            print(ch, json.dumps(r, ensure_ascii=False)[:900])
        print('page errors', errs[:6]); await b.close()
asyncio.run(main())
