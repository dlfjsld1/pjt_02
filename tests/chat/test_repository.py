"""Unit tests for user-scoped persistent chat storage."""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.chat.repository import ChatRepository


class FakeChatQuery:
    """In-memory PostgREST query double with owner filtering."""

    def __init__(self, rows: list[dict[str, str]]) -> None:
        self.rows = rows
        self.owner_id: str | None = None
        self.insert_row: dict[str, str] | None = None
        self.result_limit: int | None = None

    def select(self, fields: str) -> FakeChatQuery:
        return self

    def eq(self, field_name: str, value: str) -> FakeChatQuery:
        assert field_name == "owner_id"
        self.owner_id = value
        return self

    def order(self, field_name: str) -> FakeChatQuery:
        assert field_name == "created_at"
        return self

    def limit(self, limit: int) -> FakeChatQuery:
        self.result_limit = limit
        return self

    def insert(self, row: dict[str, str]) -> FakeChatQuery:
        self.insert_row = row
        return self

    def execute(self) -> SimpleNamespace:
        if self.insert_row is not None:
            self.rows.append(dict(self.insert_row))
            return SimpleNamespace(data=[self.insert_row])
        rows = [row for row in self.rows if row["owner_id"] == self.owner_id]
        rows.sort(key=lambda row: row["created_at"])
        if self.result_limit is not None:
            rows = rows[: self.result_limit]
        return SimpleNamespace(
            data=[
                {"role": row["role"], "content": row["content"], "created_at": row["created_at"]}
                for row in rows
            ]
        )


class FakeSupabaseClient:
    """Share one row collection between repository instances."""

    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def table(self, table_name: str) -> FakeChatQuery:
        assert table_name == "chat_messages"
        return FakeChatQuery(self.rows)


def test_chat_repository_restores_messages_after_a_new_repository_instance() -> None:
    client = FakeSupabaseClient()
    repository = ChatRepository(client=client)

    repository.save_message("user-a", "user", "논문을 찾아줘")
    repository.save_message("user-a", "assistant", "관련 논문 3건입니다.")

    reloaded_repository = ChatRepository(client=client)

    assert reloaded_repository.load_messages("user-a") == [
        {"role": "user", "content": "논문을 찾아줘", "created_at": client.rows[0]["created_at"]},
        {"role": "assistant", "content": "관련 논문 3건입니다.", "created_at": client.rows[1]["created_at"]},
    ]


def test_chat_repository_keeps_users_messages_isolated() -> None:
    client = FakeSupabaseClient()
    repository = ChatRepository(client=client)

    repository.save_message("user-a", "user", "A의 연구 질문")
    repository.save_message("user-b", "user", "B의 비공개 질문")

    user_a_messages = repository.load_messages("user-a")
    user_b_messages = repository.load_messages("user-b")

    assert [message["content"] for message in user_a_messages] == ["A의 연구 질문"]
    assert [message["content"] for message in user_b_messages] == ["B의 비공개 질문"]


def test_chat_repository_rejects_a_publishable_supabase_key() -> None:
    config_module = SimpleNamespace(
        get_supabase_credentials=lambda: ("https://example.supabase.co", "sb_publishable_test")
    )

    with patch.dict(sys.modules, {"src.config": config_module}):
        with pytest.raises(RuntimeError, match="sb_secret"):
            ChatRepository()
