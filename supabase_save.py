# supabase_config.py

from supabase import create_client, Client
import os
from pathlib import Path
import zipfile
from PIL import Image
from pydub import AudioSegment
import torch
import torchaudio

# ==== دریافت کلید و آدرس از Environment Variables ====
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL یا Key پیدا نشد! لطفا Environment Variables رو تنظیم کنید.")

# ==== ایجاد کلاینت Supabase ====
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==== توابع کمکی ====

# پردازش تصاویر (HEIC -> JPG)
def process_image(path: Path) -> Path:
    ext = path.suffix.lower()
    if ext in ['.heic', '.heif']:
        img = Image.open(path)
        new_path = path.with_suffix('.jpg')
        img.save(new_path, format="JPEG")
        return new_path
    return path

# تبدیل صوت به متن
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
asr_model = bundle.get_model()

def audio_to_text(path: Path) -> str:
    waveform, sample_rate = torchaudio.load(path)
    with torch.inference_mode():
        emissions, _ = asr_model(waveform)
        tokens = torch.argmax(emissions[0], dim=-1)
        transcript = bundle.decode(tokens)
    return transcript

# پردازش فایل ZIP و ذخیره در Supabase
def process_zip_and_save(zip_path: str, extract_path: str = "Extracted_Files"):
    os.makedirs(extract_path, exist_ok=True)
    audio_texts = []
    images_processed = []

    # استخراج ZIP
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    extracted_folder = Path(extract_path)

    # پردازش فایل‌ها
    for f in extracted_folder.rglob("*"):
        if f.suffix.lower() in ['.wav', '.mp3', '.m4a']:
            text = audio_to_text(f)
            audio_texts.append((f.name, text))
            supabase.table("ai_files").insert({
                "file_name": f.name,
                "file_type": "audio",
                "file_path": str(f),
                "transcript": text
            }).execute()
        elif f.suffix.lower() in ['.jpg', '.png', '.heic', '.heif']:
            new_image = process_image(f)
            images_processed.append(new_image.name)
            supabase.table("ai_files").insert({
                "file_name": new_image.name,
                "file_type": "image",
                "file_path": str(new_image)
            }).execute()
        elif f.suffix.lower() in ['.txt']:
            supabase.table("ai_files").insert({
                "file_name": f.name,
                "file_type": "text",
                "file_path": str(f)
            }).execute()

    return f"✅ پردازش و ذخیره فایل‌ها در Supabase کامل شد!"
