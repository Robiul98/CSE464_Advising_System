# app.py  ─────────────────────────────────────────────────────
# Main entry point for the Student Advising Portal.
# Handles login, session state, and role-based page routing.
# ─────────────────────────────────────────────────────────────

import streamlit as st
import bcrypt
from database import get_user

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="UniAdvisor Portal",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS (clean academic aesthetic) ────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0f1117;
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Kill default sidebar nav so users can't bypass role routing */
[data-testid="stSidebarNav"] { display: none !important; }

.login-card {
    max-width: 440px;
    margin: 80px auto 0;
    background: #1a1d27;
    border: 1px solid #2e3250;
    border-radius: 16px;
    padding: 48px 40px 40px;
    box-shadow: 0 24px 80px rgba(0,0,0,.6);
}

.login-logo {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #e8d5a3;
    text-align: center;
    margin-bottom: 4px;
    letter-spacing: -0.5px;
}

.login-sub {
    text-align: center;
    color: #6b7280;
    font-size: .85rem;
    font-weight: 300;
    margin-bottom: 36px;
    letter-spacing: .6px;
    text-transform: uppercase;
}

/* Streamlit form inputs */
[data-testid="stTextInput"] input {
    background: #0f1117 !important;
    border: 1px solid #2e3250 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

[data-testid="stTextInput"] input:focus {
    border-color: #e8d5a3 !important;
    box-shadow: 0 0 0 2px rgba(232,213,163,.15) !important;
}

/* Primary button */
.stButton > button[kind="primary"], .stButton > button {
    background: #e8d5a3 !important;
    color: #0f1117 !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    border: none !important;
    width: 100% !important;
    padding: 0.65rem !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    letter-spacing: .3px;
    transition: opacity .2s;
}

.stButton > button:hover { opacity: .85 !important; }

.role-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: .75rem;
    font-weight: 500;
    letter-spacing: .4px;
    text-transform: uppercase;
}
.badge-admin   { background: #3b1f6e; color: #c4a6f5; }
.badge-faculty { background: #14363a; color: #5ee7d0; }
.badge-student { background: #1f2f4a; color: #7eb8f7; }
</style>
""", unsafe_allow_html=True)


# ── Session state defaults ───────────────────────────────────
def _init_state():
    defaults = {
        "logged_in":   False,
        "user_id":     None,
        "role":        None,
        "login_error": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()


# ── If already logged in → redirect immediately ──────────────
def _redirect():
    role = st.session_state["role"]
    if role == "ADMIN":
        st.switch_page("pages/admin_ui.py")
    elif role == "FACULTY":
        st.switch_page("pages/faculty_ui.py")
    elif role == "STUDENT":
        st.switch_page("pages/student_ui.py")


if st.session_state["logged_in"]:
    _redirect()


# ── Login form ───────────────────────────────────────────────
st.markdown('<div class="login-card">', unsafe_allow_html=True)
st.markdown('<div class="login-logo">🎓 UniAdvisor</div>', unsafe_allow_html=True)
st.markdown('<div class="login-sub">Student Advising Portal</div>', unsafe_allow_html=True)

with st.form("login_form"):
    user_id  = st.text_input("User ID", placeholder="e.g. stu01 / fac01 / admin01")
    password = st.text_input("Password", type="password", placeholder="••••••••")
    submitted = st.form_submit_button("Sign In", use_container_width=True)

if submitted:
    if not user_id or not password:
        st.error("Please enter both User ID and Password.")
    else:
        user = get_user(user_id.strip())
        if user is None:
            st.error("❌ User ID not found.")
        else:
            pw_bytes   = password.encode("utf-8")
            hash_bytes = user["password_hash"].encode("utf-8")
            if bcrypt.checkpw(pw_bytes, hash_bytes):
                st.session_state["logged_in"] = True
                st.session_state["user_id"]   = user["user_id"]
                st.session_state["role"]      = user["role"]
                st.rerun()
            else:
                st.error("❌ Incorrect password.")

st.markdown("</div>", unsafe_allow_html=True)

# ── Demo credentials helper ──────────────────────────────────
with st.expander("Demo credentials"):
    st.markdown("""
| User ID | Password | Role |
|---------|----------|------|
| `admin01` | `admin123` | Admin |
| `fac01` | `faculty123` | Faculty |
| `fac02` | `faculty123` | Faculty |
| `stu01` | `student123` | Student (Senior, 90 cr) |
| `stu02` | `student123` | Student (Sophomore, 45 cr) |
| `stu03` | `student123` | Student (Freshman, 0 cr) |
""")
