"""Dye NPC regression. Needs THREE_JS_PATH (three@0.128.0) and Playwright chromium."""
import os,threading,http.server
from pathlib import Path
from playwright.sync_api import sync_playwright
os.chdir(Path(__file__).resolve().parent)
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
sv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=sv.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{sv.server_port}/?debug=1'+os.environ.get('DYE_CLS','')
html=Path('index.html').read_text().replace('loop();\n}','window.__t={P,openNpc,sea,NPCS};loop();\n}')
with sync_playwright() as p:
 b=p.chromium.launch(args=['--no-sandbox','--enable-unsafe-swiftshader']);ctx=b.new_context(viewport={'width':390,'height':844});pg=ctx.new_page();pg.set_default_timeout(90000);errs=[]
 pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
 def route(r):
  u=r.request.url
  if 'three.min.js' in u:r.fulfill(path=os.environ['THREE_JS_PATH'],content_type='application/javascript')
  elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
  elif u.split('?')[0]==url.split('?')[0]:r.fulfill(body=html,content_type='text/html')
  else:r.continue_()
 ctx.route('**/*',route)
 pg.add_init_script("if(!localStorage.seeded){localStorage.seeded='1';localStorage.selcls=new URLSearchParams(location.search).get('c')||'sea';localStorage.sel01=JSON.stringify({lv:5,xp:0,q:0,qd:0,inv:{},seen:{}});}")
 pg.goto(url,wait_until='networkidle');pg.wait_for_function('window.__t')
 col="(()=>{const c=__t.sea.userData.mainMat.color;return [c.r,c.g,c.b].map(x=>+x.toFixed(3)).join(',')})()"
 base=pg.evaluate(col)
 assert 'dye' in pg.evaluate("__t.NPCS.map(n=>n.id).join(',')")
 pg.evaluate("__t.openNpc('dye')");assert pg.locator('.dyeb').count()==9
 pg.locator('[data-dye="5"]').click();c5=pg.evaluate(col)
 assert pg.evaluate("__t.P.dy")==5 and c5!=base,(base,c5)
 pg.locator('[data-dye="1"]').click();assert pg.evaluate(col)!=c5
 pg.reload(wait_until='networkidle');pg.wait_for_function('window.__t')
 assert pg.evaluate("__t.P.dy")==1 and pg.evaluate(col)!=base
 pg.evaluate("__t.openNpc('dye')");pg.locator('[data-dye="0"]').click()
 assert pg.evaluate(col)==base and pg.evaluate("__t.P.dy")==0,(pg.evaluate(col),base)
 assert not errs,errs
 print('PASS: dye NPC, 9 colors, body colour changes and resets, persists across reload, no console errors')
