# CEE setup guide

This guide gets you from zero to talking to CEE on Telegram, for **$0/month**.

**What you get:**
- **Harness:** Hermes Agent (Nous Research), free and open source
- **Brain:** Google Gemini, free tier
- **Memory:** local and free
- **Voice:** local Whisper to hear you and Edge voices to talk back, both free
- **Channel:** Telegram
- **Server:** Oracle Cloud Always Free

⏱️ About 45–60 minutes the first time. Copy each command, paste it, and press Enter.

---

## 0. Get your keys ready (on your phone or laptop)

| What | Where | Save it as |
|---|---|---|
| Gemini key | https://aistudio.google.com/apikey → **Create API key** | `GEMINI_API_KEY` |
| Telegram bot | In Telegram, open **@BotFather** and send `/newbot`. Name it `CEE` and give it a username ending in `bot`. | `TELEGRAM_BOT_TOKEN` |
| Your Telegram ID | In Telegram, open **@userinfobot** and send any message. It replies with a number. | `TELEGRAM_ALLOWED_USERS` |
| *(optional)* Backup brain | https://openrouter.ai/keys, free sign-up | `OPENROUTER_API_KEY` |

> 💡 Give CEE a face: in @BotFather, send `/setuserpic` and upload an avatar.

---

## 1. Get a free server (Oracle Cloud Always Free)

1. Sign up at https://www.oracle.com/cloud/free/.
   - Pick **Singapore** or **Japan** as your home region. They're close to Thailand.
   - Oracle asks for a card to verify you. Always Free resources are **not charged**.
2. Go to **Compute → Instances → Create instance**.
   - **Image:** Ubuntu 24.04
   - **Shape:** Ampere **VM.Standard.A1.Flex**, 2 OCPU, 12 GB RAM. This is free.
   - Download the **SSH private key** when it's offered.
3. Click **Create** and copy the instance's **Public IP**.

> "Out of capacity" error? Try again later, or pick a different availability domain. The Ampere free tier is popular.

Connect to the server from your laptop's terminal. On Windows, use PowerShell.

```bash
ssh -i path/to/your-key.key ubuntu@YOUR_PUBLIC_IP
```

From now on, every command runs **on the server**.

### ⚡ Fast way: one command does steps 2–5

```bash
curl -fsSL https://raw.githubusercontent.com/chainsukritthikan-lab/hi/main/cee/install.sh | bash
```

It installs Hermes and CEE, asks for your keys (Gemini, Telegram token, your Telegram ID), and starts CEE 24/7. When it finishes, jump to **step 6**. If you'd rather go step by step, keep reading.

---

## 2. Install Hermes Agent

```bash
sudo apt update && sudo apt install -y git curl ffmpeg
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
source ~/.bashrc
hermes --version
```

When the installer asks to run setup, you can **skip** it. CEE brings its own config.

---

## 3. Install CEE

```bash
git clone https://github.com/chainsukritthikan-lab/hi.git ~/cee-src
hermes profile install ~/cee-src/cee --alias
```

This creates the `cee` command. Now copy in the Google Workspace skill that CEE uses for Gmail, Calendar, and Drive:

```bash
mkdir -p ~/.hermes/profiles/cee/skills/productivity
cp -rn ~/.hermes/hermes-agent/skills/productivity/google-workspace ~/.hermes/profiles/cee/skills/productivity/
```

---

## 4. Add your keys

```bash
cp ~/.hermes/profiles/cee/.env.EXAMPLE ~/.hermes/profiles/cee/.env
nano ~/.hermes/profiles/cee/.env
```

Fill it in and remove the `#` in front of any line you use:

```
GEMINI_API_KEY=your-gemini-key
TELEGRAM_BOT_TOKEN=123456789:ABC...
TELEGRAM_ALLOWED_USERS=your-telegram-number
TELEGRAM_HOME_CHANNEL=your-telegram-number
OPENROUTER_API_KEY=optional-backup-key
```

Save with **Ctrl+O**, then Enter, then **Ctrl+X**. Then lock the file so only you can read it:

```bash
chmod 600 ~/.hermes/profiles/cee/.env
cee doctor
```

---

## 5. Test it, then keep it running 24/7

Quick test in the terminal:

```bash
cee chat
```

