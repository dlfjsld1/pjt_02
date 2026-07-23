import streamlit as st;


AUTH_REQUIRED_FIELDS = (
    "redirect_uri",
    "cookie_secret",
    "client_id",
    "client_secret",
    "server_metadata_url",
);


def isAuthConfigured() -> bool:
    authConfig = st.secrets.get("auth", {});
    if not hasattr(authConfig, "get"):
        return False;
    return all(authConfig.get(fieldName) for fieldName in AUTH_REQUIRED_FIELDS);


def isLoggedIn() -> bool:
    if not isAuthConfigured():
        return True;
    return bool(st.user.is_logged_in);


def getCurrentUserId() -> str:
    if not isAuthConfigured():
        return "development-user";
    userId = getattr(st.user, "sub", None) or getattr(st.user, "email", None);
    return str(userId or "authenticated-user");


def getCurrentUserName() -> str:
    if not isAuthConfigured():
        return "개발 사용자";
    userName = getattr(st.user, "name", None) or getattr(st.user, "email", None);
    return str(userName or "사용자");


def requireLogin() -> None:
    if isAuthConfigured() and not isLoggedIn():
        st.switch_page("app.py");
