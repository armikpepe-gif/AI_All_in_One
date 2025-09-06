# keep-alive.py
import time
import requests
import os

# === URL اپلیکیشن روی Render (از Environment Variable بگیر) ===
APP_URL = os.getenv("APP_URL")  # مثلا: https://your-app.onrender.com

# === تابع ping ساده برای نگه داشتن اپ زنده ===
def keep_alive():
    while True:
        try:
            response = requests.get(APP_URL, timeout=10)
            print(f"[KEEP-ALIVE] Pinged {APP_URL} - Status: {response.status_code}")
        except Exception as e:
            print(f"[KEEP-ALIVE] Error pinging app: {e}")
        time.sleep(300)  # هر 5 دقیقه یکبار پینگ می‌کنه

if __name__ == "__main__":
    print("🟢 Keep-alive script started")
    keep_alive()
