from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()
from supabase import create_client, Client


def supabase_client():
    # Initialize the Supabase client
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    return create_client(supabase_url, supabase_key)