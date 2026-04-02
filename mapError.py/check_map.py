import re
import os

def check_completeness():
    txt_path = r'd:\KRM\25\25LA001 - Mektec\MEKTEC_APP\ESIG\mapError.py\code.txt'
    js_path = r'd:\KRM\25\25LA001 - Mektec\MEKTEC_APP\ESIG\mapError.py\ROBOT_ERROR_MAP.js'

    if not os.path.exists(txt_path) or not os.path.exists(js_path):
        print("Missing files")
        return

    with open(txt_path, 'r', encoding='utf-8') as f:
        txt_content = f.read()
    
    with open(js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()

    # Find all systemCodes in txt
    txt_codes = set(re.findall(r'systemCode:\s*(\d+)', txt_content))
    
    # Find all keys in js
    js_codes = set(re.findall(r'"(\d+)":\s*\{', js_content))

    print(f"Total codes in code.txt: {len(txt_codes)}")
    print(f"Total entries in ROBOT_ERROR_MAP.js: {len(js_codes)}")

    missing = txt_codes - js_codes
    if missing:
        print(f"Missing codes in JS: {sorted(list(missing))}")
    else:
        print("All codes from code.txt are present in ROBOT_ERROR_MAP.js")

    # Check for empty Thai translations
    empty_th = re.findall(r'"(\d+)":\s*\{[^}]*?"th":\s*""', js_content, re.DOTALL)
    if empty_th:
        print(f"Entries with empty Thai translation ({len(empty_th)}): {empty_th}")
    else:
        print("All entries have Thai translations.")

if __name__ == "__main__":
    check_completeness()
