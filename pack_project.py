import tarfile
import os

project_name = "ESIG_HUB"
version = "1.0.0"
output_file = f"{project_name}_{version}.tar.gz"

# รายการไฟล์/โฟลเดอร์ที่ไม่ต้องการรวมในแพ็คเกจ
exclude_list = {
    "__pycache__",
    ".git",
    ".venv",
    "logs",
    ".gemini",
    "node_modules",
    ".DS_Store",
    output_file,
}


def should_exclude(name):
    return any(ex in name for ex in exclude_list) or name.endswith((".tar.gz", ".zip"))


print(f"📦 Starting package process for {project_name}...")

try:
    with tarfile.open(output_file, "w:gz") as tar:
        for root, dirs, files in os.walk("."):
            # กรองโฟลเดอร์ที่ไม่เอา
            dirs[:] = [d for d in dirs if not should_exclude(d)]

            for file in files:
                if not should_exclude(file):
                    file_path = os.path.join(root, file)
                    tar.add(file_path)
                    print(f"  + Added: {file_path}")

    print(f"\n✅ Created package successfully: {output_file}")
except Exception as e:
    print(f"\n❌ Failed to create package: {e}")
