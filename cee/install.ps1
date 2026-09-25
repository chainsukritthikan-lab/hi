# CEE one-command installer for Windows (runs CEE on your PC).
# Open PowerShell and run:
#   irm https://raw.githubusercontent.com/chainsukritthikan-lab/hi/claude/laughing-hopper-d0qios/cee/install.ps1 | iex
# Installs Hermes Agent + CEE, asks for your keys, and starts CEE (auto-starts when you log in).
$ErrorActionPreference = 'Stop'

$Repo   = 'chainsukritthikan-lab/hi'
$Branch = if ($env:CEE_BRANCH) { $env:CEE_BRANCH } else { 'claude/laughing-hopper-d0qios' }
$HermesHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { "$env:LOCALAPPDATA\hermes" }
$Profile    = "$HermesHome\profiles\cee"
function Say($m) { Write-Host "`n>> $m" -ForegroundColor Green }

Say '1/5 Hermes Agent'
if (-not (Get-Command hermes -ErrorAction SilentlyContinue)) {
    & ([scriptblock]::Create((Invoke-RestMethod 'https://hermes-agent.nousresearch.com/install.ps1'))) -NonInteractive
    $env:Path = "$HermesHome\bin;$env:Path"
}
hermes --version

Say '2/5 Download CEE'
$zip = "$env:TEMP\cee-src.zip"; $src = "$env:TEMP\cee-src"
Remove-Item $zip, $src -Recurse -Force -ErrorAction SilentlyContinue
Invoke-WebRequest "https://codeload.github.com/$Repo/zip/refs/heads/$Branch" -OutFile $zip
Expand-Archive $zip -DestinationPath $src
$dist = (Get-ChildItem $src -Recurse -Filter distribution.yaml | Select-Object -First 1).DirectoryName
if (-not $dist) { throw "CEE not found in $Repo ($Branch). Is the repo public?" }

Say '3/5 Install CEE'
if (Test-Path "$Profile\distribution.yaml") {
    # Re-run: copy the fresh files over, keep memories/keys.
    hermes profile install $dist --alias -y --force
} else {
    hermes profile install $dist --alias -y
}
if ($LASTEXITCODE -ne 0 -or -not (Test-Path "$Profile\distribution.yaml")) { throw 'CEE install failed - send a screenshot of the error above.' }
$gws = "$HermesHome\hermes-agent\skills\productivity\google-workspace"
if ((Test-Path $gws) -and -not (Test-Path "$Profile\skills\productivity\google-workspace")) {
    New-Item -ItemType Directory -Force "$Profile\skills\productivity" | Out-Null
    Copy-Item $gws "$Profile\skills\productivity\" -Recurse
}

Say '4/5 Your keys'
$envFile = "$Profile\.env"
if ((Test-Path $envFile) -and (Select-String -Path $envFile -Pattern '^GEMINI_API_KEY=.+' -Quiet)) {
    Write-Host "Keys already set in $envFile - keeping them."
} else {
    function Secret($p) { $s = Read-Host $p -AsSecureString
        ([Runtime.InteropServices.Marshal]::PtrToStringBSTR([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s))).Trim() }
    function Need($p, [switch]$Hidden) {
        do { $v = if ($Hidden) { Secret $p } else { (Read-Host $p).Trim() }
             if (-not $v) { Write-Host '  (empty - please paste it, then Enter)' -ForegroundColor Yellow } } while (-not $v)
        $v }
    $gem = Need 'Gemini API key' -Hidden
    $tok = Need 'Telegram bot token (from @BotFather)' -Hidden
    if ($tok -notmatch '^\d+:[\w-]{30,}$') { Write-Host '  Hmm, bot tokens look like 123456789:AAH... - double-check it if CEE does not reply.' -ForegroundColor Yellow }
    $id  = Need 'Your Telegram user ID (number from @userinfobot)'
    $or  = Secret 'OpenRouter key (optional backup brain, Enter to skip)'
    $lines = @("GEMINI_API_KEY=$gem", "TELEGRAM_BOT_TOKEN=$tok", "TELEGRAM_ALLOWED_USERS=$id", "TELEGRAM_HOME_CHANNEL=$id")
    if ($or) { $lines += "OPENROUTER_API_KEY=$or" }
    [IO.File]::WriteAllLines($envFile, $lines)
}

Say '5/5 Start CEE'
hermes -p cee gateway install
if ($LASTEXITCODE -ne 0) { throw 'Could not register CEE to auto-start - send a screenshot.' }
hermes -p cee gateway start
Start-Sleep 3
hermes -p cee gateway status

Say 'Done! Open your bot in Telegram and say: สวัสดี CEE'
Write-Host 'Then send /cee-onboarding so CEE learns who you are.'
Write-Host 'Note: CEE only answers while this PC is on and logged in.'
