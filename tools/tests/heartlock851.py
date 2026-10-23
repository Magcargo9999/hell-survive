"""v8.51 심장 옵션 잠금: 잠그면 재설정·분해 불가 · 표시 · 저장 유지 · 해제하면 다시 가능 + 스크린샷"""
import asyncio, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
from h301 import newpage
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'build')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 800)
        await pg.wait_for_function('window.__G && __G.IMG', timeout=90000)
        await pg.evaluate("""()=>{const G=__G;G.SAVE.shards=9000;G.SAVE.heart={inv:[{id:1,g:'legend',st:'atk',v:18,b:'angel'},{id:2,g:'unique',st:'hp',v:8,b:'eye'}],eq:[1],n:2,got:{}};G.openHeart();}""")
        await pg.wait_for_timeout(300)
        R = {}
        R['before'] = await pg.evaluate("()=>({re:document.getElementById('hReroll').disabled,lock:document.getElementById('hLock').textContent})")
        await pg.click('#hLock'); await pg.wait_for_timeout(100)
        R['locked'] = await pg.evaluate("()=>({re:document.getElementById('hReroll').disabled,reTxt:document.getElementById('hReroll').textContent,dis:document.getElementById('hDis').disabled,lock:document.getElementById('hLock').textContent,mark:document.querySelectorAll('.hlk').length,err:__G.rerollHeart(1).err,disBack:__G.disHeart(1),still:__G.SAVE.heart.inv.length,shards:__G.SAVE.shards})")
        R['saved'] = await pg.evaluate("()=>{return JSON.parse(localStorage.getItem('hellSurvivorSave1')).heart.inv[0].lock}")
        await pg.screenshot(path=os.path.join(OUT, 'heart_lock.png'))
        await pg.click('#hLock'); await pg.wait_for_timeout(100)
        R['unlocked'] = await pg.evaluate("()=>({re:document.getElementById('hReroll').disabled,ok:!__G.rerollHeart(1).err})")
        print(json.dumps(R, ensure_ascii=False)); print('errs', pg.errs); await b.close()
asyncio.run(main())
