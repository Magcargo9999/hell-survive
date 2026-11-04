"""v10.28 오류 찾기(넓게): ① 마왕 21종 × 캐릭터(돌려가며) — 보스방에서 무작위로 움직이며 스킬을 쓰고(그리기 포함) 2페이즈까지 ② 지옥 8곳 필드
게임 루프는 한 프레임 오류를 삼키므로 tick·render를 try로 감싸 오류를 모은다. 플레이어는 죽지 않게 체력만 채운다(맞는 처리는 그대로).
사용: PYTHONPATH=tools GAME_URL=http://localhost:8765/build/hell_survive.html python3 tools/tests/fuzz1028.py [보스 초=40] [필드 초=50]"""
import asyncio, sys, os, json
from playwright.async_api import async_playwright
from h301 import newpage
CH = ['wolf', 'snail', 'archer', 'chimera', 'lizard', 'twins', 'ghost', 'octo', 'gun', 'fish']
LOOP = """{const G=__G,P=G.P;let s=SEED;const rnd=()=>{s=(s*1103515245+12345)&0x7fffffff;return s/0x7fffffff};
 const keys=['KeyW','KeyA','KeyS','KeyD'],E=new Set();const T=f=>{try{f()}catch(e){E.add(String(e&&e.stack||e).slice(0,300))}};let t=0,n=0,ph=false;
 while(t<SECS&&n++<60000){const st=G.state;if(st==='levelup'||st==='evolve'||st==='slot'){if(!__s()){T(()=>G.tick(1/30));if(G.slotUI)try{G.closeSlot()}catch(e){}}continue}
  if(st!=='play')break;
  if(n%30===0){for(const k of keys)G.keys.delete(k);G.keys.add(keys[Math.floor(rnd()*4)]);if(rnd()<0.5)G.keys.add(keys[Math.floor(rnd()*4)]);}
  if(P.skill&&P.skT<=0&&rnd()<0.06)T(()=>G.cast());
  if(P.hp<P.max*0.4)P.hp=P.max*0.6;
  if(BOSS&&G.boss&&!ph&&t>SECS*0.5){ph=true;G.boss.hp=Math.min(G.boss.hp,G.boss.max*0.26);}
  if(BOSS&&G.boss&&G.boss.hp<G.boss.max*0.03)G.boss.hp=G.boss.max*0.2;
  T(()=>G.tick(1/30));t+=1/30;if(n%5===0)T(()=>G.render());}
 return {t:Math.round(t),state:G.state,boss:G.boss&&G.boss.bk,st:G.boss&&G.boss.st,lvl:P.lvl,E:[...E]}}"""
async def main():
    bs = float(sys.argv[1]) if len(sys.argv) > 1 else 40; fs = float(sys.argv[2]) if len(sys.argv) > 2 else 50
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); out = []
        pg = await newpage(b, 960, 600); errs = pg.errs
        pg.on('console', lambda m: errs.append(m.text[:300]) if m.type == 'error' else None)
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000)
        order = await pg.evaluate("()=>__G.BR_ORDER||[]")
        if not order: order = await pg.evaluate("()=>Object.keys(__G.BOSS_FLOOR)")
        floors = await pg.evaluate("()=>__G.BOSS_FLOOR")
        for i, k in enumerate(order):
            ch = CH[i % len(CH)]; e0 = len(errs)
            js = """async([ch,k,tier])=>{const G=__G;Object.assign(G.SAVE.chars,{wolf:1,snail:1,archer:1,chimera:1,lizard:1,twins:1,ghost:1,octo:1,gun:1,fish:1});G.SAVE.diff.max=40;G.SAVE.shards=1e7;G.SAVE.diff.sel=tier;
              window.__rt=Math.floor(Math.random()*2);window.__fin=0;G.startGame(ch);for(let i=0;i<80&&G.state!=='play';i++)await new Promise(r=>setTimeout(r,250));
              __lv(22);G.P.bossK=k;G.P.hp=G.P.max;G.raiseCastle();G.enterArena();
              for(let i=0;i<200;i++){if(G.boss&&G.boss.bk===k||(G.boss&&k==='monkey'))break;G.tick(1/30);await new Promise(r=>setTimeout(r,60))}
              """ + LOOP.replace('SEED', str(17 + i)).replace('SECS', str(bs)).replace('BOSS', 'true') + "}"
            try: r = await pg.evaluate(js, [ch, k, floors.get(k, 3)])
            except Exception as ex: r = {'ERR': str(ex)[:300]}
            r['case'] = f'boss:{k}/{ch}'; r['console'] = errs[e0:][:5]; out.append(r); print(json.dumps(r, ensure_ascii=False)[:700], flush=True)
        for j, tier in enumerate([0, 6, 11, 16, 21, 26, 31, 36]):
            ch = CH[(j * 3) % len(CH)]; e0 = len(errs)
            js = """async([ch,tier])=>{const G=__G;G.SAVE.diff.max=40;G.SAVE.diff.sel=tier;window.__rt=1;window.__fin=1;G.startGame(ch);for(let i=0;i<80&&G.state!=='play';i++)await new Promise(r=>setTimeout(r,250));
              __lv(12);const fs=G.P.fset;""" + LOOP.replace('SEED', str(99 + j)).replace('SECS', str(fs)).replace('BOSS', 'false').replace('return {', 'return {fset:fs,') + "}"
            try: r = await pg.evaluate(js, [ch, tier])
            except Exception as ex: r = {'ERR': str(ex)[:300]}
            r['case'] = f'field:{tier + 1}층/{ch}'; r['console'] = errs[e0:][:5]; out.append(r); print(json.dumps(r, ensure_ascii=False)[:700], flush=True)
        bad = [r for r in out if r.get('E') or r.get('console') or r.get('ERR')]
        print('BAD', len(bad)); json.dump(out, open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'build', 'fuzz1028.json'), 'w'), ensure_ascii=False, indent=1)
        await b.close()
asyncio.run(main())
