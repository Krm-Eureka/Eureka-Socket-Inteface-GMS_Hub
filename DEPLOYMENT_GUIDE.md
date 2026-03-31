# ESIG HUB: IIS Offline Deployment Guide

คู่มือนี้ครอบคลุมขั้นตอนการ Deploy จากเครื่อง Development (มีอินเทอร์เน็ต) ไปยังเครื่อง Target (ไม่มีอินเทอร์เน็ต)

---

## 🛠 ส่วนที่ 1: เตรียมการบนเครื่อง Dev (มีเน็ต)

### 1.1 ดาวน์โหลดข้อมูลล่าสุด
```powershell
cd "d:\KRM\25\25LA001 - Mektec\MEKTEC_APP\ESIG"
git pull origin main
```

### 1.2 แพ็คโครงการ (รวม Offline Packages)
รันสคริปต์ `pack_project.py` เพื่อดาวน์โหลดไลบรารีและสร้างไฟล์ Archive:
```powershell
py pack_project.py
```
*   **สิ่งที่ได้:** ไฟล์ `ESIG_HUB.tar.gz` (รวบรวมโค้ดและไลบรารีทั้งหมด)
*   **Check:** ตรวจสอบว่ามีโฟลเดอร์ `packages_offline/` ถูกสร้างขึ้น

---

## 🖥 ส่วนที่ 2: ติดตั้งบนเครื่อง Target (ไม่มีเน็ต)

### 2.1 ตรวจสอบเบื้องต้น
1.  ติดตั้ง **Python 3.10+** (ถ้ายังไม่มี)
2.  ติดตั้ง **IIS Feature: WebSocket Protocol**
3.  ติดตั้ง **IIS Extension: HttpPlatformHandler v1.2**

### 2.2 แตกไฟล์โครงการ
```powershell
# สร้างโฟลเดอร์ปลายทาง
mkdir C:\inetpub\wwwroot\ESIG_HUB
# แตกไฟล์จาก USB/Network Share
tar -xzvf E:\ESIG_HUB.tar.gz -C C:\inetpub\wwwroot\ESIG_HUB
```

### 2.3 ติดตั้ง Python Packages (Offline)
```powershell
cd C:\inetpub\wwwroot\ESIG_HUB
pip install --no-index --find-links=.\packages_offline -r requirements.txt
```

### 2.4 ตรวจสอบความพร้อม (Diagnostics)
รันสคริปต์ตรวจสอบสภาพแวดล้อม:
```powershell
py check_iis.py
```
> [!IMPORTANT]
> แก้ไขรายการที่ขึ้น ❌ FAIL ให้เป็น ✅ PASS ก่อนดำเนินการต่อ

---

## 🌐 ส่วนที่ 3: ตั้งค่า IIS

### 3.1 สร้าง Website
1.  เปิด **IIS Manager** -> **Add Website**
2.  **Site name:** `ESIG_HUB`
3.  **Physical path:** `C:\inetpub\wwwroot\ESIG_HUB`
4.  **Port:** `1244`

### 3.2 ตั้งค่า Application Pool
1.  เลือก Pool `ESIG_HUB` -> **Basic Settings** -> **.NET CLR version:** `No Managed Code`
2.  **Advanced Settings** -> **Process Model** -> **Identity:** เปลี่ยนเป็น `LocalSystem` (เพื่อสิทธิ์ในการเขียน Log)

### 3.3 สิทธิ์ในการเข้าถึงไฟล์
```powershell
icacls "C:\inetpub\wwwroot\ESIG_HUB" /grant "IIS_IUSRS:(OI)(CI)M" /T
```

---

## 🚨 การตรวจสอบและแก้ไขปัญหา (Troubleshooting)

*   **HTTP 502/500:** ตรวจสอบ `logs/iis_uvicorn.log` เพื่อดู Startup Banner
*   **Socket ไม่เชื่อมต่อ:** ตรวจสอบว่าเปิด **WebSocket Protocol** ใน Windows Features หรือยัง
*   **GMS/DB Connected:** ดูผลลัพธ์จาก `startup_diagnostics` ใน Log ไฟล์

---

**ESIG HUB v2.0.2**  
*Update: 2026-03-27*
