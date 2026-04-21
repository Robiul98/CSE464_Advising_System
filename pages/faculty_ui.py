# pages/faculty_ui.py ────────────────────────────────────────
# Faculty Dashboard: time-gating, advisee management, override registration
# ─────────────────────────────────────────────────────────────

import streamlit as st
from datetime import datetime, timezone
import database as db

# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="Faculty | UniAdvisor", page_icon="🎓", layout="wide")

# ── Auth guard ───────────────────────────────────────────────
if not st.session_state.get("logged_in") or st.session_state.get("role") != "FACULTY":
    st.error("🔒 Access denied. Please log in as Faculty.")
    if st.button("Go to Login"):
        st.switch_page("app.py")
    st.stop()

# ── Shared CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #0d1a14;
    font-family: 'IBM Plex Sans', sans-serif;
    color: #e2e8f0;
}
[data-testid="stSidebarNav"] { display: none !important; }

h1, h2, h3 { font-family: 'Playfair Display', serif; color: #5ee7d0; }

.stat-card {
    background: #0f2419;
    border: 1px solid #1e4030;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 12px;
}
.stat-label { font-size: .75rem; text-transform: uppercase; letter-spacing: .8px; color: #6b7280; }
.stat-value { font-size: 1.4rem; font-weight: 500; color: #5ee7d0; margin-top: 4px; }

.window-badge {
    background: #14363a;
    color: #5ee7d0;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: .85rem;
    font-weight: 500;
    display: inline-block;
    margin-bottom: 20px;
}
.blocked-banner {
    background: #3b1414;
    border: 1px solid #7f1d1d;
    color: #fca5a5;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
}
.advisee-card {
    background: #0f2419;
    border: 1px solid #1e4030;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 8px;
}
.stButton > button {
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)

faculty_id = st.session_state["user_id"]


# ── TASK 6.1: Faculty Time Gatekeeper ───────────────────────
def check_faculty_window():
    window_df = db.get_faculty_advising_window()
    if window_df.empty:
        return False, None, None

    win   = window_df.iloc[0]
    now   = datetime.now(timezone.utc)
    start = win["start_time"]
    end   = win["end_time"]
    if hasattr(start, "tzinfo") and start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
        end   = end.replace(tzinfo=timezone.utc)

    return start <= now <= end, start, end


# ── Sidebar ──────────────────────────────────────────────────
profile = db.get_faculty_profile(faculty_id)

with st.sidebar:
    st.markdown("### 🎓 UniAdvisor")
    if profile:
        st.markdown(f"**{profile['name']}**")
        st.caption(f"{profile['department']} — Faculty")
    st.divider()
    page = st.radio("Navigate", ["🏠 Dashboard", "👥 My Advisees", "📝 Register for Advisee"])
    st.divider()
    if st.button("🚪 Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.switch_page("app.py")


# ══════════════════════════════════════════════════════════════
# PAGE 1: DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.title("Faculty Dashboard")

    window_open, start, end = check_faculty_window()

    if start and end:
        st.markdown(
            f'<div class="window-badge">📅 Faculty Advising Window: '
            f'{start.strftime("%b %d %H:%M")} → {end.strftime("%b %d %H:%M")} UTC &nbsp;|&nbsp; '
            f'{"🟢 OPEN" if window_open else "🔴 CLOSED"}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.warning("⚠️ No faculty advising window configured by Admin.")

    if not window_open:
        st.markdown('<div class="blocked-banner">⛔ The Faculty Advising Window is currently <strong>closed</strong>.<br>You cannot add or drop courses for advisees at this time.</div>', unsafe_allow_html=True)

    st.markdown("---")

    if profile:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="stat-card"><div class="stat-label">Name</div><div class="stat-value" style="font-size:1.1rem">{profile["name"]}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><div class="stat-label">Department</div><div class="stat-value" style="font-size:1.1rem">{profile["department"]}</div></div>', unsafe_allow_html=True)

    advisees_df = db.get_advisees(faculty_id)
    st.markdown(f'<div class="stat-card"><div class="stat-label">Total Advisees</div><div class="stat-value">{len(advisees_df)}</div></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 2: MY ADVISEES
# ══════════════════════════════════════════════════════════════
elif page == "👥 My Advisees":
    st.title("My Advisees")

    advisees_df = db.get_advisees(faculty_id)
    if advisees_df.empty:
        st.info("You have no assigned advisees.")
    else:
        for _, adv in advisees_df.iterrows():
            with st.expander(f"👤 {adv['name']}  ({adv['student_id']})  —  {adv['department']}"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("CGPA",     f"{float(adv['cgpa']):.2f}")
                c2.metric("Credits",  int(adv["credits_completed"]))
                c3.metric("Semester", int(adv["semester"]))
                c4.metric("Email",    adv["email"])

                st.markdown("**Current Enrollments**")
                enr = db.get_student_enrollments(adv["student_id"])
                if enr.empty:
                    st.caption("No enrollment records.")
                else:
                    latest = enr.drop_duplicates(subset=["course_code"], keep="first")
                    active = latest[latest["status"] == "ENROLLED"]
                    if active.empty:
                        st.caption("Not currently enrolled in any course.")
                    else:
                        st.dataframe(
                            active[["course_code", "title", "credits", "action_date"]].rename(columns={
                                "course_code": "Code", "title": "Title",
                                "credits": "Cr", "action_date": "Enrolled On"
                            }),
                            use_container_width=True, hide_index=True,
                        )


# ══════════════════════════════════════════════════════════════
# PAGE 3: OVERRIDE REGISTRATION  (TASK 6.3)
# ══════════════════════════════════════════════════════════════
elif page == "📝 Register for Advisee":
    st.title("Override Registration")
    st.caption("Add or drop courses on behalf of your advisees. Your Faculty ID is recorded in all provenance logs.")

    # ── TASK 6.1: Gate this page ──────────────────────────────
    window_open, start, end = check_faculty_window()

    if not window_open:
        if start:
            st.markdown(f'<div class="blocked-banner">⛔ Faculty advising window is <strong>closed</strong>.<br>It runs {start.strftime("%b %d %H:%M")} → {end.strftime("%b %d %H:%M")} UTC.<br>Come back then to manage registrations.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="blocked-banner">⛔ No faculty advising window configured by Admin.</div>', unsafe_allow_html=True)
        st.stop()

    # ── TASK 6.2: Select advisee ──────────────────────────────
    advisees_df = db.get_advisees(faculty_id)
    if advisees_df.empty:
        st.warning("You have no assigned advisees.")
        st.stop()

    advisee_options = {f"{r['name']} ({r['student_id']})": r["student_id"] for _, r in advisees_df.iterrows()}
    selected_label  = st.selectbox("Select Advisee", list(advisee_options.keys()))
    selected_sid    = advisee_options[selected_label]

    # Show current enrollments of selected advisee
    st.markdown("---")
    enr_df = db.get_student_enrollments(selected_sid)
    if not enr_df.empty:
        latest_enr = enr_df.drop_duplicates(subset=["course_code"], keep="first")
        active_enr = latest_enr[latest_enr["status"] == "ENROLLED"]
        enrolled_codes = set(active_enr["course_code"].tolist())
    else:
        active_enr = enr_df
        enrolled_codes = set()

    st.subheader(f"📋 {selected_label.split('(')[0].strip()}'s Current Enrollments")
    if active_enr.empty:
        st.caption("Not enrolled in any courses yet.")
    else:
        st.dataframe(
            active_enr[["course_code","title","credits","action_date","action_by_user_id"]].rename(columns={
                "course_code":"Code","title":"Title","credits":"Cr",
                "action_date":"Enrolled On","action_by_user_id":"Registered By"
            }),
            use_container_width=True, hide_index=True,
        )

    # ── Course action table ───────────────────────────────────
    st.markdown("---")
    st.subheader("Available Courses")
    st.caption("🔑 Faculty ID will be recorded in Action_By_User_ID for all actions below.")

    courses_df = db.get_all_courses()
    if courses_df.empty:
        st.info("No courses available.")
    else:
        for _, row in courses_df.iterrows():
            code        = row["course_code"]
            is_enrolled = code in enrolled_codes

            with st.container():
                c1, c2, c3, c4, c5 = st.columns([2, 4, 1, 1.5, 1.5])
                c1.markdown(f"**`{code}`**")
                c2.markdown(row["title"])
                c3.markdown(f"{int(row['credits'])} cr")
                c4.markdown(f"🪑 {int(row['available_seats'])} / {int(row['max_seats'])}")

                if is_enrolled:
                    # Drop — actor_id = faculty_id (provenance!)
                    if c5.button("➖ Drop", key=f"fac_drop_{code}_{selected_sid}", type="secondary"):
                        ok, msg = db.drop_course(selected_sid, code, faculty_id)
                        if ok:
                            st.toast(f"{msg} (Logged as: {faculty_id})", icon="✅")
                        else:
                            st.error(msg)
                        st.rerun()
                else:
                    if int(row['available_seats']) > 0:
                        # Add — actor_id = faculty_id (provenance!)
                        if c5.button("➕ Add", key=f"fac_add_{code}_{selected_sid}", type="primary"):
                            ok, msg = db.enroll_student(selected_sid, code, faculty_id)
                            if ok:
                                st.toast(f"{msg} (Logged as: {faculty_id})", icon="✅")
                            else:
                                st.error(msg)
                            st.rerun()
                    else:
                        c5.button("🚫 Full", key=f"fac_full_{code}_{selected_sid}", disabled=True)
            st.divider()
