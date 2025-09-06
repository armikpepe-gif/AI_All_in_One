# app_with_encrypted_storage.py
import os
import zipfile
from pathlib import Path
import tempfile
import shutil
from PIL import Image
from pydub import AudioSegment
import torch
import torchaudio
import gradio as gr
from supabase import create_client, Client
import uuid
from cryptography.fernet import Fernet

# =========================
# اتصال به Supabase
# =========================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "ai_files"
STORAGE_BUCKET = "ai-storage"

# =========================
# کلید رمزنگاری (نگهداری در Environment Variable)
# =========================
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
fernet = Fernet(ENCRYPTION_KEY)

# =========================
# مسیرهای محلی
# =========================
ZIP_PATH = "All_in_One_Final.zip"
EXTRACT_PATH = "Extracted_Files"
os.makedirs(EXTRACT_PATH, exist_ok=True)

# =========================
# مدل پردازش صوت
# =========================
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
asr_model = bundle.get_model()

def audio_to_text(path: Path):
    waveform, sample_rate = torchaudio.load(path)
    with torch.inference_mode():
        emissions, _ = asr_model(waveform)
        tokens = torch.argmax(emissions[0], dim=-1)
        transcript = bundle.decode(tokens)
    return transcript

# =========================
# پردازش تصویر
# =========================
def process_image(path: Path):
    ext = path.suffix.lower()
    if ext in ['.heic', '.heif']:
        img = Image.open(path)
        new_path = path.with_suffix('.jpg')
        img.save(new_path, format="JPEG")
        return new_path
    return path

# =========================
# ذخیره فایل تو Supabase و رمزنگاری
# =========================
def upload_file_encrypted(file_path: Path, file_type: str, transcript=None):
    file_id = str(uuid.uuid4())
    storage_path = f"{file_id}_{file_path.name}"

    # خواندن فایل و رمزنگاری
    with open(file_path, "rb") as f:
        encrypted_data = fernet.encrypt(f.read())
    
    # آپلود به Storage
    supabase.storage.from_(STORAGE_BUCKET).upload(storage_path, encrypted_data, {"upsert": True})
    
    file_url = f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{storage_path}"
    
    # رمزنگاری متن
    encrypted_transcript = fernet.encrypt(transcript.encode()).decode() if transcript else None
    
    # ذخیره در جدول
    supabase.table(TABLE_NAME).insert({
        "id": file_id,
        "file_name": file_path.name,
        "file_type": file_type,
        "file_path": file_url,
        "transcript": encrypted_transcript
    }).execute()
    
    return file_url

# =========================
# پردازش ZIP
# =========================
def process_zip(zip_path):
    shutil.rmtree(EXTRACT_PATH, ignore_errors=True)
    os.makedirs(EXTRACT_PATH, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_PATH)
    
    uploaded_files = []
    
    for f in Path(EXTRACT_PATH).rglob("*"):
        if f.is_file():
            if f.suffix.lower() in ['.wav', '.mp3', '.m4a']:
                text = audio_to_text(f)
                url = upload_file_encrypted(f, "audio", transcript=text)
                uploaded_files.append(f"{f.name} -> {url}")
            elif f.suffix.lower() in ['.jpg', '.png', '.heic', '.heif']:
                new_img = process_image(f)
                url = upload_file_encrypted(new_img, "image")
                uploaded_files.append(f"{new_img.name} -> {url}")
            elif f.suffix.lower() == '.txt':
                url = upload_file_encrypted(f, "text")
                uploaded_files.append(f"{f.name} -> {url}")
    
    return "✅ فایل‌ها رمزنگاری و آپلود شدند:\n" + "\n".join(uploaded_files)

# =========================
# چت با حافظه رمزنگاری‌شده
# =========================
def chat(user_input):
    temp_txt = Path(tempfile.gettempdir()) / f"{uuid.uuid4()}.txt"
    temp_txt.write_text(user_input, encoding="utf-8")
    upload_file_encrypted(temp_txt, "text", transcript=user_input)

    resp = supabase.table(TABLE_NAME).select("*").order("created_at").execute()
    history = ""
    if resp.data:
        for row in resp.data:
            transcript = fernet.decrypt(row["transcript"].encode()).decode() if row.get("transcript") else ""
            if row["file_type"]=="text":
                history += f"👤 {row['file_name']} -> {transcript}\n"
            else:
                history += f"📁 {row['file_type'].upper()} {row['file_name']}\n"
    else:
        history = "هنوز چیزی ذخیره نشده."
    return "پیام ذخیره شد ✅", history

# =========================
# رابط کاربری Gradio
# =========================
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI_All_in_One با حافظه و فایل‌های رمزنگاری‌شده")

    with gr.Row():
        zip_input = gr.Textbox(label="مسیر ZIP (اختیاری)", placeholder=ZIP_PATH)
        process_btn = gr.Button("پردازش و آپلود ZIP")

    zip_output = gr.Textbox(label="خروجی پردازش فایل‌ها")

    with gr.Row():
        user_input = gr.Textbox(label="پیامتو بنویس:")
        send_btn = gr.Button("ارسال پیام")

    ai_output = gr.Textbox(label="پاسخ AI")
    history_output = gr.Textbox(label="تاریخچه کامل", lines=15)

    process_btn.click(process_zip, inputs=[zip_input], outputs=[zip_output])
    send_btn.click(chat, inputs=[user_input], outputs=[ai_output, history_output])

demo.launch(share=True)
