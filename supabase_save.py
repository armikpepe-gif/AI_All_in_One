# supabase_zip_processor.py
import zipfile
from pathlib import Path
import tempfile
from datetime import datetime
from PIL import Image
import torchaudio
import torch
from supabase import create_client, Client

# ==== Supabase Config ====
SUPABASE_URL = "https://zlrztiytgzqpxkoadefg.supabase.co"
SUPABASE_KEY = "<your-anon-or-service-key>"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==== Paths ====
ZIP_PATH = "All_in_One_Final.zip"  # مسیر ZIP
EXTRACT_PATH = Path(tempfile.gettempdir()) / "Extracted_Files"

EXTRACT_PATH.mkdir(exist_ok=True)

# ==== Model for audio to text ====
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
asr_model = bundle.get_model()

def audio_to_text(path):
    waveform, sample_rate = torchaudio.load(path)
    with torch.inference_mode():
        emissions, _ = asr_model(waveform)
        tokens = torch.argmax(emissions[0], dim=-1)
        transcript = bundle.decode(tokens)
    return transcript

def process_file(path: Path):
    """
    پردازش فایل و آماده‌سازی اطلاعات برای Supabase
    """
    suffix = path.suffix.lower()
    if suffix in ['.wav', '.mp3', '.m4a']:
        transcript = audio_to_text(str(path))
        file_type = "audio"
    elif suffix in ['.jpg', '.png', '.heic', '.heif']:
        img = Image.open(path)
        file_type = "image"
        transcript = None
    else:
        file_type = "text"
        transcript = None
    
    return {
        "file_name": path.name,
        "file_type": file_type,
        "file_path": str(path),
        "transcript": transcript
    }

def save_to_supabase(file_info: dict):
    """
    ذخیره داده‌ها در جدول ai_files در Supabase
    """
    try:
        response = supabase.table("ai_files").insert({
            "file_name": file_info["file_name"],
            "file_type": file_info["file_type"],
            "file_path": file_info["file_path"],
            "transcript": file_info["transcript"],
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        if response.error:
            print(f"❌ خطا در ذخیره {file_info['file_name']}: {response.error}")
        else:
            print(f"✅ ذخیره شد: {file_info['file_name']}")
    except Exception as e:
        print(f"❌ استثناء در ذخیره {file_info['file_name']}: {e}")

def extract_zip(zip_path: str, extract_to: Path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"✅ ZIP استخراج شد به {extract_to}")

def process_zip_and_save(zip_path: str):
    extract_zip(zip_path, EXTRACT_PATH)
    for f in EXTRACT_PATH.rglob("*"):
        if f.is_file():
            info = process_file(f)
            save_to_supabase(info)

# ==== اجرا ====
if __name__ == "__main__":
    process_zip_and_save(ZIP_PATH)
