# keep_alive.py
import time
import requests

# لینک سرویس خودت رو جایگزین کن
SERVICE_URL = "https://ai-all-in-one-xrn5.onrender.com"

def keep_alive():
    while True:
        try:
            requests.get(SERVICE_URL)
            print(f"Pinged {SERVICE_URL} successfully!")
        except Exception as e:
            print(f"Ping failed: {e}")
        time.sleep(300)  # هر ۵ دقیقه یک بار

if __name__ == "__main__":
    keep_alive()
