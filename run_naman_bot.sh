#!/usr/bin/env bash
# ==============================================================================
# 📱 NAMAN SELL BOT - 24/7 AUTO-RESTART RUNNER
# Works on Android Termux, Linux VPS, Ubuntu & Cloud
# ==============================================================================

set -u

echo "========================================================"
echo "⚡ Starting Naman Sell OTP Bot 24/7 Auto-Restart Runner..."
echo "========================================================"

# Activate Termux wake-lock if on Android
if command -v termux-wake-lock >/dev/null 2>&1; then
    termux-wake-lock
    echo "🔋 Termux Wake-Lock enabled! Android CPU will stay awake."
fi

# Ensure dependencies
if ! python3 -c "import telegram" >/dev/null 2>&1; then
    echo "📦 Installing requirements..."
    pip install -r requirements.txt --break-system-packages 2>/dev/null || pip install -r requirements.txt
fi

RESTART_DELAY=3
CRASH_COUNT=0

while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 Starting naman_sell_bot.py..."
    
    python3 naman_sell_bot.py "$@"
    EXIT_CODE=$?

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ Bot stopped with exit code $EXIT_CODE."

    if [ "$EXIT_CODE" -eq 0 ]; then
        echo "🛑 Clean exit detected. Stopping runner."
        break
    fi

    CRASH_COUNT=$((CRASH_COUNT + 1))
    echo "🔄 Auto-restarting bot in ${RESTART_DELAY}s (Crash count: $CRASH_COUNT)..."
    sleep "$RESTART_DELAY"
done
