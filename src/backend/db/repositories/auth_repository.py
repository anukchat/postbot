from typing import Optional, Dict, Any
from ..repository import BaseRepository
from datetime import datetime
from supabase import Client

class AuthRepository:
    def __init__(self, supabase_client: Client):
        self.client = supabase_client

    async def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        return self.client.auth.sign_up({
            "email": email,
            "password": password
        })

    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        return self.client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

    async def sign_out(self) -> Dict[str, Any]:
        return self.client.auth.sign_out()

    async def get_user(self, token: str) -> Optional[Dict]:
        return self.client.auth.get_user(token)

    async def exchange_code_for_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self.client.auth.exchange_code_for_session(params)

    async def sign_in_with_oauth(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        return self.client.auth.sign_in_with_oauth(credentials)