Say `hi CEE`, then type `/exit`.

Make it run forever, including after a reboot:

```bash
cee gateway install
sudo loginctl enable-linger $USER
cee gateway start
cee gateway status
```

Now open your bot in Telegram and say hi. 🎉

---

## 6. First chat: teach CEE who you are

In Telegram, send:

```
/cee-onboarding
```

CEE asks about 6 quick questions (your work, goals, style, routine) and remembers the answers. You can answer with voice notes.

---

## 7. Voice

- **Talking to CEE:** send a voice note in Thai or English. It's transcribed for free on your server.
- **CEE talking back:**
  - `/voice on` to reply with voice when you send voice
  - `/voice tts` to always reply with voice
  - `/voice off` to go back to text only
- **Change the voice:** run `cee config set tts.edge.voice th-TH-PremwadeeNeural` for the female Thai voice, or `en-US-AriaNeural` for English. Then run `cee gateway restart`.

> Want the ElevenLabs voice from the reel? Its free plan is 10k characters a month. Get a key, add `ELEVENLABS_API_KEY=` to `.env`, run `cee config set tts.provider elevenlabs`, and restart.

---

## 8. Connect Gmail, Calendar and Drive (about 10 minutes, one time)

1. Go to https://console.cloud.google.com and create a project called `CEE`.
2. Go to **APIs & Services → Library** and enable the **Gmail API**, **Google Calendar API**, **Google Drive API**, **Google Docs API**, **Google Sheets API**, and **People API**.
3. Go to **Google Auth Platform → Audience**, choose **External**, and add your own Gmail address as a **Test user**.
4. Go to **Credentials → Create credentials → OAuth client ID**. Choose **Desktop app**, then click **Download JSON**.
5. Upload the file to the server by running this from your laptop:
   ```bash
   scp -i path/to/your-key.key client_secret_*.json ubuntu@YOUR_PUBLIC_IP:~/client_secret.json
   ```
6. In Telegram, tell CEE:
   > Connect my Google account. The client secret is at ~/client_secret.json

   CEE sends you a Google link. Log in and approve. Your browser then shows an error page, **which is normal**. Copy the whole address from the address bar and paste it back to CEE.

After that, try:
- "What's on my calendar tomorrow?"
- "Any important unread emails?"
- "Draft a reply to the latest email from X"

CEE always shows you drafts first and only sends when you say ok.

---

## 9. Morning brief (optional)

In Telegram:

```
/blueprint morning-brief time=07:30
```

Every morning at 07:30 Bangkok time, you'll get today's calendar, important emails, and a plan.

---

## Things to try

- `เขียนสคริปต์โฆษณา 30 วิ ให้ร้านกาแฟ กลุ่มเป้าหมายคนทำงาน`
- `Break down this reel` plus screenshots
- `Caption pack for this video, TH + EN`
- `Search the web: best AI video tools this month, compare prices`
- `Remind me every Monday 9am to post a reel`
- `/model` to see or switch the brain. You can move to Claude later with `cee model`.

---

## Useful commands

| Command | What it does |
|---|---|
| `cee gateway status` | Is CEE running? |
| `cee gateway restart` | Restart after changing config |
| `cee logs` | See what went wrong |
| `hermes update` | Update Hermes |
| `cd ~/cee-src && git pull && hermes profile update cee` | Get the latest CEE persona and skills from this repo. Your memory and keys are kept. |
| `/new` (in Telegram) | Start a fresh conversation. CEE still remembers you. |

---

## Troubleshooting

**CEE says "429" or "quota exceeded".** Gemini's free tier has daily limits, and Hermes can use several calls per message. Try these:
1. Add a free `OPENROUTER_API_KEY` in `.env`. CEE falls back to a free model automatically.
2. Use `/new` more often, because shorter chats use fewer tokens.
3. If you use CEE heavily, turn on billing in Google AI Studio. Flash models are cheap, usually a few dollars a month.

**The bot doesn't answer.**
- Run `cee gateway status`, then `cee logs`.
- Check that `TELEGRAM_ALLOWED_USERS` is *your* number from @userinfobot.

**Voice notes aren't understood.** The first voice note downloads the Whisper model, which takes about 1 minute. For better Thai, run `cee config set stt.local.model medium` and restart.
