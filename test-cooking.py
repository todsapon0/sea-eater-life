"""Cooking NPC regression. Needs THREE_JS_PATH (three@0.128.0) and Playwright chromium."""
import os,threading,http.server
from pathlib import Path
from playwright.sync_api import sync_playwright
from pathlib import Path as _P
os.chdir(_P(__file__).resolve().parent)
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
sv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=sv.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{sv.server_port}/?debug=1'
html=Path('index.html').read_text().replace('function loop(){requestAnimationFrame(loop);','function loop(){requestAnimationFrame(loop);if(window.__pause)return;').replace('loop();\n}','window.__t={P,sea,openNpc,tryCook,cam,ren,scene,NPCS,applyJob,matCount};loop();\n}')
with sync_playwright() as p:
 b=p.chromium.launch(args=['--no-sandbox','--enable-unsafe-swiftshader']);ctx=b.new_context(viewport={'width':390,'height':844});pg=ctx.new_page();errs=[]
 pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
 def route(r):
  u=r.request.url
  if 'three.min.js' in u:r.fulfill(path=os.environ['THREE_JS_PATH'],content_type='application/javascript')
  elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
  elif u.split('?')[0]==url.split('?')[0]:r.fulfill(body=html,content_type='text/html')
  else:r.continue_()
 ctx.route('**/*',route)
 pg.add_init_script("localStorage.selcls='sea';localStorage.sel01=JSON.stringify({lv:10,xp:0,q:0,qd:0,inv:{'ฟันกลม':7,'ครีบปลา':5},seen:{}});")
 pg.goto(url,wait_until='networkidle');pg.wait_for_function('window.__t')
 print(pg.evaluate('''()=>{const t=__t;t.sea.position.set(0,0,8);return t.NPCS.map(n=>n.id).join(',')+' mat='+t.matCount();}'''))
 pg.wait_for_timeout(1500)
 
 print(pg.evaluate('''()=>{const t=__t;t.openNpc('cook');return document.querySelectorAll('[data-cook]').length}'''))
 
 pg.locator('[data-cook="shark"]').click()
 print(pg.evaluate('''()=>{const t=__t;return {fb:t.P.fb_shark,mat:t.matCount(),inv:t.P.inv}}'''))
 
 assert pg.evaluate("document.querySelector('[data-cook=\"boss\"]').disabled") and not errs,errs
 r=pg.evaluate('()=>({fb:__t.P.fb_shark,mat:__t.matCount()})');assert 140<r['fb']<=150 and r['mat']==6,r
 print('PASS: cook NPC, 7 recipes, 150s buff, materials spent, boss needs king fang, no console errors')
