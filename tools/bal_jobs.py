"""빠진/잘못된 판을 찾아 작업 목록을 만든다. 사용: python3 tools/bal_jobs.py <패스 수> <출력 jobs.json> <결과 jsonl...>"""
import json, sys
VS = ["wolf:abyss","wolf:twin","wolf:blood","wolf:holy","wolf:fallen","snail:venom","snail:lava","snail:bomb","archer:red","archer:holy","archer:skel","chimera:wind","chimera:flame","chimera:dream","lizard:rage","lizard:water","lizard:guard","twins","ghost","octo"]
BK = ["monkey","eye","skel","fw"]
def good(d):
    b = d.get('boss') or {}
    if 'err' in d or b.get('t', 0) < 1: return False
    if not b.get('dead') and b.get('left', 0) > 0 and b.get('mx', 0) > 0 and b.get('t', 0) < 179: return False
    return True
have = set()
for fn in sys.argv[3:]:
    for l in open(fn):
        d = json.loads(l)
        if good(d): have.add((d['v'], d['bk'], d['seed']))
jobs = [[v, bk, 101 + i * 13 + j * 997] for i in range(int(sys.argv[1])) for j, bk in enumerate(BK) for v in VS if (v, bk, 101 + i * 13 + j * 997) not in have]
json.dump(jobs, open(sys.argv[2], 'w')); print(len(jobs), 'jobs')
