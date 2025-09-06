# app.py
import os
import gradio as gr
from supabase import create_client, Client

# === اتصال به سوپابیس با کلید و URL از Environment Variables ===
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === نام جدول حافظه ===
TABLE_NAME = "ai_memory"

# === ذخیره پیام و پاسخ در سوپابیس ===
def save_memory(user_message, ai_response):
    supabase.table(TABLE_NAME).insert({
        "user_message": user_message,
        "ai_response": ai_response
    }).execute()

# === واکشی کل تاریخچه گفتگو ===
def load_memory():
    response = supabase.table(TABLE_NAME).select("*").order("created_at").execute()
    if response.data:
        return "\n".join([f"👤 {row['user_message']}\n🤖 {row['ai_response']}" for row in response.data])
    return "هنوز گفتگویی ذخیره نشده."

# === تابع اصلی برای چت ===
def chat(user_input):
    # شبیه‌سازی پاسخ هوش مصنوعی (اینجا ساده است – میشه بعدا مدل قوی وصل کرد)
    ai_response = f"پاسخت به '{user_input}' اینه: من پیام رو گرفتم و ذخیره کردم ✅"

    # ذخیره در حافظه دائمی
    save_memory(user_input, ai_response)

    # تاریخچه کامل گفتگو
    history = load_memory()
    return ai_response, history

# === رابط کاربری Gradio ===
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI با حافظه دائمی (Supabase)")

    with gr.Row():
        user_input = gr.Textbox(label="پیامتو بنویس:")
        send_btn = gr.Button("ارسال")

    ai_output = gr.Textbox(label="پاسخ AI")
    history_output = gr.Textbox(label="تاریخچه گفتگو", lines=15)

    send_btn.click(chat, inputs=[user_input], outputs=[ai_output, history_output])

demo.launch(share=True)
