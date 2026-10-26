param(
    [switch]$Restart
)

$ErrorActionPreference = "Stop"
$src = Join-Path $PSScriptRoot "custom_components\winet"
$destRoot = "\\10.0.0.85\config\custom_components"
$backupRoot = "\\10.0.0.85\config\.winet-backups"
$dest = Join-Path $destRoot "winet"

if (-not (Test-Path $src)) {
    throw "Sorgente non trovata: $src"
}

if (Test-Path $dest) {
    New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
    $bak = Join-Path $backupRoot ("winet.bak-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
    Copy-Item $dest $bak -Recurse -Force
    Write-Host "Backup: $bak"
}

New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item (Join-Path $src "*") $dest -Recurse -Force
Write-Host "Copiato in $dest"

if ($Restart) {
    $token = $env:HA_TOKEN
    if (-not $token) {
        Write-Warning "HA_TOKEN non impostato: riavvia Home Assistant a mano."
        return
    }
    Invoke-RestMethod -Uri "http://10.0.0.85:8123/api/services/homeassistant/restart" `
        -Method Post -ContentType "application/json" `
        -Headers @{ Authorization = "Bearer $token" } -Body "{}" | Out-Null
    Write-Host "Riavvio richiesto."
}
