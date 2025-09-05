# File: app.py

import os
import zipfile
from pathlib import Path
import tempfile
import gradio as gr
from PIL import Image
from pydub import AudioSegment
import torch
import torchaudio
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import io

# ===== پیکربندی Google Drive =====
SERVICE_ACCOUNT_FILE = "service_account.json"  # کلید JSON که روی Render آپلود می‌کنیم
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# ===== مسیر ZIP روی Google Drive =====
ZIP_FILE_ID = "YOUR_DRIVE_FILE_ID_HERE"  # ID فایل ZIP در Drive
EXTRACT_PATH = Path(tempfile.gettempdir()) / "extracted_files"
OUTPUT_ZIP = Path(tempfile.gettempdir()) / "Processed_All_in_One.zip"
EXTRACT_PATH.mkdir(parents=True, exist_ok=True)

# ===== دانلود ZIP از Drive =====
def download_drive_file(file_id, dest_path):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(dest_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    return dest_path

# ===== پردازش تصاویر =====
def process_image(path):
    ext = path.suffix.lower()
    if ext in ['.heic', '.heif']:
        img = Image.open(path)
        new_path = path.with_suffix('.jpg')
        img.save(new_path, format="JPEG")
        return new_path
    return path

# ===== مدل تبدیل صوت به متن =====
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
asr_model = bundle.get_model()

def audio_to_text(path):
    waveform, sample_rate = torchaudio.load(path)
    with torch.inference_mode():
        emissions, _ = asr_model(waveform)
        tokens = torch.argmax(emissions[0], dim=-1)
        transcript = bundle.decode(tokens)
    return transcript

# ===== پردازش ZIP و ساخت خروجی =====
def process_zip(_):
    # دانلود ZIP
    local_zip = Path(tempfile.gettempdir()) / "All_in_One.zip"
    download_drive_file(ZIP_FILE_ID, local_zip)
    
    # استخراج
    with zipfile.ZipFile(local_zip, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_PATH)

    audio_texts = []
    images_processed = []

    # پردازش فایل‌ها
    for f in EXTRACT_PATH.rglob("*"):
        if f.suffix.lower() in ['.wav', '.mp3', '.m4a']:
            text = audio_to_text(f)
            audio_texts.append((f.name, text))
        elif f.suffix.lower() in ['.jpg', '.png', '.heic', '.heif']:
            new_image = process_image(f)
            images_processed.append(new_image.name)
        elif f.suffix.lower() in ['.txt']:
            continue  # متن‌ها را مستقیم اضافه می‌کنیم

    # ساخت ZIP خروجی
    with zipfile.ZipFile(OUTPUT_ZIP, 'w') as out_zip:
        for f in EXTRACT_PATH.rglob("*"):
            out_zip.write(f, arcname=f.name)
        transcript_file = Path(tempfile.gettempdir()) / "audio_transcripts.txt"
        with open(transcript_file, 'w', encoding='utf-8') as t:
            for fn, txt in audio_texts:
                t.write(f"{fn}:\n{txt}\n\n")
        out_zip.write(transcript_file, arcname="audio_transcripts.txt")

    return f"✅ پردازش کامل شد! لینک ZIP خروجی: {OUTPUT_ZIP}"

# ===== رابط کاربری Gradio =====
app = gr.Interface(
    fn=process_zip,
    inputs=gr.Textbox(label="Start", placeholder="Press Submit to process"),
    outputs=gr.Textbox(label="خروجی"),
    title="AI All-in-One Processor",
    description="این اپ فایل ZIP صوت، تصویر و متن را پردازش و خروجی ZIP نهایی تولید می‌کند."
)

# ===== اجرا روی Render =====
app.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 8080)))
