# ESIG HUB Packager - สร้างไฟล์ .tar.gz สำหรับ Deployment
$ProjectName = "ESIG_HUB"
$Version = "1.0.1"
$OutputFile = "$ProjectName`_$Version.tar.gz"

Write-Host "📦 Starting package process for $ProjectName..." -ForegroundColor Cyan

# สร้างรายการไฟล์ที่จะรวม (ไม่รวมโฟลเดอร์ที่ไม่จำเป็น)
$ExcludeList = @(
    "__pycache__/*",
    ".git/*",
    ".venv/*",
    "logs/*",
    ".DS_Store",
    "node_modules/*",
    "*.tar.gz",
    "*.zip",
    ".gemini/*"
)

# ใช้คำสั่ง tar (มีใน Windows 10/11)
# --exclude ช่วยให้เราข้ามโฟลเดอร์ที่ไม่เอาได้
$TarCommand = "tar -czvf $OutputFile --exclude=__pycache__ --exclude=.git --exclude=.venv --exclude=logs --exclude=.gemini --exclude=*.tar.gz ."

Write-Host "🚀 Running: $TarCommand" -ForegroundColor Yellow
Invoke-Expression $TarCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Created package successfully: $OutputFile" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create package." -ForegroundColor Red
}
