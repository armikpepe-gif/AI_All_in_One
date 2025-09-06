import os
import zipfile
from pathlib import Path
import tempfile
from PIL import Image
from pydub import AudioSegment
import torch
import torchaudio
import gradio as gr
from supabase_save import save_file_record  # فایل supabase_save.py

# ==== مسیر فایل ZIP ورودی ====
ZIP_PATH = "All_in_One_Final.zip"  # فایل داخل مخزن
EXTRACT_PATH = "Extracted_Files"
OUTPUT_ZIP = "Processed_All_in_One.zip"
os.makedirs(EXTRACT_PATH, exist_ok=True)

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
            save_file_record(f.name, "audio", str(f), text)
        elif f.suffix.lower() in ['.jpg', '.png', '.heic', '.heif']:
            new_image = process_image(f)
            images_processed.append(new_image.name)
            save_file_record(f.name, "image", str(new_image))
        elif f.suffix.lower() in ['.txt']:
            save_file_record(f.name, "text", str(f))
    
    # ساخت ZIP خروجی
    with zipfile.ZipFile(OUTPUT_ZIP, 'w') as out_zip:
        for f in extracted_folder.rglob("*"):
            out_zip.write(f, arcname=f.name)
        transcript_file = Path(tempfile.gettempdir()) / "audio_transcripts.txt"
        with open(transcript_file, 'w', encoding='utf-8') as t:
            for fn, txt in audio_texts:
                t.write(f"{fn}:\n{txt}\n\n")
        out_zip.write(transcript_file, arcname="audio_transcripts.txt")

    return f"✅ پردازش کامل شد! لینک دانلود: {OUTPUT_ZIP}"

# ==== رابط کاربری Gradio ====
app = gr.Interface(
    fn=process_zip,
    inputs=gr.Textbox(label="مسیر ZIP", placeholder=ZIP_PATH),
    outputs=gr.Textbox(label="خروجی"),
    title="اپ AI_All_in_One",
    description="پردازش ZIP صوت، تصویر و متن و ذخیره در Supabase"
)

# ==== اجرا و لینک اشتراک موبایل ====
app.launch(share=True)
