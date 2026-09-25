# Connect CEE to Chain's Clip Factory (Windows).
#   irm "https://raw.githubusercontent.com/chainsukritthikan-lab/hi/<commit>/cee/factory-connect.ps1" | iex
# - adds worker notebooks + the /api/feedback door to the factory (backs up files as *.before-cee)
# - gives CEE the clip-factory skill
$ErrorActionPreference = 'Stop'
$Repo   = 'chainsukritthikan-lab/hi'
$Branch = if ($env:CEE_BRANCH) { $env:CEE_BRANCH } else { 'claude/laughing-hopper-d0qios' }
$HermesHome = "$env:LOCALAPPDATA\hermes"
$CeeHome = "$HermesHome\profiles\cee"
function Say($m) { Write-Host "`n>> $m" -ForegroundColor Cyan }

Say '1/4 Find the Clip Factory'
$factory = Get-ChildItem "$env:USERPROFILE\Downloads", "$env:USERPROFILE\Desktop", "$env:USERPROFILE\Documents" -Recurse -Depth 5 `
             -Filter factory.py -ErrorAction SilentlyContinue |
           Where-Object { Test-Path (Join-Path $_.DirectoryName 'flow_agent.py') } | Select-Object -First 1
if (-not $factory) {
    $p = Read-Host 'Could not find it. Drag the clip-factory folder into this window, then press Enter'
    $factory = Get-Item (Join-Path $p.Trim().Trim('"') 'factory.py')
}
$dir = $factory.DirectoryName
Write-Host "Factory: $dir"

Say '2/4 Download'
$zip = "$env:TEMP\cee-factory.zip"; $src = "$env:TEMP\cee-factory"
Remove-Item $zip, $src -Recurse -Force -ErrorAction SilentlyContinue
Invoke-WebRequest "https://codeload.github.com/$Repo/zip/refs/heads/$Branch" -OutFile $zip
Expand-Archive $zip -DestinationPath $src
$root = (Get-ChildItem $src -Directory | Select-Object -First 1).FullName

Say '3/4 Add worker notebooks + feedback door to the factory'
python "$root\clip-factory-addon\patch_factory.py" "$dir"
if ($LASTEXITCODE -ne 0) { throw 'Patching the factory failed - send a screenshot. Your files were not changed.' }

Say '4/4 Give CEE the clip-factory skill'
New-Item -ItemType Directory -Force "$CeeHome\skills\cee" | Out-Null
Copy-Item "$root\cee\skills\cee\clip-factory" "$CeeHome\skills\cee\" -Recurse -Force
hermes gateway restart | Out-Null

Write-Host "`nDone! Now close the factory window and double-click start.bat to reopen it." -ForegroundColor Green
Write-Host "Then tell CEE: 'Check the clip factory status'"
