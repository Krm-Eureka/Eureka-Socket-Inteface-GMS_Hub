# คู่มือการใช้งาน ESIG HUB (EA Socket Interface GMS Hub) 🚀

ระบบ Middleware สำหรับเชื่อมต่อ GMS Legacy Socket เข้ากับ Web Console และระบบ Monitoring

---

## 1. การเตรียมความพร้อม (Setup)

### การติดตั้ง Libs
ก่อนรันโปรแกรมครั้งแรก ต้องติดตั้ง Dependencies ที่จำเป็น:
```bash
pip install -r requirements.txt
```

### การตั้งค่า Environment (.env)
ระบบมีสคริปต์ช่วยตั้งค่าอัตโนมัติ (Interactive Setup):
### การตั้งค่า Environment (.env)
ระบบมีสคริปต์ช่วยตั้งค่าอัตโนมัติ (Interactive Setup) รองรับทั้ง Windows และ Linux:

**Windows:**
```bash
py setup.py
```

**Linux (Ubuntu/CentOS):**
```bash
python3 setup.py
```

โปรแกรมจะถามข้อมูลที่จำเป็นทีละขั้นตอน:
1.  **Frontend URL:** ใส่ URL ของเว็บ Frontend ที่จะมาเรียกใช้งาน (เช่น `http://192.168.1.50:8000`) 
2.  **GMS IP:** IP ของเครื่อง GMS
3.  **MySQL Config:** ใส่ Host, User, Password ของฐานข้อมูล

*เมื่อเสร็จสิ้น ระบบจะสร้างไฟล์ `.env` ที่พร้อมใช้งานให้ทันทีครับ*
*(หากไม่ต้องการใช้สคริปต์ สามารถ Copy ไฟล์ `.env.example` เป็น `.env` แล้วแก้ไขค่าเองได้ครับ)*

---

## 2. การเริ่มต้นใช้งาน (Running)

รันโปรแกรมผ่าน Python:
```bash
py main.py
```
หลังจากรันสำเร็จ สามารถเข้าใช้งานผ่าน Browser ได้ที่: `http://localhost:1244` (หรือตาม IP เครื่องที่รัน)

---

## 3. ฟีเจอร์หลักในหน้า Web Console

### 🟢 หน้า CONSOLE (Real-time Logs)
- **Service Control**: กด **START SERVICE** เพื่อเริ่มเชื่อมต่อกับ GMS
- **Polling**: เปิด **Enable Polling** เพื่อให้ระบบส่งคำสั่งเช็คสถานะ GMS อัตโนมัติวนซ้ำ
- **Unified Log**: ดูข้อความที่ส่ง (SENT) และรับ (RECV) แบบ Real-time

### 📊 หน้า HEALTH (Monitoring)
- **Server Health**: ตรวจสอบการใช้งาน CPU และ RAM ของเครื่องที่รันโปรแกรม
- **MySQL Health**: ตรวจสอบสถานะฐานข้อมูล, ความเร็วในการ Query (QPS), และอัตราการตอบสนอง (Latency)
- **Storage**: ดูขนาดของฐานข้อมูลที่ใช้งานอยู่ในปัจจุบัน

### ✉️ MANUAL REQUEST (Sidebar)
- สามารถส่งคำสั่ง JSON ไปยัง GMS ได้โดยตรงเพียงระบุ `Message Type` และ `Body JSON`

---

## 4. การจัดการไฟล์ Logs
ระบบจะบันทึก Log ทั้งหมดลงในโฟลเดอร์ `logs/`:
- **server.log**: เก็บประวัติการทำงานของระบบ (จะทำการ Rotate อัตโนมัติเมื่อไฟล์เกิน 10MB)

---

---

## 6. การแพ็คไฟล์เพื่อส่งมอบ (Packing with TAR)

หากต้องการรวบรวมไฟล์ทั้งหมดเพื่อนำไปติดตั้งที่เครื่องอื่น (Deploy):
1. **ใช้ Python (แนะนำ):** รันคำสั่งใน Terminal:
   ```bash
   py pack_project.py
   ```
