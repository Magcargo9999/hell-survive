import asyncio, sys
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000)
        await pg.evaluate("()=>{__G.SAVE.chars.fish=true;__G.startGame('fish')}")
        await pg.wait_for_function("__G.state==='play'", timeout=60000)
        r = await pg.evaluate("""()=>{const G=__G,P=G.P;
          const pool=G.cardDefs().map(u=>u.id);
          return {pool: pool&&pool.includes('aura'), shard: pool&&pool.includes('shard')}}""")
        print(r)
        r = await pg.evaluate("""()=>{const G=__G,P=G.P; G.spawnEnemy&&0;
          const mk=(k)=>({x:P.x+40,y:P.y,r:20,hp:1e6,max:1e6,kind:k,vx:0,vy:0,slowT:0,hitT:0});
          const B=mk('boss'),M=mk('mob'); G.enemies.push(B,M); P.fishT=0; P.dmg=50; G.updateFish(0.016);
          return {boss:1e6-B.hp, mob:1e6-M.hp}}""")
        print(r, errs)
        await b.close()
asyncio.run(main())
