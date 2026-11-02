"""Landscape HUD layout overlap check on several phone/tablet viewports (iPhone 11/15 Pro, small phone, iPad 8).
Checks that fixed HUD blocks never overlap each other or the touch controls. Run: THREE_JS_PATH=/path/three.min.js python3 test-layout.py"""
import os, threading, http.server, itertools
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent; os.chdir(root)
three=Path(os.environ['THREE_JS_PATH'])
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=srv.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{srv.server_port}/'
html=(root/'index.html').read_text().replace('loop();\n}','window.__l={setMap};loop();\n}',1)
SIZES=[(852,393),(896,414),(844,390),(667,375),(1080,810),(1180,820)]
# blocks that must never overlap (pairs); the goal pill and name tags are allowed to float over the world
BLOCKS=['#goal','#zoneb','#hud','#minimap','#worldmini','#topbar','#stick','#bite','#slam','#devour','#taunt','#shield','#lockb']
def rects(pg):
 return pg.evaluate("""(sels)=>{const o={};for(const s of sels){const e=document.querySelector(s);if(!e)continue;const cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden')continue;const r=e.getBoundingClientRect();if(r.width<2||r.height<2)continue;o[s]=[r.left,r.top,r.right,r.bottom];}return o;}""",BLOCKS)
def ov(a,b,m=1):return min(a[2],b[2])-max(a[0],b[0])>m and min(a[3],b[3])-max(a[1],b[1])>m
bad=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 for w,h in SIZES:
  ctx=b.new_context(viewport={'width':w,'height':h});pg=ctx.new_page();errs=[]
  pg.on('pageerror',lambda e:errs.append(str(e)))
  def route(r):
   u=r.request.url
   if 'three.min.js' in u:r.fulfill(path=str(three),content_type='application/javascript')
   elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
   elif u.split('?')[0]==url:r.fulfill(body=html,content_type='text/html')
   else:r.continue_()
  ctx.route('**/*',route)
  pg.add_init_script("localStorage.selcls='sea';localStorage.sel01=JSON.stringify({lv:15,xp:0,q:0,qd:0,inv:{},seen:{},tu:9})")
  pg.goto(url,wait_until='networkidle');pg.wait_for_function('window.__l')
  for m in (0,1):
   pg.evaluate(f'__l.setMap({m})');pg.wait_for_timeout(900)
   R=rects(pg)
   for x,y in itertools.combinations(R,2):
    if ov(R[x],R[y]):bad.append((w,h,m,x,y,[round(v) for v in R[x]],[round(v) for v in R[y]]))
   for k,r in R.items():
    if r[0]<-1 or r[1]<-1 or r[2]>w+1 or r[3]>h+1:bad.append((w,h,m,k,'offscreen',[round(v) for v in r]))
  assert not errs,(w,h,errs)
  ctx.close()
 b.close()
for x in bad:print('OVERLAP',x)
assert not bad,f'{len(bad)} layout problems'
print('PASS: no overlaps among HUD blocks and controls on',len(SIZES),'landscape sizes')
