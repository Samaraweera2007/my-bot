# Telegram Direct Download Bot Deployment Guide

මෙම Bot එක VPS (Ubuntu) එකකට මුල සිටම (from scratch) දාන ආකාරය මෙහි පියවරෙන් පියවර දක්වා ඇත.

## 1. VPS එක සම්පූර්ණයෙන්ම පිරිසිදු කිරීම (Clean Up)

මුලින්ම ඔබේ VPS එකට ලොග් වී දැනට පවතින සියල්ල ඉවත් කරන්න:

```bash
# PM2 මගින් දැනට run වන දේවල් නතර කිරීම
pm2 stop all
pm2 delete all

# VPS එකේ දැනට තියෙන පරණ ෆයිල් සියල්ල මැකීම
# ප්‍රවේශමෙන් පාවිච්චි කරන්න!
rm -rf ~/*  
```

---

## 2. අවශ්‍ය දේවල් VPS එකට Install කිරීම

VPS එක අලුතින්ම setup කිරීමට පහත command ටික පිළිවෙලට run කරන්න:

```bash
# System එක update කිරීම
sudo apt update && sudo apt upgrade -y

# Python සහ අවශ්‍ය දේවල් install කිරීම
sudo apt install python3-pip python3-venv -y

# PM2 (Background runner) සහ Node.js install කිරීම
sudo apt install nodejs npm -y
sudo npm install -g pm2
```

---

## 3. Local Computer එකේ සිට Bot එක VPS එකට යැවීම

ඔබේ **Windows PowerShell** එකේ (Bot folder එක ඇතුළත සිට) මෙම command එක run කරන්න:

```powershell
# මුළු folder එකම VPS එකට copy කිරීමට
# <SSH_KEY_PATH> වෙනුවට ඔබේ .key file එකේ path එක දෙන්න.
scp -i "C:\Users\chees\OneDrive\Desktop\ssh-key-2026-03-07.key" -r . ubuntu@161.118.190.108:~/my-bot
```

---

## 4. Bot එක Start කිරීම

නැවතත් VPS එකට ලොග් වී (`ssh -i ...`) Bot එක run කරන්න:

```bash
# Bot folder එකට යන්න
cd ~/my-bot

# අවශ්‍ය Libraries install කිරීම
pip3 install -r requirements.txt

# Bot එක PM2 හරහා background එකේ start කිරීම
pm2 start bot.py --name "my-bot" --interpreter python3
pm2 save
pm2 startup
```

---

## 5. Nginx Setup කිරීම (Domain එක සඳහා)

ඔබේ `tele.cmovie.xyz` domain එක වැඩ කිරීමට Nginx configure කරන්න:

```bash
# Nginx install කිරීම
sudo apt install nginx -y

# Configuration එක copy කිරීම
sudo cp nginx_config.conf /etc/nginx/sites-available/bot
sudo ln -s /etc/nginx/sites-available/bot /etc/nginx/sites-enabled/

# Nginx restart කිරීම
sudo nginx -t
sudo systemctl restart nginx
```

---

## 6. වැදගත් කරුණු

*   **Session File:** `direct_dl_bot.session` එක අනිවාර්යයෙන්ම VPS එකට තිබිය යුතුයි. නැත්නම් Bot එකට log වෙන්න බැහැ.
*   **IP Address:** ඔබේ Domain (DNS) එකේ IP එක `161.118.190.108` ලෙස දමා ඇති බව තහවුරු කරන්න.
*   **Speed:** බාගත කිරීමේ වේගය (Speed) වැඩි කිරීමට `tgcrypto` install වී ඇති බව check කරන්න.
