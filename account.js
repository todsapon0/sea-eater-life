/* Server account mode is opt-in. Legacy saves remain in localStorage. */
window.startAccount = async function startAccount({ online = false } = {}) {
  // Child-friendly default: no login DOM, password autofill or account requests.
  if (!online) return { storage: localStorage, remote: false };
  const root = document.createElement('section');
  root.id = 'accountGate';
  root.innerHTML = '<div class="account-card"><h1>Sea Eater Life</h1><p>บัญชีผู้เล่น</p><p id="accountError" role="alert"></p><form id="accountForm"><label>อีเมล <input id="accountEmail" type="email" autocomplete="username" required></label><label>รหัสผ่าน <input id="accountPassword" type="password" autocomplete="current-password" required></label><button type="submit">เข้าสู่ระบบ</button></form><button id="localPlay" type="button">เล่นแบบในเครื่อง</button><p>เซฟในเครื่องแยกจากเซฟบัญชี และไม่ถูกย้ายอัตโนมัติ</p></div>';
  document.body.append(root);
  const error = root.querySelector('#accountError');
  const form = root.querySelector('#accountForm');
  const local = root.querySelector('#localPlay');
  const cfg = window.SEA_ACCOUNT_CONFIG || {};
  function publicKeyOnly(key) {
    if (!key || /^sb_secret_/i.test(key)) return false;
    if (key.startsWith('sb_publishable_')) return true;
    try {
      const payload = key.split('.')[1].replace(/-/g,'+').replace(/_/g,'/');
      return JSON.parse(atob(payload)).role === 'anon';
    } catch (_) { return false; }
  }
  const remoteConfigured = /^https:\/\/[a-z0-9-]+\.supabase\.co$/i.test(cfg.url || '') && publicKeyOnly(cfg.publishableKey || '');
  if (!remoteConfigured) {
    error.textContent = 'ยังไม่ได้ตั้งค่าเซิร์ฟเวอร์บัญชี กรุณาติดต่อผู้ดูแล';
    form.querySelector('button').disabled = true;
  }
  return new Promise(resolve => {
    local.onclick = () => { root.remove(); resolve({ storage: localStorage, remote: false }); };
    let client=null;
    function getClient(){
      if(!client){
        if(!window.supabase) throw new Error('โหลดระบบบัญชีไม่สำเร็จ ตรวจอินเทอร์เน็ต');
        // persistSession keeps this device signed in, so the password is not asked again on the same device.
        client=window.supabase.createClient(cfg.url, cfg.publishableKey, {auth:{persistSession:true,autoRefreshToken:true}});
      }
      return client;
    }
    // One account can own up to three characters (one per class). Each has its own save row, level and quest.
    async function showPicker(user) {
      const c=getClient();
      const {data: rows, error: readError} = await c.from('player_characters').select('character_class,save_data,revision').eq('user_id',user.id);
      if (readError || !Array.isArray(rows)) throw new Error('โหลดเซฟจากเซิร์ฟเวอร์ไม่สำเร็จ');
      form.remove(); local.remove(); error.textContent = 'เลือกตัวละคร (บัญชีเดียวมีได้หลายตัว เลเวลและเควสแยกกัน)';
      const select = document.createElement('div');
      const lock=()=>select.querySelectorAll('button').forEach(x=>x.disabled=true);
      for (const [id,label] of [['sea','Sea Eater'],['bloop','Bloop'],['maja','El Gran Maja']]) {
        const have=rows.find(r=>r.character_class===id);
        const b=document.createElement('button'); b.type='button';
        b.textContent=have ? label+' Lv.'+(have.save_data && have.save_data.lv|0) : 'สร้างตัวละคร '+label;
        b.onclick=async()=>{
          lock();
          if (have) { finish(c,user.id,have); return; }
          const initial={lv:1,xp:0,qd:0,q:0,inv:{},seen:{}};
          const result=await c.from('player_characters').insert({user_id:user.id,character_class:id,save_data:initial}).select('character_class,save_data,revision').single();
          if(result.error){error.textContent='สร้างตัวละครไม่สำเร็จ โปรดเข้าสู่ระบบใหม่เพื่อตรวจเซฟ';return;}
          finish(c,user.id,result.data);
        };
        select.append(b);
      }
      const out=document.createElement('button'); out.type='button'; out.textContent='ออกจากระบบ (เครื่องนี้)';
      out.onclick=async()=>{try{await c.auth.signOut();}catch(_){}location.reload();};
      select.append(out);
      root.querySelector('.account-card').append(select);
    }
    if (remoteConfigured && window.supabase) {
      (async()=>{
        try {
          const {data}=await getClient().auth.getSession();
          if (data && data.session && data.session.user) { error.textContent='กำลังโหลดตัวละคร…'; await showPicker(data.session.user); }
        } catch (_) { error.textContent=''; }
      })();
    }
    form.onsubmit = async e => {
      e.preventDefault();
      if (!remoteConfigured) return;
      const submit = form.querySelector('button');
      submit.disabled = true; error.textContent = 'กำลังเข้าสู่ระบบ…';
      try {
        const c = getClient();
        const { data: auth, error: loginError } = await c.auth.signInWithPassword({email:root.querySelector('#accountEmail').value,password:root.querySelector('#accountPassword').value});
        root.querySelector('#accountPassword').value = '';
        if (loginError || !auth.user) throw new Error('เข้าสู่ระบบไม่สำเร็จ ตรวจอีเมลและรหัสผ่าน');
        await showPicker(auth.user);
      } catch (err) { error.textContent=err.message || 'เชื่อมต่อไม่สำเร็จ'; submit.disabled=false; }
    };
    function finish(client,userId,row) {
      const record=row.save_data;
      const object=value=>value && typeof value==='object' && !Array.isArray(value);
      if (!['sea','bloop','maja','crab'].includes(row.character_class) || !object(record) ||
          !Number.isInteger(record.lv) || record.lv<1 || record.lv>20 ||
          !Number.isFinite(record.xp) || record.xp<0 || !Number.isInteger(record.qd) ||
          record.qd<0 || record.qd>2 || !Number.isInteger(record.q) || record.q<0 ||
          record.q >= [5,10,20][record.qd] || !object(record.inv) || !object(record.seen) ||
          !Number.isInteger(row.revision) || row.revision<0) {
        error.textContent='ข้อมูลเซฟบนเซิร์ฟเวอร์ไม่ถูกต้อง กรุณาติดต่อผู้ดูแล'; return;
      }
      const key={sea:'sel01',bloop:'sel01b',maja:'sel01m',crab:'sel01c'}[row.character_class];
      // A separate journal for this project and authenticated account; never use legacy save keys.
      const journalKey='sel-account-pending-v2:'+cfg.url+':'+userId+':'+row.character_class;
      let revision=row.revision, pending=null, saving=false, blocked=false, timer=null, attempts=0, inflight=null;
      let current=JSON.stringify(row.save_data), durable=true;
      let journal, expectedJournal=null;
      try {
        const raw=localStorage.getItem(journalKey);
        expectedJournal=raw;
        if(raw) {
          journal=JSON.parse(raw);
          if(journal.userId!==userId || journal.classId!==row.character_class ||
              !Number.isInteger(journal.baseRevision) || journal.baseRevision<0 ||
              typeof journal.snapshot!=='string' || !object(JSON.parse(journal.snapshot)) ||
              (journal.inflight!==null && typeof journal.inflight!=='string')) throw new Error('invalid journal');
          revision=journal.baseRevision; pending=current=journal.snapshot; inflight=journal.inflight;
        }
      } catch (_) {
        error.textContent='อ่านข้อมูลค้างไม่ได้ หยุดเล่นและติดต่อผู้ดูแล'; return;
      }
      const status=document.createElement('div'); status.id='accountStatus'; document.body.append(status);
      const retry=document.createElement('button'); retry.type='button'; retry.textContent='ลองบันทึกอีกครั้ง'; retry.hidden=true; status.append(retry);
      const backup=document.createElement('button'); backup.type='button'; backup.textContent='ดาวน์โหลดเซฟค้าง'; backup.hidden=true; status.append(backup);
      backup.onclick=()=>{if(pending===null)return;const url=URL.createObjectURL(new Blob([pending],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='sea-eater-pending-save.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
      const label=document.createElement('span'); label.textContent='เซฟบัญชี: โหลดแล้ว'; status.prepend(label);
      function show(message,canRetry=false){label.textContent=message;retry.hidden=!canRetry;backup.hidden=pending===null;}
      function persist(){
        try {
          if(localStorage.getItem(journalKey)!==expectedJournal){blocked=true;durable=false;show('พบเซฟค้างจากอีกแท็บ หยุดเล่นและดาวน์โหลดเซฟค้าง',false);return false;}
          const next=JSON.stringify({userId,classId:row.character_class,baseRevision:revision,snapshot:pending,inflight});
          localStorage.setItem(journalKey,next);expectedJournal=next;
          durable=true;return true;
        } catch (_) {
          durable=false;blocked=true;show('เซฟค้างเก็บในเครื่องไม่สำเร็จ หยุดเล่นและอย่าปิดหน้านี้',false);return false;
        }
      }
      function schedule(){
        if(blocked || timer) return;
        const delay=Math.min(30000,1000*Math.pow(2,Math.min(attempts++,5)));
        timer=setTimeout(()=>{timer=null;flush();},delay);
      }
      function canonical(v){if(Array.isArray(v))return v.map(canonical);if(object(v))return Object.keys(v).sort().reduce((o,k)=>(o[k]=canonical(v[k]),o),{});return v;}
      function checkError(result){if(!result.error)return;if(result.status>=400 && result.status<500 && result.status!==408 && result.status!==429){blocked=true;show('เซฟต้องตรวจสอบสิทธิ์หรือการตั้งค่า หยุดเล่นและดาวน์โหลดเซฟค้าง');}throw new Error('request failed');}
      function withTimeout(request){let timeout;return Promise.race([request,new Promise((_,reject)=>{timeout=setTimeout(()=>reject(new Error('timeout')),15000);})]).finally(()=>clearTimeout(timeout));}
      async function checkServer(){
        const result=await withTimeout(client.from('player_characters').select('character_class,save_data,revision').eq('user_id',userId).eq('character_class',row.character_class).maybeSingle());
        checkError(result);if(!result.data){blocked=true;show('ไม่พบเซฟบัญชีบนเซิร์ฟเวอร์ หยุดเล่นและดาวน์โหลดเซฟค้าง');throw new Error('missing row');}
        const server=result.data;
        if(server.character_class!==row.character_class) return false;
        if(server.revision===revision) return true;
        // A response may have been lost after a successful write. Only accept the exact sent snapshot.
        if(inflight!==null && server.revision===revision+1 && JSON.stringify(canonical(server.save_data))===JSON.stringify(canonical(JSON.parse(inflight)))){
          revision=server.revision;inflight=null;
          if(!persist()) return false;
          return true;
        }
        return false;
      }
      const storage={
        getItem(k){if(k==='selcls')return row.character_class;if(k===key)return current;return null;},
        setItem(k,value){if(k!==key)return;current=String(value);pending=current;if(!persist())return; if(!blocked){show('เซฟบัญชี: รอส่งไปเซิร์ฟเวอร์',true);queueMicrotask(flush);}},
        removeItem(){}
      };
      async function flush(){
        if(saving || blocked || pending===null)return;
        saving=true;
        show('เซฟบัญชี: กำลังลองบันทึก',true);
        try {
          if(!await checkServer()){
            if(!blocked){blocked=true;show('เซฟขัดแย้งกับอีกเครื่อง หยุดเล่น ข้อมูลค้างยังอยู่ในเครื่อง',false);}return;
          }
          const snapshot=pending;
          inflight=snapshot;if(!persist())return;
          const result=await withTimeout(client.from('player_characters').update({save_data:JSON.parse(snapshot),revision:revision+1}).eq('user_id',userId).eq('character_class',row.character_class).eq('revision',revision).select('revision').maybeSingle());
          checkError(result);
          if(!result.data){blocked=true;show('เซฟขัดแย้งกับอีกเครื่อง หยุดเล่น ข้อมูลค้างยังอยู่ในเครื่อง',false);return;}
          revision=result.data.revision;inflight=null;attempts=0;
          if(pending===snapshot){
            // Remove only after the server confirms this exact snapshot.
            try {if(localStorage.getItem(journalKey)!==expectedJournal)throw new Error('journal changed');localStorage.removeItem(journalKey);expectedJournal=null;pending=null;show('เซฟบัญชี: บันทึกแล้ว');}
            catch(_){blocked=true;show('เซฟบนเซิร์ฟเวอร์แล้ว แต่จัดการสำเนาในเครื่องไม่ได้ หยุดเล่น');}
          } else if(persist()) show('เซฟบัญชี: รอส่งไปเซิร์ฟเวอร์',true);
        } catch(_) {
          if(!blocked){show(durable?'เซฟค้างในเครื่อง รออินเทอร์เน็ต':'เซฟค้างเก็บในเครื่องไม่สำเร็จ',true);schedule();}
        } finally {saving=false;if(!blocked && pending!==null && !timer)queueMicrotask(flush);}
      }
      retry.onclick=()=>{if(timer){clearTimeout(timer);timer=null;}attempts=0;flush();};
      window.addEventListener('online',()=>{if(timer){clearTimeout(timer);timer=null;}if(!blocked)flush();});
      if(pending!==null){show('พบเซฟค้างในเครื่อง กำลังตรวจเซิร์ฟเวอร์',true);queueMicrotask(flush);}
      root.remove(); resolve({storage,remote:true});
    }
  });
};

