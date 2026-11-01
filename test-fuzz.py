"""Random-play soak: for every map, walk/bite/use skills at random for a few seconds, cross warps, and check for page errors,
console errors and NaN positions. Run: THREE_JS_PATH=/path/three.min.js python3 test-fuzz.py"""
import os, random, threading, http.server
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent; os.chdir(root)
three=Path(os.environ['THREE_JS_PATH']);random.seed(7)
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=srv.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{srv.server_port}/'
html=(root/'index.html').read_text().replace('loop();\n}','window.__f={setMap,sea,cam,PORTALS,MAPS,P};loop();\n}',1)
errs=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 import sys
 CLASSES=sys.argv[1:] or ['sea','bloop','maja']
 for cls in CLASSES:
  ctx=b.new_context(viewport={'width':852,'height':393});pg=ctx.new_page()
  pg.on('pageerror',lambda e:errs.append(('pageerror',cls,str(e))))
  pg.on('console',lambda m:errs.append(('console',cls,m.text)) if m.type=='error' else None)
  def route(r):
   u=r.request.url
   if 'three.min.js' in u:r.fulfill(path=str(three),content_type='application/javascript')
   elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
   elif u.split('?')[0]==url:r.fulfill(body=html,content_type='text/html')
   else:r.continue_()
  ctx.route('**/*',route)
  pg.add_init_script(f"localStorage.selcls='{cls}';localStorage.sel01=JSON.stringify({{lv:20,xp:0,q:0,qd:0,inv:{{}},seen:{{}},tu:9}});localStorage.sel01b=localStorage.sel01;localStorage.sel01m=localStorage.sel01;")
  pg.goto(url,wait_until='networkidle');pg.wait_for_function('window.__f')
  for m in range(16):
   pg.evaluate(f'__f.setMap({m})');pg.wait_for_timeout(300)
   for step in range(4):
    k=random.choice('wasd');pg.keyboard.down(k)
    for act in random.sample([' ','e','q','r','f','Space'],2):
     try:pg.keyboard.press(act)
     except Exception:pass
    pg.wait_for_timeout(250);pg.keyboard.up(k)
   bad=pg.evaluate("()=>{const f=__f;return [f.sea.position.x,f.sea.position.y,f.sea.position.z,f.cam.position.x,f.cam.position.y,f.cam.position.z].some(v=>!isFinite(v))}")
   if bad:errs.append(('nan',cls,m))
   # walk into a random warp circle to cross maps
   pg.evaluate("()=>{const f=__f,cur=f.PORTALS.filter(p=>f.sea&&p.g&&p.g.visible);if(cur.length){const p=cur[Math.floor(Math.random()*cur.length)];f.sea.position.set(p.x,0,p.z);}}");pg.wait_for_timeout(400)
  ctx.close()
 b.close()
for e in errs:print('ERR',e)
assert not errs,f'{len(errs)} errors'
print('PASS: random play over 16 maps x 3 characters, no page/console errors or NaN positions')
