import asyncio
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--disable-gpu']); pg=await newpage(b,1000,620)
        r=await pg.evaluate("""()=>{const G=__G,S=G.SAVE;S.heart={inv:[],eq:[],n:0,got:{}};
          for(const k of ['angel','monkey','monkey','angel','eye','eye'])G.heartGain('legend',k);
          const out={};const ids=S.heart.inv.map(q=>q.id);
          const f=G.fuseHearts(ids.slice(0,3));out.h=f.h&&{g:f.h.g,b:f.h.b,st2:!!f.h.st2,v:f.h.v,v2:f.h.v2};out.inv=S.heart.inv.length;out.got=Object.keys(S.heart.got).sort();
          const f2=G.fuseHearts(ids.slice(3,6));out.second=!!f2.h;out.fused=S.heart.inv.filter(q=>q.b==='fuse').length;out.got2=Object.keys(S.heart.got).sort();
          out.err=G.fuseHearts([1,2]).err;
          const ic=G.heartIcon?1:0;
          document.getElementById('heartBtn').click();return out}""")
        print(r, pg.errs); await b.close()
asyncio.run(main())
