from supabase import create_client
import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

class SmartAI_Memory:
    def __init__(self):
        self.context = []  # حافظه موقتی در RAM

    def remember(self, user, message, response):
        """ذخیره پیام و پاسخ در Supabase"""
        data = {
            "user": user,
            "message": message,
            "response": response
        }
        supabase.table("ai_memory").insert(data).execute()
        self.context.append(data)

    def recall(self, user, limit=5):
        """بازیابی خاطرات اخیر از Supabase"""
        res = supabase.table("ai_memory") \
                      .select("*") \
                      .eq("user", user) \
                      .order("id", desc=True) \
                      .limit(limit) \
                      .execute()
        memories = [f"Q: {r['message']} → A: {r['response']}" for r in res.data]
        return "\n".join(memories) if memories else "⛔ خاطره‌ای برای این کاربر پیدا نشد."
