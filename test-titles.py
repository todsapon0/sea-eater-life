"""Titles/medals regression. Needs THREE_JS_PATH (three@0.128.0) and Playwright chromium."""
import os,threading,http.server
from pathlib import Path
from playwright.sync_api import sync_playwright
os.chdir(Path(__file__).resolve().parent)
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
sv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=sv.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{sv.server_port}/?debug=1'
html=Path('index.html').read_text().replace('loop();\n}','window.__t={P,openNpc,sea};loop();\n}')
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
 pg.add_init_script("if(!localStorage.seeded){localStorage.seeded='1';localStorage.selcls='sea';localStorage.sel01=JSON.stringify({lv:10,xp:0,q:0,qd:0,inv:{},seen:{ray:1,shark:1},kc:{ray:40,shark:15}});}")
 pg.goto(url,wait_until='networkidle');pg.wait_for_function('window.__t')
 pg.evaluate("__t.openNpc('board')")
 n=pg.locator('.ttb').count();on=pg.locator('.ttb:not([disabled])').count()
 assert n==15 and on>=3,(n,on)  # new, h50 (55 kills), l10
 pg.locator('[data-title="h50"]').click()
 assert pg.evaluate("__t.P.ta")=='h50'
 pg.wait_for_timeout(600)
 assert 'นักล่าฝึกหัด' in pg.evaluate("document.querySelector('.nametag.me').textContent"),pg.evaluate("document.querySelector('.nametag.me').textContent")
 assert pg.locator('[data-title="h1000"]').is_disabled()
 pg.reload(wait_until='networkidle');pg.wait_for_function('window.__t')
 assert pg.evaluate("__t.P.ta")=='h50' and not errs,errs
 pg.evaluate("__t.P.ta='bogus';");pg.wait_for_timeout(600)
 assert 'bogus' not in pg.evaluate("document.querySelector('.nametag.me').textContent")
 print('PASS: titles unlock from stats, wear/unwear, name tag, persists across reload, unknown title ignored, no console errors')
