"""v7.30 스킨 가챠: 확률 · 천장 · 제외 규칙 · 조합 · 단일 장착 · 화면/인게임 스크린샷"""
import asyncio, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
from h301 import newpage
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'build', 'shots')
FRESH = "G.SAVE.skin={own:{},frag:{},on:{},pity:0,pulls:0};"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 800)
        await pg.wait_for_function('window.__G && __G.IMG && __G.IMG.sk_gunH && __G.IMG.sk_wolfE', timeout=90000)
        R = {}
        R['first'] = await pg.evaluate("()=>{const G=__G,c={epic:0,rare:0,frag:0,fr1:0,fr2:0,fe:0,fgun:0,fwolf:0},N=49000;for(let i=0;i<N;i++){" + FRESH + "const r=G.gachaRoll();if(r.type==='skin')c[G.SKINS.find(s=>s.id===r.id).grade]++;else{c.frag++;if(r.id==='gunH'){c.fgun++;c['fr'+r.n]++;}else{c.fwolf++;c.fe+=r.n===1?1:0;}}}const o={};for(const k in c)o[k]=+(c[k]/N*49).toFixed(2);o.wolfFragAlways1=c.fe===c.fwolf;return o;}")
        R['pity'] = await pg.evaluate("()=>{const G=__G;let maxGap=0,gaps=[],pityE=0,pityN=0;for(let t=0;t<3000;t++){" + FRESH + "for(let i=1;i<=30;i++){const r=G.gachaRoll();if(r.type==='skin'){gaps.push(i);if(r.pity){pityN++;if(r.id==='wolfE')pityE++;}break;}}}maxGap=Math.max(...gaps);return {maxGap,pityRate:+(pityN/3000).toFixed(3),pityEpic:+(pityE/Math.max(1,pityN)).toFixed(3)};}")
        R['pity24'] = await pg.evaluate("()=>{const G=__G;let e=0,n=0;for(let i=0;i<20000;i++){G.SAVE.skin={own:{},frag:{},on:{},pity:24,pulls:0};const r=G.gachaRoll();if(r.type==='skin'&&r.pity){n++;if(r.id==='wolfE')e++;}}return {guaranteed:n,epicRate:+(e/n).toFixed(3)};}")
        R['exclude'] = await pg.evaluate("()=>{const G=__G;" + FRESH + "G.SAVE.skin.own.gunH=true;let bad=0,got={};for(let i=0;i<3000;i++){const r=G.gachaRoll();if(!r)break;if(r.id==='gunH')bad++;got[r.type+r.id]=(got[r.type+r.id]||0)+1;if(r.type==='skin'){G.SAVE.skin.own.wolfE=false;}G.SAVE.skin.frag.wolfE=Math.min(G.SAVE.skin.frag.wolfE||0,10);}" + "const S=G.SAVE.skin;S.own={gunH:true,wolfE:true};return {bad,got,afterAll:G.gachaRoll()};}")
        R['capCraft'] = await pg.evaluate("()=>{const G=__G;" + FRESH + "const S=G.SAVE.skin;S.frag.gunH=9;let r;for(let i=0;i<200;i++){r=G.gachaRoll();if(r&&r.id==='gunH'&&r.type==='frag')break;}const cap=S.frag.gunH;const c1=G.skinCraft('gunH');const own=!!S.own.gunH,left=S.frag.gunH;"
                                     "S.own.wolfE=true;S.on={gun:'gunH'};G.skinToggle('wolfE');const on1=JSON.stringify(S.on);G.skinToggle('wolfE');const on2=S.on;G.skinToggle('gunH');return {cap,c1,own,left,on1,on2,on3:S.on};}")
        # 화면: 뽑기 · 결과 · 도감
        await pg.evaluate("()=>{const G=__G;" + FRESH + "G.SAVE.shards=99999;G.openGacha('pull');}")
        await pg.screenshot(path=os.path.join(OUT, 'gacha_main.png'))
        await pg.evaluate("()=>{const G=__G;G.SAVE.skin.pity=24;G.gachaPull(1);}"); await pg.wait_for_timeout(2200)
        await pg.screenshot(path=os.path.join(OUT, 'gacha_one.png'))
        await pg.evaluate("()=>{document.getElementById('gOk').click();const G=__G;G.SAVE.skin.own={};G.SAVE.skin.on={};G.SAVE.skin.pity=20;G.gachaPull(10);}"); await pg.wait_for_timeout(2600)
        await pg.screenshot(path=os.path.join(OUT, 'gacha_ten.png'))
        await pg.evaluate("()=>{document.getElementById('gOk').click();const G=__G;G.SAVE.skin.own={gunH:true};G.SAVE.skin.frag={wolfE:15};G.SAVE.skin.on='gunH';G.openGacha('dex');}")
        await pg.screenshot(path=os.path.join(OUT, 'gacha_dex.png'))
        await pg.evaluate("()=>{const G=__G;G.SAVE.skin.own={};G.SAVE.skin.frag={};G.SAVE.skin.on={};G.openGacha('dex');}")
        await pg.screenshot(path=os.path.join(OUT, 'gacha_dex_lock.png'))
        # 인게임: 총잡이 최종 · 늑대 0/2진화
        R['game'] = await pg.evaluate("""()=>{const G=__G;document.getElementById('gachaBox').classList.remove('show');const S=G.SAVE.skin;S.own={gunH:true,wolfE:true};
          S.on={gun:'gunH'};G.SAVE.chars.gun=true;G.startGame('gun');__lv(20);for(let i=0;i<40;i++){G.P.inv=99;G.tick(1/30);if(G.state!=='play')__s();}const a=!!G.skinOn('gun'),f=G.P.form;
          return {gunSkin:a,form:f};}""")
        await pg.evaluate("()=>{__G.render();}"); await pg.screenshot(path=os.path.join(OUT, 'skin_gun.png'), clip={'x': 440, 'y': 250, 'width': 400, 'height': 300})
        R['game2'] = await pg.evaluate("""()=>{const G=__G;const S=G.SAVE.skin;S.on={wolf:'wolfE'};G.startGame('wolf');for(let i=0;i<30;i++){G.P.inv=99;G.tick(1/30);}G.render();return {wolfSkin:!!G.skinOn('wolf'),form:G.P.form};}""")
        await pg.screenshot(path=os.path.join(OUT, 'skin_wolf0.png'), clip={'x': 440, 'y': 250, 'width': 400, 'height': 300})
        await pg.evaluate("""()=>{const G=__G;__lv(20);for(let i=0;i<60;i++){G.P.inv=99;G.tick(1/30);if(G.state!=='play')__s();}G.render();}""")
        await pg.screenshot(path=os.path.join(OUT, 'skin_wolf2.png'), clip={'x': 440, 'y': 250, 'width': 400, 'height': 300})
        print(json.dumps(R, ensure_ascii=False)); print('errs', pg.errs); await b.close()
asyncio.run(main())
