import gradio as gr

def hello_world(name):
    return f"سلام {name}! 🎉 اپ هوش مصنوعی آماده‌ست."

app = gr.Interface(
    fn=hello_world,
    inputs=gr.Textbox(label="اسم خودتو بنویس"),
    outputs=gr.Textbox(label="خروجی"),
    title="AI All in One",
    description="نسخه‌ی تست اپ – بعداً قابلیت پردازش تصویر، صوت و متن هم اضافه می‌کنیم."
)

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=8080)
