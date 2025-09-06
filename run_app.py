import subprocess
import threading

# فایل‌های اصلی
APP_FILE = "app_secure_complete.py"

# اجرای اپ اصلی در یک Thread جداگانه
def start_app():
    subprocess.run(["python", APP_FILE])

app_thread = threading.Thread(target=start_app, daemon=True)
app_thread.start()
app_thread.join()
