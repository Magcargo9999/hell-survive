"""v10.46 각성한 원숭이 마왕: 보스전 체험 진입 · 패턴 전부 발동 · 화면 확인"""
import asyncio, json, sys
from playwright.async_api import async_playwright
from h301 import newpage
START = """async (c)=>{const G=__G;window.__rt=0;window.__fin=0;G.startAmkTrial(c);let n=0;
  while(n++<4000){ if(__s())continue; if(G.arena&&G.boss&&G.boss.bk==='amk')break; G.P.hp=G.P.max;G.P.inv=9;G.tick(1/30); if(n%40===0)await new Promise(r=>setTimeout(r,30)); }
  const b=G.boss;return b?{bk:b.bk,hp:Math.round(b.hp),lvl:G.P.lvl,tier:G.P.tier,spd:Math.round(G.P.spd),K:+G.amkK().toFixed(2),fset:G.P.fset,trial:!!G.rush.trial,BRN:G.rush.round}:{st:G.state,n,arena:!!G.arena,lv:G.P.lvl}}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        print(await pg.evaluate(START, sys.argv[1] if len(sys.argv) > 1 else 'wolf'))
        seen = {}
        for step in range(70):
            r = await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss;if(!e)return null;const S={};
              for(let i=0;i<30;i++){P.hp=P.max;P.inv=0.5;if(G.state!=='play'){break}G.tick(1/30);S[e.st]=1}
              return {st:Object.keys(S),ph:e.ph,hp:+(e.hp/e.max).toFixed(2),cr:G.AMW.cracks.length,cl:G.AMW.clones.length,state:G.state}}""")
            if not r: break
            for s in r['st']:
                if s not in seen:
                    seen[s] = step; await pg.wait_for_timeout(80); await pg.screenshot(path=f'build/amk/st_{s}.png')
            if step == 25: await pg.evaluate("()=>{const e=__G.boss;e.hp=e.max*0.49}")
        print('states', seen); print('last', r); print('errs', pg.errs)
        await b.close()
asyncio.run(main())
