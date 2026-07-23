from datetime import datetime, timezone
from typing import Any

from supabase import Client, create_client

from src.config import get_supabase_credentials


class ChatRepository:
    def __init__(self) -> None:
        supabase_url, supabase_key = get_supabase_credentials()
        if not supabase_url or not supabase_key:
            raise RuntimeError("Supabase URL과 서버 키를 secrets.toml에 설정해 주세요.")
        self.client: Client = create_client(supabase_url, supabase_key)

    def load_messages(self, owner_id: str, limit: int = 100) -> list[dict[str, Any]]:
        response = (
            self.client.table("chat_messages")
            .select("role, content, created_at")
            .eq("owner_id", owner_id)
            .order("created_at")
            .limit(limit)
            .execute()
        )
        return list(response.data or [])

    def save_message(self, owner_id: str, role: str, content: str) -> None:
        self.client.table("chat_messages").insert(
            {
                "owner_id": owner_id,
                "role": role,
                "content": content,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()

