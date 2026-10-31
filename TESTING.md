# ทดสอบ v0.5.1 บน Safari โดยไม่เปลี่ยน Production

1. เปิด branch `codex/v0.5.1-integrated` บน GitHub แล้วเลือก Code → Codespaces → Create codespace on this branch (บัญชีต้องมีสิทธิ์ใช้งาน Codespaces และอาจมีค่าใช้จ่ายตามโควตา)
2. ใน Terminal ของ Codespace รัน `python3 -m http.server 8000 --bind 0.0.0.0` แล้วเปิดแท็บ Ports หากพอร์ต 8000 ไม่ปรากฏให้เพิ่มด้วย Add Port
3. คง Port Visibility เป็น Private คัดลอก Forwarded Address ซึ่งเป็น HTTPS เปิดใน Safari บน iPad หรือ iPhone แล้วเข้าสู่ GitHub ด้วยบัญชีเจ้าของ Codespace หากระบบขอ
4. ทดสอบแนวตั้งและแนวนอน จอยพร้อมโจมตี/สกิลด้วยหลายสัมผัส รวมทั้งมอนสเตอร์หลายตัว ประสิทธิภาพ เป้าหมายอย่างน้อย 30 FPS ต้องวัดบนอุปกรณ์จริงและบันทึกวิธีวัด ระยะเวลา และสภาวะทดสอบ
5. หยุด Codespace เมื่อเลิกใช้ URL นี้แยกจาก GitHub Pages Production และไม่ต้อง merge

ข้อมูล localStorage แยกตาม origin: ลิงก์ทดสอบจะไม่เห็น save จากเว็บไซต์ Production โดยอัตโนมัติ อย่าลบ save ของ Production เพื่อทดสอบ ต้องมีสำเนาข้อมูลทดสอบและวิธีย้ายที่ปลอดภัยก่อนตรวจการอัปเกรดจาก v0.4 บนอุปกรณ์จริง

อ้างอิง: https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace และ https://docs.github.com/en/codespaces/reference/security-in-github-codespaces

## ทางเลือก Cloudflare Pages Preview (ต้องได้รับอนุมัติก่อนตั้งค่าและ deploy)

1. ใน Cloudflare dashboard เลือก Workers & Pages → Create application → Pages → Import an existing Git repository แล้วเชื่อม `todsapon0/sea-eater-life` โดยเลือกสิทธิ์ GitHub เท่าที่จำเป็น การเชื่อมต่อและ deployment เป็นการเปลี่ยนแปลงบริการภายนอก จึงต้องได้รับอนุมัติจากเจ้าของก่อน
2. สร้างโปรเจกต์ Cloudflare แยกจาก GitHub Pages เดิม โดยไม่เปลี่ยน DNS หรือ custom domain ของ Production ใช้ production branch `main`, framework ไม่มี, build command `exit 0`, build output directory `/` (ราก repo) ตรวจค่าบนหน้าจอก่อนเริ่ม; การสร้างโปรเจกต์อาจเริ่ม deploy ครั้งแรกทันที
3. หลังสร้าง ไปที่ Settings → Builds & deployments → Branch controls ปิด automatic production branch deployments และกำหนด Preview เป็น Custom branches ให้เฉพาะ `codex/v0.5.1-integrated` เพื่อลดการ deploy ที่ไม่ได้ตั้งใจ แล้วบันทึก ตรวจสถานะการตั้งค่าก่อน push เพิ่มเติม
4. หลังได้รับอนุมัติให้ deploy preview ใช้ URL preview HTTPS ที่ Cloudflare แสดงในรายการ Deployments หรือ PR ตรวจว่าเป็น commit ล่าสุดของ branch รวมก่อนทดสอบ Preview URL อาจเข้าถึงได้โดยผู้ที่มีลิงก์ ต้องตั้ง Cloudflare Access หากต้องจำกัดผู้เข้าถึง อย่าใส่ข้อมูลลับ
5. เปิดสมุด (📖) → การแสดงผล → ปุ่ม `FPS: ปิด` เพื่อเปิดตัวเลข FPS กลางขอบล่าง (จำสถานะเปิด/ปิดในเครื่อง ไม่ต้องแก้ลิงก์); หรือเพิ่ม `?debug=1` ใน URL เพื่อแสดง FPS พร้อมข้อมูลหน้าจอสำหรับวิเคราะห์ ตัวเลข FPS เป็นค่าเฉลี่ยรายวินาที มาตรวัดนี้เป็นแนวทางเบื้องต้น ไม่รับประกันว่าเสถียร: วัดบน iPad 8 และ iPhone 11 จริง บันทึกแนวหน้าจอ ระยะเวลา สถานการณ์การเล่น และช่วง FPS รวมทั้งการตกต่ำในฉากมอนสเตอร์หลายตัว เป้าหมาย 30 FPS จะถือว่าผ่านได้ต่อเมื่อวัดจริง
6. URL preview และ GitHub Pages มี origin ต่างกัน จึงไม่ใช้ localStorage ร่วมกัน ทดสอบด้วยข้อมูลแยก และหยุด/ลบ preview ตามความเหมาะสมเมื่อเสร็จ

คู่มือ Cloudflare: https://developers.cloudflare.com/pages/configuration/branch-build-controls/ และ https://developers.cloudflare.com/pages/framework-guides/deploy-anything/
