
export const ROBOT_ERROR_MAP = {
    "21220": {
        "exception": {
            "en": "Identify tray exceeding error",
            "th": "ตรวจพบจำนวนถาดเกินกำหนด (Tray Exceeding)"
        },
        "solution": {
            "en": "Manual handling",
            "th": "กรุณาดำเนินการด้วยตนเอง"
        }
    },
    "21221": {
        "exception": {
            "en": "Tray QR code Identification timeout",
            "th": "การระบุ QR Code บนถาดหมดเวลา"
        },
        "solution": {
            "en": "Manual handling",
            "th": "กรุณาดำเนินการด้วยตนเอง"
        }
    },
    "21222": {
        "exception": {
            "en": "The forklift has reached the end of the task, but the baffle has not been triggered",
            "th": "รถโฟล์คลิฟท์ถึงจุดหมายแล้ว แต่เซนเซอร์กั้น (Baffle) ไม่ทำงาน"
        },
        "solution": {
            "en": "Manual handling",
            "th": "กรุณาดำเนินการด้วยตนเอง"
        }
    },
    "21223": {
        "exception": {
            "en": "The baffle is not triggered during the forklift load travel",
            "th": "เซนเซอร์กั้น (Baffle) ไม่ทำงานขณะรถโฟล์คลิฟท์บรรทุกของ"
        },
        "solution": {
            "en": "Manual handling",
            "th": "กรุณาดำเนินการด้วยตนเอง"
        }
    },
    "21224": {
        "exception": {
            "en": "pallet identification timeout",
            "th": "การค้นหาพาเลท (Pallet) หมดเวลา"
        },
        "solution": {
            "en": "Manual handling",
            "th": "กรุณาดำเนินการด้วยตนเอง"
        }
    },
    "13009": {
        "exception": {
            "en": "Charging station push rod extension failure",
            "th": "ก้านดันสถานีชาร์จยืดออกไม่สำเร็จ"
        },
        "solution": {
            "en": "Please handle the exception manually",
            "th": "กรุณาจัดการข้อผิดพลาดด้วยตนเอง"
        }
    },
    "13010": {
        "exception": {
            "en": "Charging station push rod retraction failed",
            "th": "ก้านดันสถานีชาร์จหดกลับไม่สำเร็จ"
        },
        "solution": {
            "en": "Please handle the exception manually",
            "th": "กรุณาจัดการข้อผิดพลาดด้วยตนเอง"
        }
    },
    "21119": {
        "exception": {
            "en": "Road section online",
            "th": "สถานะเส้นทางออนไลน์"
        },
        "solution": {
            "en": "Manual handling",
            "th": "ดำเนินการด้วยตนเอง"
        }
    },
    "21602": {
        "exception": {
            "en": "lang.rms.monitor.robot.modelSendFailedCode",
            "th": "ส่งข้อมูลโมเดลล้มเหลว (Model Send Failed)"
        },
        "solution": {
            "en": "1. Check if the upper computer of the robot is started; 2. Check if the IP and port issued by the model are correct (robot. https. server. sendModelUri | robot. https. server. sendBoxModelUri); 3. Check if the configuration of the shelf model is correct",
            "th": "1. ตรวจสอบคอมพิวเตอร์หลักหุ่นยนต์ 2. ตรวจสอบ IP/Port และ Model URI 3. ตรวจสอบการตั้งค่าชั้นวาง"
        }
    },
    "14100": {
        "exception": {
            "en": "Tray position needs to be updated",
            "th": "ต้องทำการอัปเดตตำแหน่งถาด"
        },
        "solution": {
            "en": "Update Location",
            "th": "อัปเดตตำแหน่งที่ตั้ง (Update Location)"
        }
    },
    "12203": {
        "exception": {
            "en": "Unreasonable robot path planning",
            "th": "การวางแผนเส้นทางหุ่นยนต์ไม่เหมาะสม"
        },
        "solution": {
            "en": "Unreasonable robot path planning",
            "th": "ตรวจสอบอุปสรรคบนเส้นทาง"
        }
    },
    "12008": {
        "exception": {
            "en": "No robots are assigned to the external shelves for intensive storage",
            "th": "ไม่มีหุ่นยนต์ถูกมอบหมายให้ชั้นวางภายนอก"
        },
        "solution": {
            "en": "Check whether there are idle robots",
            "th": "ตรวจสอบว่ามีหุ่นยนต์ว่างหรือไม่"
        }
    },
    "21117": {
        "exception": {
            "en": "Robot forced offline removal",
            "th": "หุ่นยนต์ถูกบังคับให้ออฟไลน์และลบออกจากระบบ"
        },
        "solution": {
            "en": "Manual handling",
            "th": "จัดการด้วยตนเอง"
        }
    },
    "21118": {
        "exception": {
            "en": "One-click cancel",
            "th": "งานถูกยกเลิก (One-Click Cancel)"
        },
        "solution": {
            "en": "Manual handling",
            "th": "ดำเนินการด้วยตนเอง"
        }
    },
    "81003": {
        "exception": {
            "en": "The certificate has expired, and system functionality will be restricted",
            "th": "ใบรับรองการใช้งานหมดอายุ ฟังก์ชันระบบจะถูกจำกัด"
        },
        "solution": {
            "en": "Please contact Geek+in a timely manner to apply for authorization",
            "th": "โปรดติดต่อ Geek+ เพื่อขอรับการยืนยันสิทธิ์"
        }
    },
    "3004": {
        "exception": {
            "en": "The robot detected a box on the fork when picking up the box",
            "th": "หุ่นยนต์ตรวจพบกล่องบนงา (Fork) ขณะกำลังจะหยิบกล่อง"
        },
        "solution": {
            "en": "The robot detected a box on the fork when picking up the box",
            "th": "ตรวจสอบสินค้าตกค้างบนงา"
        }
    },
    "3006": {
        "exception": {
            "en": "When the robot returns the box, it has detected that there is already a box on the shelf or basket",
            "th": "หุ่นยนต์ตรวจพบว่ามีกล่องอยู่แล้วบนชั้นหรือตะกร้าขณะนำของไปคืน"
        },
        "solution": {
            "en": "When the robot returns the box, it has detected that there is already a box on the shelf or basket",
            "th": "ตรวจสอบตำแหน่งวางของ"
        }
    },
    "3005": {
        "exception": {
            "en": "The robot detects that there are no boxes in the rack when picking up the boxes",
            "th": "หุ่นยนต์ตรวจไม่พบกล่องในชั้นวางขณะกำลังจะหยิบของ"
        },
        "solution": {
            "en": "The robot detects that there are no boxes in the rack when picking up the boxes",
            "th": "ตรวจสอบตำแหน่งกล่อง"
        }
    },
    "3007": {
        "exception": {
            "en": "When the robot returns the box, it detects that there are no boxes on the tray",
            "th": "หุ่นยนต์ตรวจไม่พบกล่องบนถาดขณะกำลังจะคืนของ"
        },
        "solution": {
            "en": "When the robot returns the box, it detects that there are no boxes on the tray",
            "th": "ตรวจสอบสินค้าบนถาด"
        }
    },
    "81002": {
        "exception": {
            "en": "Map Is Empty",
            "th": "แผนที่ว่างเปล่า"
        },
        "solution": {
            "en": "Please check the data or import the map",
            "th": "โปรดตรวจสอบข้อมูลหรือนำเข้าแผนที่"
        }
    },
    "9001": {
        "exception": {
            "en": "Tray jacking timeout - upper positioning # 1 reason",
            "th": "ยกถาดขึ้นหมดเวลา - สาเหตุจากการระบุตำแหน่งด้านบน #1"
        },
        "solution": {
            "en": "Tray jacking timeout - upper positioning # 1 reason",
            "th": "ตรวจสอบกลไกการยกและเซนเซอร์ตำแหน่งบน"
        }
    },
    "9002": {
        "exception": {
            "en": "Tray jacking timeout - upper positioning # 2 reason",
            "th": "ยกถาดขึ้นหมดเวลา - สาเหตุจากการระบุตำแหน่งด้านบน #2"
        },
        "solution": {
            "en": "Tray jacking timeout - upper positioning # 2 reason",
            "th": "ตรวจสอบเซนเซอร์ระบุตำแหน่งถาด"
        }
    },
    "9003": {
        "exception": {
            "en": "Tray lowering timeout - lower positioning # 1 reason",
            "th": "วางถาดลงหมดเวลา - สาเหตุจากการระบุตำแหน่งด้านล่าง #1"
        },
        "solution": {
            "en": "Tray lowering timeout - lower positioning # 1 reason",
            "th": "ตรวจสอบกลไกการวางและเซนเซอร์ตำแหน่งล่าง"
        }
    },
    "9004": {
        "exception": {
            "en": "Tray lowering timeout - lower positioning # 2 reason",
            "th": "วางถาดลงหมดเวลา - สาเหตุจากการระบุตำแหน่งด้านล่าง #2"
        },
        "solution": {
            "en": "Tray lowering timeout - lower positioning # 2 reason",
            "th": "ตรวจสอบเซนเซอร์ระบุตำแหน่งพื้น"
        }
    },
    "9005": {
        "exception": {
            "en": "Commutation x timeout - upper positioning # 1 reason",
            "th": "การสลับทิศทาง (Commutation X) หมดเวลา - สาเหตุ #1"
        },
        "solution": {
            "en": "Commutation x timeout - upper positioning # 1 reason",
            "th": "ตรวจสอบมอเตอร์สลับทิศทาง X"
        }
    },
    "9006": {
        "exception": {
            "en": "Commutation x timeout - upper positioning # 2 reason",
            "th": "การสลับทิศทาง (Commutation X) หมดเวลา - สาเหตุ #2"
        },
        "solution": {
            "en": "Commutation x timeout - upper positioning # 2 reason",
            "th": "ตรวจสอบเซนเซอร์ตำแหน่งการสลับทิศทาง"
        }
    },
    "9007": {
        "exception": {
            "en": "Commutation y timeout - lower positioning # 1 reason",
            "th": "การสลับทิศทาง (Commutation Y) หมดเวลา - สาเหตุ #1"
        },
        "solution": {
            "en": "Commutation y timeout - lower positioning # 1 reason",
            "th": "ตรวจสอบมอเตอร์สลับทิศทาง Y"
        }
    },
    "9008": {
        "exception": {
            "en": "Commutation y timeout - lower positioning # 2 reason",
            "th": "การสลับทิศทาง (Commutation Y) หมดเวลา - สาเหตุ #2"
        },
        "solution": {
            "en": "Commutation y timeout - lower positioning # 2 reason",
            "th": "ตรวจสอบเซนเซอร์ตำแหน่งการสลับทิศทาง Y"
        }
    },
    "9009": {
        "exception": {
            "en": "Running direction is not obtained during running",
            "th": "ไม่พบทิศทางการวิ่งขณะทำงาน"
        },
        "solution": {
            "en": "Running direction is not obtained during running",
            "th": "ตรวจสอบระบบควบคุมทิศทางหรือเซนเซอร์วัดรอบล้อ"
        }
    },
    "9010": {
        "exception": {
            "en": "Task starting point error",
            "th": "จุดเริ่มต้นของงานผิดพลาด"
        },
        "solution": {
            "en": "Task starting point error",
            "th": "ตรวจสอบว่าหุ่นยนต์อยู่ในตำแหน่งที่ถูกต้องสำหรับเริ่มงาน"
        }
    },
    "9011": {
        "exception": {
            "en": "Operation overrun",
            "th": "การทำงานเกินขอบเขต (Operation Overrun)"
        },
        "solution": {
            "en": "Operation overrun",
            "th": "รีเซ็ตหุ่นยนต์และตรวจสอบตำแหน่งบนแผนที่"
        }
    },
    "9012": {
        "exception": {
            "en": "RFID disconnection",
            "th": "RFID ขาดการเชื่อมต่อ"
        },
        "solution": {
            "en": "RFID disconnection",
            "th": "ตรวจสอบสายสัญญาณ RFID"
        }
    },
    "9013": {
        "exception": {
            "en": "Failed to read RFID tag",
            "th": "อ่านแท็ก RFID ไม่สำเร็จ"
        },
        "solution": {
            "en": "Failed to read RFID tag",
            "th": "ตรวจสอบแท็ก RFID หรือระยะห่างของหัวอ่าน"
        }
    },
    "9014": {
        "exception": {
            "en": "Failed to write RFID tag",
            "th": "เขียนข้อมูลลงแท็ก RFID ไม่สำเร็จ"
        },
        "solution": {
            "en": "Failed to write RFID tag",
            "th": "ตรวจสอบสถานะแท็ก RFID ว่าพร้อมเขียนข้อมูลหรือไม่"
        }
    },
    "9015": {
        "exception": {
            "en": "The next task is not to stop charging",
            "th": "งานถัดไปไม่ใช่การหยุดชาร์จ"
        },
        "solution": {
            "en": "The next task is not to stop charging",
            "th": "ตรวจสอบลำดับงานและสถานะการชาร์จ"
        }
    },
    "9016": {
        "exception": {
            "en": "Lost detection piece",
            "th": "อุปกรณ์ตรวจจับขาดหาย (Lost Detection Piece)"
        },
        "solution": {
            "en": "Lost detection piece",
            "th": "ตรวจสอบแผ่นตรวจจับหรือเซนเซอร์บนเส้นทาง"
        }
    },
    "9017": {
        "exception": {
            "en": "The sensor is not aligned when entering the elevator",
            "th": "เซนเซอร์ไม่ตรงตำแหน่งขณะหุ่นยนต์เข้าลิฟต์"
        },
        "solution": {
            "en": "The sensor is not aligned when entering the elevator",
            "th": "ปรับตำแหน่งหุ่นยนต์ให้ตรงกับเซนเซอร์หน้าลิฟต์"
        }
    },
    "9018": {
        "exception": {
            "en": "DENCO motor failure",
            "th": "มอเตอร์ DENCO ขัดข้อง"
        },
        "solution": {
            "en": "DENCO motor failure",
            "th": "ตรวจสอบมอเตอร์และไดรเวอร์ขับเคลื่อน DENCO"
        }
    },
    "9019": {
        "exception": {
            "en": "geek+ motor fault",
            "th": "มอเตอร์ Geek+ ขัดข้อง"
        },
        "solution": {
            "en": "geek+ motor fault",
            "th": "ตรวจสอบความร้อนและสถานะมอเตอร์ Geek+"
        }
    },
    "9020": {
        "exception": {
            "en": "kinco motor failure",
            "th": "มอเตอร์ Kinco ขัดข้อง"
        },
        "solution": {
            "en": "kinco motor failure",
            "th": "ตรวจสอบสายสัญญาณมอเตอร์ Kinco"
        }
    },
    "9021": {
        "exception": {
            "en": "Target point error",
            "th": "จุดเป้าหมาย (Target Point) ผิดพลาด"
        },
        "solution": {
            "en": "Target point error",
            "th": "ตรวจสอบพิกัดปลายทางบนแผนที่"
        }
    },
    "9022": {
        "exception": {
            "en": "Y + direction is obstructed",
            "th": "มีสิ่งกีดขวางในทิศทาง Y+"
        },
        "solution": {
            "en": "Y + direction is obstructed",
            "th": "ย้ายสิ่งกีดขวางออกจากทิศทาง Y+"
        }
    },
    "9023": {
        "exception": {
            "en": "Y-direction obstacle",
            "th": "มีสิ่งกีดขวางในทิศทาง Y-"
        },
        "solution": {
            "en": "Y-direction obstacle",
            "th": "ย้ายสิ่งกีดขวางออกจากทิศทาง Y-"
        }
    },
    "9024": {
        "exception": {
            "en": "X + direction is obstructed",
            "th": "มีสิ่งกีดขวางในทิศทาง X+"
        },
        "solution": {
            "en": "X + direction is obstructed",
            "th": "ย้ายสิ่งกีดขวางออกจากทิศทาง X+"
        }
    },
    "9025": {
        "exception": {
            "en": "X-direction obstacle",
            "th": "มีสิ่งกีดขวางในทิศทาง X-"
        },
        "solution": {
            "en": "X-direction obstacle",
            "th": "ย้ายสิ่งกีดขวางออกจากทิศทาง X-"
        }
    },
    "9030": {
        "exception": {
            "en": "Abnormal elevator entry (the upper computer commands the elevator entry, but the entrance photoelectricity is off)",
            "th": "การเข้าลิฟต์ผิดปกติ (คอมพิวเตอร์สั่งเข้า แต่เซนเซอร์แสงที่ทางเข้าไม่ทำงาน)"
        },
        "solution": {
            "en": "Abnormal elevator entry (the upper computer commands the elevator entry, but the entrance photoelectricity is off)",
            "th": "ตรวจสอบเซนเซอร์แสง (Photoelectric) และสถานะลิฟต์"
        }
    },
    "9031": {
        "exception": {
            "en": "No tray during jacking",
            "th": "ไม่พบถาด (Tray) ขณะกำลังยกขึ้น"
        },
        "solution": {
            "en": "No tray during jacking",
            "th": "ตรวจสอบว่ามีถาดวางอยู่เหนือหุ่นยนต์หรือไม่"
        }
    },
    "9032": {
        "exception": {
            "en": "Elevator traveling speed at low speed is abnormal",
            "th": "ความเร็วขณะลิฟต์เคลื่อนที่ช้าผิดปกติ"
        },
        "solution": {
            "en": "Elevator traveling speed at low speed is abnormal",
            "th": "ตรวจสอบระบบควบคุมความเร็วของลิฟต์"
        }
    },
    "9040": {
        "exception": {
            "en": "Emergency stop",
            "th": "หยุดฉุกเฉิน (Emergency Stop)"
        },
        "solution": {
            "en": "Emergency stop",
            "th": "ตรวจสอบสาเหตุการหยุดฉุกเฉินและปลดล็อคปุ่ม E-Stop"
        }
    },
    "9050": {
        "exception": {
            "en": "Loss of load during operation",
            "th": "สินค้าหรือถาดหลุดหายระหว่างเคลื่อนที่"
        },
        "solution": {
            "en": "Loss of load during operation",
            "th": "ตรวจสอบสินค้าและตำแหน่งที่สินค้าหล่น"
        }
    },
    "12301": {
        "exception": {
            "en": "Task recovery failed",
            "th": "กู้คืนงาน (Task Recovery) ไม่สำเร็จ"
        },
        "solution": {
            "en": "lang.rms.fed.robot.taskRecoveryFailSolution",
            "th": "ตรวจสอบสถานะหุ่นยนต์และลองกู้คืนงานอีกครั้งหรือยกเลิกงาน"
        }
    },
    "12302": {
        "exception": {
            "en": "Failed to recover pre-occupied tray information during task recovery",
            "th": "ไม่สามารถกู้คืนข้อมูลการจองถาด (Tray) ระหว่างกู้คืนงาน"
        },
        "solution": {
            "en": "lang.rms.fed.task.recoveryPreOccupyPalletFailSolution",
            "th": "ตรวจสอบการจองทรัพยากรบนระบบ RMS"
        }
    },
    "12038": {
        "exception": {
            "en": "Please check the status of the robot. There are too many consecutive charging failures",
            "th": "โปรดตรวจสอบสถานะหุ่นยนต์ พบความล้มเหลวในการชาร์จติดต่อกันหลายครั้ง"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "โปรดติดต่อช่างเทคนิคเพื่อตรวจสอบหัวชาร์จหรือแบตเตอรี่"
        }
    },
    "13008": {
        "exception": {
            "en": "Please check the status of the charging pile. There are too many consecutive charging failures",
            "th": "โปรดตรวจสอบสถานะแท่นชาร์จ พบการชาร์จล้มเหลวติดต่อกันหลายครั้ง"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "โปรดตรวจสอบไฟเลี้ยงแท่นชาร์จหรือหน้าสัมผัสชาร์จ"
        }
    },
    "22101": {
        "exception": {
            "en": "Charging station pull rod error or emergency stop",
            "th": "ก้านดึงสถานีชาร์จผิดปกติหรือมีการกดหยุดฉุกเฉิน"
        },
        "solution": {
            "en": "Please enable the charging point on the map operation page.",
            "th": "โปรดเปิดใช้งานจุดชาร์จบนหน้าควบคุมแผนที่"
        }
    },
    "22102": {
        "exception": {
            "en": "Charging station not available",
            "th": "สถานีชาร์จไม่พร้อมใช้งาน"
        },
        "solution": {
            "en": "Please enable the charging point on the map operation page.",
            "th": "โปรดตรวจสอบสถานะออนไลน์ของสถานีชาร์จ"
        }
    },
    "21210": {
        "exception": {
            "en": "Abnormal upward QR code recognition during robot movement",
            "th": "การระบุ QR Code ด้านบน (Upward QR) ผิดปกติขณะเคลื่อนที่"
        },
        "solution": {
            "en": "Suggest checking the robot's upward QR code camera for damage or aligning the shelves.",
            "th": "แนะนำให้ตรวจสอบเลนส์กล้องด้านบนหรือตรวจสอบความตรงของชั้นวาง"
        }
    },
    "21211": {
        "exception": {
            "en": "Robot cargo center deviation",
            "th": "ศูนย์กลางการบรรทุกสินค้าคลาดเคลื่อน"
        },
        "solution": {
            "en": "lang.rms.monitor.robot.weightCenterOverSolution",
            "th": "จัดตำแหน่งสินค้าใหม่ให้สมดุลและอยู่ตรงกลางถาด"
        }
    },
    "21212": {
        "exception": {
            "en": "After the robot completed the unloading operation, it found that there was still cargo on the belt",
            "th": "พบสินค้าตกค้างบนสายพานหลังจากหุ่นยนต์เสร็จสิ้นการนำของออก"
        },
        "solution": {
            "en": "lang.rms.monitor.robot.unloadPackageFailSolution",
            "th": "ตรวจสอบเซนเซอร์สายพานและนำสินค้าที่ตกค้างออกด้วยตนเอง"
        }
    },
    "21213": {
        "exception": {
            "en": "When the P-series robot returns goods to the bracket, it detects that there is already goods on the bracket and stops in front of the bracket",
            "th": "หุ่นยนต์ P-series ตรวจพบว่ามีสินค้าอยู่บนแท่นรองแล้ว จึงหยุดรอด้านหน้า"
        },
        "solution": {
            "en": "lang.rms.monitor.robot.returnPalletSolution",
            "th": "นำสินค้าออกจากแท่นรองเพื่อให้หุ่นยนต์สามารถวางสินค้าได้"
        }
    },
    "91002": {
        "exception": {
            "en": "DMP safety device triggers system emergency stop",
            "th": "อุปกรณ์ความปลอดภัย DMP สั่งหยุดฉุกเฉินทั้งระบบ"
        },
        "solution": {
            "en": "DMP safety device triggers system emergency stop",
            "th": "ตรวจสอบเซนเซอร์ DMP และรีเซ็ตระบบความปลอดภัย"
        }
    },
    "91003": {
        "exception": {
            "en": "DMP safety equipment triggers full fire emergency stop",
            "th": "อุปกรณ์ความปลอดภัย DMP แจ้งเหตุเพลิงไหม้และหยุดฉุกเฉิน"
        },
        "solution": {
            "en": "DMP safety equipment triggers full fire emergency stop",
            "th": "ตรวจสอบสัญญาณแจ้งเหตุเพลิงไหม้และปฏิบัติตามขั้นตอนความปลอดภัย"
        }
    },
    "91004": {
        "exception": {
            "en": "Emergency stop triggered by safety door of DMP safety equipment",
            "th": "หยุดฉุกเฉินเนื่องจากประตูความปลอดภัย DMP ถูกเปิด"
        },
        "solution": {
            "en": "Emergency stop triggered by safety door of DMP safety equipment",
            "th": "ปิดประตูความปลอดภัยให้สนิทและรีเซ็ตระบบ"
        }
    },
    "91005": {
        "exception": {
            "en": "RMS triggers system emergency stop",
            "th": "RMS สั่งหยุดฉุกเฉินทั้งระบบ"
        },
        "solution": {
            "en": "RMS triggers system emergency stop",
            "th": "ตรวจสอบสถานะบนคอนโซล RMS และรีเซ็ตงาน"
        }
    },
    "91006": {
        "exception": {
            "en": "RMS triggers fire emergency stop",
            "th": "RMS สั่งหยุดฉุกเฉินเนื่องจากเหตุเพลิงไหม้"
        },
        "solution": {
            "en": "RMS triggers fire emergency stop",
            "th": "ตรวจสอบสถานะระบบดับเพลิงและรีเซ็ตผ่าน RMS"
        }
    },
    "108003": {
        "exception": {
            "en": "Container to be confirmed",
            "th": "รอยืนยันสถานะตู้สินค้า (Container)"
        },
        "solution": {
            "en": "Please confirm the position of the cargo box",
            "th": "โปรดตรวจสอบและยืนยันตำแหน่งของกล่องสินค้า"
        }
    },
    "12033": {
        "exception": {
            "en": "The robot is on a node without a degree of freedom",
            "th": "หุ่นยนต์อยู่ในตำแหน่งที่ไม่มีเส้นทางไปต่อ (No Out-degree)"
        },
        "solution": {
            "en": "Manual forced movement is required. The current robot returns to the node with out degree",
            "th": "จำเป็นต้องเคลื่อนย้ายหุ่นยนต์ด้วยตนเองไปยังจุดที่มีเส้นทางเชื่อมต่อ"
        }
    },
    "12034": {
        "exception": {
            "en": "The robot is being forced to operate",
            "th": "หุ่นยนต์กำลังถูกสั่งให้ทำงานด้วยตนเอง (Forced Operation)"
        },
        "solution": {
            "en": "Manual node release or recovery scheduling is required",
            "th": "ทำการปล่อยโหนด (Node Release) หรือกู้คืนตารางเวลาเคลื่อนที่"
        }
    },
    "21112": {
        "exception": {
            "en": "Left motor overload fault",
            "th": "มอเตอร์ด้านซ้ายทำงานหนักเกินพิกัด (Overload)"
        },
        "solution": {
            "en": "Left motor overload fault. Please stop using and contact after-sales operation and maintenance personnel",
            "th": "หยุดใช้งานทันทีและติดต่อเจ้าหน้าที่ซ่อมบำรุง"
        }
    },
    "21113": {
        "exception": {
            "en": "Right motor overload fault",
            "th": "มอเตอร์ด้านขวาทำงานหนักเกินพิกัด (Overload)"
        },
        "solution": {
            "en": "Right motor overload fault. Please stop using and contact after-sales operation and maintenance personnel",
            "th": "หยุดใช้งานทันทีและติดต่อเจ้าหน้าที่ซ่อมบำรุง"
        }
    },
    "21114": {
        "exception": {
            "en": "Nut motor overload fault",
            "th": "มอเตอร์เกลียว (Nut Motor) ทำงานหนักเกินพิกัด"
        },
        "solution": {
            "en": "Nut motor overload fault. Please stop using and contact after-sales operation and maintenance personnel",
            "th": "หยุดใช้งานทันทีและติดต่อเจ้าหน้าที่ซ่อมบำรุง"
        }
    },
    "21115": {
        "exception": {
            "en": "Screw motor overload fault",
            "th": "มอเตอร์สกรู (Screw Motor) ทำงานหนักเกินพิกัด"
        },
        "solution": {
            "en": "Screw motor overload fault. Please stop using and contact after-sales operation and maintenance personnel",
            "th": "หยุดใช้งานทันทีและติดต่อเจ้าหน้าที่ซ่อมบำรุง"
        }
    },
    "12035": {
        "exception": {
            "en": "No task generated for external shelf",
            "th": "ไม่มีการสร้างงานสำหรับชั้นวางภายนอก"
        },
        "solution": {
            "en": "Check whether there are idle robots",
            "th": "ตรวจสอบว่ามีหุ่นยนต์ว่างและสามารถเข้าถึงพื้นที่ได้หรือไม่"
        }
    },
    "12201": {
        "exception": {
            "en": "There is a tray at the end",
            "th": "พบถาดขวางอยู่ที่จุดปลายทาง"
        },
        "solution": {
            "en": "There is a tray at the end, please confirm",
            "th": "โปรดตรวจสอบพิกัดปลายทางและย้ายถาดที่ขวางออก"
        }
    },
    "12202": {
        "exception": {
            "en": "No pallet at the starting point",
            "th": "ไม่พบพาเลท (Pallet) ที่จุดเริ่มต้น"
        },
        "solution": {
            "en": "No pallet at the starting point, please confirm",
            "th": "โปรดตรวจสอบว่าพาเลทวางอยู่ในตำแหน่งที่ถูกต้อง"
        }
    },
    "21201": {
        "exception": {
            "en": "The robot emergency stop button is pressed",
            "th": "ปุ่มหยุดฉุกเฉินบนตัวหุ่นยนต์ถูกกด"
        },
        "solution": {
            "en": "The robot emergency stop button is pressed",
            "th": "ตรวจสอบความปลอดภัยและปลดล็อคปุ่ม E-Stop บนหุ่นยนต์"
        }
    },
    "12027": {
        "exception": {
            "en": "Robot path scheduling is stopped",
            "th": "การจัดตารางเส้นทางของหุ่นยนต์ถูกระงับ"
        },
        "solution": {
            "en": "If there is a path for the robot, please contact the dispatcher",
            "th": "โปรดติดต่อเจ้าหน้าที่ควบคุมระบบ (Dispatcher) เพื่อตรวจสอบเส้นทาง"
        }
    },
    "12028": {
        "exception": {
            "en": "The robot exceeds the farthest allocation point limit of path scheduling",
            "th": "หุ่นยนต์เคลื่อนที่เกินจุดจัดสรรที่ไกลที่สุดของเส้นทาง"
        },
        "solution": {
            "en": "The robot exceeds the farthest allocation point limit of path scheduling",
            "th": "รีเซ็ตตำแหน่งหุ่นยนต์และให้ระบบคำนวณเส้นทางใหม่"
        }
    },
    "12029": {
        "exception": {
            "en": "Obstacles in robot path scheduling",
            "th": "พบสิ่งกีดขวางในการจัดตารางเส้นทางหุ่นยนต์"
        },
        "solution": {
            "en": "Obstacles in robot path scheduling",
            "th": "ตรวจสอบอุปสรรคทางกายภาพหรือหุ่นยนต์ตัวอื่นที่ขวางทาง"
        }
    },
    "12030": {
        "exception": {
            "en": "Robot path scheduling deadlock avoidance",
            "th": "ระบบป้องกันการติดขัด (Deadlock) ของเส้นทางทำงาน"
        },
        "solution": {
            "en": "Robot path scheduling deadlock avoidance",
            "th": "ตรวจสอบพื้นที่ที่มีการจราจรหนาแน่นและระบายหุ่นยนต์ออก"
        }
    },
    "12031": {
        "exception": {
            "en": "Robot path scheduling the current position of the robot is not on the planned path",
            "th": "ตำแหน่งปัจจุบันของหุ่นยนต์ไม่อยู่บนเส้นทางที่วางแผนไว้"
        },
        "solution": {
            "en": "Robot path scheduling the current position of the robot is not on the planned path",
            "th": "ตรวจสอบตำแหน่งหุ่นยนต์และทำการปรับเทียบ (Calibration) ใหม่"
        }
    },
    "12032": {
        "exception": {
            "en": "The QR code robot cannot run on the slam path",
            "th": "หุ่นยนต์ระบบ QR Code ไม่สามารถวิ่งบนเส้นทาง SLAM ได้"
        },
        "solution": {
            "en": "The QR code robot cannot run on the slam path",
            "th": "โปรดตรวจสอบประเภทหุ่นยนต์และการกำหนดเส้นทางบนแผนที่"
        }
    },
    "12106": {
        "exception": {
            "en": "The robot needs to be restarted",
            "th": "หุ่นยนต์จำเป็นต้องได้รับการรีสตาร์ท"
        },
        "solution": {
            "en": "Restart robot",
            "th": "ปิดเครื่องและเปิดใหม่เพื่อรีเซ็ตระบบ"
        }
    },
    "13007": {
        "exception": {
            "en": "Charge point disabled",
            "th": "จุดชาร์จถูกปิดใช้งาน"
        },
        "solution": {
            "en": "Please enable the charging point on the map operation page.",
            "th": "โปรดเปิดใช้งานจุดชาร์จผ่านหน้าตั้งค่าแผนที่"
        }
    },
    "81001": {
        "exception": {
            "en": "Emergency stop in area",
            "th": "มีการหยุดฉุกเฉินในพื้นที่"
        },
        "solution": {
            "en": "Check the emergency stop area and resume",
            "th": "ตรวจสอบพื้นที่ที่มีการหยุดฉุกเฉินและกู้คืนสถานะ"
        }
    },
    "12101": {
        "exception": {
            "en": "The robot is in deadlock",
            "th": "หุ่นยนต์ติดขัดอยู่ในสภาวะ Deadlock"
        },
        "solution": {
            "en": "Find the key robot to deal with the abnormal and untie the dead lock ring",
            "th": "ค้นหาหุ่นยนต์ที่เป็นต้นเหตุและแก้ไขสถานะเพื่อปลดล็อควงจร Deadlock"
        }
    },
    "12102": {
        "exception": {
            "en": "The robot did not move for a long time",
            "th": "หุ่นยนต์ไม่มีการเคลื่อนไหวเป็นเวลานาน"
        },
        "solution": {
            "en": "Find the key robot to deal with the abnormal",
            "th": "ตรวจสอบหุ่นยนต์เพื่อหาจุดที่ทำงานผิดปกติ"
        }
    },
    "12103": {
        "exception": {
            "en": "The robot is crashed",
            "th": "ซอฟต์แวร์หุ่นยนต์เกิดการขัดข้อง (Crash)"
        },
        "solution": {
            "en": "Find the robot to deal with the abnormal",
            "th": "ตรวจสอบสถานะหุ่นยนต์และรีสตาร์ทระบบ"
        }
    },
    "12104": {
        "exception": {
            "en": "The robot is in an emergency stop",
            "th": "หุ่นยนต์อยู่ในสถานะหยุดฉุกเฉิน (E-Stop)"
        },
        "solution": {
            "en": "Recovery robot",
            "th": "ปลดล็อคปุ่มหยุดฉุกเฉินและกู้คืนสถานะ"
        }
    },
    "12105": {
        "exception": {
            "en": "The robot is suspended",
            "th": "หุ่นยนต์ถูกระงับการทำงาน (Suspended)"
        },
        "solution": {
            "en": "Recovery robot",
            "th": "ตรวจสอบสาเหตุการระงับและกู้คืนการทำงาน"
        }
    },
    "12026": {
        "exception": {
            "en": "Robot battery temperature is too low",
            "th": "อุณหภูมิแบตเตอรี่หุ่นยนต์ต่ำเกินไป"
        },
        "solution": {
            "en": "Please place the robot in a constant temperature environment to wait or manually push it into the charging station to charge",
            "th": "ย้ายหุ่นยนต์ไปยังพื้นที่ที่มีอุณหภูมิปกติ หรือเข็นเข้าสถานีชาร์จเพื่ออุ่นแบตเตอรี่"
        }
    },
    "13004": {
        "exception": {
            "en": "Too many robots failed to charge",
            "th": "หุ่นยนต์จำนวนมากไม่สามารถชาร์จไฟได้"
        },
        "solution": {
            "en": "Please check the charging station status or restart the charging station",
            "th": "ตรวจสอบสถานะสถานีชาร์จหรือทำการรีสตาร์ทสถานีชาร์จ"
        }
    },
    "13005": {
        "exception": {
            "en": "Charging pile restart",
            "th": "แท่นชาร์จกำลังทำการรีสตาร์ท"
        },
        "solution": {
            "en": "Please wait a little, if you wait, please contact the operation and maintenance person if you have no response.",
            "th": "โปรดรอสักครู่ หากยังไม่ตอบสนองกรุณาติดต่อเจ้าหน้าที่ซ่อมบำรุง"
        }
    },
    "13006": {
        "exception": {
            "en": "Charging pile upgrade",
            "th": "แท่นชาร์จกำลังทำการอัปเกรดระบบ"
        },
        "solution": {
            "en": "Please wait a little, if you wait, please contact the operation and maintenance person if you have no response.",
            "th": "โปรดรอให้การอัปเกรดเสร็จสิ้น หากมีปัญหาโปรดติดต่อเจ้าหน้าที่"
        }
    },
    "91000": {
        "exception": {
            "en": "Stop button pressed down",
            "th": "ปุ่มหยุด (Stop Button) ถูกกดค้างไว้"
        },
        "solution": {
            "en": "Please check whether the emergency stop button is operating normally, if not, please contact the technical staff for handling",
            "th": "ตรวจสอบปุ่มหยุดว่าทำงานปกติหรือไม่ หากมีปัญหาโปรดติดต่อฝ่ายเทคนิค"
        }
    },
    "91001": {
        "exception": {
            "en": "Stop button disconnected",
            "th": "สายสัญญาณปุ่มหยุดขาดการเชื่อมต่อ"
        },
        "solution": {
            "en": "Please check whether the connection between the emergency stop button device and the RMS service is normal. If it is normal, please contact a technician for handling",
            "th": "ตรวจสอบการเชื่อมต่อระหว่างปุ่มหยุดกับระบบ RMS หากปกติโปรดติดต่อช่าง"
        }
    },
    "81000": {
        "exception": {
            "en": "Average robot power is low",
            "th": "พลังงานเฉลี่ยของหุ่นยนต์ต่ำ"
        },
        "solution": {
            "en": "Check robot charging strategy configuration",
            "th": "ตรวจสอบการตั้งค่ากลยุทธ์การชาร์จไฟของหุ่นยนต์"
        }
    },
    "13002": {
        "exception": {
            "en": "Start sending charging station command timeout",
            "th": "การส่งคำสั่งเริ่มงานไปยังสถานีชาร์จหมดเวลา"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "โปรดตรวจสอบการเชื่อมต่อเครือข่ายของสถานีชาร์จ"
        }
    },
    "13003": {
        "exception": {
            "en": "End of charging station command sending timeout",
            "th": "การส่งคำสั่งสิ้นสุดงานไปยังสถานีชาร์จหมดเวลา"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "โปรดตรวจสอบระบบควบคุมสถานีชาร์จ"
        }
    },
    "12009": {
        "exception": {
            "en": "Robot fetched shelf timeout",
            "th": "หุ่นยนต์หยิบชั้นวางหมดเวลา"
        },
        "solution": {
            "en": "Check the QR code at the bottom of the shelf or robot camera",
            "th": "ตรวจสอบ QR Code ใต้ชั้นวางหรือความสะอาดของเลนส์กล้องหุ่นยนต์"
        }
    },
    "12010": {
        "exception": {
            "en": "Not reaching the shelf position",
            "th": "หุ่นยนต์ไม่สามารถเข้าถึงตำแหน่งชั้นวางได้"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "ตรวจสอบสิ่งกีดขวางรอบชั้นวางหรือความถูกต้องของแผนที่"
        }
    },
    "12011": {
        "exception": {
            "en": "Did not reach the waiting point for a long time",
            "th": "หุ่นยนต์ไม่เข้าสู่จุดรอ (Waiting Point) เป็นเวลานาน"
        },
        "solution": {
            "en": "Check whether the ground QR code or the robot has deviated from the route",
            "th": "ตรวจสอบ QR Code บนพื้นหรือดูว่าหุ่นยนต์วิ่งออกนอกเส้นทางหรือไม่"
        }
    },
    "12012": {
        "exception": {
            "en": "Robot power does not increase for a long time",
            "th": "ระดับพลังงานหุ่นยนต์ไม่เพิ่มขึ้นหลังจากชาร์จเป็นเวลานาน"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "ตรวจสอบหน้าสัมผัสการชาร์จหรือสถานะแบตเตอรี่"
        }
    },
    "12013": {
        "exception": {
            "en": "Robot achieves low electricity ratio",
            "th": "หุ่นยนต์มีระดับพลังงานต่ำเกินเกณฑ์"
        },
        "solution": {
            "en": "It is recommended that the robot first perform the charging task to ensure the normal operation of the robot",
            "th": "แนะนำให้ส่งหุ่นยนต์ไปชาร์จไฟก่อนเพื่อให้ทำงานได้ตามปกติ"
        }
    },
    "12014": {
        "exception": {
            "en": "The charging task cannot be executed without matching to the charging station",
            "th": "ไม่สามารถชาร์จได้เนื่องจากไม่พบสถานีชาร์จที่รองรับ"
        },
        "solution": {
            "en": "Check if the charging station cannot be used by the current robot model",
            "th": "ตรวจสอบว่าสถานีชาร์จรองรับหุ่นยนต์รุ่นนี้หรือไม่"
        }
    },
    "12015": {
        "exception": {
            "en": "Without an idle charging station, the charging task cannot be executed",
            "th": "ไม่สามารถชาร์จได้เนื่องจากไม่มีสถานีชาร์จว่าง"
        },
        "solution": {
            "en": "Check if all charging stations are in use",
            "th": "รอจนกว่าจะมีสถานีชาร์จว่างหรือตรวจสอบจำนวนสถานีชาร์จ"
        }
    },
    "12016": {
        "exception": {
            "en": "There is no available charging station, and the charging task cannot be executed",
            "th": "ไม่มีสถานีชาร์จที่พร้อมใช้งานในขณะนี้"
        },
        "solution": {
            "en": "Check whether the charging station is disabled, whether the charging station is abnormal, whether the charging station is offline, and whether the charging station channel is normal",
            "th": "ตรวจสอบสถานะออนไลน์ การเปิดใช้งาน และความผิดปกติของสถานีชาร์จ"
        }
    },
    "12017": {
        "exception": {
            "en": "The cell of the charging station is occupied by other robots",
            "th": "ตำแหน่ง (Cell) ของสถานีชาร์จถูกหุ่นยนต์ตัวอื่นจองไว้แล้ว"
        },
        "solution": {
            "en": "If the cell is occupied by a robot, remove the occupied robot. If there is no robot occupied on the cell, remove the robot occupied by the cell and then add the robot again.",
            "th": "ย้ายหุ่นยนต์ที่ขวางอยู่ออก หรือรีเซ็ตสถานะการจองในระบบ"
        }
    },
    "12018": {
        "exception": {
            "en": "Cross-region charging failed",
            "th": "การส่งหุ่นยนต์ข้ามเขต (Cross-region) ไปชาร์จล้มเหลว"
        },
        "solution": {
            "en": "Check cross-region charging configuration",
            "th": "ตรวจสอบการตั้งค่าการเชื่อมต่อระหว่างเขตพื้นที่"
        }
    },
    "12019": {
        "exception": {
            "en": "Charging across floors fails",
            "th": "การส่งหุ่นยนต์ไปชาร์จข้ามชั้น (Cross-floor) ล้มเหลว"
        },
        "solution": {
            "en": "Check cross-floor charging configuration",
            "th": "ตรวจสอบการตั้งค่าลิฟต์และการเข้าถึงจุดชาร์จต่างชั้น"
        }
    },
    "12020": {
        "exception": {
            "en": "The current task is blocked and the charging task cannot be executed",
            "th": "งานปัจจุบันถูกขัดจังหวะ ไม่สามารถดำเนินการชาร์จพ่วงได้"
        },
        "solution": {
            "en": "Check whether the robot avoids obstacles, the path is blocked, and the robot deviates",
            "th": "ตรวจสอบว่าหุ่นยนต์ติดสิ่งกีดขวาง เส้นทางถูกปิดกั้น หรือหุ่นยนต์วิ่งออกนอกเส้นทางหรือไม่"
        }
    },
    "12021": {
        "exception": {
            "en": "The current task is not completed and the charging task cannot be performed",
            "th": "งานปัจจุบันยังไม่เสร็จสิ้น ไม่สามารถเริ่มงานชาร์จได้"
        },
        "solution": {
            "en": "End the current task or remove the current robot and replace other robots to perform this task",
            "th": "ยุติงานปัจจุบัน หรือนำหุ่นยนต์ออกและใช้หุ่นยนต์ตัวอื่นทำงานแทน"
        }
    },
    "12022": {
        "exception": {
            "en": "Charging time is too long",
            "th": "ระยะเวลาการชาร์จไฟนานเกินกำหนด"
        },
        "solution": {
            "en": "Modify the safe power and configure charging duration",
            "th": "ปรับเปลี่ยนระดับพลังงานปลอดภัยและตั้งค่าระยะเวลาการชาร์จใหม่"
        }
    },
    "12023": {
        "exception": {
            "en": "The robot battery temperature is too high",
            "th": "อุณหภูมิแบตเตอรี่หุ่นยนต์สูงเกินไป"
        },
        "solution": {
            "en": "Move the robot off to another location on the map, remove the robot, turn on the robot, and rejoin the system",
            "th": "เคลื่อนย้ายหุ่นยนต์ไปยังจุดอื่น นำออกจากระบบแล้วค่อยให้หุ่นยนต์กลับเข้าสู่ระบบใหม่"
        }
    },
    "12024": {
        "exception": {
            "en": "No stops found",
            "th": "ไม่พบจุดหยุดพัก (Stop Point)"
        },
        "solution": {
            "en": "Check rest point configuration",
            "th": "ตรวจสอบการกำหนดค่าจุดพักผ่อนในระบบ"
        }
    },
    "16000": {
        "exception": {
            "en": "The robot is abnormal, please check the problem according to the color of the robot light strip",
            "th": "หุ่นยนต์ทำงานผิดปกติ โปรดตรวจสอบปัญหาตามสีของแถบไฟ (Light Strip)"
        },
        "solution": {
            "en": "Please check the problem according to the color of the robot light strip. If you can’t judge, please contact a technician",
            "th": "ตรวจสอบสีของแถบไฟเพื่อวิเคราะห์ปัญหาเบื้องต้น หากไม่แน่ใจโปรดติดต่อช่าง"
        }
    },
    "21103": {
        "exception": {
            "en": "Depth camera data loss",
            "th": "ข้อมูลจากกล้องตรวจจับความลึก (Depth Camera) ขาดหาย"
        },
        "solution": {
            "en": "The depth camera data is interrupted. Please stop using and contact after-sales operation and maintenance personnel",
            "th": "การเชื่อมต่อกล้องขัดข้อง โปรดหยุดใช้งานและติดต่อเจ้าหน้าที่ซ่อมบำรุง"
        }
    },
    "21104": {
        "exception": {
            "en": "Fisheye camera data loss",
            "th": "ข้อมูลจากกล้องตาปลา (Fisheye Camera) ขาดหาย"
        },
        "solution": {
            "en": "Fisheye camera data is interrupted. Please stop using and contact after-sales operation and maintenance personnel",
            "th": "การเชื่อมต่อกล้อง Fisheye ขัดข้อง โปรดหยุดใช้งานและติดต่อเจ้าหน้าที่ซ่อมบำรุง"
        }
    },
    "21105": {
        "exception": {
            "en": "Network interruption",
            "th": "การเชื่อมต่อเครือข่ายขัดข้อง (Network Interruption)"
        },
        "solution": {
            "en": "The network signal is interrupted. Please wait 3 minutes to try to recover. If it cannot be restored, please press the unbrake button, push the robot to an area with good network signal, and then turn it on again to try to restore",
            "th": "สัญญาณเครือข่ายขัดข้อง โปรดรอ 3 นาที หรือเข็นหุ่นยนต์ไปยังพื้นที่ที่มีสัญญาณดีแล้วเริ่มระบบใหม่"
        }
    },
    "21106": {
        "exception": {
            "en": "Drive data loss, or device failure",
            "th": "ข้อมูลชุดขับเคลื่อนขาดหาย หรืออุปกรณ์ขัดข้อง"
        },
        "solution": {
            "en": "Drive data is interrupted. Please stop using and contact after-sales operation and maintenance personnel",
            "th": "ระบบขับเคลื่อนขัดข้อง โปรดหยุดใช้งานและติดต่อเจ้าหน้าที่ซ่อมบำรุง"
        }
    },
    "21107": {
        "exception": {
            "en": "Trigger STO",
            "th": "ระบบนิรภัย STO ทำงาน (Safe Torque Off)"
        },
        "solution": {
            "en": "Please contact after-sales operation and maintenance personnel",
            "th": "โปรดติดต่อเจ้าหน้าที่เทคนิคเพื่อตรวจสอบระบบนิรภัย"
        }
    },
    "21108": {
        "exception": {
            "en": "Press to release the brake",
            "th": "กำลังกดปุ่มเพื่อปล่อยเบรก (Release Brake)"
        },
        "solution": {
            "en": "Press the release brake button, please reset after reaching the position",
            "th": "กดปุ่มเพื่อเคลื่อนย้ายหุ่นยนต์ แล้วทำการรีเซ็ตเมื่อถึงตำแหน่งที่ต้องการ"
        }
    },
    "21109": {
        "exception": {
            "en": "Dead battery",
            "th": "แบตเตอรี่หมด (Dead Battery)"
        },
        "solution": {
            "en": "The battery is exhausted. Please press the release button to push the robot to charge more than 20% in the manual mode of the charging station. After charging is complete, switch the charging station to interactive mode",
            "th": "แบตเตอรี่หมดสนิท โปรดเข็นหุ่นยนต์เข้าชาร์จแบบแมนนวลจนถึง 20% ก่อนกลับสู่โหมดปกติ"
        }
    },
    "21110": {
        "exception": {
            "en": "Weighing overload or partial load exceeding limit",
            "th": "น้ำหนักบรรทุกเกินพิกัด หรือสินค้าวางไม่สมดุลเกินกำหนด"
        },
        "solution": {
            "en": "The cargo is overloaded or unbalanced, and the operation can be resumed after reducing the cargo or aligning the cargo",
            "th": "นำสินค้าส่วนเกินออกหรือจัดวางสินค้าใหม่ให้สมดุลก่อนเริ่มงานใหม่"
        }
    },
    "21111": {
        "exception": {
            "en": "Location loss",
            "th": "สูญเสียการระบุตำแหน่ง (Location Loss)"
        },
        "solution": {
            "en": "Positioning is lost, please press the release button to push the robot a certain distance, or push to the top of the QR code to try to recover",
            "th": "หุ่นยนต์ไม่ทราบตำแหน่ง โปรดเข็นหุ่นยนต์ไปไว้เหนือจุด QR Code บนพื้นเพื่อกู้คืนตำแหน่ง"
        }
    },
    "12025": {
        "exception": {
            "en": "Robot is Locked",
            "th": "หุ่นยนต์ถูกล็อคสถานะ (Locked)"
        },
        "solution": {
            "en": "Robot is Locked",
            "th": "ตรวจสอบสาเหตุการล็อคของหุ่นยนต์ในระบบ RMS"
        }
    },
    "22000": {
        "exception": {
            "en": "RMS communication interrupted",
            "th": "การสื่อสารกับ RMS ขาดหาย"
        },
        "solution": {
            "en": "Please handle the exception manually",
            "th": "โปรดดำเนินการเพื่อกู้คืนสถานะด้วยตนเอง"
        }
    },
    "22001": {
        "exception": {
            "en": "CAN communication interrupted",
            "th": "การสื่อสารระบบ CAN ภายในขัดข้อง"
        },
        "solution": {
            "en": "Please handle the exception manually",
            "th": "โปรดติดต่อฝ่ายซ่อมบำรุงเพื่อตรวจสอบสายสัญญาณ"
        }
    },
    "22002": {
        "exception": {
            "en": "Screen communication is interrupted",
            "th": "การสื่อสารกับหน้าจอหุ่นยนต์ขัดข้อง"
        },
        "solution": {
            "en": "Please handle the exception manually",
            "th": "ตรวจสอบสายเชื่อมต่อหน้าจอหรือรีสตาร์ทหุ่นยนต์"
        }
    },
    "22003": {
        "exception": {
            "en": "RMS data abnormal",
            "th": "ข้อมูลจากระบบ RMS ผิดปกติ"
        },
        "solution": {
            "en": "Please handle the exception manually",
            "th": "ตรวจสอบความสอดคล้องของข้อมูลในระบบควบคุม"
        }
    },
    "22004": {
        "exception": {
            "en": "RMS command exception",
            "th": "คำสั่งจาก RMS ไม่ถูกต้อง"
        },
        "solution": {
            "en": "Please handle the exception manually",
            "th": "ยกเลิกคำสั่งเดิมและลองส่งคำสั่งใหม่"
        }
    },
    "22005": {
        "exception": {
            "en": "Forklift charging station presses emergency stop",
            "th": "มีการกดปุ่มหยุดฉุกเฉินที่สถานีชาร์จรถโฟล์คลิฟท์"
        },
        "solution": {
            "en": "Please handle the exception manually",
            "th": "ตรวจสอบความปลอดภัยและปลดปุ่ม E-Stop ที่สถานีชาร์จ"
        }
    },
    "22006": {
        "exception": {
            "en": "Forklift charging station does not detect sensors",
            "th": "สถานีชาร์จรถโฟล์คลิฟท์ตรวจไม่พบเซนเซอร์"
        },
        "solution": {
            "en": "Please handle the exception manually",
            "th": "ตรวจสอบสถานะและตำแหน่งของเซนเซอร์ที่สถานีชาร์จ"
        }
    },
    "22007": {
        "exception": {
            "en": "Charging module over temperature",
            "th": "โมดูลการชาร์จไฟมีอุณหภูมิสูงเกินกำหนด"
        },
        "solution": {
            "en": "Please handle the exception manually",
            "th": "หยุดพักการชาร์จและรอให้อุณหภูมิลดลง"
        }
    },
    "22008": {
        "exception": {
            "en": "Charging current in automatic mode is 0",
            "th": "กระแสไฟชาร์จเป็น 0 ในโหมดอัตโนมัติ"
        },
        "solution": {
            "en": "Please handle the exception manually",
            "th": "ตรวจสอบหน้าสัมผัสการชาร์จและระบบจ่ายไฟของแท่นชาร์จ"
        }
    },
    "22009": {
        "exception": {
            "en": "Charging module warning status",
            "th": "โมดูลการชาร์จแจ้งเตือนสถานะผิดปกติ"
        },
        "solution": {
            "en": "Please handle the exception manually",
            "th": "ตรวจสอบรหัสคำเตือนเพิ่มเติมที่โมดูลชาร์จ"
        }
    },
    "22010": {
        "exception": {
            "en": "Charging module error status",
            "th": "โมดูลการชาร์จเกิดข้อผิดพลาด (Error)"
        },
        "solution": {
            "en": "Please handle the exception manually",
            "th": "รีเซ็ตโมดูลการชาร์จหรือติดต่อช่างเทคนิค"
        }
    },
    "22011": {
        "exception": {
            "en": "Charging station unavailable",
            "th": "สถานีชาร์จไม่สามารถใช้งานได้"
        },
        "solution": {
            "en": "Please handle the exception manually",
            "th": "ตรวจสอบสถานะกำลังไฟและการเชื่อมต่อของสถานีชาร์จ"
        }
    },
    "13000": {
        "exception": {
            "en": "Charging station lost contact",
            "th": "สถานีชาร์จขาดการติดต่อ (Lost Contact)"
        },
        "solution": {
            "en": "Recover later automatically",
            "th": "ระบบจะรอการกู้คืนการเชื่อมต่ออัตโนมัติ"
        }
    },
    "13001": {
        "exception": {
            "en": "Charging station is offline",
            "th": "สถานีชาร์จอยู่ในสถานะออฟไลน์"
        },
        "solution": {
            "en": "Please handle the exception manually",
            "th": "ตรวจสอบการเชื่อมต่อเครือข่ายของสถานีชาร์จ"
        }
    },
    "21044": {
        "exception": {
            "en": "Gyro temperature changes too much",
            "th": "อุณหภูมิของเซนเซอร์ Gyro เปลี่ยนแปลงมากเกินไป"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบอุณหภูมิสภาพแวดล้อมหรือประสิทธิภาพการระบายความร้อนของหุ่นยนต์"
        }
    },
    "21045": {
        "exception": {
            "en": "The base values of two calibrations before and after by the gyro have changed too much",
            "th": "ค่าพื้นฐานจากการปรับเทียบ Gyro สองครั้งล่าสุดมีความแตกต่างมากเกินไป"
        },
        "solution": {
            "en": NaN,
            "th": "ทำการปรับเทียบ (Calibration) หุ่นยนต์ใหม่ในแนวราบที่ไม่มีความลาดเอียง"
        }
    },
    "21046": {
        "exception": {
            "en": "The driver wheel skidded as it rotated",
            "th": "ล้อขับเคลื่อนเกิดการหมุนฟรีหรือลื่นไถลขณะเลี้ยว"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบความสะอาดของพื้น (คราบน้ำมัน/น้ำ) หรือสภาพยางล้อ"
        }
    },
    "21047": {
        "exception": {
            "en": "No obstacle avoidance data update within 2 seconds",
            "th": "ไม่มีข้อมูลการหลบหลีกสิ่งกีดขวางอัปเดตภายใน 2 วินาที"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบการเชื่อมต่อของเซนเซอร์ Lidar หรือเซนเซอร์ตรวจจับสิ่งกีดขวาง"
        }
    },
    "21048": {
        "exception": {
            "en": "No battery update data is received in 200 seconds.",
            "th": "ไม่ได้รับข้อมูลแบตเตอรี่อัปเดตภายใน 200 วินาที"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบการเชื่อมต่อ BMS หรือสายสัญญาณแบตเตอรี่"
        }
    },
    "21049": {
        "exception": {
            "en": "Driver wheel lock failure",
            "th": "ระบบล็อคล้อขับเคลื่อนขัดข้อง"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบเบรกไฟฟ้าหรือกลไกการล็อคล้อ"
        }
    },
    "21050": {
        "exception": {
            "en": "The left wheel skids when moving in a straight line",
            "th": "ล้อซ้ายลื่นไถลขณะเคลื่อนที่ในแนวตรง"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบสภาพพื้นผิวหน้าล้อซ้าย หรือคราบสกปรกบนพื้น"
        }
    },
    "21051": {
        "exception": {
            "en": "The right wheel skids when moving in a straight line",
            "th": "ล้อขวาลื่นไถลขณะเคลื่อนที่ในแนวตรง"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบสภาพพื้นผิวหน้าล้อขวา หรือคราบสกปรกบนพื้น"
        }
    },
    "21052": {
        "exception": {
            "en": "Failed to save image",
            "th": "บันทึกภาพไม่สำเร็จ"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบหน่วยความจำสำรองหรือสิทธิ์การบันทึกข้อมูลในเครื่องหุ่นยนต์"
        }
    },
    "21053": {
        "exception": {
            "en": "non-QR code area image feedback",
            "th": "การตอบสนองภาพจากพื้นที่ที่ไม่มี QR Code"
        },
        "solution": {
            "en": NaN,
            "th": "ย้ายหุ่นยนต์กลับเข้าสู่พื้นที่ที่มี QR Code หรือตรวจสอบเลนส์กล้อง"
        }
    },
    "21054": {
        "exception": {
            "en": "The lifter motor cannot lift",
            "th": "มอเตอร์ชุดยกไม่สามารถทำงานได้"
        },
        "solution": {
            "en": "Robot shutdown and restart",
            "th": "ปิดเครื่องและรีสตาร์ทหุ่นยนต์ หากยังไม่หายให้ตรวจสอบกลไกการยก"
        }
    },
    "21055": {
        "exception": {
            "en": "Pulse count of the drive wheel encoder  was not updated.",
            "th": "ไม่มีการอัปเดตจำนวนพัลส์ (Pulse) จากเอ็นโค้ดเดอร์ล้อขับเคลื่อน"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบสายสัญญาณเอ็นโค้ดเดอร์ (Encoder) หรือการเชื่อมต่อชุดขับเคลื่อน"
        }
    },
    "21056": {
        "exception": {
            "en": "Driver wheel encoder pulse number overflow",
            "th": "จำนวนพัลส์ของเอ็นโค้ดเดอร์ล้อขับเคลื่อนมีค่าสูงเกินขอบเขต (Overflow)"
        },
        "solution": {
            "en": NaN,
            "th": "รีสตาร์ทหุ่นยนต์เพื่อล้างค่าพัลส์สะสมในระบบ"
        }
    },
    "21057": {
        "exception": {
            "en": "Front bumper trigger",
            "th": "กันชนด้านหน้า (Front Bumper) ถูกกระแทก"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "ตรวจสอบสิ่งกีดขวางด้านหน้าและทำการกู้คืนสถานะกันชน"
        }
    },
    "21058": {
        "exception": {
            "en": "The decoding of the shelf QR code is incorrect. For example: the black frame has been read, but the code value is wrong",
            "th": "การถอดรหัส QR Code ของชั้นวางผิดพลาด (ตรวจพบกรอบรูปแต่ข้อมูลข้างในไม่ถูกต้อง)"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบความสะอาดหรือความเสียหายของป้าย QR Code ใต้ชั้นวาง"
        }
    },
    "21059": {
        "exception": {
            "en": "Rear bumper is triggered",
            "th": "กันชนด้านหลัง (Rear Bumper) ถูกกระแทก"
        },
        "solution": {
            "en": "Restart robot",
            "th": "ตรวจสอบสิ่งกีดขวางด้านหลังและรีสตาร์ทหุ่นยนต์เพื่อรีเซ็ตสถานะ"
        }
    },
    "21060": {
        "exception": {
            "en": "The obstacle avoidance is triggered",
            "th": "ระบบหลบหลีกสิ่งกีดขวางทำงาน"
        },
        "solution": {
            "en": "Check for obstacles ahead of the robot",
            "th": "ตรวจสอบสิ่งกีดขวางที่อยู่ด้านหน้าเส้นทางของหุ่นยนต์"
        }
    },
    "21061": {
        "exception": {
            "en": "The lift motor cannot be lowered. For example, the shelf cannot be placed within 40s",
            "th": "มอเตอร์ชุดยกไม่สามารถวางลงได้ (เช่น วางชั้นวางไม่สำเร็จภายใน 40 วินาที)"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบกลไกชุดยกและตรวจสอบว่ามีอะไรขัดขวางการวางชั้นวางหรือไม่"
        }
    },
    "21062": {
        "exception": {
            "en": "Failed to parse the checksum of the image data uploaded by the camera.",
            "th": "การตรวจสอบค่า Checksum ของข้อมูลรูปภาพจากกล้องผิดพลาด"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบสายเชื่อมต่อกล้องหรือประสิทธิภาพการส่งข้อมูลในเครื่องหุ่นยนต์"
        }
    },
    "21063": {
        "exception": {
            "en": "No charging current",
            "th": "ไม่มีกระแสไฟฟ้าไหลเข้าขณะชาร์จ"
        },
        "solution": {
            "en": "Drag out of the charging station and restart the robot",
            "th": "เข็นหุ่นยนต์ออกจากสถานีชาร์จแล้วเริ่มระบบใหม่ ตรวจสอบหน้าสัมผัสการชาร์จ"
        }
    },
    "21064": {
        "exception": {
            "en": "Charging sensor failure",
            "th": "เซนเซอร์ตรวจจับการชาร์จขัดข้อง"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบการเชื่อมต่อและความสะอาดของเซนเซอร์ตรวจจับที่จุดชาร์จ"
        }
    },
    "21065": {
        "exception": {
            "en": "The original data of obstacle avoidance was not updated within two seconds",
            "th": "ข้อมูลดิบสำหรับการหลบหลีกสิ่งกีดขวางไม่อัปเดตภายใน 2 วินาที"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบการทำงานของเซนเซอร์ Lidar และสายสัญญาณเชื่อมต่อ"
        }
    },
    "21066": {
        "exception": {
            "en": "The driver wheel is overcharged",
            "th": "เกิดภาวะจ่ายกระแสเกินที่มอเตอร์ล้อขับเคลื่อน"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบสิ่งขัดขวางที่ล้อหรือน้ำหนักบรรทุกที่มากเกินไป"
        }
    },
    "21067": {
        "exception": {
            "en": "The driver wheel motor over-current",
            "th": "กระแสไฟฟ้าที่มอเตอร์ล้อขับเคลื่อนสูงเกินพิกัด"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "หยุดการทำงานและส่งช่างเทคนิคตรวจสอบชุดไดรเวอร์มอเตอร์"
        }
    },
    "21068": {
        "exception": {
            "en": "Lifter motor over-current",
            "th": "กระแสไฟฟ้าที่มอเตอร์ชุดยกสูงเกินพิกัด"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "ตรวจสอบความฝืดของชุดยกหรือน้ำหนักสินค้าที่อาจเกินกำลังยก"
        }
    },
    "21069": {
        "exception": {
            "en": "DSP lost heartbeat",
            "th": "สัญญาณ Heartbeat ของระบบประมวลผล DSP ขาดหาย"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบเมนบอร์ดหรือทำการรีสตาร์ทบอร์ดควบคุมหุ่นยนต์"
        }
    },
    "21070": {
        "exception": {
            "en": "DSP data feedback error",
            "th": "ข้อมูลตอบสนองจากระบบ DSP ผิดพลาด"
        },
        "solution": {
            "en": "Reappear after restart, and check whether the upper and lower lens hardware is damaged.",
            "th": "หากยังเป็นหลังรีสตาร์ท ให้ตรวจสอบความเสียหายของเลนส์กล้องทั้งชุดบนและล่าง"
        }
    },
    "21071": {
        "exception": {
            "en": "Failed to parse the QR code of the shelf.",
            "th": "ไม่สามารถวิเคราะห์ข้อมูล QR Code ของชั้นวางได้"
        },
        "solution": {
            "en": NaN,
            "th": "ตรวจสอบคุณภาพการพิมพ์ป้าย QR Code หรือเช็ดเลนส์กล้องให้สะอาด"
        }
    },
    "21072": {
        "exception": {
            "en": "Shelf QR code decoding timeout",
            "th": "การถอดรหัส QR Code ชั้นวางหมดเวลา"
        },
        "solution": {
            "en": "Check if the shelves are crooked",
            "th": "ตรวจสอบว่าชั้นวางตั้งเอียงหรือไม่อยู่ในตำแหน่งศูนย์กลางหุ่นยนต์หรือไม่"
        }
    },
    "21073": {
        "exception": {
            "en": "Driver temperature is too high",
            "th": "อุณหภูมิชุดขับเคลื่อนมอเตอร์สูงเกินไป"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "หยุดใช้งานเพื่อให้เครื่องเย็นลง และตรวจสอบพัดลมระบายอากาศภายใน"
        }
    },
    "21074": {
        "exception": {
            "en": "Lidar data lost or component malfunction",
            "th": "ข้อมูลระบบ Lidar ขาดหาย หรือส่วนประกอบขัดข้อง"
        },
        "solution": {
            "en": "Data connection has been restored but the robot has deviated from path: Push the robot onto the correct SLAM path or push it on top of the QR code. The robot will continue the task after releasing the brake button. For robots with unrecoverable data connections: Turn the robot off then on again, put the shelf down first, then analyze the fault in detail.",
            "th": "หากสัญญาณกลับมาแต่หุ่นยนต์เบี่ยงจากเส้นทาง: เข็นหุ่นยนต์กลับเข้าสู่เส้นทาง SLAM หรือวางไว้เหนือ QR Code หากยังเชื่อมต่อไม่ได้: ปิดและเปิดเครื่องใหม่ วางชั้นวางลงแล้วตรวจสอบโดยละเอียด"
        }
    },
    "21075": {
        "exception": {
            "en": "Battery data lost",
            "th": "ข้อมูลระดับพลังงานแบตเตอรี่ขาดหาย"
        },
        "solution": {
            "en": "If the battery data is lost for a long time, try restarting the robot. If it isn’t restored after restarting, then remove the robot from the system and contact a technician for analysis.",
            "th": "หากข้อมูลไม่มานานเกินไป ให้ลองรีสตาร์ทหุ่นยนต์ หากยังไม่หายให้ถอดออกแล้วส่งวิเคราะห์ทางเทคนิค"
        }
    },
    "21076": {
        "exception": {
            "en": "Battery over-temperature protection",
            "th": "ระบบป้องกันแบตเตอรี่ร้อนเกินพิกัดทำงาน"
        },
        "solution": {
            "en": "This may be caused by continuous charging with a large current in a high temperature environment. The robot needs to be moved away from the charging station.",
            "th": "อาจเกิดจากการชาร์จไฟแรงต่อเนื่องในที่ร้อนจัด ให้รีบย้ายหุ่นยนต์ออกจากสถานีชาร์จทันที"
        }
    },
    "21077": {
        "exception": {
            "en": "Motor module can recover from fault",
            "th": "โมดูลมอเตอร์เกิดข้อผิดพลาดที่กู้คืนสถานะได้"
        },
        "solution": {
            "en": "This may be caused by the motor overheating, over-current, or tracking error. Multiple reasons: Could be overloading or the shelf is too big. You can try restoring by turning the robot off then on again.",
            "th": "อาจเกิดจากมอเตอร์ร้อนจัด กระแสเกิน หรือตามตำแหน่งผิดพลาด ลองปิดและเปิดหุ่นยนต์ใหม่เพื่อกู้คืนสถานะ"
        }
    },
    "21078": {
        "exception": {
            "en": "Motor module cannot recover from fault (replace part)",
            "th": "โมดูลมอเตอร์ขัดข้องรุนแรง (ต้องทำการเปลี่ยนอะไหล่)"
        },
        "solution": {
            "en": "Possible reasons: STO drive wheel has been triggered too frequently or the braking mechanism has failed. Replacement required",
            "th": "สาเหตุ: ระบบ STO ทำงานบ่อยเกินไปหรือกลไกการเบรกพัง ต้องเปลี่ยนชิ้นส่วนมอเตอร์หรือบอร์ดไดรเวอร์"
        }
    },
    "21079": {
        "exception": {
            "en": "Absolute value of encoder battery is low",
            "th": "แบตเตอรี่ของชุดเอ็นโค้ดเดอร์ (Encoder) ต่ำเกินไป"
        },
        "solution": {
            "en": "Battery has reached the end of its service life and requires replacement",
            "th": "แบตเตอรี่สำรองของระบบเอ็นโค้ดเดอร์เสื่อมสภาพ จำเป็นต้องเปลี่ยนทันที"
        }
    },
    "21080": {
        "exception": {
            "en": "Weight sensor data lost",
            "th": "ข้อมูลจากเซนเซอร์ชั่งน้ำหนักขาดหาย"
        },
        "solution": {
            "en": "Weight sensor data lost",
            "th": "ตรวจสอบสายสัญญาณใต้ฐานชั่งหรือรีสตาร์ทบอร์ดควบคุมน้ำหนัก"
        }
    },
    "21081": {
        "exception": {
            "en": "Communication between main controller and task controller disconnected",
            "th": "การเชื่อมต่อระหว่างคอนโทรลเลอร์หลักและตัวควบคุมงานขาดหาย"
        },
        "solution": {
            "en": "Communication between main controller and task controller disconnected",
            "th": "ตรวจสอบสายแลน (LAN) หรือการเชื่อมต่อภายในเครื่องระหว่างบอร์ดประมวลผล"
        }
    },
    "21000": {
        "exception": {
            "en": "Positioning lateral deviation of the end-side QR code > 20 mm; angle is greater than 2°.",
            "th": "ความคลาดเคลื่อนด้านข้างของ QR Code ปลายทาง > 20 มม. หรือมุมเอียง > 2 องศา"
        },
        "solution": {
            "en": "1. Check the labeling accuracy of ground QR code / shelf QR code. 2. Remove the robot first and then join",
            "th": "1. ตรวจสอบความแม่นยำของตำแหน่งป้าย QR Code บนพื้น/ชั้นวาง 2. นำหุ่นยนต์ออกจากระบบแล้วกลับเข้าใหม่"
        }
    },
    "21001": {
        "exception": {
            "en": "The angle deviation of straight walking is more than 3°",
            "th": "มุมเบี่ยงเบนขณะเดินตรงมากกว่า 3 องศา"
        },
        "solution": {
            "en": "Check driving wheels or floor surface to ensure the robot can walk straight normally",
            "th": "ตรวจสอบล้อขับเคลื่อนหรือพื้นผิวเพื่อให้หุ่นยนต์เดินตรงตามปกติ"
        }
    },
    "21002": {
        "exception": {
            "en": "The difference between the angle of rotation integral and the angle of encoder exceeds the limit",
            "th": "ผลต่างระหว่างมุมหมุนสะสมและค่าจากเอ็นโค้ดเดอร์เกินกำหนด"
        },
        "solution": {
            "en": "Check for deviations in the Gyro sensor and wheel encoders",
            "th": "ตรวจสอบความคลาดเคลื่อนของเซนเซอร์ Gyro และเอ็นโค้ดเดอร์ล้อ"
        }
    },
    "21003": {
        "exception": {
            "en": "Robot center position offset exceeds the limit",
            "th": "ตำแหน่งศูนย์กลางหุ่นยนต์เยื้องเกินขอบเขตที่กำหนด"
        },
        "solution": {
            "en": "Recalibrate the robot's center position",
            "th": "ทำการตั้งค่าจุดศูนย์กลาง (Calibration) ของหุ่นยนต์ใหม่"
        }
    },
    "21004": {
        "exception": {
            "en": "The driver wheel skidded as it rotated",
            "th": "ล้อขับเคลื่อนหมุนลื่นไถลขณะหมุน"
        },
        "solution": {
            "en": "This fault often occurs, so it is necessary to check the ground conditions: depression, water stain, greasy",
            "th": "ตรวจสอบสภาพพื้น: พื้นหลุม, มีน้ำขัง หรือคราบน้ำมัน"
        }
    },
    "21005": {
        "exception": {
            "en": "The direction of control instruction is not consistent with the direction of actual angle rotation",
            "th": "ทิศทางของคำสั่งควบคุมไม่สอดคล้องกับการหมุนจริง"
        },
        "solution": {
            "en": "Check motor wiring or driver phase settings",
            "th": "ตรวจสอบการต่อสายมอเตอร์หรือการตั้งค่าเฟสของไดรเวอร์"
        }
    },
    "21006": {
        "exception": {
            "en": "When fitting the arc according to the point, the accumulated error of the track smoothness exceeds the limit.",
            "th": "ความคลาดเคลื่อนสะสมในการเข้าโค้งตามจุดอ้างอิงเกินกำหนด"
        },
        "solution": {
            "en": "Verify coordinate continuity in the map or check wheel odometry",
            "th": "ตรวจสอบความต่อเนื่องของพิกัดในแผนที่หรือตรวจสอบการนับก้าวล้อ"
        }
    },
    "21007": {
        "exception": {
            "en": "The error of target attitude and stop attitude is over limit",
            "th": "ค่าความผิดพลาดขององศาเป้าหมายและองศาหยุดเกินขีดจำกัด"
        },
        "solution": {
            "en": "Robot stopped at an excessive tilt. Please check stop parameters",
            "th": "หุ่นยนต์หยุดเอียงเกินไป โปรดตรวจสอบพารามิเตอร์การหยุด"
        }
    },
    "21008": {
        "exception": {
            "en": "Shelf rotation angle is more than 180°",
            "th": "มุมหมุนของชั้นวางมากกว่า 180 องศา"
        },
        "solution": {
            "en": "Check rotation mechanism or QR code labels under the shelf",
            "th": "ตรวจสอบกลไกการหมุนหรือป้าย QR Code ใต้ชั้นวาง"
        }
    },
    "21009": {
        "exception": {
            "en": "The relative error of the shelf QR code and the ground QR code is over limit",
            "th": "ค่าความผิดพลาดสัมพัทธ์ระหว่าง QR ชั้นวางและ QR บนพื้นเกินกำหนด"
        },
        "solution": {
            "en": "Verify shelf placement aligns with the ground markers",
            "th": "ตรวจสอบตำแหน่งการวางชั้นวางให้ตรงกับจุดบนพื้น"
        }
    },
    "21010": {
        "exception": {
            "en": "Crooked while lifting the shelf.",
            "th": "ชั้นวางเอียงขณะกำลังทำการยก"
        },
        "solution": {
            "en": "Exceeding the limit (40mm or 4 °) will stop reporting other fault codes and wait for people to deal with it.",
            "th": "หากเกินขีดจำกัด (40 มม. หรือ 4 องศา) ระบบจะหยุดรอให้เจ้าหน้าที่มาจัดการ"
        }
    },
    "21011": {
        "exception": {
            "en": "Gyro integral detection in robot stop mode",
            "th": "พบความผิดปกติของ Gyro ขณะหุ่นยนต์หยุดนิ่ง"
        },
        "solution": {
            "en": "Check for vibrations or Gyro sensor stability",
            "th": "ตรวจสอบการสั่นสะเทือนหรือความเสถียรของเซนเซอร์ Gyro"
        }
    },
    "21012": {
        "exception": {
            "en": "Angle change detection of image fusion in robot stop mode",
            "th": "พบการเปลี่ยนมุมจากการประมวลผลภาพขณะหุ่นยนต์หยุดนิ่ง"
        },
        "solution": {
            "en": "Check camera stability or algorithm deviations",
            "th": "ตรวจสอบความเสถียรของกล้องหรือความคลาดเคลื่อนของอัลกอริทึม"
        }
    },
    "21013": {
        "exception": {
            "en": "Angle change detection of encoder in robot stop mode",
            "th": "พบการเปลี่ยนมุมจากเอ็นโค้ดเดอร์ขณะหุ่นยนต์หยุดนิ่ง"
        },
        "solution": {
            "en": "Check wheel brakes or unintended wheel movement",
            "th": "ตรวจสอบเบรกล้อหรือการเคลื่อนที่ของล้อขณะไม่ได้สั่งงาน"
        }
    },
    "21014": {
        "exception": {
            "en": "The robot moves to the charging station with a xy coordinate deviation of 20mm",
            "th": "หุ่นยนต์เคลื่อนที่เข้าสถานีชาร์จโดยมีพิกัดเบี่ยงเบน 20 มม."
        },
        "solution": {
            "en": "Reposition the robot and verify charging point accuracy",
            "th": "จัดตำแหน่งหุ่นยนต์ใหม่และตรวจสอบความแม่นยำของจุดชาร์จ"
        }
    },
    "21015": {
        "exception": {
            "en": "The position of the charging station xy deviates from the integer coordinate by 20 mm",
            "th": "พิกัดสถานีชาร์จเบี่ยงเบนจากพิกัดอ้างอิงจริง 20 มม."
        },
        "solution": {
            "en": "Verify and correct the charging station coordinates in the map file",
            "th": "ตรวจสอบและแก้ไขพิกัดสถานีชาร์จในไฟล์แผนที่"
        }
    },
    "21016": {
        "exception": {
            "en": "The backward direction of charging is wrong.",
            "th": "ทิศทางการถอยหลังเข้าชาร์จไม่ถูกต้อง"
        },
        "solution": {
            "en": "Check Heading configuration for the charging station frontend",
            "th": "ตรวจสอบการกำหนดค่าทิศทาง (Heading) ของหน้าสถานีชาร์จ"
        }
    },
    "21017": {
        "exception": {
            "en": "The height parameter is wrong when descending",
            "th": "พารามิเตอร์ความสูงผิดพลาดขณะกำลังวางชุดยกลง"
        },
        "solution": {
            "en": "Check height sensor values or floor level settings",
            "th": "ตรวจสอบค่าเซนเซอร์ความสูงหรือตรวจสอบการตั้งค่าระดับพื้น"
        }
    },
    "21018": {
        "exception": {
            "en": "The height parameter is wrong when descending",
            "th": "พารามิเตอร์ความสูงผิดพลาดขณะกำลังวางชุดยกลง"
        },
        "solution": {
            "en": "Check height sensor connection",
            "th": "ตรวจสอบการเชื่อมต่อเซนเซอร์วัดค่าความสูง"
        }
    },
    "21019": {
        "exception": {
            "en": "The robot's current point and path starting position exceed the limit",
            "th": "ตำแหน่งปัจจุบันและจุดเริ่มเส้นทางของหุ่นยนต์ห่างกันเกินกำหนด"
        },
        "solution": {
            "en": "The probability is the problem of RMS. If you often report an error, you need to report the work order to RMS.",
            "th": "มีความเป็นไปได้ว่าเป็นปัญหาที่ระบบ RMS กรุณาแจ้งฝ่ายสนับสนุน RMS"
        }
    },
    "21020": {
        "exception": {
            "en": "It is bad to adjust the shelf while rotating",
            "th": "การปรับตำแหน่งชั้นวางระหว่างหมุนทำงานผิดพลาด"
        },
        "solution": {
            "en": "Check shelf balance and robot rotation axis mechanism",
            "th": "ตรวจสอบความสมดุลของชั้นวางและกลไกแกนหมุนหุ่นยนต์"
        }
    },
    "21021": {
        "exception": {
            "en": "Crooked while lifting the shelf.",
            "th": "ชั้นวางเอียงขณะกำลังทำการยก"
        },
        "solution": {
            "en": "After manual processing, the monitored parameters return to the normal range, and the robot is lowered.",
            "th": "หลังจากแก้ไขด้วยมือแล้ว ค่าจะกลับมาปกติ และหุ่นยนต์จะวางชุดยกลงได้"
        }
    },
    "21022": {
        "exception": {
            "en": "More than 2 QR codes on the ground lost",
            "th": "สูญเสียการตรวจจับ QR Code บนพื้นมากกว่า 2 จุด"
        },
        "solution": {
            "en": "Try to restart the robot and check the QR code around the robot",
            "th": "ลองรีสตาร์ทหุ่นยนต์และตรวจสอบป้าย QR Code รอบๆ ตัวหุ่นยนต์"
        }
    },
    "21023": {
        "exception": {
            "en": "Timeout of getting the DSP data ceil rect",
            "th": "หมดเวลาในการรับข้อมูลตีกรอบ (Rect) จากระบบ DSP"
        },
        "solution": {
            "en": "Check whether the shelf is skewed; Check whether the QR code of the shelf is stained, blocked, dropped and restored.",
            "th": "เช็คชั้นวางว่าเอียงหรือไม่ เช็คว่า QR ชั้นวางสกปรก หลุด หรือมีอะไรบังหรือไม่"
        }
    },
    "21024": {
        "exception": {
            "en": "Timeout of getting the DSP data ceil decode",
            "th": "หมดเวลาในการถอดรหัส (Decode) ข้อมูลจากระบบ DSP"
        },
        "solution": {
            "en": "Check whether the shelf is skewed; Check whether the QR code of the shelf is stained, blocked, dropped and restored.",
            "th": "เช็คชั้นวางเอียงหรือ QR ชั้นวางสกปรก/มีอะไรบัง"
        }
    },
    "21025": {
        "exception": {
            "en": "Wrong angle when planning small path",
            "th": "มุมไม่ถูกต้องขณะวางแผนเส้นทางย่อย (Small Path)"
        },
        "solution": {
            "en": "Restart.",
            "th": "ทำการรีสตาร์ทหุ่นยนต์"
        }
    },
    "21026": {
        "exception": {
            "en": "Performing task error when in manual mode received",
            "th": "ได้รับคำสั่งงานขณะหุ่นยนต์อยู่ในโหมดแมนนวล (Manual Mode)"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "เปลี่ยนโหมดหุ่นยนต์เป็นอัตโนมัติก่อนเริ่มงาน"
        }
    },
    "21027": {
        "exception": {
            "en": "Failed to charge",
            "th": "การชาร์จไฟพ่วงล้มเหลว"
        },
        "solution": {
            "en": "Check whether the docking is successful and check the charging pile status",
            "th": "ตรวจสอบว่าหุ่นยนต์เข้าตำแหน่งชาร์จสำเร็จหรือไม่และเช็คสถานะแท่นชาร์จ"
        }
    },
    "21028": {
        "exception": {
            "en": "The QR code of the up-facing shelf is not in the field of vision while moving",
            "th": "มองไม่เห็น QR Code ของชั้นวางในมุมมองกล้องขณะเคลื่อนที่"
        },
        "solution": {
            "en": "Recoverable fault status can be cleared manually. QR code was recognized after placing the shelf. Robot has restored its task.",
            "th": "สถานะนี้กู้คืนได้ด้วยตนเอง เมื่อ QR Code ถูกพบหลังวางชั้นวาง หุ่นยนต์จะทำภารกิจต่อ"
        }
    },
    "21029": {
        "exception": {
            "en": "Could not find any QR codes on the ground after switching to QR code navigation mode",
            "th": "ไม่พบ QR Code บนพื้นหลังจากสลับเข้าสู่โหมดนำทางด้วย QR Code"
        },
        "solution": {
            "en": "Push the robot on top of the QR code. The robot will continue the task after releasing the brake button.",
            "th": "เข็นหุ่นยนต์ไปไว้เหนือจุด QR Code แล้วปล่อยปุ่มเบรกเพื่อให้งานทำต่อ"
        }
    },
    "21030": {
        "exception": {
            "en": "Wheels skidded while moving",
            "th": "ล้อเกิดการลื่นไถล (Skid) ขณะเคลื่อนที่"
        },
        "solution": {
            "en": "Push the robot onto the correct SLAM path or push it on top of the QR code. The robot will continue the task after releasing the brake button.",
            "th": "เข็นหุ่นยนต์เข้าสู่เส้นทางที่ถูกต้องหรือไว้เหนือ QR Code แล้วทำภารกิจต่อ"
        }
    },
    "21031": {
        "exception": {
            "en": "Shelf model identification error",
            "th": "การระบุรุ่นของชั้นวางผิดพลาด"
        },
        "solution": {
            "en": "Manual handling",
            "th": "โปรดดำเนินการตรวจสอบด้วยตนเอง"
        }
    },
    "21032": {
        "exception": {
            "en": "Emergency stop triggered",
            "th": "มีการเปิดใช้งานการหยุดฉุกเฉิน (E-Stop)"
        },
        "solution": {
            "en": "Manual handling",
            "th": "ตรวจสอบความปลอดภัยและปลดล็อคด้วยตนเอง"
        }
    },
    "21033": {
        "exception": {
            "en": "Switched to manual mode ",
            "th": "ถูกสลับเข้าสู่โหมดแมนนวล"
        },
        "solution": {
            "en": "Manual handling",
            "th": "ดำเนินการควบคุมด้วยตนเองหรือสลับกลับเข้าสู่โหมดอัตโนมัติ"
        }
    },
    "21034": {
        "exception": {
            "en": "Obstacle avoidance box or upper computer did not receive obstacle avoidance sensor data",
            "th": "ระบบไม่ได้รับข้อมูลจากเซนเซอร์หลบหลีกสิ่งกีดขวาง"
        },
        "solution": {
            "en": "Check signal cables for the obstacle avoidance system",
            "th": "ตรวจสอบสายสัญญาณเชื่อมต่อระบบหลบหลีกสิ่งกีดขวาง"
        }
    },
    "21035": {
        "exception": {
            "en": "Abnormal communication link between the obstacle avoidance box and master control",
            "th": "การสื่อสารระหว่างกล่องหลบหลีกสิ่งกีดขวางและตัวควบคุมหลักผิดปกติ"
        },
        "solution": {
            "en": "Check communication cables between the obstacle avoidance bus and main board",
            "th": "เช็คสายสื่อสารระหว่างบอร์ดบัสหลบหลีกและบอร์ดหลัก"
        }
    },
    "21036": {
        "exception": {
            "en": "Error obstacle-avoidance sensor data received by the obstacle avoidance box or upper computer",
            "th": "ได้รับข้อมูลที่ผิดพลาดจากเซนเซอร์ระบบหลบหลีกสิ่งกีดขวาง"
        },
        "solution": {
            "en": "Sensor may be reporting incorrect data. Try cleaning the sensor surface",
            "th": "เซนเซอร์อาจรายงานค่าผิดพลาด ให้ลองพ่นทำความสะอาดหน้าเซนเซอร์"
        }
    },
    "21037": {
        "exception": {
            "en": "Abnormal communication link between the power box and main control",
            "th": "การสื่อสารระหว่างกล่องพลังงาน (Power Box) และตัวควบคุมหลักผิดปกติ"
        },
        "solution": {
            "en": "Check CAN or RS485 communication cables for the power unit",
            "th": "ตรวจสอบสายสื่อสาร CAN หรือ RS485 ของชุดพลังงาน"
        }
    },
    "21038": {
        "exception": {
            "en": "The power box received incorrect battery data",
            "th": "กล่องพลังงานได้รับข้อมูลแบตเตอรี่ที่ไม่ถูกต้อง"
        },
        "solution": {
            "en": "Check battery BMS board and data transmission to the power box",
            "th": "ตรวจสอบบอร์ด BMS ของแบตเตอรี่และการส่งข้อมูลไปยังกล่องพลังงาน"
        }
    },
    "21039": {
        "exception": {
            "en": "CAN1 communication failure",
            "th": "การสื่อสารผ่านช่องสัญญาณ CAN1 ล้มเหลว"
        },
        "solution": {
            "en": "Check CAN1 signal cables or restart the control board",
            "th": "ตรวจสอบสายสัญญาณ CAN วงจรที่ 1 หรือรีสตาร์ทบอร์ดควบคุม"
        }
    },
    "21040": {
        "exception": {
            "en": "CAN2 communication failure",
            "th": "การสื่อสารผ่านช่องสัญญาณ CAN2 ล้มเหลว"
        },
        "solution": {
            "en": "Check CAN2 signal cables and related devices",
            "th": "ตรวจสอบสายสัญญาณ CAN วงจรที่ 2 และอุปกรณ์ที่เกี่ยวข้อง"
        }
    },
    "21041": {
        "exception": {
            "en": "Driver disconnected",
            "th": "ชุดขับเคลื่อน (Driver) ขาดการเชื่อมต่อ"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "ตรวจสอบไฟเลี้ยงไดรเวอร์และสายสื่อสารข้อมูล"
        }
    },
    "21042": {
        "exception": {
            "en": "Encoder disconnected",
            "th": "เซนเซอร์เอ็นโค้ดเดอร์ (Encoder) ขาดการเชื่อมต่อ"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "ตรวจสอบสายสัญญาณเอ็นโค้ดเดอร์ที่ชุดล้อ"
        }
    },
    "21043": {
        "exception": {
            "en": "DSP lost",
            "th": "สูญเสียการเชื่อมต่อกับหน่วยประมวลผล DSP"
        },
        "solution": {
            "en": "Restart the robot. If the issue persists, the control board may be damaged",
            "th": "รีสตาร์ทหุ่นยนต์ หากไม่หายมีโอกาสที่บอร์ดควบคุมจะเสียหาย"
        }
    },
    "12000": {
        "exception": {
            "en": "The robot is disconnected",
            "th": "หุ่นยนต์ขาดการเชื่อมต่อกับระบบควบคุมสีส่วนกลาง"
        },
        "solution": {
            "en": "Please wait a while, then restart the robot and check the network if it can not connect with the RMS for a long time",
            "th": "รอสักครู่ หากยังไม่เชื่อมต่อให้ตรวจสอบสัญญาณ Wi-Fi หรือรีสตาร์ทหุ่นยนต์"
        }
    },
    "12001": {
        "exception": {
            "en": "Timeout of sending subtask",
            "th": "การส่งงานย่อย (Subtask) หมดเวลา"
        },
        "solution": {
            "en": "Please wait a while, then restart the robot if timeout all the time.",
            "th": "รอการตอบสนองจากระบบ หากยังหมดเวลาต่อเนื่องให้ลองรีสตาร์ทงานใหม่"
        }
    },
    "21082": {
        "exception": {
            "en": "Task state machine switching error",
            "th": "การสลับสถานะของชุดคำสั่งงานทำงานผิดพลาด"
        },
        "solution": {
            "en": "Cancel current task and recover state to start a new task",
            "th": "ยกเลิกงานปัจจุบันและกู้คืนสถานะเพื่อเริ่มงานใหม่"
        }
    },
    "21083": {
        "exception": {
            "en": "An error command is given at the end of the task",
            "th": "พบคำสั่งที่ผิดพลาดในช่วงท้ายของภารกิจ"
        },
        "solution": {
            "en": "Verify task sequence in the RMS system",
            "th": "ตรวจสอบลำดับขั้นตอนของงานในระบบ RMS"
        }
    },
    "21084": {
        "exception": {
            "en": "Task step stage error",
            "th": "ข้อผิดพลาดในขั้นตอนย่อยของภารกิจ (Step Stage Error)"
        },
        "solution": {
            "en": "Check robot status and try to restart the step",
            "th": "ตรวจสอบสถานะหุ่นยนต์และลองเริ่มขั้นตอนใหม่อีกครั้ง"
        }
    },
    "12002": {
        "exception": {
            "en": "Path plan failed",
            "th": "การวางแผนเส้นทางล้มเหลว"
        },
        "solution": {
            "en": "Contact the technician for help if you fails to plan all the time.",
            "th": "หากวางแผนเส้นทางไม่ได้ต่อเนื่อง โปรดติดต่อเจ้าหน้าที่ดูแลระบบ"
        }
    },
    "12003": {
        "exception": {
            "en": "The robot is out of map",
            "th": "หุ่นยนต์อยู่นอกพื้นที่แผนที่"
        },
        "solution": {
            "en": "1. Restart the robot. 2. Check the map.",
            "th": "1. รีสตาร์ทหุ่นยนต์ 2. ตรวจสอบพิกัดในแผนที่ว่าเป็นพิกัดที่ถูกต้องหรือไม่"
        }
    },
    "12004": {
        "exception": {
            "en": "The start point or end point of the task is an obstacle",
            "th": "จุดเริ่มต้นหรือจุดสิ้นสุดของงานมีสิ่งกีดขวางพิกัดอยู่"
        },
        "solution": {
            "en": "Push the robot to another cell to restart",
            "th": "เข็นหุ่นยนต์ไปยังพิกัดอื่นที่ว่างอยู่แล้วค่อยเริ่มงานใหม่"
        }
    },
    "12005": {
        "exception": {
            "en": "Barriers on the way",
            "th": "พบสิ่งกีดขวางระหว่างเส้นทาง"
        },
        "solution": {
            "en": "Check whether the obstacle shelf has tasks or update the current shelf position",
            "th": "ตรวจสอบว่าชั้นวางที่ขวางอยู่มีงานค้างอยู่หรือไม่ หรืออัปเดตพิกัดชั้นวางใหม่"
        }
    },
    "12006": {
        "exception": {
            "en": "Obstacle robot on the way",
            "th": "มีหุ่นยนต์ตัวอื่นขวางเส้นทางอยู่"
        },
        "solution": {
            "en": "Check whether the obstacle robot is faulty or restart the obstacle robot",
            "th": "ตรวจสอบว่าหุ่นยนต์ที่ขวางทางอยู่เกิดข้อผิดพลาดหรือไม่ หรือสั่งงานให้เคลื่อนที่ออกไป"
        }
    },
    "12007": {
        "exception": {
            "en": "There is no path to plan",
            "th": "ไม่มีเส้นทางที่สามารถวางแผนได้"
        },
        "solution": {
            "en": "1. Restart the robot. 2. Check the map.",
            "th": "1. รีสตาร์ทหุ่นยนต์ 2. ตรวจสอบส่วนเชื่อมต่อในแผนที่ว่ามีทางไปหรือไม่"
        }
    },
    "21085": {
        "exception": {
            "en": "Driver command error",
            "th": "คำสั่งควบคุมชุดขับเคลื่อนผิดพลาด"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "ตรวจสอบพารามิเตอร์ของไดรเวอร์หรือแจ้งช่างเพื่อรีเซ็ตระบบ"
        }
    },
    "21086": {
        "exception": {
            "en": "Driver motor phase error",
            "th": "เฟสมอเตอร์ของชุดขับเคลื่อนผิดปกติ (Phase Error)"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "ตรวจสอบการเชื่อมต่อสายไฟมอเตอร์ทั้ง 3 เฟส"
        }
    },
    "21087": {
        "exception": {
            "en": "Driver tracking error",
            "th": "ข้อผิดพลาดในการติดตามตำแหน่งของชุดขับเคลื่อน (Tracking Error)"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "ตรวจสอบภาระโหลดที่ล้อหรือความตึงของชุดสายพาน/เกียร์"
        }
    },
    "21088": {
        "exception": {
            "en": "Driver feedback error",
            "th": "ข้อมูลตอบกลับจากชุดขับเคลื่อนผิดพลาด (Feedback Error)"
        },
        "solution": {
            "en": "Please contact a technician for resolution",
            "th": "ตรวจสอบสายสัญญาณเอ็นโค้ดเดอร์ที่ต่อเข้ากับไดรเวอร์"
        }
    },
    "21089": {
        "exception": {
            "en": "Driver under voltage",
            "th": "แรงดันไฟฟ้าเข้าชุดขับเคลื่อนต่ำเกินไป (Under Voltage)"
        },
        "solution": {
            "en": "Check battery voltage or main power supply system",
            "th": "ตรวจสอบแรงดันแบตเตอรี่หรือระบบจ่ายไฟหลัก"
        }
    },
    "21090": {
        "exception": {
            "en": "Driver over voltage",
            "th": "แรงดันไฟฟ้าเข้าชุดขับเคลื่อนสูงเกินไป (Over Voltage)"
        },
        "solution": {
            "en": "Check charging system or surge during sudden braking",
            "th": "ตรวจสอบระบบชาร์จไฟหรือแรงดันเกินขณะเบรกกะทันหัน"
        }
    },
    "21091": {
        "exception": {
            "en": "Driver over-current",
            "th": "กระแสไฟฟ้าในชุดขับเคลื่อนเกินกำหนด (Over-current)"
        },
        "solution": {
            "en": "Check for motor stalling or obstacles at the wheels",
            "th": "ตรวจสอบว่ามอเตอร์ติดขัดหรือมีสิ่งกีดขวางที่ล้อหรือไม่"
        }
    },
    "21092": {
        "exception": {
            "en": "Driver current short-circuited",
            "th": "เกิดการลัดวงจรของกระแสไฟฟ้าในชุดขับเคลื่อน (Short-circuit)"
        },
        "solution": {
            "en": "Check motor cables for damage or contact",
            "th": "ตรวจสอบสายไฟมอเตอร์ว่าชำรุดหรือแตะกันหรือไม่"
        }
    },
    "21093": {
        "exception": {
            "en": "Driver motor temperature is too high",
            "th": "อุณหภูมิมอเตอร์ของชุดขับเคลื่อนสูงเกินไป"
        },
        "solution": {
            "en": "Stop operation to let motor cool down and check workload",
            "th": "หยุดการใช้งานเพื่อให้มอเตอร์เย็นลง และตรวจสอบภาระงาน"
        }
    },
    "21094": {
        "exception": {
            "en": "Driver motor temperature is too low",
            "th": "อุณหภูมิมอเตอร์ของชุดขับเคลื่อนต่ำเกินไป"
        },
        "solution": {
            "en": "Check operating environment or humidity",
            "th": "ตรวจสอบสภาพแวดล้อมที่หุ่นยนต์ทำงานหรือความชื้น"
        }
    },
    "21095": {
        "exception": {
            "en": "Driver temperature is too high",
            "th": "อุณหภูมิของตัวไดรเวอร์สูงเกินไป"
        },
        "solution": {
            "en": "lang.rms.monitor.robot.ampOverTemperatureSolution",
            "th": "ตรวจสอบพัดลมระบายความร้อนของชุดไดรเวอร์"
        }
    },
    "21096": {
        "exception": {
            "en": "Driver temperature is too low",
            "th": "อุณหภูมิของตัวไดรเวอร์ต่ำเกินไป"
        },
        "solution": {
            "en": "Check ventilation system or accumulated humidity",
            "th": "ตรวจสอบระบบระบายอากาศหรือความชื้นสะสม"
        }
    },
    "21097": {
        "exception": {
            "en": "Drive over-speed alarm",
            "th": "การแจ้งเตือนความเร็วรอบของชุดขับเคลื่อนเกินกำหนด"
        },
        "solution": {
            "en": "Reduce running speed or check maximum speed settings",
            "th": "ลดความเร็วในการวิ่งหรือตรวจสอบการตั้งค่าความเร็วสูงสุด"
        }
    },
    "21098": {
        "exception": {
            "en": "Driver address error",
            "th": "รหัสระบุตัวตน (Address) ของชุดขับเคลื่อนผิดพลาด"
        },
        "solution": {
            "en": "Check driver ID in the CAN bus system",
            "th": "ตรวจสอบ ID ของไดรเวอร์ในระบบบัส CAN"
        }
    },
    "21099": {
        "exception": {
            "en": "Component delivery abnormality ",
            "th": "ความผิดปกติในการส่งมอบส่วนประกอบ"
        },
        "solution": {
            "en": "It may be stuck, manual handling required.",
            "th": "อาจเกิดการติดขัดของกลไก โปรดตรวจสอบด้วยตนเอง"
        }
    },
    "21100": {
        "exception": {
            "en": "Component receipt abnormality",
            "th": "ความผิดปกติในการรับส่วนประกอบ"
        },
        "solution": {
            "en": "It may be stuck, manual handling required.",
            "th": "อาจเกิดการติดขัดขณะรับชั้นวางหรืออุปกรณ์"
        }
    },
    "21101": {
        "exception": {
            "en": "Component communication interrupted",
            "th": "การสื่อสารระหว่างส่วนประกอบขาดหาย"
        },
        "solution": {
            "en": "Manual handling required",
            "th": "เช็คสายส่งสัญญาณข้อมูลระหว่างโมดูล"
        }
    },
    "21102": {
        "exception": {
            "en": "Component fault",
            "th": "ส่วนประกอบย่อยเกิดข้อผิดพลาด"
        },
        "solution": {
            "en": "Manual handling required",
            "th": "ตรวจสอบอุปกรณ์ภายนอกที่เชื่อมต่อกับหุ่นยนต์"
        }
    },
    "14000": {
        "exception": {
            "en": "Shelf location needs to be updated",
            "th": "จำเป็นต้องอัปเดตตำแหน่งพิกัดของชั้นวาง"
        },
        "solution": {
            "en": "Update Location",
            "th": "กดอัปเดตตำแหน่งชั้นวางในระบบจัดการพัสดุ"
        }
    },
    "12112": {
        "exception": {
            "en": "The robot floor is confirmed abnormal.",
            "th": "ยืนยันความผิดปกติของชั้นที่หุ่นยนต์อยู่"
        },
        "solution": {
            "en": "The robot floor is abnormal. Please check whether the floor is updated correctly or drag the robot out of the elevator to restart the robot.",
            "th": "ชั้นที่อยู่ผิดพลาด โปรดตรวจสอบว่าเลขชั้นอัปเดตถูกต้อง หรือเข็นออกจากลิฟต์เพื่อเริ่มระบบใหม่"
        }
    },
    "12107": {
        "exception": {
            "en": "Robot has abnormal task loss",
            "th": "ข้อมูลภารกิจสูญหายอย่างผิดปกติ (Type 12107)"
        },
        "solution": {
            "en": "The robot task is lost. Please try the following: 1. Record the robot ID and task ID. 2. remove the robot. 3. rejoin the robot. 3. notify the upstream business system for post-processing.",
            "th": "งานหายไปจากหุ่นยนต์: 1. จดเลขหุ่น/งาน 2. นำหุ่นออกจากระบบ 3. นำกลับเข้าใหม่ 4. แจ้งระบบจัดการงาน"
        }
    },
    "12108": {
        "exception": {
            "en": "Robot has abnormal task loss",
            "th": "ข้อมูลภารกิจสูญหายอย่างผิดปกติ (Type 12108)"
        },
        "solution": {
            "en": "The robot task is lost. Please try the following: 1. Record the robot ID and task ID. 2. remove the robot. 3. rejoin the robot. 3. notify the upstream business system for post-processing.",
            "th": "งานหาย: นำหุ่นออกจากระบบแล้วลบงานเก่าทิ้งก่อนเริ่มใหม่"
        }
    },
    "12109": {
        "exception": {
            "en": "Robot has abnormal task loss",
            "th": "ข้อมูลภารกิจสูญหายอย่างผิดปกติ (Type 12109)"
        },
        "solution": {
            "en": "The robot task is lost. Please try the following: 1. Record the robot ID and task ID. 2. remove the robot. 3. rejoin the robot. 3. notify the upstream business system for post-processing.",
            "th": "ภารกิจขัดข้อง: ตรวจสอบประวัติการส่งงานในระบบ RMS"
        }
    },
    "12110": {
        "exception": {
            "en": "Robot has abnormal task loss",
            "th": "ข้อมูลภารกิจสูญหายอย่างผิดปกติ (Type 12110)"
        },
        "solution": {
            "en": "The robot task is lost. Please try the following: 1. Record the robot ID and task ID. 2. remove the robot. 3. rejoin the robot. 3. notify the upstream business system for post-processing.",
            "th": "งานสูญหาย: รีสตาร์ทการเชื่อมต่อเครือข่ายของหุ่นยนต์"
        }
    },
    "12111": {
        "exception": {
            "en": "The floor where the robot is located is to be confirmed.",
            "th": "รอการยืนยันชั้นที่หุ่นยนต์ตั้งอยู่"
        },
        "solution": {
            "en": "The robot floor is to be confirmed, and the floor operation needs to be updated after manual confirmation.",
            "th": "ต้องทำการตรวจสอบชั้นด้วยตาเปล่าและอัปเดตข้อมูลชั้นในระบบให้ตรงกัน"
        }
    },
    "80002": {
        "exception": {
            "en": "If the battery fails, please contact the maintenance personnel in time to replace the battery",
            "th": "แบตเตอรี่ล้มเหลว โปรดติดต่อเจ้าหน้าที่ซ่อมบำรุงเพื่อเปลี่ยนแบตเตอรี่ทันที"
        },
        "solution": {
            "en": "If the battery fails, please contact the maintenance personnel in time to replace the battery",
            "th": "ต้องรีบเปลี่ยนแบตเตอรี่ก้อนใหม่เนื่องจากเสื่อมสภาพรุนแรง"
        }
    },
    "80001": {
        "exception": {
            "en": "If the battery fails, please contact the maintenance personnel in time to replace the battery",
            "th": "แบตเตอรี่ล้มเหลว โปรดติดต่อฝ่ายเทคนิคเพื่อเปลี่ยนอุปกรณ์"
        },
        "solution": {
            "en": "If the battery fails, please contact the maintenance personnel in time to replace the battery",
            "th": "แบตเตอรี่หมดสภาพการใช้งาน ต้องแจ้งเปลี่ยนแบตเตอรี่ใหม่"
        }
    }
};

/**
 * @param {string|number} code
 * @param {string} lang
 */
export function getSystemError(code, lang = 'th') {
    if (!code) return { exception: "", solution: "" };

    const cleanCode = code.toString()
        .replace("lang.rms.monitor.robot.", "")
        .replace("lang.rms.monitor.task.", "");

    const errorData = ROBOT_ERROR_MAP[cleanCode];

    if (!errorData) {
        return {
            exception: lang === 'th' ? `ข้อผิดพลาดไม่ระบุ (Code: ${cleanCode})` : `Unknown Error (Code: ${cleanCode})`,
            solution: lang === 'th' ? "โปรดติดต่อฝ่ายซ่อมบำรุง" : "Please contact technical support."
        };
    }

    return {
        exception: errorData.exception[lang] || errorData.exception['en'] || "Unknown Exception",
        solution: errorData.solution[lang] || errorData.solution['en'] || "No solution provided."
    };
}
