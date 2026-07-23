from typing import Any;

import streamlit as st;


def readSecret(*names: str, default: str = "") -> str:
    for name in names:
        value = st.secrets.get(name);
        if value:
            return str(value);
    return default;


def readNestedSecret(sectionName: str, *names: str, default: str = "") -> str:
    section: Any = st.secrets.get(sectionName, {});
    for name in names:
        value = section.get(name) if hasattr(section, "get") else None;
        if value:
            return str(value);
    return default;


def getSupabaseCredentials() -> tuple[str, str]:
    supabaseUrl = readSecret("SUPABASE_URL", "supabase_url");
    supabaseKey = readSecret(
        "SUPABASE_SECRET_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_KEY",
        "supabase_secret_key",
        "supabase_key",
    );
    if not supabaseUrl:
        supabaseUrl = readNestedSecret("supabase", "url");
    if not supabaseKey:
        supabaseKey = readNestedSecret("supabase", "secret_key", "service_role_key", "key");
    return supabaseUrl, supabaseKey;


def getOpenAiApiKey() -> str:
    apiKey = readSecret("OPENAI_API_KEY", "openai_api_key");
    if apiKey:
        return apiKey;
    return readNestedSecret("openai", "api_key");


def getOpenAiModel() -> str:
    model = readSecret("OPENAI_MODEL", "openai_model");
    if model:
        return model;
    return readNestedSecret("openai", "model", default="gpt-5.6-luna");

