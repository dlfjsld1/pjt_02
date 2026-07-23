import streamlit as st


AUTH_REQUIRED_FIELDS = (
    "redirect_uri",
    "cookie_secret",
    "client_id",
    "client_secret",
    "server_metadata_url",
)


def is_auth_configured() -> bool:
    auth_config = st.secrets.get("auth", {})
    if not hasattr(auth_config, "get"):
        return False
    return all(auth_config.get(field_name) for field_name in AUTH_REQUIRED_FIELDS)


def is_logged_in() -> bool:
    if not is_auth_configured():
        return True
    return bool(st.user.is_logged_in)


def get_current_user_id() -> str:
    if not is_auth_configured():
        return "development-user"
    user_id = getattr(st.user, "sub", None) or getattr(st.user, "email", None)
    return str(user_id or "authenticated-user")


def get_current_user_name() -> str:
    if not is_auth_configured():
        return "개발 사용자"
    user_name = getattr(st.user, "name", None) or getattr(st.user, "email", None)
    return str(user_name or "사용자")


def require_login() -> None:
    if is_auth_configured() and not is_logged_in():
        st.switch_page("app.py")
