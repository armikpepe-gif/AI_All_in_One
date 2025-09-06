import gradio as gr
from smart_ai_memory import SmartAI_Memory

ai_memory = SmartAI_Memory()

def chat(user, message):
    # بازیابی خاطرات اخیر
    past = ai_memory.recall(user, limit=3)

    # شبیه‌سازی یک پاسخ هوشمند (اینجا میشه مدل AI وصل کرد)
    response = f"🔹 پیام شما: {message}\n\n📜 خاطرات اخیر:\n{past}"

    # ذخیره مکالمه
    ai_memory.remember(user, message, response)
    return response

app = gr.Interface(
    fn=chat,
    inputs=[gr.Textbox(label="👤 نام کاربر"), gr.Textbox(label="💬 پیام")],
    outputs=gr.Textbox(label="🤖 پاسخ AI"),
    title="هوش مصنوعی با حافظه دائمی"
)

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=8000)
