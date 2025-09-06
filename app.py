# app.py
import os
from pathlib import Path
import zipfile
import tempfile
from shutil import make_archive

from supabase_config import supabase, process_image, audio_to_text
import gradio as gr

# ==== مسیر فایل ZIP ورودی ====
ZIP_PATH_DEFAULT = "All_in_One_Final.zip"
EXTRACT_PATH = "Extracted_Files"
OUTPUT_ZIP_DEFAULT = "Processed_All_in_One"

# ==== پردازش ZIP و ذخیره در Supabase ====
def process_zip(zip_path: str):
    if not os.path.exists(zip_path):
        return f"❌ فایل {zip_path} پیدا نشد!"

    os.makedirs(EXTRACT_PATH, exist_ok=True)
    audio_texts = []
    images_processed = []

    # استخراج ZIP
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_PATH)

    extracted_folder = Path(EXTRACT_PATH)

    # پردازش فایل‌ها و ذخیره در Supabase
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

    # ==== ساخت ZIP خروجی نهایی ====
    output_zip_path = f"{OUTPUT_ZIP_DEFAULT}.zip"
    make_archive(OUTPUT_ZIP_DEFAULT, 'zip', EXTRACT_PATH)

    return f"✅ پردازش کامل شد!\nفایل نهایی ZIP: {output_zip_path}\nتعداد فایل‌های صوتی: {len(audio_texts)}, تصاویر: {len(images_processed)}"

# ==== رابط کاربری Gradio ====
app = gr.Interface(
    fn=process_zip,
    inputs=gr.Textbox(label="مسیر ZIP", placeholder=ZIP_PATH_DEFAULT),
    outputs=gr.Textbox(label="نتیجه"),
    title="اپ AI_All_in_One با Supabase و خروجی ZIP",
    description="فایل ZIP شامل صوت، تصویر و متن را پردازش و اطلاعات آن را در Supabase ذخیره و خروجی ZIP نهایی می‌سازد."
)

# ==== اجرا و اشتراک لینک موبایل ====
if __name__ == "__main__":
    app.launch(share=True)
