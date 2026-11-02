import http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
os.chdir(os.path.dirname(os.path.abspath(__file__)))
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
sv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=sv.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{sv.server_port}/'
html=Path('index.html').read_text().replace('loop();\n}','window.__t={P,weeklyAdd,weeklyInit,weeklyPick,weeklyHtml,weekIdx,WK_POOL};loop();\n}')
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
 r=pg.evaluate("""()=>{const t=__t,o={};const wk=t.weeklyInit(),L=t.weeklyPick(wk.w);o.ids=L.map(m=>m[0]);o.distinct=new Set(o.ids).size===3;o.html=t.weeklyHtml().includes('ภารกิจประจำสัปดาห์');
  const pearl0=t.P.inv['ไข่มุกทะเล']||0;const first=L[0];t.weeklyAdd(first[0],first[1]);o.f0=t.P.wk.f[0];o.pearl1=(t.P.inv['ไข่มุกทะเล']||0)-pearl0;
  t.weeklyAdd(first[0],5);o.noDouble=(t.P.inv['ไข่มุกทะเล']||0)-pearl0===o.pearl1;
  L.forEach(m=>t.weeklyAdd(m[0],m[1]));o.allDone=t.P.wk.f.every(x=>x===1);o.bonus=(t.P.inv['ไข่มุกทะเล']||0)-pearl0>=2*3+5;
  t.P.wk.w-=1;const w2=t.weeklyInit();o.reset=w2.w===t.weekIdx()&&w2.k.every(x=>x===0);return o;}""")
 print(json.dumps(r,ensure_ascii=False))
 assert r['distinct'] and r['html'] and r['f0']==1 and r['pearl1']==2 and r['noDouble'] and r['allDone'] and r['bonus'] and r['reset']
 pg.evaluate("__t.weeklyAdd('kill',1)");pg.reload(wait_until='networkidle');pg.wait_for_timeout(800)
 assert pg.evaluate("__t.P.wk&&__t.P.wk.w===__t.weekIdx()"),'week persists'
 assert not errs,errs[:2]
 print('PASS: weekly missions pick 3 distinct, reward once each + bonus, reset on new week, persist across reload')
