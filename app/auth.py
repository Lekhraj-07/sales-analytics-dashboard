"""Simple session-based auth gate for Streamlit."""
import streamlit as st


def login_gate(cfg_auth: dict) -> bool:
    """Return True if authenticated. Renders login form otherwise."""
    if not cfg_auth.get("enabled", False):
        return True
    if st.session_state.get("authed"):
        return True

    st.title("🔐 Sign in")
    st.caption("Demo credentials shown below for portfolio reviewers.")
    with st.form("login"):
        u = st.text_input("Username", value="")
        p = st.text_input("Password", type="password", value="")
        submitted = st.form_submit_button("Sign in", type="primary")
    st.info(f"Demo username: `{cfg_auth['username']}` · password: `{cfg_auth['password']}`")
    if submitted:
        if u == cfg_auth["username"] and p == cfg_auth["password"]:
            st.session_state["authed"] = True
            st.rerun()
        else:
            st.error("Invalid credentials.")
    return False


def logout_button() -> None:
    if st.sidebar.button("Sign out"):
        st.session_state.pop("authed", None)
        st.rerun()
