# CEE one-shot update for Windows: CEE + orb + computer control, in one go.
#   irm "https://raw.githubusercontent.com/chainsukritthikan-lab/hi/<commit>/cee/update.ps1" | iex
# Click "Yes" if Windows asks for permission (needed once for computer control).
$ErrorActionPreference = 'Stop'
$Repo   = 'chainsukritthikan-lab/hi'
$Branch = if ($env:CEE_BRANCH) { $env:CEE_BRANCH } else { 'claude/laughing-hopper-d0qios' }

$zip = "$env:TEMP\cee-update.zip"; $src = "$env:TEMP\cee-update"
Remove-Item $zip, $src -Recurse -Force -ErrorAction SilentlyContinue
Invoke-WebRequest "https://codeload.github.com/$Repo/zip/refs/heads/$Branch" -OutFile $zip
Expand-Archive $zip -DestinationPath $src
$cee = (Get-ChildItem $src -Recurse -Filter distribution.yaml | Select-Object -First 1).DirectoryName

# Run from the fresh download (iex avoids the script execution policy).
iex (Get-Content -Raw "$cee\install.ps1")
iex (Get-Content -Raw "$cee\orb\setup-orb.ps1")

if (-not $CeeCuaOk) {
    Write-Host "`n>> Computer control: Windows will ask for permission - click Yes." -ForegroundColor Cyan
    Start-Process powershell -Verb RunAs -Wait -ArgumentList '-NoProfile', '-Command',
        'hermes computer-use install; hermes computer-use status; Start-Sleep 4'
    hermes gateway restart
}
Write-Host "`n>> All done. Double-click CEE on your desktop." -ForegroundColor Green
