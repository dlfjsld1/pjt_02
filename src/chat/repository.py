from datetime import datetime, timezone
from typing import Any

class ChatRepository:
    """Persist chat messages with the server-only Supabase key."""

    def __init__(self, client: Any | None = None) -> None:
        if client is not None:
            self.client = client
            return

        from src.config import get_supabase_credentials

        supabase_url, supabase_key = get_supabase_credentials()
        if not supabase_url or not supabase_key:
            raise RuntimeError("Supabase URL과 서버 키를 secrets.toml에 설정해 주세요.")
        if supabase_key.startswith("sb_publishable_"):
            raise RuntimeError(
                "SUPABASE_SECRET_KEY에는 publishable 키가 아닌 sb_secret 서버 키를 설정해 주세요."
            )

        from supabase import create_client

        self.client = create_client(supabase_url, supabase_key)

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

