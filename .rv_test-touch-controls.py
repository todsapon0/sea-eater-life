"""Local Chromium touch regression; uses the same prerequisites as test-evolution.py.
Run: THREE_JS_PATH=/path/to/three-r128.min.js python3 test-touch-controls.py
No real backend requests or production saves. Images stay outside the repository.
"""
import os, json, threading, http.server
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent
os.chdir(root)
artifacts=Path(os.environ.get('EVOLUTION_ARTIFACTS','/tmp/sea-evolution'))
artifacts.mkdir(parents=True,exist_ok=True)
three=Path(os.environ.get('THREE_JS_PATH','/tmp/sea-evolution/three.min.js'))
assert three.is_file(), 'Set THREE_JS_PATH to a trusted local Three.js r128 file'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/?debug=1'
html=(root/'index.html').read_text().replace('loop();\n}', 'window.__touchTest=()=>({jx,jz,sid,biteT});loop();\n}')
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 for width,height in [(390,844),(844,390),(320,568),(768,1024),(1024,768),(844,500)]:
  context=browser.new_context(viewport={'width':width,'height':height},has_touch=True,is_mobile=True)
  page=context.new_page();errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
  def route(r):
   u=r.request.url
   if 'three.min.js' in u:r.fulfill(path=str(three),content_type='application/javascript')
   elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
   elif '.supabase.co' in u:raise AssertionError('Unexpected backend request')
   elif u.split('?')[0]==url.split('?')[0]:r.fulfill(body=html,content_type='text/html')
   else:r.continue_()
  context.route('**/*',route)
  page.add_init_script("localStorage.setItem('selcls','sea');localStorage.setItem('sel01',JSON.stringify({lv:1,xp:0,q:0,qd:0,inv:{},seen:{}}));")
  page.goto(url,wait_until='networkidle');assert page.locator('#accountGate').count()==0;page.wait_for_function('window.__touchTest')
  # Every action stays independently tappable on phones AND iPad dimensions.
  controls=['#bite','#slam','#devour','#taunt','#shield','#lockb','#stick']
  boxes={sel:page.locator(sel).bounding_box() for sel in controls}
  for sel,a in boxes.items():
   assert a['x']>=0 and a['y']>=0 and a['x']+a['width']<=width and a['y']+a['height']<=height,(sel,a)
   for other,b in boxes.items():
    if sel>=other:continue
    overlap=min(a['x']+a['width'],b['x']+b['width'])>max(a['x'],b['x']) and min(a['y']+a['height'],b['y']+b['height'])>max(a['y'],b['y'])
    assert not overlap,('controls overlap',sel,other,a,b)
   if sel!='#stick':
    hit=page.evaluate('([x,y])=>document.elementFromPoint(x,y).id',[a['x']+a['width']/2,a['y']+a['height']/2])
    assert hit==sel[1:],('control obscured',sel,hit)
  cdp=context.new_cdp_session(page)
  def pt(i,x,y):return {'id':i,'x':x,'y':y,'radiusX':7,'radiusY':7,'force':1}
  def touch(kind,*points):cdp.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':list(points)})
  rect=page.locator('#stick').bounding_box();zone=page.locator('#movezone').bounding_box()
  assert rect['width']>=132 and zone['width']>rect['width']
  cx=rect['x']+rect['width']/2;cy=rect['y']+rect['height']/2
  yaw=page.evaluate('__cam.yaw')
  # Start just outside the visible circle: still movement, never camera drag.
  miss=min(zone['x']+zone['width']-2,rect['x']+rect['width']+8)
  target=page.evaluate('([x,y])=>document.elementFromPoint(x,y).id',[miss,cy]);assert target=='movezone',target
  touch('touchStart',pt(1,miss,cy));assert page.evaluate('__touchTest().jx')>0
  touch('touchMove',pt(1,miss+70,cy-90))
  assert page.evaluate('__cam.yaw')==yaw
  assert page.evaluate('__touchTest().sid') is not None
  touch('touchEnd');assert page.evaluate('__touchTest().jx===0 && __touchTest().jz===0 && __touchTest().sid===null')
  # A second touch on the pad must not steal the first pointer.
  touch('touchStart',pt(1,cx+30,cy));owner=page.evaluate('__touchTest().sid')
  touch('touchStart',pt(1,cx+30,cy),pt(2,cx-25,cy))
  assert page.evaluate('__touchTest().sid')==owner
  touch('touchEnd',pt(2,cx-25,cy))
  assert page.evaluate('__touchTest().sid')==owner
  # Walking + attack at the same time, with no camera motion.
  bite=page.locator('#bite').bounding_box();bx=bite['x']+bite['width']/2;by=bite['y']+bite['height']/2
  touch('touchStart',pt(1,cx+30,cy),pt(3,bx,by))
  assert page.evaluate('__touchTest().jx>0 && __touchTest().biteT>0')
  assert page.evaluate('__cam.yaw')==yaw
  touch('touchEnd');assert page.evaluate('__touchTest().sid===null')
  # Walking + intentional camera drag use independent pointers, not pinch zoom.
  camx=width*.55;camy=height*.35;dist=page.evaluate('__cam.dist')
  touch('touchStart',pt(1,cx+30,cy))
  touch('touchStart',pt(1,cx+30,cy),pt(4,camx,camy))
  touch('touchMove',pt(1,cx+30,cy),pt(4,camx+40,camy))
  assert page.evaluate('__cam.yaw')!=yaw
  assert page.evaluate('__cam.dist')==dist
  assert page.evaluate('__touchTest().jx')>0
  touch('touchEnd')
  # Cancellation resets the joystick so walking cannot get stuck.
  touch('touchStart',pt(1,cx+30,cy));touch('touchCancel')
  assert page.evaluate('__touchTest().sid===null && __touchTest().jx===0')
  # Two fingers on the canvas retain pinch-to-zoom.
  touch('touchStart',pt(5,camx,camy))
  touch('touchStart',pt(5,camx,camy),pt(6,camx+40,camy))
  touch('touchMove',pt(5,camx-20,camy),pt(6,camx+60,camy))
  assert page.evaluate('__cam.dist')<dist
  touch('touchEnd')
  page.screenshot(path=str(artifacts/f'touch-controls-{width}x{height}.png'))
  assert not errors,errors
  print(json.dumps({'viewport':[width,height],'stick_width':rect['width'],'movement_pad':zone,'result':'PASS: near-miss, capture, multitouch, attack, independent camera, cancel and pinch','errors':errors}),flush=True)
  context.close()
 browser.close()
server.shutdown()
