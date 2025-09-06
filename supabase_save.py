import os
from supabase import create_client, Client
from supabase.lib.auth_client import SupabaseAuthClient

# === دریافت کلید و URL از Environment Variables ===
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# === ایجاد کلاینت Supabase ===
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === نام جدول ===
TABLE_NAME = "ai_files"

# === بررسی وجود جدول با استفاده از metadata ===
def ensure_table_exists():
    try:
        tables = supabase.rpc("pg_tables").execute()
        if TABLE_NAME not in [t['tablename'] for t in tables.data]:
            # جدول وجود ندارد، رکورد موقت اضافه می‌کنیم تا جدول ساخته شود
            print(f"⚡ جدول {TABLE_NAME} وجود ندارد، ایجاد خودکار...")
            supabase.table(TABLE_NAME).insert({
                "file_name": "init_file.txt",
                "file_type": "text",
                "file_path": "/init/path"
            }).execute()
            print(f"✅ جدول {TABLE_NAME} ساخته شد.")
    except Exception:
        # اگر metadata پیدا نشد، فرض می‌کنیم جدول ساخته نشده
        supabase.table(TABLE_NAME).insert({
            "file_name": "init_file.txt",
            "file_type": "text",
            "file_path": "/init/path"
        }).execute()
        print(f"✅ جدول {TABLE_NAME} ساخته شد (fallback).")

# === تابع ذخیره رکورد فایل ===
def save_file_record(file_name: str, file_type: str, file_path: str, transcript: str = None):
    ensure_table_exists()  # ابتدا جدول را بررسی کن
    data = {
        "file_name": file_name,
        "file_type": file_type,
        "file_path": file_path,
        "transcript": transcript
    }
    response = supabase.table(TABLE_NAME).insert(data).execute()
    if response.status_code != 201:
        print(f"⚠️ خطا در ذخیره رکورد: {response}")
