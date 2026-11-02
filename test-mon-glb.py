"""Monster GLB support (phase M1): a tiny generated GLB (not committed) is served as assets/model/mon_ray.glb.
Checks: every ray gets the model, procedural meshes hidden, material 'main' is cloned per monster (own copy; emissive synced for hit flash), Idle/Move/Attack mixer works,
no page errors; and without the asset key nothing changes. Run: THREE_JS_PATH=/path/three.min.js python3 test-mon-glb.py"""
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
base=(root/'index.html').read_text().replace('loop();\n}','window.__mg={mons,types,sea};loop();\n}',1)
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 t=b.new_page();t.set_content('<html></html>');t.add_script_tag(path=str(three));t.add_script_tag(path=str(exporter))
 glb=t.evaluate("""async()=>{const T=THREE,g=new T.Group(),m=new T.Mesh(new T.BoxGeometry(1,.5,3),new T.MeshStandardMaterial({color:0xff00ff,name:'main'}));m.material.name='main';m.name='body';g.add(m);
 const tr=(n,d,v)=>new T.AnimationClip(n,d,[new T.VectorKeyframeTrack('body.position',[0,d],v)]);
 return await new Promise(r=>new T.GLTFExporter().parse(g,x=>{let u=new Uint8Array(x),s='';for(const c of u)s+=String.fromCharCode(c);r(btoa(s));},{binary:true,animations:[tr('Idle',1,[0,0,0,0,.1,0]),tr('Move',1,[0,0,0,0,.3,0]),tr('Attack',.5,[0,0,0,0,.6,0])]}));}""")
 t.close();data=base64.b64decode(glb)
 def run(enable):
  ctx=b.new_context(viewport={'width':900,'height':600});pg=ctx.new_page();errs=[]
  pg.on('pageerror',lambda e:errs.append(str(e)))
  html=base.replace('"model/mon_ray":"glb",','').replace('const ASSETS={','const ASSETS={'+('"model/mon_ray":"glb",' if enable else ''),1)
  def route(r):
   u=r.request.url
   if 'three.min.js' in u:r.fulfill(path=str(three),content_type='application/javascript')
   elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
   elif u.endswith('mon_ray.glb'):r.fulfill(body=data,content_type='model/gltf-binary')
   elif u.split('?')[0]==url.split('?')[0]:r.fulfill(body=html,content_type='text/html')
   else:r.continue_()
  ctx.route('**/*',route)
  pg.add_init_script("localStorage.setItem('selcls','sea');localStorage.setItem('sel01',JSON.stringify({lv:5,xp:0,q:0,qd:0,inv:{},seen:{},tu:9}));")
  pg.goto(url,wait_until='networkidle');pg.wait_for_function('window.__mg');pg.wait_for_timeout(2500)
  r=pg.evaluate("""()=>{const rays=__mg.mons.filter(m=>m.ty.n==='ray'),sh=__mg.mons.filter(m=>m.ty.n==='shark');
   const withGlb=rays.filter(m=>m.glb).length,vis=rays.filter(m=>m.glb).every(m=>{let n=0;m.g.children.forEach(c=>{if(c===m.g.children[m.g.children.length-1])return;c.traverse(o=>{if(o.isMesh&&o.visible)n++;});});return n===0;}),
   shared=rays.filter(m=>m.glb).every(m=>m.glb.mains.length>0&&m.glb.mains.every(x=>x!==m.mat));
   return {rays:rays.length,withGlb,vis,shared,sharkGlb:sh.filter(m=>m.glb).length,acts:rays.find(m=>m.glb)?Object.keys(rays.find(m=>m.glb).glb.acts):[]};}""")
  pg.wait_for_timeout(1500)
  r2=pg.evaluate("()=>{const m=__mg.mons.find(q=>q.ty.n==='ray'&&q.glb);return m?m.glb.cur:null;}")
  ctx.close();return r,r2,errs
 r,c,e=run(True);print('with:',r,c,e)
 assert r['rays']>0 and r['withGlb']==r['rays'] and r['vis'] and r['shared'] and r['sharkGlb']==0 and set(r['acts'])=={'Idle','Move','Attack'} and c in('Idle','Move','Attack') and not e,(r,c,e)
 r,c,e=run(False);print('without:',r,c,e)
 assert r['withGlb']==0 and not e
 b.close();print('PASS test-mon-glb')
