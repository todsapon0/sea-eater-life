import http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
os.chdir(os.path.dirname(os.path.abspath(__file__)))
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
sv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=sv.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{sv.server_port}/'
html=Path('index.html').read_text().replace('loop();\n}','window.__t={P,sea,setMap,evtSpawn,updateEvent,updateGoal,getEvt:()=>evt,FOODKEYS};loop();\n}')
with sync_playwright() as p:
 b=p.chromium.launch(args=['--no-sandbox','--enable-unsafe-swiftshader']);ctx=b.new_context(viewport={'width':844,'height':390});pg=ctx.new_page();errs=[]
 pg.on('pageerror',lambda e:errs.append(str(e)))
 def route(r):
  u=r.request.url
  if 'three.min.js' in u:r.fulfill(path=os.environ['THREE_JS_PATH'],content_type='application/javascript')
  elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
  elif u.split('?')[0]==base:r.fulfill(body=html,content_type='text/html')
  else:r.continue_()
 ctx.route('**/*',route);pg.add_init_script("localStorage.selcls='sea';localStorage.sel01=JSON.stringify({lv:10,xp:0,q:0,qd:0,inv:{},seen:{ray:1},kc:{ray:3},tu:9});")
 pg.goto(base,wait_until='networkidle');pg.wait_for_timeout(1000)
 r=pg.evaluate("""()=>{const t=__t,o={};
  t.setMap(0);for(let i=0;i<5;i++)t.updateEvent(100);o.townNoEvent=t.getEvt()===null;
  t.setMap(1);t.evtSpawn();const e=t.getEvt();o.spawned=!!e&&e.map===1;t.updateGoal(1);o.goalTxt=document.getElementById('gtx').textContent;
  e.kind='chest';const p0=t.P.inv['ไข่มุกทะเล']||0;t.sea.position.set(e.x,0,e.z);t.updateEvent(.1);o.chestPearl=(t.P.inv['ไข่มุกทะเล']||0)-p0;o.cleared1=t.getEvt()===null;
  t.evtSpawn();const e2=t.getEvt();e2.kind='bubble';t.sea.position.set(e2.x,0,e2.z);t.updateEvent(.1);o.food=t.FOODKEYS.some(k=>(t.P['fb_'+k]||0)>0);o.cleared2=t.getEvt()===null;
  t.evtSpawn();t.getEvt().t=.05;t.sea.position.set(-1000,0,-1000);t.updateEvent(.1);o.expired=t.getEvt()===null;
  t.evtSpawn();t.setMap(5);t.updateEvent(.1);o.mapChangeClears=t.getEvt()===null;
  return o;}""")
 print(json.dumps(r,ensure_ascii=False))
 assert r['townNoEvent'] and r['spawned'] and 'ปรากฏ' in r['goalTxt']
 assert r['chestPearl']>=1 and r['cleared1'] and r['food'] and r['cleared2'] and r['expired'] and r['mapChangeClears']
 assert not errs,errs[:2]
 print('PASS: random map events spawn only in field maps, show in the goal pill, chest/bubble rewards, expire and clear on map change')
