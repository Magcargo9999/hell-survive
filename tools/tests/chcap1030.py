"""v10.30 챌린지 한계 돌파: 최대 레벨 3 이상 카드를 상한 너머(+4)까지 적용해 본다 — 능력치가 NaN/Infinity가 되거나 설명에 undefined가 나오면 CAP_NO 후보
사용: PYTHONPATH=tools GAME_URL=http://localhost:8765/build/hell_survive.html python3 tools/tests/chcap1030.py"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1100, 700); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        r = await pg.evaluate("""async()=>{const G=__G,S=G.SAVE;for(const c of Object.keys(G.CHARS))S.chars[c]=true;S.ch.open=true;S.diff.max=5;S.diff.clr=4;const bad={},chars=Object.keys(G.CHARS);
          for(const ch of chars){G.startChallenge(ch);for(let i=0;i<120&&G.state!=='play';i++)await new Promise(r=>setTimeout(r,250));if(!G.chal)continue;__lv(21);const P=G.P;G.chal.cap=4;
            const defs=G.cardDefs().concat([]);
            for(const u of G.UPGRADES.concat(G.UNIQUE[ch]||[])){const mx=u.max||5;if(mx<3)continue;
              const snap=JSON.stringify(P,(k,v)=>typeof v==='number'?v:(typeof v==='object'?v:undefined));
              let msg='';try{for(let n=(P.up[u.id]||0)+1;n<=mx+4;n++){const t=u.txt(n);if(/undefined|NaN|Infinity/.test(String(t)))msg='txt:'+String(t).slice(0,60);u.apply(P);P.up[u.id]=n;}
                for(const k in P){const v=P[k];if(typeof v==='number'&&!isFinite(v))msg+=' P.'+k+'='+v;}
              }catch(e){msg='ERR '+e.message}
              bad._n=(bad._n||0)+1;if(msg)(bad[u.id]=bad[u.id]||[]).push(ch+':'+msg.slice(0,90));}
            G.state!=='menu'}
          return bad}""")
        print(json.dumps(r, ensure_ascii=False, indent=0)); print('errs', errs[:5]); await b.close()
asyncio.run(main())