2. **ใช้ PowerShell:** คลิกขวาที่ไฟล์ `pack_project.ps1` แล้วเลือก **Run with PowerShell**
3. **Manual:** หรือรันคำสั่งโดยตรง:
   ```bash
   tar -czvf ESIG_HUB.tar.gz --exclude=__pycache__ --exclude=.git --exclude=.venv --exclude=logs .
   ```
*ระบบจะสร้างไฟล์ `ESIG_HUB.tar.gz` ซึ่งตัดไฟล์ที่ไม่จำเป็นออกให้โดยอัตโนมัติ*

---

---

## 7. วิธีการติดตั้งระดับมืออาชีพ (Deployment Depth)

### 🪟 วิธีที่ 1: ติดตั้งบน Windows (ผ่าน IIS)
เหมาะสำหรับการรันบน Server ที่ต้องการให้ระบบเปิดเองเมื่อ Restart เครื่อง

1.  **ติดตั้ง HttpPlatformHandler:**
    - ดาวน์โหลดและติดตั้ง [HttpPlatformHandler v1.2](https://www.iis.net/downloads/microsoft/httpplatformhandler) (เป็น Extension ของ IIS)
2.  **เตรียมโฟลเดอร์:**
    - นำไฟล์ที่ได้จากการแตกไฟล์ `.tar.gz` ไปวางใน Path ที่ต้องการ (เช่น `C:\inetpub\wwwroot\ESIG_HUB`)
3.  **ตั้งค่า IIS:**
    - เปิด **IIS Manager** -> คลิกขวาที่ **Sites** -> เลือก **Add Website**
    - ระบุ **Site name** (เช่น ESIG_HUB) และ **Physical path** ไปที่โฟลเดอร์โปรเจกต์
    - กำหนด **Port** (เช่น 1244)
4.  **แก้ไขไฟล์ web.config:**
    - เข้าไปที่โฟลเดอร์ `deployment/` แล้วแก้ไขไฟล์ `web.config`
    - ตรงส่วน `processPath` ให้ระบุ Path ของ `python.exe` ในเครื่องท่าน เช่น:
      `processPath="C:\Python311\python.exe"`
    - ตรวจสอบว่า `arguments` ระบุไฟล์ `main:socket_app` (ไม่ใช่ bff_main) ถูกต้อง
5.  **ตรวจสอบสิทธิ์ (Permissions):**
    - ตรวจสอบว่า User `IIS AppPool\ESIG_HUB` (หรือชื่อสถ่านะ Site) มีสิทธิ์ **Read/Write** ในโฟลเดอร์ `logs/`

---

### 🐧 วิธีที่ 2: ติดตั้งบน Linux (Ubuntu/CentOS ผ่าน systemd)
เหมาะสำหรับ Production ที่ต้องการความเสถียรสูงสุดและระบบ Auto-restart

1.  **เตรียม Virtual Environment:**
    ```bash
    cd /path/to/ESIG_HUB
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
2.  **สร้างไฟล์ Service:**
    - สร้างไฟล์ชื่อ `/etc/systemd/system/esigh.service` ด้วยคำสั่ง `sudo nano`
    - คัดลอกเนื้อหานี้ไปวาง (ปรับ Path ให้ตรงตามจริง):
    ```ini
    [Unit]
    Description=ESIG HUB Service
    After=network.target

    [Service]
    User=youruser
    Group=www-data
    WorkingDirectory=/path/to/ESIG_HUB
    Environment="PATH=/path/to/ESIG_HUB/venv/bin"
    ExecStart=/path/to/ESIG_HUB/venv/bin/python main.py
    Restart=always
    RestartSec=5

    [Install]
    WantedBy=multi-user.target
    ```
3.  **เปิดใช้งาน Service:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable esigh
    sudo systemctl start esigh
    ```
4.  **วิธีดู Log การรัน:**
    ```bash
    sudo journalctl -u esigh -f
    ```

---

## 8. การตั้งค่า Firewall
อย่าลืมเปิดพอร์ตในระบบเพื่อให้เครื่องอื่นเข้าใช้งานได้:
- **Windows:** ตั้งค่า Inbound Rule ใน Windows Firewall สำหรับ Port ที่ระบุใน IIS
- **Linux:** `sudo ufw allow 1244/tcp` (หรือเครื่องมืออื่นๆ เช่น firewalld)
