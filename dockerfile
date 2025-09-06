# تصویر پایه Python 3.11-slim
FROM python:3.11-slim

# نصب کتابخانه‌های سیستمی مورد نیاز
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# مسیر کاری پروژه
WORKDIR /app

# کپی فایل requirements.txt و نصب pip و setuptools
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel

# نصب همه پکیج‌ها
RUN pip install --no-cache-dir -r requirements.txt

# کپی باقی فایل‌های پروژه
COPY . .

# باز کردن پورت برای FastAPI / Gradio
EXPOSE 7860

# اجرای FastAPI روی Render
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
