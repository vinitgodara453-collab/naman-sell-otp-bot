#!/usr/bin/env bash
# ==============================================================================
# 📱 NAMAN SELL BOT - 1-CLICK AUTOMATED VPS INSTALLER
# For Ubuntu 20.04 / 22.04 / 24.04, Debian 11 / 12 & Linux VPS
# ==============================================================================

set -e

echo -e "\033[1;36m=====================================================\033[0m"
echo -e "\033[1;32m  📱 NAMAN SELL OTP BOT - 24/7 VPS AUTO-DEPLOYMENT   \033[0m"
echo -e "\033[1;36m=====================================================\033[0m"

APP_DIR="$(pwd)"

echo -e "\n\033[1;33m[1/5] Updating system packages & installing Python3...\033[0m"
apt-get update -y
apt-get install -y python3 python3-pip python3-venv git curl sqlite3

echo -e "\n\033[1;33m[2/5] Installing Python dependencies...\033[0m"
pip3 install --upgrade pip 2>/dev/null || true
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || pip3 install -r requirements.txt

echo -e "\n\033[1;33m[3/5] Configuring Bot Credentials & 5SIM API...\033[0m"
if [ ! -f .env ]; then
    read -p "👉 Enter your Telegram BOT_TOKEN from @BotFather: " BOT_TOKEN_INPUT
    read -p "👉 Enter your Telegram ADMIN_ID (numeric): " ADMIN_ID_INPUT
    cat <<EOF > .env
BOT_TOKEN="${BOT_TOKEN_INPUT}"
ADMIN_ID="${ADMIN_ID_INPUT}"
DATABASE_PATH="naman_sell.db"

# 5SIM Official API Key
FIVESIM_API_KEY="eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MjM4OTk0NDYsImlhdCI6MTc5MjM2MzQ0NiwicmF5IjoiODc2MzBlNTk3ZDFkZjA3MmY5YzZjMDBmMDVkMGUxNzIiLCJzdWIiOjQ1NjkyOTF9.gtfaH2AJA1OSkyGPHKR3Xl9aFw5UYmxDIXLtCb_ec7_HdMWBM91H3JiKcAAMDogYh9Ud-YnTGIaVZhjXKWz7C6u9EnnBUqCrq8CHhvHvYX5GK1m6pR9ytxvSfwEH4onkqrWG9_-ZrCtl2S65_CdH4VHMCdVhnWLq_vsh3gqSXV-E1FPNlTOtDq1imBFdGWBEX_77tCqv0LeggUqYUeyDOuYXiwFRrFvFxDSOh6l2YZbtEKHsIC9gW2kcomZZL2MHAcVd8_AvrrbKn9T7ajZ2OQeHJaoIw885XZuxtpuASndTxtR9Bbv6IYXTl2UtIxp2bKl2svPC0ErAJYsgMUMI1w"

# UPI Wallet Configuration
UPI_ID="vinit-godara@fam"
UPI_NAME="Vinit Godara"
EOF
    echo -e "\033[1;32m✓ .env configuration created successfully!\033[0m"
else
    echo -e "\033[1;34m✓ Existing .env found, keeping current settings.\033[0m"
fi

echo -e "\n\033[1;33m[4/5] Setting up Systemd 24/7 Background Service...\033[0m"
cat <<EOF > /etc/systemd/system/namansell.service
[Unit]
Description=Naman Sell 5SIM Direct OTP Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
ExecStart=/usr/bin/python3 ${APP_DIR}/naman_sell_bot.py
Restart=always
RestartSec=4

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable namansell.service
systemctl restart namansell.service

echo -e "\n\033[1;33m[5/5] Checking Bot Status...\033[0m"
sleep 2
systemctl is-active --quiet namansell.service && echo -e "\033[1;32m🎉 SUCCESS! Naman Sell Bot is RUNNING 24/7 on your VPS!\033[0m" || echo -e "\033[1;31m⚠️ Service started. Check logs: journalctl -u namansell -f\033[0m"

echo -e "\n\033[1;36mCommands for your VPS:\033[0m"
echo -e "  • Check live logs: \033[1;33mjournalctl -u namansell -f\033[0m"
echo -e "  • Restart bot:     \033[1;33msystemctl restart namansell\033[0m"
echo -e "  • Stop bot:        \033[1;33msystemctl stop namansell\033[0m"
echo -e "  • Service status:  \033[1;33msystemctl status namansell\033[0m"
