import http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
os.chdir(os.path.dirname(os.path.abspath(__file__)))
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
sv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=sv.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{sv.server_port}/'
html=Path('index.html').read_text().replace('loop();\n}','window.__t={mons,kill,spawn,P,MAPS,xpFactor};loop();\n}')
with sync_playwright() as p:
 b=p.chromium.launch(args=['--no-sandbox','--enable-unsafe-swiftshader']);ctx=b.new_context(viewport={'width':844,'height':390});pg=ctx.new_page();pg.set_default_timeout(90000);errs=[]
 pg.on('pageerror',lambda e:errs.append(str(e)))
 def route(r):
  u=r.request.url
  if 'three.min.js' in u:r.fulfill(path=os.environ['THREE_JS_PATH'],content_type='application/javascript')
  elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
  elif u.split('?')[0]==base:r.fulfill(body=html,content_type='text/html')
  else:r.continue_()
 ctx.route('**/*',route);pg.add_init_script("localStorage.selcls='sea';")
 pg.goto(base+'?debug=1',wait_until='networkidle');pg.wait_for_timeout(1200)
 r=pg.evaluate("""()=>{const t=__t,mv=t.mons.filter(m=>m.mvp),out={};out.maps=mv.map(m=>m.map).sort((a,b)=>a-b);out.names=mv.every(m=>m.ty.nm.startsWith('👑 ราชา'));
  out.hp=mv.every(m=>Math.abs(m.mhp-m.ty.hp*t.MAPS[m.map].hpScale*1.8*6)<1e-6&&m.hp===m.mhp);
  out.normalCount=t.mons.filter(m=>!m.mvp).length;out.total=t.mons.length;
  const m=mv[0],dr=m.ty.dr,before=t.P.inv[dr]||0,kc=t.P.kc[m.ty.n]||0;t.kill(m);out.mvpDead=m.dead;out.drop=(t.P.inv[dr]||0)-before>=3;out.kc=(t.P.kc[m.ty.n]||0)-kc;
  t.spawn(m);out.respawnHp=m.hp===m.mhp&&m.dead===0;
  const n=t.mons.find(q=>!q.mvp&&q.ty.n!=='boss');t.kill(n);out.normalDead=n.dead;
  const a=t.mons.find(q=>q.map===1),ar=t.mons.find(q=>t.MAPS[q.map].arena),f=l=>{t.P.lv=l;return +t.xpFactor(a).toFixed(2);};out.xf=[f(5),f(6),f(7),f(16),f(60)];t.P.lv=60;out.xfArena=t.xpFactor(ar);
  return out;}""")
 print(json.dumps(r,ensure_ascii=False))
 assert r['maps']==[2,3,6,8,9,10,11,13,15],r
 assert r['names'] and r['hp'],r
 assert r['mvpDead']==480 and r['drop'] and r['kc']==1 and r['respawnHp'] and r['normalDead']==6,r
 assert r['total']==175,r
 assert r['xf']==[1,1,.9,.2,.2],r
 assert r['xfArena']==1,r
 assert not errs,errs[:2]
 print('PASS: 9 MVP elites in far maps, HP x6, 8-minute respawn, extra drops, normal monsters unchanged, 175 monsters')
