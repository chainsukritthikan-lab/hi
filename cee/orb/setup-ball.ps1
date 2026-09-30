# CEE taskbar ball (Windows): a yellow face on your taskbar. Tap Ctrl+Shift and talk.
#   irm "https://raw.githubusercontent.com/chainsukritthikan-lab/hi/<commit>/cee/orb/setup-ball.ps1" | iex
$ErrorActionPreference = 'Stop'
$Repo   = 'chainsukritthikan-lab/hi'
$Branch = if ($env:CEE_BRANCH) { $env:CEE_BRANCH } else { 'claude/laughing-hopper-d0qios' }
$HermesHome = if ($env:HERMES_HOME -and $env:HERMES_HOME -notmatch '\\profiles\\') { $env:HERMES_HOME } else { "$env:LOCALAPPDATA\hermes" }
$OrbDir = "$HermesHome\cee-orb"
if (-not (Test-Path "$OrbDir\config.js")) { throw 'Set up the CEE orb first (setup-orb.ps1).' }

# Files: from the orb setup's download if we were called from it, else download now.
if (-not $CeeBallSrc) {
    $zip = "$env:TEMP\cee-ball.zip"; $src = "$env:TEMP\cee-ball-src"
    Remove-Item $zip, $src -Recurse -Force -ErrorAction SilentlyContinue
    Invoke-WebRequest "https://codeload.github.com/$Repo/zip/refs/heads/$Branch" -OutFile $zip
    Expand-Archive $zip -DestinationPath $src
    $CeeBallSrc = (Get-ChildItem $src -Recurse -Filter cee_ball.pyw | Select-Object -First 1).DirectoryName
}
foreach ($f in 'cee_ball.pyw', 'ear.html') { Copy-Item "$CeeBallSrc\$f" "$OrbDir\$f" -Force }

$py = Get-ChildItem $HermesHome -Recurse -Depth 6 -Filter pythonw.exe -ErrorAction SilentlyContinue |
      Sort-Object { if ($_.FullName -match 'venv') { 0 } else { 1 } } | Select-Object -First 1
if (-not $py) { throw 'Could not find Python for the ball - send a screenshot.' }

# Restart the ball (and its old hidden Edge "ear").
Get-CimInstance Win32_Process -Filter "Name='pythonw.exe' OR Name='python.exe'" | Where-Object { $_.CommandLine -match 'cee_ball' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Get-CimInstance Win32_Process -Filter "Name='msedge.exe'" | Where-Object { $_.CommandLine -match 'cee-orb\\ear-profile' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep 1
Remove-Item "$OrbDir\ball.log" -ErrorAction SilentlyContinue
$ballArgs = "`"$OrbDir\cee_ball.pyw`""
$p = Start-Process $py.FullName -ArgumentList $ballArgs -PassThru
$sh = New-Object -ComObject WScript.Shell
$bl = $sh.CreateShortcut([Environment]::GetFolderPath('Startup') + '\CEE Ball.lnk')
$bl.TargetPath = $py.FullName; $bl.Arguments = $ballArgs; $bl.Save()

Start-Sleep 5
$alive = Get-CimInstance Win32_Process -Filter "Name='pythonw.exe' OR Name='python.exe'" | Where-Object { $_.CommandLine -match 'cee_ball' }
if ($alive) {
    Write-Host "`n>> CEE ball is running - look at the bottom-left of your screen." -ForegroundColor Green
    Write-Host 'Tap Ctrl+Shift (or click the ball) and talk. Drag it anywhere. Right-click for options.'
} else {
    Write-Host "`n>> The ball did not start. Send Claude a screenshot of this:" -ForegroundColor Red
    Write-Host "Python: $($py.FullName)"
    if (Test-Path "$OrbDir\ball.log") { Get-Content "$OrbDir\ball.log" -Tail 25 } else { Write-Host '(no log)' }
}
