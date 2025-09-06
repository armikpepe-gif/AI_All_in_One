# run_app.py
import os
import gradio as gr
from supabase import create_client, Client
import uuid

# =========================
# اتصال به Supabase
# =========================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "ai_files"

# =========================
# ذخیره پیام و پاسخ
# =========================
def save_memory(user_message, ai_response):
    supabase.table(TABLE_NAME).insert({
        "id": str(uuid.uuid4()),
        "file_name": user_message,
        "file_type": "text",
        "file_path": "",
        "transcript": ai_response
    }).execute()

# =========================
# واکشی کل تاریخچه گفتگو
# =========================
def load_memory():
    response = supabase.table(TABLE_NAME).select("*").order("created_at").execute()
    if response.data:
        return "\n".join([f"👤 {row['file_name']}\n🤖 {row['transcript']}" for row in response.data])
    return "هنوز گفتگویی ذخیره نشده."

# =========================
# تابع اصلی چت
# =========================
def chat(user_input):
    ai_response = f"پاسخت به '{user_input}' دریافت شد ✅"
    save_memory(user_input, ai_response)
    history = load_memory()
    return ai_response, history

# =========================
# رابط کاربری Gradio
# =========================
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI با حافظه دائمی (Supabase)")

    with gr.Row():
        user_input = gr.Textbox(label="پیامتو بنویس:")
        send_btn = gr.Button("ارسال")

    ai_output = gr.Textbox(label="پاسخ AI")
    history_output = gr.Textbox(label="تاریخچه گفتگو", lines=15)

    send_btn.click(chat, inputs=[user_input], outputs=[ai_output, history_output])

demo.launch(share=True)
