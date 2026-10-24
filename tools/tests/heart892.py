import asyncio
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--disable-gpu']); pg=await newpage(b,1000,620)
        r=await pg.evaluate("""()=>{const G=__G,S=G.SAVE;S.heart={inv:[],eq:[],n:0,got:{}};const out={};
          // 영혼 조각 옵션 범위
          const rng={};for(const g of ['rare','epic','unique','legend']){let lo=999,hi=0,n=0;for(let i=0;i<4000;i++){const h=G.heartMake(g,'monkey');if(h.st==='shard'){n++;lo=Math.min(lo,h.v);hi=Math.max(hi,h.v);}}rng[g]=[lo,hi,n>0]}out.rng=rng;
          // 6개 레전더리 → 합성 2개 → 3줄
          for(const k of ['angel','monkey','eye','tox','qn','adm','shk','skel','angel'])G.heartGain('legend',k);
          let ids=S.heart.inv.map(q=>q.id);
          const f1=G.fuseHearts(ids.slice(0,3)),f2=G.fuseHearts(ids.slice(3,6)),f3=G.fuseHearts(ids.slice(6,9));
          out.fuse=[f1.h.b,f2.h.b,f3.h.b];
          const fz=S.heart.inv.filter(q=>q.b==='fuse').map(q=>q.id);
          out.mix=G.fuseHearts([fz[0],fz[1],99]).err;
          const g=G.fuseHearts(fz);out.g3=g.h&&{b:g.h.b,g:g.h.g,st3:g.h.st3,n:G.hOpt(g.h).split(' · ').length};out.left=S.heart.inv.length;
          // 재설정 3줄 유지
          S.shards=5000;const rr=G.rerollHeart(g.h.id);out.re=!!(rr.after.st3&&rr.after.st2);
          // 보너스/영혼 조각
          const h=G.heartMake('legend','monkey');h.st='shard';h.v=40;S.heart.inv.push(h);S.heart.eq=[h.id];out.bonus=G.heartBonus().shard;
          out.sum=document.body?1:0;
          document.getElementById('heartBtn').click();
          return out}""")
        print(r, pg.errs); await b.close()
asyncio.run(main())
