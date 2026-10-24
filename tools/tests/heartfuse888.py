import asyncio, sys
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--disable-gpu']); pg=await newpage(b,1000,620)
        r=await pg.evaluate("""()=>{const G=__G,S=G.SAVE;S.heart={inv:[],eq:[],n:0,got:{}};
          G.heartGain('legend','angel');G.heartGain('legend','monkey');G.heartGain('legend','monkey');
          const ids=S.heart.inv.map(q=>q.id);const out={};
          out.before=Object.keys(S.heart.got).sort();
          const f=G.fuseHearts(ids);out.err=f.err||null;out.after=Object.keys(S.heart.got).sort();
          out.dropMonkey=(()=>{let n=0;const o=Math.random;Math.random=()=>0.5;n=G.rollHeartDrop('monkey')?1:0;Math.random=()=>0.1;n+=G.rollHeartDrop('monkey')?10:0;Math.random=o;return n})();
          S.heart={inv:[{id:1,g:'rare',st:'atk',v:2}],eq:[1],n:1,got:{}};
          Math.random=()=>0.1;out.legacyAngel=G.rollHeartDrop('angel');out.otherBoss=G.rollHeartDrop('eye');return out}""")
        print(r, pg.errs); await b.close()
asyncio.run(main())
