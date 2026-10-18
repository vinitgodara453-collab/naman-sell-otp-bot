#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
💎 NAMAN SELL BOT (@Namansellbot) - 5SIM DIRECT OTP & VIRTUAL ACCOUNT STORE
VIP Telegram Premium UI • Automatic 3-Second Live OTP Listener • 24/7 VPS Ready
==============================================================================
"""

import os
import re
import sys
import time
import json
import sqlite3
import asyncio
import logging
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus

# Auto-load .env file if present
def _load_env_file():
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    ]
    for p in candidates:
        if os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            if k and k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass
            break

_load_env_file()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("NamanSellBot")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0") or "0")
DATABASE_PATH = os.environ.get("DATABASE_PATH", "naman_sell.db")

# 5SIM Official API Key (Pre-configured)
FIVESIM_API_KEY = os.environ.get(
    "FIVESIM_API_KEY",
    "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MjM4OTk0NDYsImlhdCI6MTc5MjM2MzQ0NiwicmF5IjoiODc2MzBlNTk3ZDFkZjA3MmY5YzZjMDBmMDVkMGUxNzIiLCJzdWIiOjQ1NjkyOTF9.gtfaH2AJA1OSkyGPHKR3Xl9aFw5UYmxDIXLtCb_ec7_HdMWBM91H3JiKcAAMDogYh9Ud-YnTGIaVZhjXKWz7C6u9EnnBUqCrq8CHhvHvYX5GK1m6pR9ytxvSfwEH4onkqrWG9_-ZrCtl2S65_CdH4VHMCdVhnWLq_vsh3gqSXV-E1FPNlTOtDq1imBFdGWBEX_77tCqv0LeggUqYUeyDOuYXiwFRrFvFxDSOh6l2YZbtEKHsIC9gW2kcomZZL2MHAcVd8_AvrrbKn9T7ajZ2OQeHJaoIw885XZuxtpuASndTxtR9Bbv6IYXTl2UtIxp2bKl2svPC0ErAJYsgMUMI1w"
).strip()

# UPI Wallet Topup Details
UPI_ID = os.environ.get("UPI_ID", "vinit-godara@fam").strip()
UPI_NAME = os.environ.get("UPI_NAME", "Vinit Godara").strip()

RUB_TO_INR_RATE = float(os.environ.get("RUB_TO_INR_RATE", "1.20"))

# Telegram Premium Custom Emoji Document IDs with fallback
EMOJI_SHIELD = "5368324170671202286"
EMOJI_VERIFIED = "5449747923766094392"
EMOJI_ALERT = "5370908842851965692"
EMOJI_FIRE = "5371077754646307137"
EMOJI_STAR = "5409166649855057077"
EMOJI_DIAMOND = "5411270216690704481"
EMOJI_CROWN = "5472164874886772598"
EMOJI_LIGHTNING = "5373142079070410427"

def pe(emoji_id: str, fallback: str) -> str:
    """Format Telegram Premium Custom Emoji in HTML mode."""
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
    return fallback

# VIP Aesthetic Font Converters
def font_bold_sans(text: str) -> str:
    res = []
    for c in text:
        code = ord(c)
        if 65 <= code <= 90:
            res.append(chr(0x1D5D4 + (code - 65)))
        elif 97 <= code <= 122:
            res.append(chr(0x1D5EE + (code - 97)))
        elif 48 <= code <= 57:
            res.append(chr(0x1D7EC + (code - 48)))
        else:
            res.append(c)
    return "".join(res)

def font_small_caps(text: str) -> str:
    norm = "abcdefghijklmnopqrstuvwxyz"
    caps = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
    tr = str.maketrans(norm, caps)
    return text.lower().translate(tr)

# ==============================================================================
# FAIR PROFIT MARGIN CATALOG (सस्ते दाम + आपका पक्का प्रॉफिट)
# ==============================================================================
SUPPORTED_SERVICES = {
    "telegram": {"name": "Telegram", "icon": "💬", "code": "telegram", "retail_inr": 5.0},
    "whatsapp": {"name": "WhatsApp", "icon": "📱", "code": "whatsapp", "retail_inr": 10.0},
    "google": {"name": "Google / Gmail", "icon": "🔴", "code": "google", "retail_inr": 6.0},
    "instagram": {"name": "Instagram", "icon": "📸", "code": "instagram", "retail_inr": 4.0},
    "facebook": {"name": "Facebook", "icon": "🔵", "code": "facebook", "retail_inr": 4.0},
    "twitter": {"name": "Twitter / X", "icon": "🐦", "code": "twitter", "retail_inr": 4.0},
    "openai": {"name": "OpenAI / ChatGPT", "icon": "🤖", "code": "openai", "retail_inr": 7.0},
    "amazon": {"name": "Amazon", "icon": "🛍️", "code": "amazon", "retail_inr": 5.0},
    "discord": {"name": "Discord", "icon": "🎮", "code": "discord", "retail_inr": 5.0},
    "tiktok": {"name": "TikTok", "icon": "🎵", "code": "tiktok", "retail_inr": 4.0},
    "snapchat": {"name": "Snapchat", "icon": "👻", "code": "snapchat", "retail_inr": 5.0},
    "netflix": {"name": "Netflix", "icon": "🎬", "code": "netflix", "retail_inr": 8.0},
    "microsoft": {"name": "Microsoft / Outlook", "icon": "💻", "code": "microsoft", "retail_inr": 6.0},
    "steam": {"name": "Steam", "icon": "🕹️", "code": "steam", "retail_inr": 5.0},
    "uber": {"name": "Uber", "icon": "🚗", "code": "uber", "retail_inr": 5.0},
    "other": {"name": "Any Other Service", "icon": "🌐", "code": "other", "retail_inr": 6.0}
}

SUPPORTED_COUNTRIES = {
    "india": {"name": "India", "flag": "🇮🇳", "code": "india"},
    "russia": {"name": "Russia (Lowest)", "flag": "🇷🇺", "code": "russia"},
    "indonesia": {"name": "Indonesia", "flag": "🇮🇩", "code": "indonesia"},
    "usa": {"name": "USA", "flag": "🇺🇸", "code": "usa"},
    "england": {"name": "United Kingdom", "flag": "🇬🇧", "code": "england"},
    "vietnam": {"name": "Vietnam", "flag": "🇻🇳", "code": "vietnam"},
    "philippines": {"name": "Philippines", "flag": "🇵🇭", "code": "philippines"},
    "brazil": {"name": "Brazil", "flag": "🇧🇷", "code": "brazil"},
    "kazakhstan": {"name": "Kazakhstan", "flag": "🇰🇿", "code": "kazakhstan"},
    "nigeria": {"name": "Nigeria", "flag": "🇳🇬", "code": "nigeria"}
}

def calculate_selling_price(service_code: str, rub_cost: float) -> float:
    """Calculates fair, attractive retail price ensuring steady owner profit."""
    srv = SUPPORTED_SERVICES.get(service_code, {"retail_inr": 5.0})
    base = srv.get("retail_inr", 5.0)
    cost_inr = rub_cost * RUB_TO_INR_RATE
    # Ensure at least ₹3.50 profit margin above 5sim cost
    selling_price = max(base, round(cost_inr + 3.5, 1))
    return selling_price

# ==============================================================================
# 5SIM API CLIENT
# ==============================================================================
class FiveSimClient:
    BASE_URL = "https://5sim.net/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _request(self, endpoint: str, method: str = "GET", data: Optional[dict] = None) -> Any:
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": "NamanSellBot/1.0"
        }
        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="ignore")
            logger.error(f"5SIM Error {e.code}: {raw}")
            raise Exception(f"5SIM Error ({e.code}): {raw or e.reason}")
        except Exception as e:
            raise Exception(f"5SIM Connection Error: {str(e)}")

    def get_profile(self) -> Dict[str, Any]:
        return self._request("user/profile")

    def buy_number(self, country: str, product: str, operator: str = "any") -> Dict[str, Any]:
        return self._request(f"user/buy/activation/{country}/{operator}/{product}")

    def check_order(self, order_id: int) -> Dict[str, Any]:
        return self._request(f"user/check/{order_id}")

    def cancel_order(self, order_id: int) -> Dict[str, Any]:
        return self._request(f"user/cancel/{order_id}")

    def finish_order(self, order_id: int) -> Dict[str, Any]:
        return self._request(f"user/finish/{order_id}")

fivesim = FiveSimClient(FIVESIM_API_KEY)

# ==============================================================================
# DATABASE MANAGEMENT
# ==============================================================================
def init_database():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            balance REAL DEFAULT 0.0,
            total_spent REAL DEFAULT 0.0,
            orders_count INTEGER DEFAULT 0,
            joined_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            service TEXT,
            country TEXT,
            phone TEXT,
            cost_rub REAL,
            price_inr REAL,
            status TEXT DEFAULT 'PENDING',
            otp TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            amount REAL,
            utr TEXT UNIQUE,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_or_create_user(user_id: int, username: str = "", first_name: str = "") -> Dict[str, Any]:
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, username, first_name, balance, total_spent, orders_count FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        c.execute("""
            INSERT INTO users (user_id, username, first_name, balance, total_spent, orders_count, joined_at)
            VALUES (?, ?, ?, 0.0, 0.0, 0, ?)
        """, (user_id, username, first_name, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        row = (user_id, username, first_name, 0.0, 0.0, 0)
    conn.close()
    return {
        "user_id": row[0],
        "username": row[1],
        "first_name": row[2],
        "balance": row[3],
        "total_spent": row[4],
        "orders_count": row[5]
    }

def update_user_balance(user_id: int, delta: float):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (delta, user_id))
    conn.commit()
    conn.close()

# ==============================================================================
# TELEGRAM BOT HANDLERS WITH VIP PREMIUM UI
# ==============================================================================
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """VIP Premium Home Interface."""
    user = update.effective_user
    u = get_or_create_user(user.id, user.username or "", user.first_name or "Friend")

    star_icon = pe(EMOJI_STAR, "⭐")
    bolt_icon = pe(EMOJI_LIGHTNING, "⚡")
    diamond_icon = pe(EMOJI_DIAMOND, "💎")
    crown_icon = pe(EMOJI_CROWN, "👑")

    try:
        prof = fivesim.get_profile()
        fivesim_badge = "🟢 5SIM SERVER ONLINE"
    except Exception:
        fivesim_badge = "🟡 5SIM CONNECTING"

    welcome_text = (
        f"╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│  {crown_icon} <b>{font_bold_sans('NAMAN SELL OTP STORE')}</b> {star_icon}  │\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"👋 <i>नमस्ते {user.first_name}! आपका स्वागत है सबसे तेज़ <b>{font_bold_sans('Direct OTP Platform')}</b> पर।</i>\n\n"
        f"💰 <b>{font_small_caps('WALLET BALANCE')}:</b> <code>₹{u['balance']:.2f} INR</code>\n"
        f"📦 <b>{font_small_caps('TOTAL ORDERS')}:</b> <code>{u['orders_count']}</code>\n"
        f"⚡ <b>{font_small_caps('SERVER STATUS')}:</b> <b>{fivesim_badge}</b>\n\n"
        f"<blockquote expandable>"
        f"<b>💎 {font_bold_sans('SERVICES & PRICE LIST')}</b>\n"
        f"• 💬 <b>Telegram:</b> ₹5 मात्र\n"
        f"• 📱 <b>WhatsApp:</b> ₹10 मात्र\n"
        f"• 🔴 <b>Google / Gmail:</b> ₹6 मात्र\n"
        f"• 📸 <b>Instagram:</b> ₹4 मात्र\n"
        f"• 🤖 <b>OpenAI / ChatGPT:</b> ₹7 मात्र\n"
        f"• 🛍️ <b>Amazon / Flipkart:</b> ₹5 मात्र\n"
        f"• 🎮 <b>Discord / Steam:</b> ₹5 मात्र\n\n"
        f"🛡️ <b>100% रिफंड पॉलिसी:</b> OTP न आने पर 1-क्लिक में पूरा पैसा वापस!\n"
        f"</blockquote>\n\n"
        f"👇 <i>नंबर लेने या वॉलेट रिचार्ज करने के लिए नीचे दिए स्टाइलिश बटन दबाएं:</i>"
    )

    keyboard = [
        [
            InlineKeyboardButton(f"🛒 {font_small_caps('BUY NUMBER')} | नंबर खरीदें", callback_data="btn_services"),
            InlineKeyboardButton(f"💳 {font_small_caps('ADD FUNDS')} | रिचार्ज", callback_data="btn_wallet")
        ],
        [
            InlineKeyboardButton(f"📋 {font_small_caps('MY ORDERS')} | ऑर्डर्स", callback_data="btn_my_orders"),
            InlineKeyboardButton(f"💰 {font_small_caps('BALANCE')} | बैलेंस", callback_data="btn_balance")
        ],
        [
            InlineKeyboardButton(f"👑 {font_small_caps('5SIM STATUS')}", callback_data="btn_5sim_info"),
            InlineKeyboardButton(f"ℹ️ {font_small_caps('HELP')} | सहायता", callback_data="btn_help")
        ]
    ]

    target = update.message if update.message else update.callback_query.message
    await target.reply_text(
        text=welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )

async def services_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Catalog of all apps."""
    query = update.callback_query
    await query.answer()

    diamond_icon = pe(EMOJI_DIAMOND, "💎")

    text = (
        f"╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│  {diamond_icon} <b>{font_bold_sans('CHOOSE APPLICATION')}</b> 📱  │\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"👉 <i>जिस ऐप के लिए OTP चाहिए, उस पर क्लिक करें:</i>"
    )

    keyboard = []
    row = []
    for code, info in SUPPORTED_SERVICES.items():
        row.append(InlineKeyboardButton(f"{info['icon']} {info['name']} (₹{info['retail_inr']:.0f})", callback_data=f"srv_{code}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(f"🔙 {font_small_caps('MAIN MENU')}", callback_data="btn_home")])

    await query.edit_message_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def country_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, service_code: str):
    """Country selection for app."""
    query = update.callback_query
    await query.answer()

    service_info = SUPPORTED_SERVICES.get(service_code, {"name": service_code.title(), "icon": "📱", "retail_inr": 5.0})

    text = (
        f"╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│  🌍 <b>{font_bold_sans('CHOOSE COUNTRY')}</b> {service_info['icon']}  │\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"📌 <b>सेवा:</b> {service_info['icon']} <b>{service_info['name']}</b> (शुरुआती कीमत: <b>₹{service_info['retail_inr']:.0f}</b>)\n\n"
        f"👉 <i>जिस देश का वर्चुअल नंबर चाहिए, चुनें:</i>\n\n"
        f"💡 <i>टिप: रूस 🇷🇺, वियतनाम 🇻🇳 और इंडोनेशिया 🇮🇩 के नंबर सबसे तेज व सस्ते होते हैं!</i>"
    )

    keyboard = []
    row = []
    for c_code, c_info in SUPPORTED_COUNTRIES.items():
        row.append(InlineKeyboardButton(f"{c_info['flag']} {c_info['name']}", callback_data=f"buy_{service_code}_{c_code}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(f"🔙 {font_small_caps('BACK TO APPS')}", callback_data="btn_services")])

    await query.edit_message_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, service_code: str, country_code: str):
    """Executes the purchase on 5SIM with profit calculation."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    u = get_or_create_user(user.id, user.username or "", user.first_name or "")

    service_info = SUPPORTED_SERVICES.get(service_code, {"name": service_code.title(), "icon": "📱", "retail_inr": 5.0})
    country_info = SUPPORTED_COUNTRIES.get(country_code, {"name": country_code.title(), "flag": "🌍"})

    # Check user balance
    expected_price = service_info["retail_inr"]
    if u["balance"] < expected_price:
        need = expected_price - u["balance"]
        insufficient_text = (
            f"⚠️ <b>अपर्याप्त बैलेंस (INSUFFICIENT BALANCE)</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 <b>सेवा:</b> {service_info['icon']} {service_info['name']}\n"
            f"💰 <b>कीमत:</b> ₹{expected_price:.2f} INR\n"
            f"💳 <b>आपका बैलेंस:</b> ₹{u['balance']:.2f} INR\n\n"
            f"कृपया पहले वॉलेट में कम से कम <b>₹{need:.2f}</b> रिचार्ज करें!"
        )
        keyboard = [
            [InlineKeyboardButton("💳 वॉलेट रिचार्ज करें (Add Funds)", callback_data="btn_wallet")],
            [InlineKeyboardButton("🔙 मुख्य मेनू", callback_data="btn_home")]
        ]
        await query.edit_message_text(
            text=insufficient_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Loading indicator
    await query.edit_message_text(
        f"⏳ <b>5SIM सर्वर से {country_info['flag']} {country_info['name']} का नंबर बुक किया जा रहा है...</b>\nकृपया 2-3 सेकंड रुकें...",
        parse_mode=ParseMode.HTML
    )

    try:
        order = fivesim.buy_number(country_code, service_code, operator="any")

        order_id = order.get("id")
        phone = order.get("phone")
        cost_rub = float(order.get("price", 1.0))
        selling_price_inr = calculate_selling_price(service_code, cost_rub)

        # Deduct balance
        update_user_balance(user.id, -selling_price_inr)

        # Record Order
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO orders (order_id, user_id, service, country, phone, cost_rub, price_inr, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING', ?)
        """, (order_id, user.id, service_code, country_code, phone, cost_rub, selling_price_inr, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
        c.execute("UPDATE users SET orders_count = orders_count + 1, total_spent = total_spent + ? WHERE user_id = ?", (selling_price_inr, user.id))
        conn.commit()
        conn.close()

        star_icon = pe(EMOJI_STAR, "⭐")
        bolt_icon = pe(EMOJI_LIGHTNING, "⚡")

        order_text = (
            f"╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│  🎉 <b>{font_bold_sans('NUMBER ALLOCATED')}</b> {bolt_icon}  │\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
            f"📌 <b>{font_small_caps('SERVICE')}:</b> {service_info['icon']} <b>{service_info['name']}</b>\n"
            f"🌍 <b>{font_small_caps('COUNTRY')}:</b> {country_info['flag']} <b>{country_info['name']}</b>\n"
            f"📞 <b>{font_small_caps('PHONE NUMBER')}:</b> <code>{phone}</code> (क्लिक करके कॉपी करें)\n"
            f"🆔 <b>{font_small_caps('ORDER ID')}:</b> <code>{order_id}</code>\n"
            f"💰 <b>{font_small_caps('PRICE CHARGED')}:</b> <b>₹{selling_price_inr:.2f} INR</b>\n"
            f"⏳ <b>{font_small_caps('EXPIRY TIME')}:</b> 15 मिनट\n\n"
            f"<blockquote expandable>"
            f"<b>📲 आसान 3 स्टेप्स:</b>\n"
            f"1. ऊपर दिए गए नंबर <code>{phone}</code> को कॉपी करें।\n"
            f"2. अपने {service_info['name']} ऐप में डालें और OTP सेंड करें।\n"
            f"3. <b>हमारा बॉट लाइव OTP सुन रहा है!</b> जैसे ही कोड आएगा, यहाँ तुरंत दिखेगा।\n"
            f"4. यदि OTP न आए, तो नीचे <b>कैंसिल व रिफंड</b> दबाएं — आपका पैसा तुरंत वापस आ जाएगा!"
            f"</blockquote>\n\n"
            f"⏳ <i>{font_bold_sans('LIVE OTP LISTENING')}... (इंतज़ार जारी है)</i>"
        )

        keyboard = [
            [
                InlineKeyboardButton("🔄 रिफ्रेश OTP", callback_data=f"chk_{order_id}"),
                InlineKeyboardButton("❌ कैंसिल व रिफंड", callback_data=f"can_{order_id}")
            ],
            [InlineKeyboardButton("🔙 मुख्य मेनू", callback_data="btn_home")]
        ]

        await query.edit_message_text(
            text=order_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        # Launch background poller
        asyncio.create_task(poll_otp_loop(context, query.message.chat_id, order_id, phone, service_info["name"], selling_price_inr, user.id))

    except Exception as e:
        logger.error(f"Purchase failed: {e}")
        await query.edit_message_text(
            f"❌ <b>नंबर बुकिंग विफल:</b>\n<code>{e}</code>\n\n💡 <i>टिप: इस देश का स्टॉक अस्थायी रूप से खाली हो सकता है। कृपया दूसरा देश (जैसे रूस या इंडोनेशिया) चुनें।</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 दूसरा देश चुनें", callback_data=f"srv_{service_code}")]])
        )

