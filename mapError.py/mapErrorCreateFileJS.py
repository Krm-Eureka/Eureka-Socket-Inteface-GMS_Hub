import pandas as pd
import json
import re
import os


def main():
    # --- ตั้งค่าชื่อไฟล์ (ตรวจสอบชื่อไฟล์ให้ตรงกับที่มีอยู่จริง) ---
    xlsx_filename = "i18n_en_us_20260402094307.xlsx"
    json_filename = "code.txt"
    output_filename = "ROBOT_ERROR_MAP.js"

    # ตรวจสอบว่ามีไฟล์อยู่จริงหรือไม่
    if not os.path.exists(xlsx_filename) or not os.path.exists(json_filename):
        print("❌ ไม่พบไฟล์ .xlsx หรือ code.txt ในโฟลเดอร์เดียวกัน")
        return

    print("⏳ กำลังเริ่มประมวลผล...")

    # 1. อ่านไฟล์ Excel (.xlsx)
    try:
        # อ่าน Sheet แรก
        df = pd.read_excel(xlsx_filename)
        # สร้าง Dictionary { 'Key': 'Value' }
        # ใช้ .strip() เพื่อลบช่องว่างส่วนเกินที่อาจติดมาใน Excel
        i18n = pd.Series(
            df.languageItemValue.values, index=df.languageItemCode.str.strip()
        ).to_dict()
        print(f"✅ อ่านไฟล์ Excel สำเร็จ (พบ {len(i18n)} รายการ)")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการอ่าน Excel: {e}")
        return

    # 2. อ่านไฟล์ code.txt
    try:
        with open(json_filename, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # ใช้ Regex สกัดข้อมูล systemCode, exception, และ solution
        # รองรับกรณีที่ Key ไม่มีเครื่องหมาย " (ฟันหนู) เช่น systemCode: 123
        pattern = (
            r'systemCode:\s*(\d+).*?exception:\s*"([^"]*)".*?solution:\s*"([^"]*)"'
        )
        records_found = re.findall(pattern, raw_content, re.DOTALL)

        if not records_found:
            print("❌ ไม่พบรูปแบบข้อมูลที่ต้องการใน code.txt")
            return

        print(f"✅ สกัดข้อมูลจาก code.txt สำเร็จ (พบ {len(records_found)} รายการ)")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการอ่าน code.txt: {e}")
        return

    # 3. สร้าง Final Map (แก้ไข NaN)
    final_map = {}
    for r in records_found:
        sys_code = r[0]
        ex_key = r[1].strip()
        sol_key = r[2].strip()

        # ดึงคำแปลจาก i18n
        ex_en = i18n.get(ex_key, ex_key)
        sol_en = i18n.get(sol_key, sol_key)

        # จัดการ NaN จาก Pandas
        if pd.isna(ex_en): ex_en = ex_key
        if pd.isna(sol_en): sol_en = sol_key

        final_map[sys_code] = {
            "exception": {"en": ex_en, "th": ""},
            "solution": {"en": sol_en, "th": ""},
        }

    # 4. แบ่งกลุ่ม Error ตามช่วง Code
    groups = {
        "LowLevelRobotStateErrors": [],
        "SafetyAndSystemErrors": [],
        "TaskAndControlErrors": [],
        "HardwareSensorErrors": [],
        "ChargingStationErrors": [],
        "CargoAndShelfErrors": []
    }

    for code, data in final_map.items():
        c = int(code)
        if (9001 <= c <= 9050) or c in [21082, 21083, 21084, 16000]:
            groups["LowLevelRobotStateErrors"].append((code, data))
        elif (91000 <= c <= 91006) or (81000 <= c <= 81003) or (80001 <= c <= 80002):
            groups["SafetyAndSystemErrors"].append((code, data))
        elif (12000 <= c <= 12038) or (12101 <= c <= 12112) or (12201 <= c <= 12203) or (12301 <= c <= 12302):
            groups["TaskAndControlErrors"].append((code, data))
        elif (13000 <= c <= 13010) or (22000 <= c <= 22102):
            groups["ChargingStationErrors"].append((code, data))
        elif c in [3004, 3005, 3006, 3007, 14000, 14100, 108003]:
            groups["CargoAndShelfErrors"].append((code, data))
        else:
            groups["HardwareSensorErrors"].append((code, data))

    header = """/**\n * AUTO-GENERATED ROBOT ERROR MAP\n * Grouped Structure\n */\n\n"""
    
    body = ""
    g_list = []
    for gn, entries in groups.items():
        if not entries: continue
        g_list.append(gn)
        body += f"// --- {gn} ---\nconst {gn} = "
        # การจัดเรียงตามรหัส
        sorted_entries = dict(sorted(entries, key=lambda x: int(x[0])))
        body += json.dumps(sorted_entries, indent=4, ensure_ascii=False) + ";\n\n"

    export_map = "export const ROBOT_ERROR_MAP = {\n"
    export_map += ",\n".join([f"    ...{gn}" for gn in g_list])
    export_map += "\n};\n"

    footer = """
/**
 * ฟังก์ชันสำหรับดึงข้อมูล Error
 */
export function getSystemError(code, lang = 'th') {
    if (!code) return { exception: "", solution: "" };
    const cleanCode = code.toString().replace("lang.rms.monitor.robot.", "").replace("lang.rms.monitor.task.", "");
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
"""

    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(header + body + export_map + footer)
        print(f"🚀 สร้างไฟล์สำเร็จ: {output_filename}")
    except Exception as e:
        print(f"❌ ไม่สามารถเขียนไฟล์ได้: {e}")


if __name__ == "__main__":
    main()
