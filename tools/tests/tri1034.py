"""v10.34 ∞ 챌린지 전용 마왕 '무한의 삼위일체' — Lv.30 등장 · 돌진 · 룬 · 자폭 하수인 · 순환 끊기 · 2페이즈 소용돌이 · 처치 · 규칙 9 · 콘솔 오류
사용: GAME_URL=http://localhost:8765/build/hell_survive.html PYTHONPATH=tools python3 tools/tests/tri1034.py [폴더]"""
import asyncio, sys, json
from h301 import *
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else 'build/qa'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 760)
        await pg.evaluate("()=>{const S=__G.SAVE;S.ch.open=true;S.diff.max=39;S.diff.clr=38}")
        await pg.evaluate("()=>__G.startChallenge('wolf')")
        for _ in range(160):
            if await pg.evaluate("()=>__G.state==='play'&&!!__G.chal"): break
            await pg.wait_for_timeout(250)
        # Lv.30 마왕 = 삼위일체
        r = await pg.evaluate("()=>{const G=__G,P=G.P;P.inv=999;P.need=1e12;for(const e of G.enemies)e.hp=0;P.lvl=30;G.chal.next=30;G.chBossCall();return {k:G.chal.bossK,met:G.chal.triMet}}"); print('call', r)
        for _ in range(120):
            ok = await pg.evaluate("()=>{const G=__G;G.P.inv=999;G.P.hp=G.P.max;for(let i=0;i<10;i++)G.tick(1/30);return !!(G.boss&&G.boss.bk==='tri')}")
            if ok: break
            await pg.wait_for_timeout(200)
        base = "const G=__G,P=G.P,e=G.boss;P.inv=999;P.hp=P.max;P.need=1e12;G.banner=null;"
        r = await pg.evaluate("()=>{"+base+"for(let i=0;i<80;i++)G.tick(1/30);return {st:e.st,hp:Math.round(e.max),img:!!G.IMG.tri}}"); print('spawn', r)
        async def shot(n, js, ticks=0):
            await pg.evaluate("()=>{"+base+js+"for(let i=0;i<"+str(ticks)+";i++){P.inv=999;P.hp=P.max;G.tick(1/60)}G.banner=null}")
            await pg.screenshot(path=f'{OUT}/tri_{n}.png')
        await shot('dash', "e.x=P.x+300;e.y=P.y-60;e.st='chase';e.stT=0;e.ci=0;", 40)
        await shot('dashrun', "", 22)
        await shot('rune', "e.at=null;e.st='chase';e.stT=0;e.ci=1;e.x=P.x+300;e.y=P.y-80;", 50)
        await shot('bomb', "G.TRW.tele=[];e.at=null;e.st='chase';e.stT=0;e.ci=2;e.x=P.x+300;e.y=P.y-80;", 70)
        r = await pg.evaluate("()=>{"+base+"return {bombs:G.enemies.filter(q=>q.kind==='trb').length,wave:!!G.TRW.wave,loop:e.loop}}"); print('bomb', r)
        # 순환 끊기: 하수인 모두 처치
        r = await pg.evaluate("()=>{"+base+"for(const q of G.enemies)if(q.kind==='trb')G.hurtEnemy(q,q.hp+1,0,0,0,true);for(let i=0;i<5;i++)G.tick(1/60);const h0=e.hp;G.hurtEnemy(e,1000,0,0,0,true);return {st:e.st,vuln:e.vuln>0,loop:e.loop,dmg:Math.round(h0-e.hp),combo:G.chal.combo}}"); print('break', r)
        await shot('stag', "", 4)
        # 하수인이 터지면 끊기지 않음
        r = await pg.evaluate("()=>{"+base+"e.st='chase';e.stT=0;e.ci=2;e.vuln=0;for(let i=0;i<90;i++){P.inv=999;G.tick(1/60)}const B=G.enemies.filter(q=>q.kind==='trb');for(const q of B){q.x=P.x+10;q.y=P.y}for(let i=0;i<200;i++){P.inv=999;P.hp=P.max;G.tick(1/60)}return {st:e.st,left:G.enemies.filter(q=>q.kind==='trb'&&q.hp>0).length,wave:!!G.TRW.wave}}"); print('boom', r)
        # 2페이즈
        r = await pg.evaluate("()=>{"+base+"e.hp=e.max*0.49;e.st='chase';e.stT=0;for(let i=0;i<10;i++)G.tick(1/60);const st=e.st;for(let i=0;i<140;i++){P.inv=999;P.hp=P.max;G.tick(1/60)}return {st0:st,ph2:e.ph2,st:e.st}}"); print('ph2', r)
        r = await pg.evaluate("()=>{"+base+"e.st='chase';e.stT=0;e.ci=3;for(let i=0;i<5;i++)G.tick(1/60);return {vort:!!G.TRW.vort,st:e.st}}"); print('vort', r)
        await shot('vort', "", 80)
        # 규칙 9: 소용돌이 안에서 걸어 나가기 — 끌림 < 이속
        r = await pg.evaluate("()=>{"+base+"return {pull:G.TRI.vort.pull,spd:P.spd,dashW:G.TRI.dash.w,minWarn:+(G.TRI.dash.warn*(1-G.TRI.loopMax*G.TRI.loopK)).toFixed(2),bombSp:G.TRI.bomb.sp}}"); print('rule9', r)
        # 처치
        r = await pg.evaluate("()=>{"+base+"G.TRW.vort=null;e.st='chase';e.invul=false;e.vuln=0;e.hp=5;G.hurtEnemy(e,1e9,0,0,0);for(let i=0;i<30;i++){P.inv=999;G.tick(1/60)}return {dead:!G.boss||G.boss.hp<=0,tot:G.SAVE.ch.triTot,kill:G.SAVE.dex.kills.boss25,death:!!G.TRW.death,bossN:G.chal.bossN}}"); print('kill', r)
        await shot('death', "", 30)
        r = await pg.evaluate("()=>{const G=__G;G.chStatsLive();return {ach:!!G.SAVE.ach.done.c_tri}}"); print('ach', r)
        print('오류:', pg.errs); await b.close()
asyncio.run(main())
