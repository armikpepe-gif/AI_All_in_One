# run_app.py
import subprocess
import threading
import os

# === مسیر فایل‌ها ===
APP_FILE = "app_secure_complete.py"
KEEP_ALIVE_FILE = "keep_alive.py"  # اگه فایل Keep-Alive داری، همینجا قرار بده

# === اجرای keep-alive در یک Thread جداگانه ===
def start_keep_alive():
    if os.path.exists(KEEP_ALIVE_FILE):
        subprocess.run(["python", KEEP_ALIVE_FILE])
    else:
        print(f"❌ فایل {KEEP_ALIVE_FILE} پیدا نشد. Keep-Alive اجرا نمی‌شود.")

keep_alive_thread = threading.Thread(target=start_keep_alive, daemon=True)
keep_alive_thread.start()

# === اجرای اپ اصلی ===
subprocess.run(["python", APP_FILE])
