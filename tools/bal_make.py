import os
R=os.path.dirname(os.path.abspath(__file__))
rd=lambda f:open(os.path.join(R,f),encoding='utf8').read()
open(os.path.join(R,'bal_js.js'),'w',encoding='utf8').write(rd('bal_head.js')+rd('bal_bot.js')+rd('bal_field.js'))
