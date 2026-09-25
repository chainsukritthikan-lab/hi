# CEE Orb setup (Windows): turns on CEE's local API and installs the Jarvis-style orb page.
# Run in PowerShell:
#   irm "https://raw.githubusercontent.com/chainsukritthikan-lab/hi/<commit>/cee/orb/setup-orb.ps1" | iex
$ErrorActionPreference = 'Stop'

$Repo   = 'chainsukritthikan-lab/hi'
$Branch = if ($env:CEE_BRANCH) { $env:CEE_BRANCH } else { 'claude/laughing-hopper-d0qios' }
$HermesHome = if ($env:HERMES_HOME -and $env:HERMES_HOME -notmatch '\\profiles\\') { $env:HERMES_HOME } else { "$env:LOCALAPPDATA\hermes" }
Remove-Item Env:HERMES_HOME, Env:PYTHONPATH -ErrorAction SilentlyContinue   # a profile-scoped leftover would redirect hermes
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
# The orb page is served from this PC at http://127.0.0.1:8765 (so the browser remembers mic permission).
Set-EnvVar $hostEnv 'API_SERVER_CORS_ORIGINS' 'http://127.0.0.1:8765'
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
Copy-Item (Join-Path $page.DirectoryName 'serve.py') "$OrbDir\serve.py" -Force
[IO.File]::WriteAllText("$OrbDir\config.js", "window.CEE = { url: 'http://127.0.0.1:8642/p/cee/v1', key: '$ceeKey' };`n")

Say '3/4 Restart CEE'
# Computer use: lets CEE see the screen and click/type in apps (one-time driver download).
hermes computer-use install
$CeeCuaOk = ($LASTEXITCODE -eq 0)
if (-not $CeeCuaOk) { Write-Host '  Computer control needs one admin step: open PowerShell as Administrator and run:  hermes computer-use install' -ForegroundColor Yellow }
hermes gateway restart
Start-Sleep 8

Say '4/4 Local orb server + desktop shortcut'
# Tiny local web server (Hermes' own Python), only reachable from this PC, auto-starts at login.
$py = Get-ChildItem $HermesHome -Recurse -Depth 6 -Filter pythonw.exe -ErrorAction SilentlyContinue |
      Sort-Object { if ($_.FullName -match 'venv') { 0 } else { 1 } } | Select-Object -First 1
if (-not $py) { $py = Get-Command pythonw.exe -ErrorAction SilentlyContinue | ForEach-Object { Get-Item $_.Source } }
if (-not $py) { throw 'Could not find Python for the orb server - send a screenshot.' }
$srvArgs = "`"$OrbDir\serve.py`""
Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" | Where-Object { $_.CommandLine -match 'http.server 8765|cee-orb' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Process $py.FullName -ArgumentList $srvArgs -WindowStyle Hidden
$sh = New-Object -ComObject WScript.Shell
$st = $sh.CreateShortcut([Environment]::GetFolderPath('Startup') + '\CEE Orb Server.lnk')
$st.TargetPath = $py.FullName; $st.Arguments = $srvArgs; $st.WindowStyle = 7; $st.Save()

# Open in Microsoft Edge app mode: supports voice input + natural Thai voices, and looks like an app.
$edge = @("${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe", "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe") |
        Where-Object { Test-Path $_ } | Select-Object -First 1
$url = 'http://127.0.0.1:8765/'
$lnk = $sh.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\CEE.lnk')
if ($edge) { $lnk.TargetPath = $edge; $lnk.Arguments = "--app=$url" } else { $lnk.TargetPath = $url }
$lnk.Save()

Say 'Done! Opening CEE...'
Start-Sleep 2
if ($edge) { Start-Process $edge "--app=$url" } else { Start-Process $url }
Write-Host 'Click the orb (or press Space) and talk. Click Allow for the microphone ONCE - it is remembered now.'
Write-Host 'Next time: double-click "CEE" on your desktop.'
