from typing import Any

import streamlit as st


def read_secret(*names: str, default: str = "") -> str:
    for name in names:
        value = st.secrets.get(name)
        if value:
            return str(value)
    return default


def read_nested_secret(section_name: str, *names: str, default: str = "") -> str:
    section: Any = st.secrets.get(section_name, {})
    for name in names:
        value = section.get(name) if hasattr(section, "get") else None
        if value:
            return str(value)
    return default


def get_supabase_credentials() -> tuple[str, str]:
    supabase_url = read_secret("SUPABASE_URL", "supabase_url")
    supabase_key = read_secret(
        "SUPABASE_SECRET_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_KEY",
        "supabase_secret_key",
        "supabase_key",
    )
    if not supabase_url:
        supabase_url = read_nested_secret("supabase", "url")
    if not supabase_key:
        supabase_key = read_nested_secret("supabase", "secret_key", "service_role_key", "key")
    return supabase_url, supabase_key


def get_openai_api_key() -> str:
    api_key = read_secret("OPENAI_API_KEY", "openai_api_key")
    if api_key:
        return api_key
    return read_nested_secret("openai", "api_key")


def get_openai_model() -> str:
    model = read_secret("OPENAI_MODEL", "openai_model")
    if model:
        return model
    return read_nested_secret("openai", "model", default="gpt-5.6-luna")

