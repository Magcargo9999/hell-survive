"""v6.22: 딜 미터기 이름 점검 — 모든 변형을 필드에서 돌리고 DMETER 이름에 '?'·영문 id가 없는지 확인 (사용: python3 tools/tests/dmeter22.py [변형...])"""
import asyncio, sys, os, json, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('SIMURL', 'file://' + os.path.join(ROOT, 'build', 'hell_survive.html'))
os.environ.update(RANDPICK='1', RAW='1', PAR='2', SEED='5')
sys.argv = ['sim600.py', 'L', json.dumps(sys.argv[1:] or ["wolf:blood","wolf:twin","snail:venom","snail:lava","archer:red","chimera:wind","chimera:flame","chimera:dream","lizard:guard","octo","ghost","twins"]), '1', 'std', '0']
os.environ['STAGES'] = '[[24,600]]'
exec(open(os.path.join(ROOT, 'tools', 'sim600.py'), encoding='utf8').read())
