# app.py
import os
import zipfile
from pathlib import Path
import tempfile
from PIL import Image
from pydub import AudioSegment
import torch
import torchaudio
import gradio as gr
from supabase import create_client

# ==== مسیر فایل ZIP ورودی (همراه پروژه یا آپلود شده روی رندر) ====
ZIP_PATH = "All_in_One_Final.zip"
EXTRACT_PATH = "Extracted_Files"
OUTPUT_ZIP = "Processed_All_in_One.zip"
os.makedirs(EXTRACT_PATH, exist_ok=True)

# ==== اتصال به Supabase ====
SUPABASE_URL = "https://zlrztiytgzqpxkoadefg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpscnp0aXl0Z3pxcHhrb2FkZWZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTcxMzgxMDEsImV4cCI6MjA3MjcxNDEwMX0.V213ENLlZLu54pitDhyYhHNvsc_ImP3PQIRe8cPs0uk"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==== استخراج ZIP ====
with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
    zip_ref.extractall(EXTRACT_PATH)

# ==== پردازش تصاویر ====
def process_image(path):
    ext = path.suffix.lower()
    if ext in ['.heic', '.heif']:
        img = Image.open(path)
        new_path = path.with_suffix('.jpg')
        img.save(new_path, format="JPEG")
        # ذخیره در Supabase
        supabase.table("images_processed").insert({
            "file_id": None,
            "new_path": str(new_path)
        }).execute()
        return new_path
    return path

# ==== مدل تبدیل صوت به متن ====
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
asr_model = bundle.get_model()

def audio_to_text(path):
    waveform, sample_rate = torchaudio.load(path)
    with torch.inference_mode():
        emissions, _ = asr_model(waveform)
        tokens = torch.argmax(emissions[0], dim=-1)
        transcript = bundle.decode(tokens)
    # ذخیره در Supabase
    supabase.table("audio_transcripts").insert({
        "file_id": None,
        "transcript": transcript
    }).execute()
    return transcript

# ==== پردازش ZIP و ساخت خروجی نهایی ====
def process_zip(zip_path):
    extracted_folder = Path(EXTRACT_PATH)
    audio_texts = []
    images_processed = []

    # پردازش فایل‌ها
    for f in extracted_folder.rglob("*"):
        if f.suffix.lower() in ['.wav', '.mp3', '.m4a']:
            text = audio_to_text(f)
            audio_texts.append((f.name, text))
            supabase.table("files").insert({"name": f.name, "type": "audio", "path": str(f)}).execute()
        elif f.suffix.lower() in ['.jpg', '.png', '.heic', '.heif']:
            new_image = process_image(f)
            images_processed.append(new_image.name)
            supabase.table("files").insert({"name": new_image.name, "type": "image", "path": str(new_image)}).execute()
        elif f.suffix.lower() in ['.txt']:
            supabase.table("files").insert({"name": f.name, "type": "text", "path": str(f)}).execute()
    
    # ساخت ZIP خروجی
    with zipfile.ZipFile(OUTPUT_ZIP, 'w') as out_zip:
        for f in extracted_folder.rglob("*"):
            out_zip.write(f, arcname=f.name)
        # اضافه کردن فایل متن خروجی
        transcript_file = Path(tempfile.gettempdir()) / "audio_transcripts.txt"
        with open(transcript_file, 'w', encoding='utf-8') as t:
            for fn, txt in audio_texts:
                t.write(f"{fn}:\n{txt}\n\n")
        out_zip.write(transcript_file, arcname="audio_transcripts.txt")

    return f"✅ پردازش کامل شد! لینک دانلود: {OUTPUT_ZIP}"

# ==== رابط کاربری Gradio ====
app = gr.Interface(
    fn=process_zip,
    inputs=gr.Textbox(label="مسیر ZIP در گوگل درایو یا پروژه", placeholder=ZIP_PATH),
    outputs=gr.Textbox(label="خروجی"),
    title="اپ AI_All_in_One با Supabase",
    description="این اپ فایل ZIP صوت، تصویر و متن را پردازش و خروجی ZIP نهایی با لینک مستقیم تولید و رکوردها را در Supabase ذخیره می‌کند."
)

# ==== اجرا و لینک اشتراک موبایل ====
app.launch(share=True)
