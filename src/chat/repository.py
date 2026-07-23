from datetime import datetime, timezone
from typing import Any

from supabase import Client, create_client

from src.config import getSupabaseCredentials


class ChatRepository:
    def __init__(self) -> None:
        supabaseUrl, supabaseKey = getSupabaseCredentials()
        if not supabaseUrl or not supabaseKey:
            raise RuntimeError("Supabase URL과 서버 키를 secrets.toml에 설정해 주세요.")
        self.client: Client = create_client(supabaseUrl, supabaseKey)

    def loadMessages(self, ownerId: str, limit: int = 100) -> list[dict[str, Any]]:
        response = (
            self.client.table("chat_messages")
            .select("role, content, created_at")
            .eq("owner_id", ownerId)
            .order("created_at")
            .limit(limit)
            .execute()
        )
        return list(response.data or [])

    def saveMessage(self, ownerId: str, role: str, content: str) -> None:
        self.client.table("chat_messages").insert(
            {
                "owner_id": ownerId,
                "role": role,
                "content": content,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()

