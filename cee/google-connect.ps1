# Connect CEE to Gmail + Google Calendar (+ Drive/Docs) on Windows.
#   irm "https://raw.githubusercontent.com/chainsukritthikan-lab/hi/<commit>/cee/google-connect.ps1" | iex
$ErrorActionPreference = 'Stop'
$HermesHome = if ($env:HERMES_HOME -and $env:HERMES_HOME -notmatch 'profiles') { $env:HERMES_HOME } else { "$env:LOCALAPPDATA\hermes" }
$CeeHome = "$HermesHome\profiles\cee"
$agent   = "$HermesHome\hermes-agent"
function Say($m) { Write-Host "`n>> $m" -ForegroundColor Cyan }

# Google tools live in the CEE profile.
$gws = "$CeeHome\skills\productivity\google-workspace"
if (-not (Test-Path $gws)) {
    New-Item -ItemType Directory -Force "$CeeHome\skills\productivity" | Out-Null
    Copy-Item "$agent\skills\productivity\google-workspace" "$CeeHome\skills\productivity\" -Recurse
}
$setup = "$gws\scripts\setup.py"
$py = Get-ChildItem $HermesHome -Recurse -Depth 6 -Filter python.exe -ErrorAction SilentlyContinue |
      Sort-Object { if ($_.FullName -match 'venv') { 0 } else { 1 } } | Select-Object -First 1
if (-not $py) { throw "Could not find Hermes' Python - send a screenshot." }
$env:HERMES_HOME = $CeeHome; $env:PYTHONPATH = $agent
function Run-Setup { & $py.FullName $setup @args }

Say '1/3 Find your Google key file'
$dirs = @("$env:USERPROFILE\Downloads", "$env:USERPROFILE\OneDrive\Downloads", "$env:USERPROFILE\Desktop")
try { $dirs = @((New-Object -ComObject Shell.Application).NameSpace('shell:Downloads').Self.Path) + $dirs } catch {}
$secret = Get-ChildItem $dirs -Filter 'client_secret*.json' -ErrorAction SilentlyContinue |
          Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $secret) {
    $p = Read-Host 'Could not find it. Drag the client_secret .json file into this window, then press Enter'
    $secret = Get-Item $p.Trim().Trim('"')
}
Write-Host "Using: $($secret.FullName)"
Run-Setup --client-secret $secret.FullName

Say '2/3 Sign in to Google'
$url = (Run-Setup --auth-url | Where-Object { $_ -match '^https://' } | Select-Object -Last 1)
if (-not $url) { throw 'Could not create the Google sign-in link - send a screenshot.' }
Start-Process $url
Write-Host 'A Google page opened. Pick your account -> Continue (if it says "not verified") -> tick all boxes -> Continue.'
Write-Host 'The page will then show an ERROR - that is normal.' -ForegroundColor Yellow
$cb = Read-Host 'Copy the WHOLE address from that error page, paste it here, press Enter'
Run-Setup --auth-code $cb.Trim()

Say '3/3 Check'
Run-Setup --check
if ($LASTEXITCODE -eq 0) {
    hermes gateway restart | Out-Null
    Write-Host "`nConnected! Ask CEE: 'Any important emails today?' or 'What's on my calendar tomorrow?'" -ForegroundColor Green
} else { Write-Host 'Not connected yet - send a screenshot.' -ForegroundColor Red }
