import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "ai_files"

def save_file_record(file_name: str, file_type: str, file_path: str, transcript: str = None):
    data = {
        "file_name": file_name,
        "file_type": file_type,
        "file_path": file_path,
        "transcript": transcript
    }
    supabase.table(TABLE_NAME).insert(data).execute()
