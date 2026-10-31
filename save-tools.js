/* SAVE-001: import a save backup and copy/paste a save code.
 * Pure functions only (no DOM) so they can be tested with node.
 * Works with the same backup format the existing Export button writes:
 *   { format:'sea-eater-save', version:1, characters:{sea|bloop|maja:{...}}, selectedClass? }
 */
(function (root) {
  'use strict';
  var FORMAT = 'sea-eater-save', VERSION = 1, PREFIX = 'SEL1.', MAX_TEXT = 200000;
  var CLASS_KEYS = { sea: 'sel01', bloop: 'sel01b', maja: 'sel01m' };
  var CLASS_NAMES = { sea: 'Sea Eater', bloop: 'Bloop', maja: 'El Gran Maja' };

  var isPlain = function (v) { return v !== null && typeof v === 'object' && !Array.isArray(v); };
  var isInt = function (v, lo, hi) { return typeof v === 'number' && isFinite(v) && Math.floor(v) === v && v >= lo && v <= hi; };
  var fail = function (m) { throw new Error(m); };

  function checkRecord(name, r) {
    if (!isPlain(r)) fail('เซฟของ ' + CLASS_NAMES[name] + ' รูปแบบไม่ถูกต้อง');
    if (!isInt(r.lv, 1, 20)) fail('เลเวลของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง');
    if (r.xp !== undefined && !(typeof r.xp === 'number' && isFinite(r.xp) && r.xp >= 0 && r.xp <= 1e7)) fail('EXP ของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง');
    if (r.qd !== undefined && !isInt(r.qd, 0, 2)) fail('เควสต์ของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง');
    if (r.q !== undefined && !isInt(r.q, 0, 20)) fail('ความคืบหน้าเควสต์ของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง');
    ['rf', 'rp'].forEach(function (f) {
      if (r[f] === undefined) return;
      if (!isPlain(r[f])) fail('ตีบวกของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง');
      Object.keys(r[f]).forEach(function (k) { if (['head', 'back', 'tail'].indexOf(k) < 0 || !isInt(r[f][k], 0, 10)) fail('ตีบวกของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง'); });
    });
    if (r.ar !== undefined && !(typeof r.ar === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(r.ar))) fail('สนามคลื่นของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง');
    if (r.tr !== undefined && (!Array.isArray(r.tr) || r.tr.length > 26 || r.tr.some(function (id, i, a) { return typeof id !== 'string' || !/^[cp](?:[1-9]|1[0-3])$/.test(id) || a.indexOf(id) !== i; }))) fail('สมบัติของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง');
    if (r.dy !== undefined && !isInt(r.dy, 0, 8)) fail('สีของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง');
    if (r.ta !== undefined && !(typeof r.ta === 'string' && r.ta.length <= 20)) fail('ฉายาของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง');
    if (r.ev !== undefined && !isInt(r.ev, 0, 3)) fail('ขั้นวิวัฒนาการไม่ถูกต้อง');
    if (r.es !== undefined && !isInt(r.es, 0, 1e7)) fail('เอสเซนส์ไม่ถูกต้อง');
    if (r.mu !== undefined) {
      if (!isPlain(r.mu) || (Object.getPrototypeOf(r.mu) !== Object.prototype && Object.getPrototypeOf(r.mu) !== null)) fail('อวัยวะไม่ถูกต้อง');
      Object.keys(r.mu).forEach(function (k) { if (['head','back','tail'].indexOf(k) < 0 || typeof r.mu[k] !== 'string' || r.mu[k].length > 20) fail('อวัยวะไม่ถูกต้อง'); });
    }
    if (r.st !== undefined && !isInt(r.st, 0, 10)) fail('ดาวระดับของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง');
    if (r.job !== undefined && !(typeof r.job === 'string' && r.job.length <= 20)) fail('อาชีพของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง');
    if (r.kc !== undefined) {
      if (!isPlain(r.kc)) fail('สถิติของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง');
      Object.keys(r.kc).forEach(function (k) { if (k.length > 30 || !isInt(r.kc[k], 0, 1e7)) fail('สถิติของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง'); });
    }
    if (r.dly !== undefined && r.dly !== null) {
      var d = r.dly, okArr = function (a, f) { return Array.isArray(a) && a.length === 3 && a.every(f); };
      if (!isPlain(d) || typeof d.d !== 'string' || d.d.length > 12 || typeof d.last !== 'string' || d.last.length > 12 || !isInt(d.s, 0, 99999) ||
          !okArr(d.k, function (v) { return isInt(v, 0, 9999); }) || !okArr(d.f, function (v) { return v === 0 || v === 1; }) || !(d.b === 0 || d.b === 1) ||
          !okArr(d.qs, function (q) { return isPlain(q) && typeof q.e === 'string' && q.e.length <= 20 && isInt(q.n, 1, 999); })) fail('ภารกิจรายวันของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง');
    }
    ['inv', 'seen'].forEach(function (f) {
      if (r[f] === undefined) return;
      if (!isPlain(r[f])) fail('ข้อมูล ' + f + ' ของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง');
      Object.keys(r[f]).forEach(function (k) {
        var v = r[f][k];
        if (f === 'inv' && k.indexOf('eq:') === 0 && !/^eq:(fang|helm|jaw|bub|horn|scale|fin|shell|wing|crys|whip|rud|spike|glow|orb|crest|spine|lance):([1-9]|1[0-9]|20):(common|rare|epic)$/.test(k)) fail('อุปกรณ์ในเซฟไม่ถูกต้อง');
        if (k.length > 60 || !(f === 'inv' ? isInt(v, 0, 99999) : (v === 1 || v === true))) fail('ข้อมูล ' + f + ' ของ ' + CLASS_NAMES[name] + ' ไม่ถูกต้อง');
      });
    });
  }

  // Parse and validate backup JSON text. Throws Error (Thai message) when anything is wrong.
  function parseBackup(text) {
    if (typeof text !== 'string' || !text.trim()) fail('ไม่มีข้อมูลเซฟ');
    if (text.length > MAX_TEXT) fail('ข้อมูลเซฟใหญ่เกินไป');
    var b;
    try { b = JSON.parse(text); } catch (e) { fail('ข้อมูลเซฟไม่ใช่ JSON ที่อ่านได้'); }
    if (!isPlain(b) || b.format !== FORMAT) fail('ไม่ใช่ไฟล์เซฟของ Sea Eater Life');
    if (b.version !== VERSION) fail('เซฟเวอร์ชันนี้ยังไม่รองรับ');
    if (!isPlain(b.characters)) fail('ไม่พบข้อมูลตัวละครในเซฟ');
    var names = Object.keys(b.characters);
    if (!names.length) fail('ไม่พบข้อมูลตัวละครในเซฟ');
    names.forEach(function (n) {
      if (!Object.prototype.hasOwnProperty.call(CLASS_KEYS, n)) fail('พบตัวละครที่ไม่รู้จักในเซฟ');
      checkRecord(n, b.characters[n]);
    });
    if (b.selectedClass !== undefined && (!Object.prototype.hasOwnProperty.call(CLASS_KEYS, b.selectedClass) || !Object.prototype.hasOwnProperty.call(b.characters, b.selectedClass))) fail('ตัวละครที่เลือกในเซฟไม่ถูกต้อง');
    return b;
  }

  function toB64Url(text) {
    var bytes = new TextEncoder().encode(text), s = '';
    for (var i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]);
    return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }
  function fromB64Url(code) {
    var s = code.replace(/-/g, '+').replace(/_/g, '/');
    while (s.length % 4) s += '=';
    var bin;
    try { bin = atob(s); } catch (e) { fail('รหัสเซฟไม่ถูกต้อง'); }
    var bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    try { return new TextDecoder('utf-8', { fatal: true }).decode(bytes); } catch (e) { fail('รหัสเซฟไม่ถูกต้อง'); }
  }

  // Backup object -> short text code that can be pasted into chat/notes.
  function encodeCode(backup) {
    parseBackup(JSON.stringify(backup));
    return PREFIX + toB64Url(JSON.stringify(backup));
  }
  // Text code (or raw backup JSON) -> validated backup object.
  function decodeCode(text) {
    var t = String(text || '').replace(/\s+/g, '');
    if (!t) fail('ไม่มีรหัสเซฟ');
    if (t.charAt(0) === '{') return parseBackup(String(text).trim());
    if (t.indexOf(PREFIX) !== 0) fail('รหัสเซฟต้องขึ้นต้นด้วย ' + PREFIX);
    return parseBackup(fromB64Url(t.slice(PREFIX.length)));
  }

  function levelOf(storage, key) {
    var raw = storage.getItem(key);
    if (raw === null || raw === undefined) return null;
    try { var r = JSON.parse(raw); return r && isInt(r.lv, 1, 99) ? r.lv : '?'; } catch (e) { return '?'; }
  }

  // Decide what an import would write, without writing anything.
  function planImport(backup, storage) {
    var writes = [], lines = [], names = Object.keys(backup.characters);
    names.forEach(function (n) {
      var key = CLASS_KEYS[n], old = levelOf(storage, key), nw = backup.characters[n].lv;
      writes.push([key, JSON.stringify(backup.characters[n])]);
      lines.push(CLASS_NAMES[n] + ': Lv.' + nw + (old === null ? ' (ไม่มีเซฟเดิม)' : ' (เขียนทับ Lv.' + old + ')'));
    });
    var current = storage.getItem('selcls');
    var sel = backup.selectedClass || (current && Object.prototype.hasOwnProperty.call(CLASS_KEYS, current) ? current : names[0]);
    return { writes: writes, selcls: sel, lines: lines };
  }

  // Apply a plan. If any write fails, everything touched is put back as it was.
  function applyImport(storage, plan) {
    var keys = plan.writes.map(function (w) { return w[0]; }).concat(['selcls']);
    var before = keys.map(function (k) { return [k, storage.getItem(k)]; });
    try {
      plan.writes.forEach(function (w) { storage.setItem(w[0], w[1]); });
      storage.setItem('selcls', plan.selcls);
    } catch (e) {
      before.forEach(function (p) { try { if (p[1] === null || p[1] === undefined) storage.removeItem(p[0]); else storage.setItem(p[0], p[1]); } catch (x) { /* best effort */ } });
      fail('บันทึกเซฟที่นำเข้าไม่สำเร็จ ข้อมูลเดิมถูกคืนให้แล้ว');
    }
  }

  root.SeaSaveTools = { parseBackup: parseBackup, encodeCode: encodeCode, decodeCode: decodeCode, planImport: planImport, applyImport: applyImport, CODE_PREFIX: PREFIX };
  if (typeof module !== 'undefined' && module.exports) module.exports = root.SeaSaveTools;
})(typeof window !== 'undefined' ? window : globalThis);
