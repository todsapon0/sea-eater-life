"""GLB hero-model loader test (phase B). Builds a tiny GLB in the browser (not committed), serves it as assets/model/sea_eater.glb,
checks: loader loads, procedural body hidden, Idle/Move/Bite clips mapped, bite plays, no page errors; and that with no asset key nothing changes.
Run: THREE_JS_PATH=/path/to/three-r128.min.js python3 test-glb.py"""
import os, base64, threading, http.server
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent; os.chdir(root)
three=Path(os.environ['THREE_JS_PATH']); exporter=three.parent.parent/'examples/js/exporters/GLTFExporter.js'
assert three.is_file() and exporter.is_file()
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=srv.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{srv.server_port}/?debug=1'
base=(root/'index.html').read_text().replace('loop();\n}','window.__g=()=>({mix:!!heroMixer,acts:Object.keys(heroActs),cur:heroCur,biting:heroBiting,glb:!!heroGlb,vis:(()=>{let n=0;sea.userData.root.traverse(o=>{if(!o.isMesh||!o.visible)return;let a=o,org=false;while(a&&a!==sea.userData.root){if(a.userData&&a.userData.t){org=true;break;}a=a.parent;}if(!org)n++;});return n;})()});loop();\n}',1)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('CHROME','/usr/bin/chromium') if os.path.exists('/usr/bin/chromium') else None,headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 t=b.new_page();t.set_content('<html></html>');t.add_script_tag(path=str(three));t.add_script_tag(path=str(exporter))
 glb=t.evaluate("""async()=>{const T=THREE,g=new T.Group(),m=new T.Mesh(new T.BoxGeometry(2,1,5),new T.MeshStandardMaterial({color:0xff00ff}));m.name='body';g.add(m);
 const tr=(n,d,v)=>new T.AnimationClip(n,d,[new T.VectorKeyframeTrack('body.position',[0,d],v)]);
 return await new Promise(r=>new T.GLTFExporter().parse(g,x=>{let u=new Uint8Array(x),s='';for(const c of u)s+=String.fromCharCode(c);r(btoa(s));},{binary:true,animations:[tr('Idle',1,[0,0,0,0,.1,0]),tr('Bite',.4,[0,0,0,0,.3,0]),tr('Move',1,[0,0,0,0,.2,0])]}));}""")
 t.close();data=base64.b64decode(glb)
 def run(enable):
  ctx=b.new_context(viewport={'width':1024,'height':768});pg=ctx.new_page();errs=[]
  pg.on('pageerror',lambda e:errs.append(str(e)))
  html=base.replace('"model/sea_eater":"glb",','').replace('const ASSETS={','const ASSETS={'+('"model/sea_eater":"glb",' if enable else ''),1)
  def route(r):
   u=r.request.url
   if 'three.min.js' in u:r.fulfill(path=str(three),content_type='application/javascript')
   elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
   elif ('/assets/model/' in u and u.endswith('.glb')):r.fulfill(body=data,content_type='model/gltf-binary')
   elif u.split('?')[0]==url.split('?')[0]:r.fulfill(body=html,content_type='text/html')
   else:r.continue_()
  ctx.route('**/*',route)
  pg.add_init_script("localStorage.setItem('selcls','sea');localStorage.setItem('sel01',JSON.stringify({lv:5,xp:0,q:0,qd:0,inv:{},seen:{}}));")
  pg.goto(url,wait_until='networkidle');pg.wait_for_function('window.__g');pg.wait_for_timeout(1500)
  r=pg.evaluate('__g()')
  if enable:
   pg.keyboard.press('Space');pg.wait_for_timeout(100);r2=pg.evaluate('__g()');pg.wait_for_timeout(900);r3=pg.evaluate('__g()')
   return r,r2,r3,errs
  return r,None,None,errs
 r,r2,r3,e=run(True)
 print('with glb:',r,r2['biting'],r3['biting'],r3['cur'],e)
 assert r['mix'] and r['glb'] and set(r['acts'])=={'Idle','Move','Bite'},r
 assert r['vis']==0,r
 assert r2['biting'] and not r3['biting'],(r2,r3)
 assert not e,e
 r,_,_,e=run(False)
 print('without:',r,e)
 assert not r['mix'] and not r['glb'] and r['vis']>0 and not e
 b.close();print('PASS test-glb')