async def poll_otp_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, order_id: int, phone: str, service_name: str, price: float, user_id: int):
    """Background polling loop listening for OTP."""
    for _ in range(120):  # ~6 minutes
        await asyncio.sleep(3)
        try:
            order_data = fivesim.check_order(order_id)
            status = order_data.get("status")
            sms_list = order_data.get("sms", [])

            if status in ("CANCELED", "TIMEOUT"):
                break

            if sms_list and len(sms_list) > 0:
                latest = sms_list[-1]
                code = latest.get("code") or "RECEIVED"
                full_text = latest.get("text", "")

                # Update Order in DB
                conn = sqlite3.connect(DATABASE_PATH)
                c = conn.cursor()
                c.execute("UPDATE orders SET status = 'RECEIVED', otp = ? WHERE order_id = ?", (code, order_id))
                conn.commit()
                conn.close()

                try:
                    fivesim.finish_order(order_id)
                except Exception:
                    pass

                star_icon = pe(EMOJI_STAR, "⭐")
                fire_icon = pe(EMOJI_FIRE, "🔥")

                otp_banner = (
                    f"╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                    f"│  {fire_icon} <b>{font_bold_sans('OTP RECEIVED SUCCESSFULLY')}</b> {star_icon}  │\n"
                    f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                    f"📌 <b>{font_small_caps('SERVICE')}:</b> <b>{service_name}</b>\n"
                    f"📞 <b>{font_small_caps('PHONE')}:</b> <code>{phone}</code>\n"
                    f"🔑 <b>{font_bold_sans('YOUR OTP CODE')}:</b> <code>{code}</code> (क्लिक करके कॉपी करें)\n\n"
                    f"💬 <b>पूरा मैसेज:</b>\n"
                    f"<code>{full_text}</code>\n\n"
                    f"✅ <i>सफलतापूर्वक कार्य संपन्न! हमारे साथ डील करने के लिए धन्यवाद।</i>"
                )

                keyboard = [
                    [InlineKeyboardButton("🛒 नया नंबर खरीदें", callback_data="btn_services")],
                    [InlineKeyboardButton("🔙 मुख्य मेनू", callback_data="btn_home")]
                ]

                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=otp_banner,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                except Exception:
                    pass
                break
        except Exception:
            pass

