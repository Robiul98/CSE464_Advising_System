# pages/student_ui.py ────────────────────────────────────────
# Student Dashboard: time-gating, profile, CGPA sim, add/drop
# ─────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import database as db

# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="Student | UniAdvisor", page_icon="🎓", layout="wide")

# ── Auth guard ───────────────────────────────────────────────
if not st.session_state.get("logged_in") or st.session_state.get("role") != "STUDENT":
    st.error("🔒 Access denied. Please log in as a Student.")
    if st.button("Go to Login"):
        st.switch_page("app.py")
    st.stop()

# ── Shared CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #0f1117;
    font-family: 'IBM Plex Sans', sans-serif;
    color: #e2e8f0;
}
[data-testid="stSidebarNav"] { display: none !important; }

h1, h2, h3 { font-family: 'Playfair Display', serif; color: #e8d5a3; }

.stat-card {
    background: #1a1d27;
    border: 1px solid #2e3250;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
}
.stat-label { font-size: .75rem; text-transform: uppercase; letter-spacing: .8px; color: #6b7280; }
.stat-value { font-size: 1.6rem; font-weight: 500; color: #e8d5a3; margin-top: 4px; }

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
    font-size: 1rem;
}

table { width: 100% !important; }
thead th { background: #1a1d27 !important; color: #e8d5a3 !important; }

.stButton > button {
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)

student_id = st.session_state["user_id"]

# ── Sidebar navigation ───────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎓 UniAdvisor")
    st.markdown(f"**{student_id}** — Student")
    st.divider()
    page = st.radio("Navigate", ["📋 Profile", "📅 Registration", "🧮 CGPA Simulator", "📜 My Enrollments"])
    st.divider()
    if st.button("🚪 Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.switch_page("app.py")


# ── Load student data ─────────────────────────────────────────
profile = db.get_student_profile(student_id)
if not profile:
    st.error("Student profile not found in database.")
    st.stop()

credits = int(profile["credits_completed"])


# ══════════════════════════════════════════════════════════════
# PAGE 1: PROFILE
# ══════════════════════════════════════════════════════════════
if page == "📋 Profile":
    st.title("My Profile")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Name</div><div class="stat-value" style="font-size:1.1rem">{profile["name"]}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Department</div><div class="stat-value" style="font-size:1.1rem">{profile["department"]}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><div class="stat-label">CGPA</div><div class="stat-value">{float(profile["cgpa"]):.2f}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Credits Completed</div><div class="stat-value">{credits}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Semester</div><div class="stat-value" style="font-size:1.1rem">Semester {profile["semester"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-card"><div class="stat-label">Email</div><div class="stat-value" style="font-size:1rem">{profile["email"]}</div></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Assigned Advisor</div><div class="stat-value" style="font-size:1rem">{profile.get("advisor_name","N/A")}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-card"><div class="stat-label">Advisor Dept</div><div class="stat-value" style="font-size:1rem">{profile.get("advisor_dept","N/A")}</div></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 2: REGISTRATION  (time-gated)
# ══════════════════════════════════════════════════════════════
elif page == "📅 Registration":
    st.title("Course Registration")

    # ── TASK 5.1: Time Gatekeeper ────────────────────────────
    window_df = db.get_advising_window_for_student(credits)

    if window_df.empty:
        st.markdown('<div class="blocked-banner">⛔ No advising window is configured for your credit level.<br>Please contact the Registrar.</div>', unsafe_allow_html=True)
        st.stop()

    win = window_df.iloc[0]
    now = datetime.now(timezone.utc)

    # Oracle TIMESTAMP comes back as timezone-aware or naive depending on driver
    start = win["start_time"]
    end   = win["end_time"]
    if hasattr(start, "tzinfo") and start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
        end   = end.replace(tzinfo=timezone.utc)

    window_open = start <= now <= end

    st.markdown(
        f'<div class="window-badge">📅 Your registration window: '
        f'{start.strftime("%b %d, %Y %H:%M")} → {end.strftime("%b %d, %Y %H:%M")} UTC &nbsp;|&nbsp; '
        f'{"🟢 OPEN" if window_open else "🔴 CLOSED"}</div>',
        unsafe_allow_html=True,
    )

    if not window_open:
        if now < start:
            st.markdown(f'<div class="blocked-banner">⏳ Registration opens on <strong>{start.strftime("%B %d, %Y at %H:%M UTC")}</strong>.<br>Check back then!</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="blocked-banner">⛔ Your registration window has closed.<br>Contact your advisor if you need changes.</div>', unsafe_allow_html=True)
        st.stop()

    # ── TASK 5.3: Registration Hub ──────────────────────────
    st.subheader("Available Courses")
    st.caption("Only courses with open seats are shown. Lock icon = already enrolled.")

    courses_df     = db.get_all_courses()
    my_enrollments = db.get_student_enrollments(student_id)
    if not my_enrollments.empty:
        latest_enrollments = my_enrollments.drop_duplicates(subset=["course_code"], keep="first")
        enrolled_codes = set(
            latest_enrollments[latest_enrollments["status"] == "ENROLLED"]["course_code"].tolist()
        )
    else:
        enrolled_codes = set()

    if courses_df.empty:
        st.info("No courses available at the moment.")
    else:
        for _, row in courses_df.iterrows():
            code      = row["course_code"]
            is_enrolled = code in enrolled_codes

            with st.container():
                c1, c2, c3, c4, c5 = st.columns([2, 4, 1, 1.5, 1.5])
                c1.markdown(f"**`{code}`**")
                c2.markdown(row["title"])
                c3.markdown(f"{int(row['credits'])} cr")
                c4.markdown(f"🪑 {int(row['available_seats'])} / {int(row['max_seats'])}")

                if is_enrolled:
                    if c5.button("➖ Drop", key=f"drop_{code}", type="secondary"):
                        ok, msg = db.drop_course(student_id, code, student_id)
                        if ok:
                            st.toast(msg, icon="✅")
                        else:
                            st.error(msg)
                        st.rerun()
                else:
                    if int(row['available_seats']) > 0:
                        if c5.button("➕ Add", key=f"add_{code}", type="primary"):
                            ok, msg = db.enroll_student(student_id, code, student_id)
                            if ok:
                                st.toast(msg, icon="✅")
                            else:
                                st.error(msg)
                            st.rerun()
                    else:
                        c5.button("🚫 Full", key=f"full_{code}", disabled=True)
            st.divider()


# ══════════════════════════════════════════════════════════════
# PAGE 3: CGPA SIMULATOR  (TASK 5.2 — pure Python, no DB write)
# ══════════════════════════════════════════════════════════════
elif page == "🧮 CGPA Simulator":
    st.title("CGPA Simulator")
    st.caption("Estimate your CGPA after hypothetical grades — nothing is saved to the database.")

    GRADE_POINTS = {"A+": 4.0, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0,
                    "B-": 2.7, "C+": 2.3, "C": 2.0, "C-": 1.7, "D": 1.0, "F": 0.0}

    current_cgpa    = float(profile["cgpa"])
    current_credits = credits

    st.markdown(f"**Current CGPA:** `{current_cgpa:.2f}` over `{current_credits}` credits")
    st.markdown("---")

    st.subheader("Add Hypothetical Courses")
    num_courses = st.slider("Number of new courses", 1, 5, 3)

    new_entries = []
    for i in range(num_courses):
        cols = st.columns([3, 1, 2])
        with cols[0]:
            cname  = st.text_input(f"Course {i+1} Name", value=f"Course {i+1}", key=f"cname_{i}")
        with cols[1]:
            cr     = st.number_input(f"Credits", min_value=1, max_value=4, value=3, key=f"cr_{i}")
        with cols[2]:
            grade  = st.selectbox("Grade", list(GRADE_POINTS.keys()), key=f"grade_{i}")
        new_entries.append((cname, cr, grade))

    if st.button("Calculate Projected CGPA", type="primary"):
        new_quality_points = sum(GRADE_POINTS[g] * c for _, c, g in new_entries)
        new_credits        = sum(c for _, c, _ in new_entries)

        existing_quality_pts = current_cgpa * current_credits
        total_quality_pts    = existing_quality_pts + new_quality_points
        total_credits        = current_credits + new_credits
        projected_cgpa       = total_quality_pts / total_credits if total_credits > 0 else 0

        delta = projected_cgpa - current_cgpa
        col1, col2, col3 = st.columns(3)
        col1.metric("Projected CGPA", f"{projected_cgpa:.2f}", f"{delta:+.2f}")
        col2.metric("New Credits",    new_credits)
        col3.metric("Total Credits",  total_credits)

        st.markdown("---")
        st.subheader("Breakdown")
        rows = [{"Course": n, "Credits": c, "Grade": g, "Grade Points": GRADE_POINTS[g], "Quality Points": GRADE_POINTS[g]*c}
                for n, c, g in new_entries]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
# PAGE 4: MY ENROLLMENTS
# ══════════════════════════════════════════════════════════════
elif page == "📜 My Enrollments":
    st.title("My Enrollment History")

    enr_df = db.get_student_enrollments(student_id)
    if enr_df.empty:
        st.info("You have no enrollment records yet.")
    else:
        latest = enr_df.drop_duplicates(subset=["course_code"], keep="first")
        active = latest[latest["status"] == "ENROLLED"]
        dropped = enr_df[enr_df["status"] == "DROPPED"]

        st.subheader(f"Currently Enrolled ({len(active)} courses)")
        if not active.empty:
            st.dataframe(
                active[["course_code", "title", "credits", "action_date", "action_by_user_id"]].rename(columns={
                    "course_code": "Code", "title": "Title", "credits": "Cr",
                    "action_date": "Enrolled On", "action_by_user_id": "Registered By"
                }),
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("No active enrollments.")

        st.markdown("---")
        st.subheader(f"Drop History ({len(dropped)} records)")
        if not dropped.empty:
            st.dataframe(
                dropped[["course_code", "title", "action_date", "action_by_user_id"]].rename(columns={
                    "course_code": "Code", "title": "Title",
                    "action_date": "Dropped On", "action_by_user_id": "Dropped By"
                }),
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("No drop history.")
