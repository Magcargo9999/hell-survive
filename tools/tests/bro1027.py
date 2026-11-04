"""v10.27 ⚔ 보스 러시 전용 빌드(build/hell_survive_bossrush.html): 모든 캐릭터 · 마왕 큐 · 옵션 · 라운드 진행 · 완주 기록 · 세이브 분리
사용: PYTHONPATH=tools GAME_URL=http://localhost:8765/build/hell_survive_bossrush.html python3 tools/tests/bro1027.py"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
B = os.path.join(h301.ROOT, 'build') + '/'
async def ev(pg, js, a=None):
    try: return await pg.evaluate(js, a)
    except Exception as ex: return 'ERR ' + str(ex).split('\n')[0][:300]
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 800); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await pg.wait_for_timeout(1500); R = {}
        R['menu'] = await ev(pg, """()=>{const G=__G;G.buildCards();const cards=[...document.querySelectorAll('#charCards .card')];
          return {BRO:G.BRO,title:document.title,chars:cards.length,all:Object.keys(G.CHARS).length,locked:cards.filter(c=>c.classList.contains('locked')).length,
            bossBtns:document.querySelectorAll('#broPanel .broB').length,menuRow:getComputedStyle(document.getElementById('menuRow')).display,start:document.getElementById('startBtn').textContent}}""")
        R['queue'] = await ev(pg, """()=>{const G=__G;G.broQ=[];G.broRender();const btn=k=>document.querySelector('#broPanel .broB[data-b="'+k+'"]');
          btn('ttn').click();btn('monkey').click();btn('monkey').click();document.querySelector('#broPanel .broC[data-i="2"]').click();
          const sel=document.getElementById('broTier');sel.value='own';sel.dispatchEvent(new Event('change'));
          const m=document.getElementById('broMods');m.value='all';m.dispatchEvent(new Event('change'));
          return {q:G.broQ.join(','),opt:JSON.stringify(G.BRO_OPT),saved:localStorage.getItem('hsBroOpt'),start:document.getElementById('startBtn').textContent}}""")
        await pg.screenshot(path=B + 'bro_menu.png')
        # 숨은 캐릭터(마계 물고기)로 시작 → 시작 버튼
        R['start'] = await ev(pg, """()=>{const G=__G;const c=document.querySelector('#charCards .card[data-c="fish"]');c&&c.click();document.getElementById('startBtn').click();
          return {state:G.state,rush:!!G.rush,char:G.P.char,ord:G.rush&&G.rush.ord.join(','),N:G.rush&&G.rush.ord.length}}""")
        R['prep'] = await ev(pg, """()=>{const G=__G;let g=0;while(g++<900){if(__s())continue;if(G.state==='play'&&G.rush&&G.rush.init){G.tick(1/30);continue}break}return [G.state,G.P.lvl]}""")
        rounds = []
        for k in range(2):
            ent = await ev(pg, """async()=>{const G=__G;for(let i=0;i<1500;i++){G.P.inv=99;G.P.hp=G.P.max;while(__s());G.tick(1/30);if(G.boss&&G.boss.st!=='intro'&&G.rush.ph==='fight')break;if(i%20===0)await new Promise(r=>setTimeout(r,30))}
              const P=G.P,r=G.rush;return {bk:G.boss&&(G.boss.bk||'monkey'),round:r.round,tier:P.tier,mods:r.modifiers.join('+'),lvl:P.lvl}}""")
            if k == 0:
                await ev(pg, "()=>{for(let i=0;i<60;i++){__G.P.inv=99;__G.tick(1/30)}}"); await pg.screenshot(path=B + 'bro_fight.png')
            kill = await ev(pg, """()=>{const G=__G,e=G.boss;e.invul=false;e.hp=1;G.hurtEnemy(e,1e9,0,0,0,false);for(let i=0;i<60;i++){G.P.inv=99;while(__s());G.tick(1/30)}const r=G.rush;return {state:G.state,times:(r.times||[]).map(t=>+t.toFixed(1)),lvl:G.P.lvl,picked:r.totalCardsPicked}}""")
            rounds.append([ent, kill])
        R['rounds'] = rounds
        await ev(pg, "async()=>{for(let i=0;i<120;i++){__G.tick(1/30);if(i%20===0)await new Promise(r=>setTimeout(r,30))}}")
        await pg.wait_for_timeout(600)
        R['over'] = await ev(pg, """()=>({title:document.getElementById('overTitle').textContent,stats:document.getElementById('overStats').innerText.slice(0,300),shardsHidden:getComputedStyle(document.getElementById('overShards')).display,
          keys:Object.keys(localStorage).filter(k=>k.startsWith('hell')).join(','),reward:!!__G.rush.reward,stones:(__G.SAVE.stone&&__G.SAVE.stone.inv.length)|0})""")
        await pg.screenshot(path=B + 'bro_over.png')
        # 다시 도전(R) → 같은 큐 · 메뉴로
        R['retry'] = await ev(pg, """()=>{document.getElementById('retryBtn').click();const G=__G;return {state:G.state,ord:G.rush.ord.join(','),tier:G.brTierAt(0,'ttn'),mods:G.brModsAt(3).join('+')}}""")
        R['menu2'] = await ev(pg, """()=>{document.getElementById('menuBtn').click();return {panel:getComputedStyle(document.getElementById('broPanel')).display,q:__G.broQ.join(',')}}""")
        for k, v in R.items(): print(k, json.dumps(v, ensure_ascii=False))
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
