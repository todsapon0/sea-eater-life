"""What's New popup regression. Needs THREE_JS_PATH (three@0.128.0) and Playwright chromium."""
import os,threading,http.server
from pathlib import Path
from playwright.sync_api import sync_playwright
os.chdir(Path(__file__).resolve().parent)
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
sv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=sv.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{sv.server_port}/'
html=Path('index.html').read_text()
with sync_playwright() as p:
 b=p.chromium.launch(args=['--no-sandbox','--enable-unsafe-swiftshader']);ctx=b.new_context(viewport={'width':390,'height':844});pg=ctx.new_page();pg.set_default_timeout(90000);errs=[]
 pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
 def route(r):
  u=r.request.url
  if 'three.min.js' in u:r.fulfill(path=os.environ['THREE_JS_PATH'],content_type='application/javascript')
  elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
  elif u.split('?')[0]==base:r.fulfill(body=html,content_type='text/html')
  else:r.continue_()
 ctx.route('**/*',route)
 pg.add_init_script("localStorage.selcls='sea';if(!localStorage.seeded){localStorage.seeded='1';localStorage.sel01=JSON.stringify({lv:5,xp:0,q:0,qd:0,inv:{},seen:{}});}")
 # automation (webdriver) must NOT show the popup by default so other tests are unaffected
 pg.goto(base+'?debug=1',wait_until='networkidle');pg.wait_for_timeout(1500)
 assert pg.evaluate("getComputedStyle(document.getElementById('whatsnew')).display")=='none'
 assert 'v0.8.0' in pg.title() and 'v0.8.0' in pg.evaluate("document.getElementById('gver').textContent")
 # forced popup shows, lists rows, closes, and remembers the version
 pg.goto(base+'?debug=1&whatsnew=1',wait_until='networkidle');pg.wait_for_timeout(2000)
 assert pg.evaluate("getComputedStyle(document.getElementById('whatsnew')).display")=='flex'
 assert pg.locator('#whatsnew .wrow').count()==6
 pg.locator('#wnok').click()
 assert pg.evaluate("getComputedStyle(document.getElementById('whatsnew')).display")=='none'
 assert pg.evaluate("localStorage.getItem('seenver')").startswith('v0.8.0')
 assert not errs,errs
 print('PASS: single GAME_VERSION in title/HUD, What\'s New popup forced via ?whatsnew=1, 6 rows, closes and remembers version, hidden under automation by default')
