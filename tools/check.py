"""문법 확인: 템플릿의 메인 <script> 를 node --check 로 검사"""
import os,subprocess,sys,tempfile
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s=open(os.path.join(ROOT,'src','game_template.html'),encoding='utf8').read()
i=s.index('<script>',s.index('</style>')); j=s.rindex('</script>')
f=tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf8'); f.write(s[i+8:j]); f.close()
r=subprocess.run(['node','--check',f.name],capture_output=True,text=True); print(r.stderr[:1500] or 'syntax ok'); sys.exit(1 if r.returncode else 0)
