<#
.SYNOPSIS
    Log Rotation — ลบ log เก่ากว่า 120 วัน

.DESCRIPTION
    ลบไฟล์ใน ESIG/logs/ ที่เก่ากว่า 120 วัน
    ตั้ง Windows Task Scheduler ให้รันทุกวัน เวลา 02:00

.SETUP
    ตั้ง Task Scheduler:
    schtasks /create /tn "ESIG_LogRotation" /tr "powershell -File D:\MEKTEC_APP\ESIG\maintenance\log_rotation.ps1" /sc daily /st 02:00 /ru SYSTEM
#>

# ─── Config ───────────────────────────────────────────────────────────────────
$LOG_DIR        = Join-Path $PSScriptRoot "..\logs"
$RETENTION_DAYS = 120
$LOG_SELF       = Join-Path $PSScriptRoot "log_rotation_history.log"

# ─── Run ──────────────────────────────────────────────────────────────────────
$cutoff = (Get-Date).AddDays(-$RETENTION_DAYS)
$deleted = 0
$freedMB = 0

Get-ChildItem -Path $LOG_DIR -Filter "*.log" -File -ErrorAction SilentlyContinue |
    ForEach-Object {
        # ดึงวันที่จากชื่อไฟล์เช่น server_2026-02-25.log หรือ server_2026-02-25.2026-...log
        if ($_.Name -match '(\d{4}-\d{2}-\d{2})') {
            try {
                $fileDate = [datetime]::ParseExact($Matches[1], 'yyyy-MM-dd', $null)
                if ($fileDate -lt $cutoff) {
                    $freedMB += [math]::Round($_.Length / 1MB, 2)
                    Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
                    $deleted++
                }
            } catch { /* วันที่ parse ไม่ได้ข้าม */ }
        }
    }

# ─── Self-log ─────────────────────────────────────────────────────────────────
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$msg = "[$timestamp] Deleted $deleted file(s), freed ${freedMB} MB (retention: ${RETENTION_DAYS} days)"
Add-Content -Path $LOG_SELF -Value $msg

Write-Host $msg -ForegroundColor $(if ($deleted -gt 0) { "Yellow" } else { "Green" })
