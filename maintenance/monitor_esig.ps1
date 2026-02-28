<#
.SYNOPSIS
    ESIG Health Monitor — แจ้งเตือนถ้า ESIG หยุดทำงาน

.DESCRIPTION
    Ping ESIG /health endpoint ทุก 60 วินาที
    ถ้าล้มเหลว 2 ครั้งติดกัน → เขียน alert log + พยายาม restart ESIG

.SETUP
    ตั้ง Task Scheduler ให้รันตอน boot:
    schtasks /create /tn "ESIG_Monitor" /tr "powershell -WindowStyle Hidden -File D:\MEKTEC_APP\ESIG\maintenance\monitor_esig.ps1" /sc onstart /ru SYSTEM /f

.PARAMETERS (แก้ตรงนี้)
#>

# ─── Config ───────────────────────────────────────────────────────────────────
$ESIG_URL       = "http://localhost:9001/health"   # ← เปลี่ยน port ถ้าจำเป็น
$CHECK_INTERVAL = 60                               # วินาที
$FAIL_THRESHOLD = 2                               # กี่ครั้งติดกันถึง alert
$ALERT_LOG      = Join-Path $PSScriptRoot "monitor_alert.log"
$ESIG_EXE       = Join-Path $PSScriptRoot "..\ESIG.exe"  # ← path ของ ESIG WinApp
$AUTO_RESTART   = $true                           # ← $false ถ้าไม่ต้องการ auto-restart

# ─── State ────────────────────────────────────────────────────────────────────
$failCount    = 0
$wasDown      = $false

function Write-Alert($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] $msg"
    Add-Content -Path $ALERT_LOG -Value $line
    Write-Host $line -ForegroundColor Red
}

function Write-Ok($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$ts] ✅ $msg" -ForegroundColor Green
}

Write-Ok "ESIG Monitor started. Checking $ESIG_URL every ${CHECK_INTERVAL}s..."

# ─── Main Loop ────────────────────────────────────────────────────────────────
while ($true) {
    try {
        $resp = Invoke-WebRequest -Uri $ESIG_URL -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        $ok   = ($resp.StatusCode -eq 200)
    } catch {
        $ok = $false
    }

    if ($ok) {
        if ($wasDown) {
            Write-Alert "ESIG RECOVERED after $failCount failed checks."
            $wasDown = $false
        } else {
            Write-Ok "ESIG OK (HTTP 200)"
        }
        $failCount = 0
    } else {
        $failCount++
        Write-Alert "ESIG UNREACHABLE (attempt $failCount / $FAIL_THRESHOLD)"

        if ($failCount -ge $FAIL_THRESHOLD) {
            Write-Alert "⚠️  ESIG is DOWN — $failCount consecutive failures!"
            $wasDown = $true

            # Auto-restart
            if ($AUTO_RESTART -and (Test-Path $ESIG_EXE)) {
                Write-Alert "🔄 Attempting auto-restart: $ESIG_EXE"
                try {
                    Start-Process -FilePath $ESIG_EXE -WindowStyle Hidden
                    Write-Alert "🟢 Restart command sent. Waiting 30s for ESIG to boot..."
                    Start-Sleep -Seconds 30
                    $failCount = 0
                } catch {
                    Write-Alert "❌ Auto-restart FAILED: $_"
                }
            }
        }
    }

    Start-Sleep -Seconds $CHECK_INTERVAL
}
