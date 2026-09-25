# CEE Orb setup (Windows): turns on CEE's local API and installs the Jarvis-style orb page.
# Run in PowerShell:
#   irm "https://raw.githubusercontent.com/chainsukritthikan-lab/hi/<commit>/cee/orb/setup-orb.ps1" | iex
$ErrorActionPreference = 'Stop'

$Repo   = 'chainsukritthikan-lab/hi'
$Branch = if ($env:CEE_BRANCH) { $env:CEE_BRANCH } else { 'claude/laughing-hopper-d0qios' }
$HermesHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { "$env:LOCALAPPDATA\hermes" }
$CeeHome    = "$HermesHome\profiles\cee"
$OrbDir     = "$HermesHome\cee-orb"
function Say($m) { Write-Host "`n>> $m" -ForegroundColor Cyan }

if (-not (Test-Path "$CeeHome\distribution.yaml")) { throw 'CEE is not installed yet - run the CEE installer first.' }

function Set-EnvVar($file, $name, $value) {
    $lines = @(); if (Test-Path $file) { $lines = @(Get-Content $file | Where-Object { $_ -notmatch "^\s*$name=" }) }
    $lines += "$name=$value"
    [IO.File]::WriteAllLines($file, [string[]]$lines)
}
function Get-EnvVar($file, $name) {
    if (Test-Path $file) { $m = Select-String -Path $file -Pattern "^\s*$name=(.+)$" | Select-Object -First 1; if ($m) { return $m.Matches[0].Groups[1].Value.Trim() } }
    return $null
}
function New-Key { ([guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')) }

Say '1/4 Turn on CEE local API (only this PC can reach it)'
$hostEnv = "$HermesHome\.env"
Set-EnvVar $hostEnv 'API_SERVER_ENABLED' 'true'
if (-not (Get-EnvVar $hostEnv 'API_SERVER_KEY')) { Set-EnvVar $hostEnv 'API_SERVER_KEY' (New-Key) }
# The orb page is opened from a file, which browsers send as origin "null".
Set-EnvVar $hostEnv 'API_SERVER_CORS_ORIGINS' 'null'
$ceeKey = Get-EnvVar "$CeeHome\.env" 'API_SERVER_KEY'
if (-not $ceeKey) { $ceeKey = New-Key; Set-EnvVar "$CeeHome\.env" 'API_SERVER_KEY' $ceeKey }

Say '2/4 Download the orb'
$zip = "$env:TEMP\cee-orb.zip"; $src = "$env:TEMP\cee-orb-src"
Remove-Item $zip, $src -Recurse -Force -ErrorAction SilentlyContinue
Invoke-WebRequest "https://codeload.github.com/$Repo/zip/refs/heads/$Branch" -OutFile $zip
Expand-Archive $zip -DestinationPath $src
$page = Get-ChildItem $src -Recurse -Filter index.html | Where-Object { $_.DirectoryName -like '*\cee\orb' } | Select-Object -First 1
if (-not $page) { throw 'Orb page not found in the download.' }
New-Item -ItemType Directory -Force $OrbDir | Out-Null
Copy-Item $page.FullName "$OrbDir\index.html" -Force
[IO.File]::WriteAllText("$OrbDir\config.js", "window.CEE = { url: 'http://127.0.0.1:8642/p/cee/v1', key: '$ceeKey' };`n")

Say '3/4 Restart CEE'
hermes gateway restart
Start-Sleep 8

Say '4/4 Desktop shortcut'
$lnk = [Environment]::GetFolderPath('Desktop') + '\CEE.lnk'
$sh = New-Object -ComObject WScript.Shell; $s = $sh.CreateShortcut($lnk)
$s.TargetPath = "$OrbDir\index.html"; $s.Save()

Say 'Done! Opening CEE...'
Start-Process "$OrbDir\index.html"
Write-Host 'Click the orb (or press Space) and talk. Allow the microphone when the browser asks.'
Write-Host 'Next time: double-click "CEE" on your desktop.'
