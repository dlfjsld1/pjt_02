from typing import Any;

from supabase import Client, create_client;

from src.config import getSupabaseCredentials;


class PaperRepository:
    def __init__(self) -> None:
        supabaseUrl, supabaseKey = getSupabaseCredentials();
        if not supabaseUrl or not supabaseKey:
            raise RuntimeError("Supabase URL과 서버 키를 secrets.toml에 설정해 주세요.");
        self.client: Client = create_client(supabaseUrl, supabaseKey);

    def loadPapers(self, limit: int = 1000) -> list[dict[str, Any]]:
        response = self.client.table("papers").select("*").limit(limit).execute();
        return list(response.data or []);

