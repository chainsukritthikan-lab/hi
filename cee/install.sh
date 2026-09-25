#!/usr/bin/env bash
# CEE one-command installer (run on your Ubuntu server):
#   curl -fsSL https://raw.githubusercontent.com/chainsukritthikan-lab/hi/main/cee/install.sh | bash
# Installs Hermes Agent + CEE, asks for your keys, and starts CEE 24/7.
set -euo pipefail

REPO="${CEE_REPO:-https://github.com/chainsukritthikan-lab/hi.git}"
BRANCHES=("${CEE_BRANCH:-main}" "claude/laughing-hopper-d0qios")
SRC="$HOME/cee-src"
PROFILE="$HOME/.hermes/profiles/cee"
export PATH="$HOME/.local/bin:$PATH"

say() { printf '\n\033[1;32m▶ %s\033[0m\n' "$*"; }

say "1/5 System packages"
sudo apt-get update -qq
sudo apt-get install -y -qq git curl ffmpeg >/dev/null

say "2/5 Hermes Agent"
if ! command -v hermes >/dev/null 2>&1; then
  curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --non-interactive
fi
hermes --version

say "3/5 CEE"
rm -rf "$SRC"
for b in "${BRANCHES[@]}"; do
  if git clone -q --depth 1 -b "$b" "$REPO" "$SRC" 2>/dev/null && [ -f "$SRC/cee/distribution.yaml" ]; then
    echo "Using branch: $b"; break
  fi
  rm -rf "$SRC"
done
[ -f "$SRC/cee/distribution.yaml" ] || { echo "Could not download CEE from $REPO"; exit 1; }

if [ -d "$PROFILE" ]; then
  hermes profile install "$SRC/cee" --alias -y --force
else
  hermes profile install "$SRC/cee" --alias -y
fi
mkdir -p "$PROFILE/skills/productivity"
cp -rn "$HOME/.hermes/hermes-agent/skills/productivity/google-workspace" "$PROFILE/skills/productivity/" 2>/dev/null || true
mkdir -p "$PROFILE/skills/note-taking"
cp -rn "$HOME/.hermes/hermes-agent/skills/note-taking/obsidian" "$PROFILE/skills/note-taking/" 2>/dev/null || true

say "4/5 Your keys (typing is hidden for secrets)"
if [ -f "$PROFILE/.env" ] && grep -qE '^(NVIDIA|GEMINI)_API_KEY=.+' "$PROFILE/.env"; then
  echo "Keys already set in $PROFILE/.env — keeping them."
else
  exec 3</dev/tty
  read -r -s -u 3 -p "NVIDIA API key (free, build.nvidia.com): " NV; echo
  read -r -s -u 3 -p "Gemini API key (optional backup brain, Enter to skip): " GEMINI; echo
  read -r -s -u 3 -p "Telegram bot token (from @BotFather): " TG_TOKEN; echo
  read -r -u 3 -p "Your Telegram user ID (number from @userinfobot): " TG_ID
  read -r -s -u 3 -p "OpenRouter key (optional backup brain, Enter to skip): " OR_KEY; echo
  umask 077
  {
    echo "NVIDIA_API_KEY=$NV"
    [ -n "$GEMINI" ] && echo "GEMINI_API_KEY=$GEMINI"
    echo "TELEGRAM_BOT_TOKEN=$TG_TOKEN"
    echo "TELEGRAM_ALLOWED_USERS=$TG_ID"
    echo "TELEGRAM_HOME_CHANNEL=$TG_ID"
    [ -n "$OR_KEY" ] && echo "OPENROUTER_API_KEY=$OR_KEY"
  } > "$PROFILE/.env"
  chmod 600 "$PROFILE/.env"
fi

# CEE Brain (Obsidian vault) on the server; sync it with your PC later (Syncthing).
VAULT="$HOME/CEE Brain"
if [ ! -d "$VAULT" ]; then mkdir -p "$VAULT" && cp -rn "$SRC/cee/vault-template/." "$VAULT/" && find "$VAULT" -name .keep -delete; fi
grep -q '^OBSIDIAN_VAULT_PATH=' "$PROFILE/.env" || echo "OBSIDIAN_VAULT_PATH=$VAULT" >> "$PROFILE/.env"

say "5/5 Start CEE 24/7"
# One host gateway (default profile) serves every profile, including cee.
hermes gateway install
sudo loginctl enable-linger "$USER"
hermes gateway restart 2>/dev/null || hermes gateway start
sleep 5
hermes gateway status || true

say "Done! Open your bot in Telegram and say: hi CEE"
echo "Then send /cee-onboarding so CEE learns who you are."
