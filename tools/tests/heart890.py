import asyncio
from playwright.async_api import async_playwright
from h301 import newpage, URL
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--disable-gpu']); pg=await newpage(b,1100,700)
        await pg.evaluate("""()=>{const G=__G,S=G.SAVE;S.heart={inv:[{id:1,g:'legend',b:'monkey',st:'atk',v:18,st2:'hp',v2:16},{id:2,g:'rare',b:'eye',st:'atk',v:2}],eq:[1,2],n:2,got:{monkey:true,eye:true}};G.saveSave&&G.saveSave();localStorage.setItem('hellSurvivorSave1',JSON.stringify(S))}""")
        await pg.reload(); await pg.wait_for_function('window.__G&&__G.ready',timeout=60000)
        print(await pg.evaluate("()=>{const S=__G.SAVE.heart;return {inv:S.inv.map(q=>q.b+':'+q.g),got:Object.keys(S.got)}}"))
        await pg.evaluate("document.getElementById('heartBtn').click()"); await pg.wait_for_timeout(400)
        await pg.screenshot(path='build/shots/heart890.png'); await pg.keyboard.press('Escape')
        await pg.evaluate("()=>{const G=__G;G.SAVE.perks.banish=3;G.startGame('wolf');G.P.banish=3;G.addExp(G.P.need);}")
        await pg.wait_for_timeout(200)
        t=await pg.evaluate("()=>({st:__G.state,ids:__G.choices.map(c=>c.id)})"); print(t)
        await pg.keyboard.down('Shift'); await pg.keyboard.press('Digit2'); await pg.keyboard.up('Shift')
        t2=await pg.evaluate("()=>({st:__G.state,ids:__G.choices.map(c=>c.id),ban:__G.P.banish})"); print(t2)
        await pg.keyboard.press('Digit1'); print(await pg.evaluate("()=>__G.state"), pg.errs); await b.close()
asyncio.run(main())
