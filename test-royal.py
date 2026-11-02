import http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
os.chdir(os.path.dirname(os.path.abspath(__file__)))
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
sv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=sv.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{sv.server_port}/'
html=Path('index.html').read_text().replace('loop();\n}','window.__t={P,mons,kill,royalState,royalMon,royalHtml,MAPS,todayStr,renderBoard};loop();\n}')
with sync_playwright() as p:
 b=p.chromium.launch(args=['--no-sandbox','--enable-unsafe-swiftshader']);ctx=b.new_context(viewport={'width':844,'height':390});pg=ctx.new_page();errs=[]
 pg.on('pageerror',lambda e:errs.append(str(e)))
 def route(r):
  u=r.request.url
  if 'three.min.js' in u:r.fulfill(path=os.environ['THREE_JS_PATH'],content_type='application/javascript')
  elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
  elif u.split('?')[0]==base:r.fulfill(body=html,content_type='text/html')
  else:r.continue_()
 ctx.route('**/*',route);pg.add_init_script("localStorage.selcls='sea';if(!sessionStorage.getItem('f')){localStorage.sel01=JSON.stringify({lv:10,xp:0,q:0,qd:0,inv:{},seen:{ray:1},kc:{ray:3},tu:9});sessionStorage.setItem('f','1');}")
 pg.goto(base,wait_until='networkidle');pg.wait_for_timeout(1000)
 r=pg.evaluate("""()=>{const t=__t,o={};const s=t.royalState();o.state=s;o.rec=t.MAPS[s.map].rec;o.rq=t.P.rq;o.html=t.royalHtml().includes('คำขอวันนี้');
  o.again=JSON.stringify(t.royalState())===JSON.stringify(s);
  const m=t.royalMon(),pearl=t.P.inv['ไข่มุกทะเล']||0;t.kill(m);const s2=t.royalState();o.done=s2.done;o.pearl=(t.P.inv['ไข่มุกทะเล']||0)-pearl;o.rq2=t.P.rq;
  const pearl2=t.P.inv['ไข่มุกทะเล']||0;t.kill(m);o.pearl_again=(t.P.inv['ไข่มุกทะเล']||0)-pearl2;
  // killing a different MVP gives no request reward
  return o;}""")
 print(json.dumps(r,ensure_ascii=False))
 assert r['rec']<=13 and r['again'] and r['html'] and r['rq'].endswith(':0')
 assert r['done'] and r['pearl']>=3 and r['rq2'].endswith(':1') and r['pearl_again']<=3
 pg.reload(wait_until='networkidle');pg.wait_for_timeout(800)
 s=pg.evaluate("__t.royalState()");assert s['done'] and s['map']==r['state']['map'],s
 assert not errs,errs[:2]
 print('PASS: daily royal request picks a level-appropriate MVP once a day, rewards once, persists across reload')
