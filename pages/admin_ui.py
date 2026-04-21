# pages/admin_ui.py ──────────────────────────────────────────
# Admin Dashboard: schedule management, freshman onboarding, provenance search
# ─────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import database as db

# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="Admin | UniAdvisor", page_icon="🎓", layout="wide")

# ── Auth guard ───────────────────────────────────────────────
if not st.session_state.get("logged_in") or st.session_state.get("role") != "ADMIN":
    st.error("🔒 Access denied. Please log in as Admin.")
    if st.button("Go to Login"):
        st.switch_page("app.py")
    st.stop()

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #120a1f;
    font-family: 'IBM Plex Sans', sans-serif;
    color: #e2e8f0;
}
[data-testid="stSidebarNav"] { display: none !important; }

h1, h2, h3 { font-family: 'Playfair Display', serif; color: #c4a6f5; }

.stat-card {
    background: #1a1027;
    border: 1px solid #3b2060;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 12px;
}
.stat-label { font-size: .75rem; text-transform: uppercase; letter-spacing: .8px; color: #6b7280; }
.stat-value { font-size: 1.4rem; font-weight: 500; color: #c4a6f5; margin-top: 4px; }

.provenance-row {
    background: #1a1027;
    border-left: 3px solid #c4a6f5;
    border-radius: 4px;
    padding: 10px 16px;
    margin-bottom: 6px;
    font-size: .88rem;
}

.badge-admin   { background: #3b1f6e; color: #c4a6f5; padding: 2px 8px; border-radius: 99px; font-size:.75rem; }
.badge-faculty { background: #14363a; color: #5ee7d0; padding: 2px 8px; border-radius: 99px; font-size:.75rem; }
.badge-student { background: #1f2f4a; color: #7eb8f7; padding: 2px 8px; border-radius: 99px; font-size:.75rem; }

.stButton > button {
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
}

.schedule-card {
    background: #1a1027;
    border: 1px solid #3b2060;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
}

.freshman-card {
    background: #1a1027;
    border: 1px solid #3b2060;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

admin_id = st.session_state["user_id"]

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎓 UniAdvisor")
    st.markdown(f"**{admin_id}** — Administrator")
    st.divider()
    page = st.radio("Navigate", [
        "🏠 Overview",
        "📅 Schedule Management",
        "🎓 Freshman Onboarding",
        "🔍 Provenance Search",
        "📊 All Students",
    ])
    st.divider()
    if st.button("🚪 Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.switch_page("app.py")


# ══════════════════════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ══════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("Admin Dashboard")

    students_df  = db.get_all_students_summary()
    schedules_df = db.get_all_schedules()
    courses_df   = db.get_all_courses()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Total Students</div><div class="stat-value">{len(students_df)}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Total Courses</div><div class="stat-value">{len(courses_df)}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Active Schedules</div><div class="stat-value">{len(schedules_df)}</div></div>', unsafe_allow_html=True)
    with col4:
        freshmen_count = len(students_df[students_df["credits_completed"] == 0]) if not students_df.empty else 0
        st.markdown(f'<div class="stat-card"><div class="stat-label">Freshmen (0 cr)</div><div class="stat-value">{freshmen_count}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Current Advising Schedules")
    if schedules_df.empty:
        st.info("No schedules configured.")
    else:
        now = datetime.now(timezone.utc)
        for _, s in schedules_df.iterrows():
            start = s["start_time"]
            end   = s["end_time"]
            if hasattr(start, "tzinfo") and start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
                end   = end.replace(tzinfo=timezone.utc)
            active = start <= now <= end
            status = "🟢 ACTIVE" if active else "🔴 INACTIVE"
            role_badge = "STUDENT" if s["target_role"] == "STUDENT" else "FACULTY"
            cr_range = f"{int(s['min_credits'])}–{int(s['max_credits'])} cr"
            st.markdown(
                f'<div class="schedule-card">'
                f'<strong>{s["label"]}</strong> &nbsp; <span class="badge-{role_badge.lower()}">{role_badge}</span> &nbsp; {status}<br>'
                f'<small>{start.strftime("%b %d %H:%M")} → {end.strftime("%b %d %H:%M")} UTC &nbsp;|&nbsp; Credits: {cr_range}</small>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════════
# PAGE 2: SCHEDULE MANAGEMENT  (TASK 4.1)
# ══════════════════════════════════════════════════════════════
elif page == "📅 Schedule Management":
    st.title("Schedule Management")
    st.caption("Create, edit, or delete the time windows that control when students and faculty can register.")

    schedules_df = db.get_all_schedules()

    # ── Create new schedule ───────────────────────────────────
    with st.expander("➕ Create New Schedule Window", expanded=False):
        with st.form("create_schedule"):
            col1, col2 = st.columns(2)
            with col1:
                target_role  = st.selectbox("Target Role", ["STUDENT", "FACULTY"])
                label        = st.text_input("Label", placeholder="e.g. Senior Registration Window")
            with col2:
                min_credits  = st.number_input("Min Credits", min_value=0, max_value=9999, value=0)
                max_credits  = st.number_input("Max Credits", min_value=0, max_value=9999, value=9999)

            col3, col4 = st.columns(2)
            with col3:
                start_date = st.date_input("Start Date", value=datetime.now().date())
                start_time = st.time_input("Start Time", value=datetime.now().replace(hour=0, minute=0).time())
            with col4:
                end_date   = st.date_input("End Date", value=(datetime.now() + timedelta(days=7)).date())
                end_time   = st.time_input("End Time", value=datetime.now().replace(hour=23, minute=59).time())

            submitted = st.form_submit_button("Create Schedule", type="primary")
            if submitted:
                start_dt = datetime.combine(start_date, start_time)
                end_dt   = datetime.combine(end_date, end_time)
                if start_dt >= end_dt:
                    st.error("Start time must be before end time.")
                elif not label:
                    st.error("Please provide a label.")
                else:
                    db.create_schedule(target_role, min_credits, max_credits, start_dt, end_dt, label)
                    st.success("✅ Schedule created!")
                    st.rerun()

    # ── Existing schedules ────────────────────────────────────
    st.markdown("---")
    st.subheader("Existing Schedules")

    if schedules_df.empty:
        st.info("No schedules yet.")
    else:
        for _, s in schedules_df.iterrows():
            sid = int(s["schedule_id"])
            with st.expander(f"📅 {s['label']}  ({s['target_role']}, cr {int(s['min_credits'])}–{int(s['max_credits'])})"):
                with st.form(f"edit_{sid}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        new_label = st.text_input("Label", value=str(s["label"]))
                        new_start = st.date_input("Start Date", value=s["start_time"].date() if hasattr(s["start_time"], "date") else datetime.now().date(), key=f"sd_{sid}")
                        new_start_t = st.time_input("Start Time", value=s["start_time"].time() if hasattr(s["start_time"], "time") else datetime.now().time(), key=f"st_{sid}")
                    with c2:
                        new_end   = st.date_input("End Date",   value=s["end_time"].date()   if hasattr(s["end_time"],   "date") else datetime.now().date(), key=f"ed_{sid}")
                        new_end_t = st.time_input("End Time",   value=s["end_time"].time()   if hasattr(s["end_time"],   "time") else datetime.now().time(), key=f"et_{sid}")

                    col_save, col_del, _ = st.columns([1, 1, 4])
                    save_btn   = col_save.form_submit_button("💾 Save", type="primary")
                    delete_btn = col_del.form_submit_button("🗑️ Delete", type="secondary")

                    if save_btn:
                        start_dt = datetime.combine(new_start, new_start_t)
                        end_dt   = datetime.combine(new_end, new_end_t)
                        db.update_schedule(sid, start_dt, end_dt, new_label)
                        st.success("✅ Updated!")
                        st.rerun()

                    if delete_btn:
                        db.delete_schedule(sid)
                        st.success("🗑️ Deleted.")
                        st.rerun()


# ══════════════════════════════════════════════════════════════
# PAGE 3: FRESHMAN ONBOARDING  (TASK 4.2)
# ══════════════════════════════════════════════════════════════
elif page == "🎓 Freshman Onboarding":
    st.title("Freshman Onboarding")
    st.caption("Force-enroll 0-credit students into foundational courses. **Bypasses time lock.** Still uses row-level locking for seat integrity.")

    freshmen_df = db.get_freshmen()
    courses_df  = db.get_all_courses()

    if freshmen_df.empty:
        st.info("No students with 0 credits in the system.")
    else:
        course_options = {f"{r['course_code']} — {r['title']} ({int(r['available_seats'])} seats)": r["course_code"]
                         for _, r in courses_df.iterrows()}

        for _, stu in freshmen_df.iterrows():
            sid = stu["student_id"]

            with st.container():
                st.markdown(f'<div class="freshman-card">', unsafe_allow_html=True)

                c1, c2, c3 = st.columns([2, 3, 2])
                c1.markdown(f"**{stu['name']}**  \n`{sid}`")
                c2.markdown(f"Dept: {stu['department']} | Sem: {int(stu['semester'])}")

                # Get courses this student is NOT already enrolled in
                enr_df      = db.get_student_enrollments(sid)
                if not enr_df.empty:
                    latest = enr_df.drop_duplicates(subset=["course_code"], keep="first")
                    enrolled_codes = set(latest[latest["status"]=="ENROLLED"]["course_code"].tolist())
                else:
                    enrolled_codes = set()
                available_opts = {k: v for k, v in course_options.items() if v not in enrolled_codes}

                if not available_opts:
                    c3.caption("All courses assigned.")
                else:
                    chosen_label = c3.selectbox("Assign Course", list(available_opts.keys()), key=f"fresh_sel_{sid}")
                    chosen_code  = available_opts[chosen_label]

                    if c3.button("✅ Assign", key=f"fresh_btn_{sid}", type="primary"):
                        # TASK 4.2: Bypass time check, but still use SELECT FOR UPDATE
                        ok, msg = db.enroll_student(sid, chosen_code, admin_id)
                        if ok:
                            st.success(f"{stu['name']}: {msg}  *(Admin ID {admin_id} logged)*")
                        else:
                            st.error(f"{stu['name']}: {msg}")
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

                # Show current enrollments
                if not enr_df.empty:
                    latest_all = enr_df.drop_duplicates(subset=["course_code"], keep="first")
                    active = latest_all[latest_all["status"]=="ENROLLED"]
                    if not active.empty:
                        with st.expander(f"View {stu['name']}'s current courses"):
                            st.dataframe(
                            active[["course_code","title","action_date","action_by_user_id"]].rename(columns={
                                "course_code":"Code","title":"Title",
                                "action_date":"Enrolled On","action_by_user_id":"By"
                            }),
                            use_container_width=True, hide_index=True,
                        )


# ══════════════════════════════════════════════════════════════
# PAGE 4: PROVENANCE SEARCH  (TASK 4.3)
# ══════════════════════════════════════════════════════════════
elif page == "🔍 Provenance Search":
    st.title("Provenance Search")
    st.caption("Full audit trail: every enrollment action, exactly who performed it, and when.")

    students_df = db.get_all_students_summary()

    col_input, col_btn = st.columns([3, 1])
    with col_input:
        search_id = st.text_input("Enter Student ID", placeholder="e.g. stu01")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("🔍 Search", type="primary")

    # Quick-select from all students
    with st.expander("Or select from all students"):
        all_ids = students_df["student_id"].tolist() if not students_df.empty else []
        quick_sel = st.selectbox("Select Student", [""] + all_ids)
        if quick_sel:
            search_id = quick_sel

    if search_id or search_btn:
        sid = (search_id or "").strip()
        if not sid:
            st.warning("Please enter a Student ID.")
        else:
            prov_df = db.get_provenance(sid)

            if prov_df.empty:
                st.info(f"No enrollment records found for **{sid}**.")
            else:
                stu_name = prov_df.iloc[0]["student_name"]
                st.subheader(f"📋 Audit Trail for {stu_name} ({sid})")
                st.caption(f"{len(prov_df)} total action(s) recorded")

                # Role badge helper
                def role_badge(role):
                    css = {"ADMIN": "badge-admin", "FACULTY": "badge-faculty", "STUDENT": "badge-student"}
                    return f'<span class="{css.get(role,"badge-student")}">{role}</span>'

                for _, row in prov_df.iterrows():
                    status_icon = "✅" if row["status"] == "ENROLLED" else "❌"
                    st.markdown(
                        f'<div class="provenance-row">'
                        f'{status_icon} <strong>{row["status"]}</strong> — '
                        f'<code>{row["course_code"]}</code> {row["course_title"]}<br>'
                        f'<small>🕐 {row["action_date"]}  &nbsp;|&nbsp;  '
                        f'Actor: <code>{row["action_by_user_id"]}</code> {role_badge(str(row["actor_role"]))}</small>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                st.markdown("---")
                st.subheader("Raw Table View")
                st.dataframe(
                    prov_df.rename(columns={
                        "enrollment_id":"ID","student_id":"Student","student_name":"Name",
                        "course_code":"Code","course_title":"Course","status":"Status",
                        "action_date":"Action Date","action_by_user_id":"Actor ID","actor_role":"Actor Role"
                    }),
                    use_container_width=True, hide_index=True,
                )


# ══════════════════════════════════════════════════════════════
# PAGE 5: ALL STUDENTS
# ══════════════════════════════════════════════════════════════
elif page == "📊 All Students":
    st.title("All Students")

    students_df = db.get_all_students_summary()
    if students_df.empty:
        st.info("No students in the database.")
    else:
        # Filter controls
        col1, col2 = st.columns(2)
        with col1:
            dept_filter = st.multiselect("Filter by Department",
                                         options=sorted(students_df["department"].unique().tolist()))
        with col2:
            cr_min, cr_max = int(students_df["credits_completed"].min()), int(students_df["credits_completed"].max())
            cr_range = st.slider("Credits Completed Range", cr_min, cr_max, (cr_min, cr_max))

        filtered = students_df.copy()
        if dept_filter:
            filtered = filtered[filtered["department"].isin(dept_filter)]
        filtered = filtered[
            (filtered["credits_completed"] >= cr_range[0]) &
            (filtered["credits_completed"] <= cr_range[1])
        ]

        st.caption(f"Showing {len(filtered)} of {len(students_df)} students")
        st.dataframe(
            filtered.rename(columns={
                "student_id":"ID","name":"Name","department":"Dept",
                "semester":"Sem","cgpa":"CGPA","credits_completed":"Credits",
                "advisor_id":"Advisor ID","advisor_name":"Advisor"
            }),
            use_container_width=True, hide_index=True,
        )
