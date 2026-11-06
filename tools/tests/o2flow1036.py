"""보스 러시를 실제 흐름(처치 → 증강 선택 → 다음 라운드)대로 4라운드 돌리며 산소 게이지가 그려지는지 본다"""
import asyncio, sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
PICK = """(want)=>{const G=__G;let g=0;while(g++<900){const t=document.getElementById('levelTitle').textContent;
  if(G.state==='levelup'&&t.indexOf('몇 개')>=0){G.pick(want===5?1:0);continue}
  if(__s())continue; if(G.state==='play'&&G.rush&&G.rush.init){G.tick(1/30);continue} break}
  return [G.state,G.P.lvl]}"""
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720)
        await pg.wait_for_timeout(1500)
        await pg.evaluate("""()=>{const G=__G;Object.assign(G.SAVE.dex.kills,{boss:3,boss2:1,boss14:2,boss19:1,boss21:1,boss20:1,boss16:1});G.SAVE.diff.clr=29;G.SAVE.diff.max=5;G.SAVE.diff.sel=0;G.SAVE.shards=1e6;
          const c=G.ctx,f=c.fillText.bind(c);window.__o2n=0;c.fillText=function(t,...a){if(typeof t==='string'&&t.indexOf('🫧')>=0)window.__o2n++;return f(t,...a)};G.startRush('wolf')}""")
        await pg.evaluate(PICK, 2)
        for k in range(4):
            ent = await pg.evaluate("""async()=>{const G=__G;for(let i=0;i<1500;i++){G.P.inv=99;G.P.hp=G.P.max;G.tick(1/30);if(G.boss&&G.boss.st!=='intro'&&G.rush.ph==='fight')break;if(i%20===0)await new Promise(r=>setTimeout(r,30))}
              return {bk:G.boss&&G.boss.bk,round:G.rush.round,mods:G.rush.modifiers.join('+')}}""")
            seq = []
            for part in range(4):   # 싸우는 동안 5초씩 4번 (체력을 단계로 깎음)
                r = await pg.evaluate("""async(part)=>{const G=__G,P=G.P,e=G.boss,r=G.rush;if(part>0){e.invul=false;e.hp=e.max*(1-part*0.22)}e.invul=true;window.__o2n=0;
                  for(let i=0;i<150;i++){P.inv=99;P.hp=P.max;G.tick(1/30);await new Promise(q=>setTimeout(q,16))}
                  return {has:r.has('o2'),o2:Math.round(P.o2),drawn:window.__o2n,hp:Math.round(e.hp/e.max*100),ph:r.ph,boss:!!G.boss,st:G.state}}""", part)
                seq.append(r)
            print(k, ent, json.dumps(seq, ensure_ascii=False))
            await pg.evaluate("""()=>{const G=__G,e=G.boss;e.invul=false;e.shield=0;if(e.st==='guard'||e.st==='intro')e.st='chase';G.hurtEnemy(e,1e13,0,0,0);for(let i=0;i<3;i++)G.tick(1/30)}""")
            if k < 3: await pg.evaluate(PICK, [2, 5, 2][k])
        print('errs', pg.errs[:5]); await b.close()
asyncio.run(main())
