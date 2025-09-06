import os
from supabase import create_client, Client
from fastapi import FastAPI

# گرفتن کلیدها از Environment (Render)
SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ SUPABASE_URL یا SUPABASE_KEY تنظیم نشده است!")

# ساخت کلاینت Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ساخت FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "سلام از Render 🚀"}

@app.get("/users")
def get_users():
    # فرض کن جدول users داری
    response = supabase.table("users").select("*").execute()
    return response.data
