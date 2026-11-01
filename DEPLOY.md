# การ deploy และการทดสอบ

เกมเป็นไฟล์สถิต (`index.html` กับไฟล์ข้างเคียง) ไม่ต้อง build เพื่อเล่น

## Production (เกมจริงของครอบครัว)
- GitHub Pages ชี้ที่สาขา `main` เท่านั้น
- Cloudflare Pages `sea-eater-test` ปิด "automatic production branch deployments" ไว้ ไม่มีอะไร deploy ขึ้น Production เองจากการ push
- ไม่ merge เข้า `main` จนกว่าเจ้าของทดสอบบนอุปกรณ์จริงและอนุมัติ

## Preview สำหรับทดสอบบน iPad 8 / iPhone 11 / iPhone 15 Pro
Cloudflare Pages `sea-eater-test` → Settings → Branch control → Preview branch = **Custom branches**
รายการ Include ตอนนี้:

- `codex/ios-safari-controls`
- `codex/v0.5.1-safari-combined`
- `codex/v0.5.2-game-feel`
- `codex/roadmap-a1-a2-export`
- `codex/player-account-server-save`
- `claude/family-build`

สาขาที่ไม่อยู่ในรายการจะถูกข้าม (skipped) และไม่มี URL ให้เปิด ถ้าเปิดสาขาใหม่ ต้องเพิ่มชื่อสาขาในรายการนี้ก่อน ลิงก์พรีวิวจะถูกโพสต์เป็นคอมเมนต์ใน PR โดยบอท Cloudflare

ทดสอบบนพรีวิวจริงเสมอ ไม่ใช่ในหน้า claude.ai หรือกรอบแสดงผลอื่น เพราะกรอบเหล่านั้นกว้างกว่าจอโทรศัพท์ทำให้ปุ่มล้นจอ

## ระบบบัญชีออนไลน์ (Supabase) ยังไม่เปิดในพรีวิวนี้
`account-config.js` ใน git เว้นว่างไว้โดยตั้งใจ (repo เป็น Public) เกมจึงเล่นในโหมดเครื่องตัวเองได้ตามปกติ

ถ้าจะเปิดบัญชีในพรีวิว:
1. Cloudflare → Settings → Variables and Secrets → ฝั่ง Preview เพิ่ม
   `SUPABASE_URL` และ `SUPABASE_PUBLISHABLE_KEY` (publishable/anon เท่านั้น ห้ามใช้ service-role)
2. Settings → Builds → Build command = `node build-config.mjs`
3. สคริปต์ `build-config.mjs` จะเขียน `account-config.js` ตอน build และปฏิเสธถ้าคีย์ไม่ปลอดภัย

## ทดสอบอัตโนมัติ (ไม่ต้องใช้เน็ต)
```
node test-save-tools.cjs
node test-account-recovery.cjs
```
