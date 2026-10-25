"""v9.24 팔열지옥(지하 26~30층) — 잠금 · 필드 바닥/소품 · 휴식존 · 열기 게이지 · 열기 가득 시 체력 감소 · 휴식존에서 식음 + 스크린샷
사용: PYTHONPATH=tools python3 tools/tests/fire924.py   (스크린샷 build/fire924_*.png)"""
import asyncio, sys, json
sys.path.insert(0, '/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
B = '/home/claude/hell-survive/build/'
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await pg.wait_for_function('__G.IMG&&__G.IMG.ffloor&&__G.IMG.fprops', timeout=90000)
        R = {}
        # 1) 잠금: 25층을 깬 기록이 있어도 26층은 못 고른다, 6번째 지옥 탭은 잠김
        R['lock'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=99;G.SAVE.diff.sel=27;G.SAVE.shards=1e7;G.startGame('wolf');
          const r={top:G.TOP_TIER,open:G.OPEN_TIER,tier:G.P.tier,fset:G.P.fset,set25:G.floorSet(25),set29:G.floorSet(29)};return r}""")
        await pg.evaluate("()=>{__G.state='menu'}")
        # 2) 팔열지옥 필드 강제 (테스트용): 판을 시작한 뒤 세트만 바꾼다
        R['start'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=24;G.SAVE.diff.sel=0;G.startGame('wolf');const P=G.P;P.tier=25;P.fset='fire';G.clearGround();
          for(let i=0;i<20;i++){__s();G.tick(1/30)}const z=G.restNearest(P.x,P.y);return {fire:G.isFireSet(),heat:P.heat,near:Math.round(Math.hypot(z.x-P.x,z.y-P.y))}}""")
        # 휴식존 간격: 넓은 범위에서 아무 점이나 가장 가까운 휴식존까지 최대 거리
        R['spacing'] = await pg.evaluate("""()=>{const G=__G;let mx=0;for(let i=0;i<3000;i++){const x=(Math.random()-0.5)*20000,y=(Math.random()-0.5)*20000,z=G.restNearest(x,y);mx=Math.max(mx,Math.hypot(z.x-x,z.y-y))}return Math.round(mx)}""")
        # 3) 열기 오름: 휴식존 밖 60초
        R['fill60'] = await pg.evaluate("""()=>{const G=__G,P=G.P;let t=0;while(t<60){if(G.restNear(P.x,P.y,G.HEAT.r+10)){P.x+=300}P.inv=9;G.tick(1/30);__s();t+=1/30}return {heat:Math.round(P.heat),hp:Math.round(P.hp),max:P.max}}""")
        await pg.evaluate("()=>{__G.render&&__G.render()}"); await pg.screenshot(path=B + 'fire924_field.png')
        # 4) 가득 → 체력 감소
        R['burn'] = await pg.evaluate("""()=>{const G=__G,P=G.P;P.heat=100;P.hp=P.max;const h0=P.hp;let t=0;while(t<4){if(G.restNear(P.x,P.y,G.HEAT.r+10)){P.x+=300}G.tick(1/30);__s();t+=1/30}return {lost:Math.round(h0-P.hp),pct:+((h0-P.hp)/P.max*100).toFixed(1),state:G.state}}""")
        await pg.evaluate("()=>{const G=__G,P=G.P;P.heat=100;P.hp=P.max;G.tick(1/30)}"); await pg.screenshot(path=B + 'fire924_hot.png')
        # 5) 휴식존 안 → 식음
        R['cool'] = await pg.evaluate("""()=>{const G=__G,P=G.P;const z=G.restNearest(P.x,P.y);P.x=z.x;P.y=z.y;P.heat=100;P.hp=P.max;let t=0;while(t<2){P.x=z.x;P.y=z.y;G.tick(1/30);__s();t+=1/30}return {heat:Math.round(P.heat),inRest:P.inRest}}""")
        await pg.screenshot(path=B + 'fire924_rest.png')
        # 6) 휴식존 둘레엔 용암 없음
        R['nolava'] = await pg.evaluate("""()=>{const G=__G;let bad=0;for(let gx=-6;gx<6;gx++)for(let gy=-6;gy<6;gy++){const z=G.restAt(gx,gy);for(let a=0;a<12;a++){const r=G.HEAT.r*Math.random(),x=z.x+Math.cos(a)*r,y=z.y+Math.sin(a)*r;if(G.isLava(Math.floor(x/64),Math.floor(y/64)))bad++}}return bad}""")
        # 7) 보스방에서는 열기 없음
        R['arena'] = await pg.evaluate("""()=>{const G=__G,P=G.P;P.heat=80;__lv(26);G.raiseCastle();G.enterArena();for(let i=0;i<30;i++){__s();P.inv=9;G.tick(1/30)}return {heat:P.heat,arena:!!G.arena}}""")
        # 8) 시작 화면 6지옥 탭
        await pg.evaluate("()=>{const G=__G;location.hash='';}")
        R['tabs'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=24;G.SAVE.diff.sel=24;G.updateDiff&&G.updateDiff();const t=[...document.querySelectorAll('#hellTabs button')].map(b=>[b.textContent,b.disabled]);return t}""")
        R['errs'] = errs[:6]
        print(json.dumps(R, ensure_ascii=False, indent=1)); await b.close()
asyncio.run(main())