async def wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wallet topup via dynamic QR code."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    u = get_or_create_user(user.id, user.username or "", user.first_name or "")

    upi_intent = f"upi://pay?pa={UPI_ID}&pn={quote_plus(UPI_NAME)}&am=50&cu=INR&tn={quote_plus(f'WALLET_{user.id}')}"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&margin=12&data={quote_plus(upi_intent)}"

    crown_icon = pe(EMOJI_CROWN, "👑")

    text = (
        f"╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│  {crown_icon} <b>{font_bold_sans('WALLET RECHARGE')}</b> 💳  │\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"💰 <b>वर्तमान बैलेंस:</b> <code>₹{u['balance']:.2f} INR</code>\n\n"
        f"💳 <b>ऑफिशियल UPI ID:</b> <code>{UPI_ID}</code> (क्लिक करके कॉपी करें)\n"
        f"👤 <b>प्राप्तकर्ता:</b> <b>{UPI_NAME}</b>\n\n"
        f"<blockquote expandable>"
        f"<b>📌 रिचार्ज प्रक्रिया:</b>\n"
        f"1. नीचे दिए QR कोड को PhonePe, Paytm या Google Pay से स्कैन करें।\n"
        f"2. अपनी पसंद की राशि (जैसे ₹30, ₹50, ₹100) भेजें।\n"
        f"3. पेमेंट के बाद 12-अंकों का UTR नंबर इस प्रकार भेजें:\n"
        f"   <code>/submitutr 412345678901 50</code>\n"
        f"4. आपका बैलेंस तुरंत खाते में जुड़ जाएगा!"
        f"</blockquote>"
    )

    keyboard = [
        [InlineKeyboardButton("📲 Pay via UPI App (PhonePe/GPay)", url=upi_intent)],
        [InlineKeyboardButton("🔙 मुख्य मेनू", callback_data="btn_home")]
    ]

    try:
        await query.message.reply_photo(
            photo=qr_url,
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception:
        await query.edit_message_text(text=text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main callback router."""
    query = update.callback_query
    data = query.data

    if data == "btn_home":
        await start_command(update, context)
    elif data == "btn_services":
        await services_handler(update, context)
    elif data.startswith("srv_"):
        await country_handler(update, context, data.replace("srv_", ""))
    elif data.startswith("buy_"):
        parts = data.split("_")
        if len(parts) >= 3:
            await buy_handler(update, context, parts[1], parts[2])
    elif data == "btn_wallet":
        await wallet_handler(update, context)
    elif data == "btn_balance":
        user = update.effective_user
        u = get_or_create_user(user.id)
        await query.answer(f"💰 बैलेंस: ₹{u['balance']:.2f} INR", show_alert=True)
    elif data == "btn_my_orders":
        user = update.effective_user
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT service, phone, price_inr, status, otp FROM orders WHERE user_id = ? ORDER BY order_id DESC LIMIT 5", (user.id,))
        rows = c.fetchall()
        conn.close()

        if not rows:
            await query.answer("अभी तक कोई ऑर्डर नहीं मिला।", show_alert=True)
            return

        lines = [f"• <b>{r[0].upper()}:</b> <code>{r[1]}</code> (₹{r[2]:.2f}) | स्थिति: <b>{r[3]}</b> | OTP: <code>{r[4] or 'Waiting'}</code>" for r in rows]
        await query.message.reply_text("📋 <b>आपके हालिया ऑर्डर्स:</b>\n\n" + "\n".join(lines), parse_mode=ParseMode.HTML)
    elif data == "btn_5sim_info":
        try:
            prof = fivesim.get_profile()
            info_text = (
                f"👑 <b>5SIM.NET LIVE STATUS</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 ईमेल: <code>{prof.get('email')}</code>\n"
                f"🆔 यूज़र ID: <code>{prof.get('id')}</code>\n"
                f"💰 5SIM बैलेंस: <b>{prof.get('balance')} RUB</b>\n"
                f"⭐ रेटिंग: <code>{prof.get('rating')}/100</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ लाइव डायरेक्ट 5SIM कनेक्शन सक्रिय!"
            )
        except Exception as e:
            info_text = f"❌ 5SIM त्रुटि: {e}"
        await query.message.reply_text(info_text, parse_mode=ParseMode.HTML)
    elif data.startswith("chk_"):
        oid = int(data.replace("chk_", ""))
        try:
            res = fivesim.check_order(oid)
            sms = res.get("sms", [])
            if sms:
                await query.answer(f"🎉 OTP: {sms[-1].get('code')}", show_alert=True)
            else:
                await query.answer("⏳ अभी SMS नहीं आया, 10 सेकंड बाद फिर चेक करें।", show_alert=True)
        except Exception as e:
            await query.answer(f"एरर: {e}", show_alert=True)
    elif data.startswith("can_"):
        oid = int(data.replace("can_", ""))
        try:
            fivesim.cancel_order(oid)
            # Refund in DB
            conn = sqlite3.connect(DATABASE_PATH)
            c = conn.cursor()
            c.execute("SELECT user_id, price_inr FROM orders WHERE order_id = ?", (oid,))
            row = c.fetchone()
            if row:
                uid, refund_amt = row
                c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (refund_amt, uid))
                c.execute("UPDATE orders SET status = 'CANCELED' WHERE order_id = ?", (oid,))
                conn.commit()
            conn.close()
            await query.edit_message_text("✅ <b>ऑर्डर सफलतापूर्वक कैंसिल हो गया और पूरा बैलेंस तुरंत वापस कर दिया गया!</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await query.answer(f"कैंसिल एरर: {e}", show_alert=True)
    elif data == "btn_help":
        await help_command(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        f"📱 <b>NAMAN SELL BOT - कमांड सूची:</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"• <code>/start</code> - मुख्य स्टोर मेनू खोलें\n"
        f"• <code>/buy</code> - किसी भी ऐप का नंबर खरीदें\n"
        f"• <code>/wallet</code> - वॉलेट बैलेंस व रिचार्ज QR\n"
        f"• <code>/submitutr &lt;UTR&gt; &lt;RASHI&gt;</code> - UTR सबमिट करें\n"
        f"• <code>/5sim</code> - 5SIM अकाउंट स्थिति देखें\n"
        f"• <code>/help</code> - यह सहायता मेनू"
    )
    target = update.message if update.message else update.callback_query.message
    await target.reply_text(help_text, parse_mode=ParseMode.HTML)

async def submit_utr_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("ℹ️ उपयोग: <code>/submitutr 12_DIGIT_UTR RASHI</code>\nउदा: <code>/submitutr 412345678901 50</code>", parse_mode=ParseMode.HTML)
        return
    utr = context.args[0].strip()
    amt = float(context.args[1]) if len(context.args) > 1 and context.args[1].replace('.', '', 1).isdigit() else 50.0

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO deposits (user_id, username, amount, utr, status, created_at) VALUES (?, ?, ?, ?, 'pending', ?)",
                  (user.id, user.username or user.first_name, amt, utr, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        await update.message.reply_text(f"✅ <b>UTR {utr} प्राप्त हुआ!</b> एडमिन द्वारा पुष्टि होते ही ₹{amt} आपके वॉलेट में जुड़ जाएंगे।", parse_mode=ParseMode.HTML)
    except sqlite3.IntegrityError:
        await update.message.reply_text(f"⚠️ यह UTR (<code>{utr}</code>) पहले ही सबमिट किया गया है!", parse_mode=ParseMode.HTML)
    conn.close()

# Keep-Alive Background HTTP Server for 24/7 VPS & Cloud Hosting
def start_keepalive_server():
    port_env = os.environ.get("PORT")
    keep_alive_env = os.environ.get("KEEP_ALIVE", "").lower() in ("1", "true", "yes")
    if not port_env and not keep_alive_env:
        return
    port = int(port_env) if port_env else 8080
    try:
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import threading
        class KeepAliveHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "online", "bot": "Naman Sell VIP Store"}).encode("utf-8"))
            def log_message(self, format, *args):
                pass
        server = HTTPServer(("0.0.0.0", port), KeepAliveHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
    except Exception:
        pass

def main():
    print("=" * 65)
    print("📱 Starting Naman Sell Bot with VIP Premium UI & 5SIM API...")
    print("=" * 65)
    init_database()
    token = ""
    if len(sys.argv) > 1 and sys.argv[1].strip() and not sys.argv[1].startswith("-"):
        token = sys.argv[1].strip()
    if not token:
        token = os.environ.get("BOT_TOKEN", "").strip()
    if not token or token == "your_bot_token_here":
        if sys.stdin and sys.stdin.isatty():
            try:
                token = input("👉 Enter Telegram BOT_TOKEN: ").strip()
            except (EOFError, KeyboardInterrupt):
                token = ""
    if not token or token == "your_bot_token_here":
        print("\n❌ Error: Bot Token missing!")
        print("Usage: python naman_sell_bot.py YOUR_BOT_TOKEN\n")
        sys.exit(1)

    try:
        app = Application.builder().token(token).build()
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("buy", services_handler))
        app.add_handler(CommandHandler("wallet", wallet_handler))
        app.add_handler(CommandHandler("deposit", wallet_handler))
        app.add_handler(CommandHandler("submitutr", submit_utr_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CallbackQueryHandler(callback_router))
        start_keepalive_server()
        print("✅ Naman Sell Bot is ONLINE!")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"❌ Launch Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
