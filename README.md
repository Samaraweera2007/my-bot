# Telegram Direct Download Bot - Fresh Installation Guide

මෙම Bot එක VPS එකක මුල සිටම (from scratch) ඉතා පිරිසිදුව සහ උපරිම වේගයෙන් (100MB/s+) install කරන ආකාරය මෙහි දැක්වේ.

---

## 1. කලින් තිබූ හැමදේම මකා දැමීම (Full Reset)

ඔබට දැනට VPS එකේ ඇති පරණ Bot එක, Files සහ Process සියල්ල ඉවත් කිරීමට VPS එකට ලොග් වී මෙම command එක ලබා දෙන්න:

```bash
# PM2 නතර කිරීම සහ Bot folder එක මකා දැමීම
pm2 stop all && pm2 delete all && rm -rf ~/my-bot
```

---

## 2. VPS එකේ අවශ්‍ය දේවල් Install කිරීම

අලුතින්ම වැඩේ පටන් ගැනීමට පහත command ටික පිළිවෙළට run කරන්න:

```bash
# System එක update කිරීම
sudo apt update && sudo apt upgrade -y

# Python සහ අවශ්‍ය දේවල් install කිරීම
sudo apt install python3-pip python3-venv python3-full -y

# PM2 සහ Nginx install කිරීම
sudo apt install nodejs npm nginx -y
sudo npm install -g pm2
```

---

## 3. GitHub එකෙන් Bot එක ලබා ගැනීම (Git Clone)

VPS එක ඇතුළත සිට මෙම command එක ලබා දෙන්න:

```bash
# GitHub එකෙන් files ලබා ගැනීම
git clone https://github.com/Samaraweera2007/my-bot.git ~/my-bot

# Folder එක ඇතුළට යාම
cd ~/my-bot
```

> [!IMPORTANT]
> ඔබ දැනටමත් Bot ගේ `bot.py` වැනි ෆයිල් වෙනස් කර ඇත්නම්, එම වෙනස්කම් GitHub එකට **Push** කර පසුව VPS එකේදී **Clone** හෝ **Pull** කරන්න. නැතහොත් මම ලබා දුන් අලුත් Code එක VPS එකේදී manual update කරන්න.

---

## 4. Bot එක Setup කිරීම සහ ලොග් වීම

VPS එකට ලොග් වී පහත පියවර අනුගමනය කරන්න:

```bash
cd ~/my-bot

# අවශ්‍ය Libraries සහ Tgcrypto (Speed සඳහා) install කිරීම
pip3 install -r requirements.txt
pip3 install --upgrade tgcrypto

# මුලින්ම ලොග් වීමට Bot එක run කරන්න
python3 bot.py
```
*   මෙහිදී දුරකථන අංකය සහ Telegram code එක ලබා දී සාර්ථකව ලොග් වී `Bot is ready!` ආ පසු **`Ctrl + C`** ඔබන්න.

---

## 5. Bot එක "Off" නොවී දිගටම පවත්වා ගැනීම (Always Online)

දැන් Bot එක PM2 හරහා background එකේ start කරමු:

```bash
# අලුත් settings සමඟ start කිරීම
pm2 start bot.py --name "my-bot" --interpreter python3 --restart-delay 3000

# VPS එක Reboot වුවත් Bot එක On වීමට (මෙය අනිවාර්යයි):
pm2 startup
# (ඉහත command එක ගැසූ පසු ලැබෙන sudo... පේළිය copy කර paste කරන්න)

# දැනට ඇති setups save කිරීම
pm2 save
```

---

## 6. Nginx සහ Speed Optimization (Domain)

Domain එක හරහා උපරිම වේගය (100MB/s) ලබා ගැනීමට:

```bash
# Configuration එක copy කිරීම
sudo cp ~/my-bot/nginx_config.conf /etc/nginx/sites-available/bot
sudo ln -s /etc/nginx/sites-available/bot /etc/nginx/sites-enabled/

# Nginx පරීක්ෂා කර restart කිරීම
sudo nginx -t
sudo systemctl restart nginx
```

---

## වැදගත් කරුණු:
*   **Logs බැලීම:** `pm2 logs my-bot`
*   **Status බැලීම:** `pm2 status`
*   **Speed:** උපරිම වේගය ලබා ගැනීමට **IDM (32 connections)** භාවිතා කරන්න. browser එකෙන් download කරන විට ඔබේ VPS speed එක සහ connection එක අනුව වේගය තීරණය වේ.
*   **Session Error:** කවදා හෝ `SESSION_REVOKED` ආවොත් `direct_dl_bot.session` මකා දමා නැවත **4 වන පියවර** කරන්න.
