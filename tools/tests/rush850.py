"""v8.50 보스 러시: 잠금/해금 · 준비 레벨업 연쇄 · 7종 순서대로 입장 · 처치 후 회복+카드 · 완주 보상 · 사망 결과 · 20층 해금 조건 · 스크린샷"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
B='/home/claude/hell-survive/build/'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.adm&&__G.IMG.zom',timeout=60000)
        print('locked', await pg.evaluate("()=>[__G.rushOpen(), document.getElementById('rushBtn').textContent]"))
        # 20층 마왕 처치 → 해금 (일반 판)
        r=await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=19;G.SAVE.diff.sel=0;G.SAVE.shards=99999;G.startGame('wolf');const P=G.P;P.tier=19;P.bossK='monkey';G.enterArena();for(let i=0;i<40;i++)G.tick(1/30);return [!!G.boss]}""")
        await pg.evaluate("()=>{__G.boss.invul=false;__G.boss.st='chase'}")
        r=await pg.evaluate("""()=>{const G=__G;G.hurtEnemy(G.boss,1e12,0,0,0);for(let i=0;i<5;i++)G.tick(1/30);return [G.state,G.rushOpen(),G.P.rushOpen]}""")
        print('unlock by 20F clear', r)
        for ch in ['wolf','snail','lizard']:
            r=await pg.evaluate("""(ch)=>{const G=__G;G.SAVE.chars[ch]=true;G.SAVE.diff.max=19;G.SAVE.diff.sel=0;G.startRush(ch);const P=G.P;let g=0;while(g++<400&&(G.state==='levelup'||G.state==='evolve'))__s();
              return [G.state,P.lvl,P.form,G.rush.ph,Math.round(P.exp),P.need,P.char]}""",ch)
            print('prep',ch,r)
        await pg.evaluate("()=>{__G.SAVE.chars.wolf=true;__G.startRush('wolf');let g=0;while(g++<400&&(__G.state==='levelup'||__G.state==='evolve'))__s();}")
        out=[]
        for k in range(9):   # BR_ORDER 9종 (v8.70)
            # 입장 대기
            ok=await pg.evaluate("""()=>{const G=__G;for(let i=0;i<400;i++){G.P.inv=99;G.P.hp=G.P.max;G.tick(1/30);if(G.boss&&G.boss.st!=='intro')break}return [G.boss&&G.boss.bk||'monkey',G.rush.i,G.rush.ph,!!(G.arena&&G.arena.sealed),G.P.bossK,Math.round(G.boss?G.boss.max:0)]}""")
            if k in (0,3,6): await pg.screenshot(path=B+f'rush_{k}.png')
            r=await pg.evaluate("""()=>{const G=__G,P=G.P;P.hp=1;const e=G.boss;e.invul=false;e.shield=0;e.st='chase';G.hurtEnemy(e,1e13,0,0,0);for(let i=0;i<3;i++)G.tick(1/30);const o=[G.state,G.rush.i,G.rush.kills,Math.round(G.rush.shards),P.lvl,Math.round(P.hp===P.max?1:0)];let g=0;while(g++<400&&(G.state==='levelup'||G.state==='evolve'))__s();return o.concat([G.state,P.lvl,G.rush.ph])}""")
            out.append((ok,r)); print(k,json.dumps(ok),json.dumps(r))
        r=await pg.evaluate("""()=>{const G=__G;for(let i=0;i<200;i++){G.tick(1/30)}return [G.state,G.SAVE.rush,G.P.earned]}""")
        print('final',json.dumps(r))
        # 사망
        r=await pg.evaluate("""()=>{const G=__G;G.SAVE.chars.wolf=true;G.startRush('wolf');let g=0;while(g++<400&&(G.state==='levelup'||G.state==='evolve'))__s();for(let i=0;i<300;i++){G.P.inv=99;G.tick(1/30);if(G.boss)break}const s0=G.SAVE.shards;G.P.inv=0;G.P.shield=0;G.P.hp=0;G.die?0:0;return [!!G.boss,G.rush.i]}""")
        print('death-prep',r)
        print('errs',pg.errs[:6]); await b.close()
asyncio.run(main())
