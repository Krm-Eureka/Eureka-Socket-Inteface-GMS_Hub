# ESIG HUB Packager
$ProjectName = "ESIG_HUB"
$Version = "2.0.2"
$OutputFile = "$ProjectName`_$Version.tar.gz"

Write-Host "Starting package process for $ProjectName..." -ForegroundColor Cyan

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

# Use tar command (built into Windows 10/11)
# --exclude helps exclude directories we don't want
$TarCommand = "tar -czvf $OutputFile --exclude=__pycache__ --exclude=.git --exclude=.venv --exclude=logs --exclude=.gemini --exclude=*.tar.gz ."

Write-Host "Running: $TarCommand" -ForegroundColor Yellow
Invoke-Expression $TarCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "Created package successfully: $OutputFile" -ForegroundColor Green
} else {
    Write-Host "Failed to create package." -ForegroundColor Red
}
