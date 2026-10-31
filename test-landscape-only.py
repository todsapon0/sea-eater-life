"""Landscape-only regression: portrait shows the rotate hint; landscape does not; automation skips it unless ?portrait=1."""
import os,threading,http.server
from pathlib import Path
from playwright.sync_api import sync_playwright
os.chdir(Path(__file__).resolve().parent)
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
sv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=sv.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{sv.server_port}/';html=Path('index.html').read_text()
vis="getComputedStyle(document.getElementById('rotatehint')).display"
with sync_playwright() as p:
 b=p.chromium.launch(args=['--no-sandbox','--enable-unsafe-swiftshader']);errs=[]
 def mk(w,h):
  ctx=b.new_context(viewport={'width':w,'height':h});pg=ctx.new_page();pg.set_default_timeout(90000)
  pg.on('pageerror',lambda e:errs.append(str(e)))
  def route(r):
   u=r.request.url
   if 'three.min.js' in u:r.fulfill(path=os.environ['THREE_JS_PATH'],content_type='application/javascript')
   elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
   elif u.split('?')[0]==base:r.fulfill(body=html,content_type='text/html')
   else:r.continue_()
  ctx.route('**/*',route);pg.add_init_script("localStorage.selcls='sea';");return pg
 pg=mk(390,844);pg.goto(base+'?debug=1',wait_until='load');assert pg.evaluate(vis)=='none','automation portrait must not be blocked by default'
 pg=mk(390,844);pg.goto(base+'?debug=1&portrait=1',wait_until='load');assert pg.evaluate(vis)=='flex','portrait shows rotate hint';assert 'แนวนอน' in pg.evaluate("document.getElementById('rotatehint').innerText")
 pg=mk(844,390);pg.goto(base+'?debug=1&portrait=1',wait_until='load');assert pg.evaluate(vis)=='none','landscape never shows it'
 assert not errs,errs
 print('PASS: portrait shows rotate hint (with ?portrait=1 under automation), landscape and default automation do not')
