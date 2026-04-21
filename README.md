# 🎓 Student Advising Portal
### Oracle + Streamlit | Role-Based | Concurrency-Controlled

---

## Project Structure

```
student_advising_portal/
│
├── app.py                  # Login + role-based routing (entry point)
├── database.py             # All Oracle DB logic (queries, transactions, locks)
├── requirements.txt        # Python dependencies
├── generate_hashes.py      # One-time utility: generate bcrypt hashes
├── 1_schema_and_seed.sql   # Oracle DDL + seed INSERT statements
│
└── pages/
    ├── admin_ui.py         # Admin: schedules, freshman onboarding, provenance
    ├── faculty_ui.py       # Faculty: advisees, time-gated override registration
    └── student_ui.py       # Student: profile, CGPA sim, time-gated add/drop
```

---

## Setup Instructions

### Step 1 — Install Python dependencies
```bash
cd student_advising_portal
pip install -r requirements.txt
```

### Step 2 — Generate password hashes
```bash
python generate_hashes.py
```
Copy the printed SQL `INSERT INTO Users ...` lines into `1_schema_and_seed.sql`,
replacing the placeholder hashes already there.

### Step 3 — Run the Oracle SQL script
Open SQLPlus and run:
```sql
@1_schema_and_seed.sql
```
This will:
- Drop any existing tables (safe to re-run)
- Create all 6 tables in the correct FK order
- Insert demo users, faculty, students, courses, and advising schedules

### Step 4 — Configure the DB connection
Open `database.py` and edit the top section:
```python
DB_USER     = "your_oracle_username"
DB_PASSWORD = "your_oracle_password"
DB_DSN      = "localhost:1521/XEPDB1"  # your host:port/service
```

> **Thin mode (no Oracle Client needed):**  
> Comment out `oracledb.init_oracle_client()` and the driver runs in pure-Python thin mode.

### Step 5 — Launch the app
```bash
streamlit run app.py
```

---

## Demo Credentials

| User ID | Password | Role | Details |
|---------|----------|------|---------|
| `admin01` | `admin123` | Admin | Full system access |
| `fac01` | `faculty123` | Faculty | Advisor to stu01, stu02 |
| `fac02` | `faculty123` | Faculty | Advisor to stu03 |
| `stu01` | `student123` | Student | Senior — 90 credits |
| `stu02` | `student123` | Student | Sophomore — 45 credits |
| `stu03` | `student123` | Student | Freshman — **0 credits** |

---

## Feature Checklist

### Admin
- [x] Create / Edit / Delete advising schedule windows
- [x] Force-enroll freshmen (bypasses time check, keeps seat lock)
- [x] Provenance search: full audit trail with actor role badges

### Faculty
- [x] Time-gated access (blocked outside faculty advising window)
- [x] View all advisees and their current enrollments
- [x] Add/Drop courses **for** advisees — Faculty ID logged in provenance

### Student
- [x] Dynamic time gate based on `Credits_Completed`
- [x] Profile page (Name, Dept, CGPA, Advisor, Semester)
- [x] CGPA Simulator — pure Python, no DB writes
- [x] Registration Hub — Add/Drop with live seat counts
- [x] Enrollment history view

### Concurrency Engine
- [x] `SELECT ... FOR UPDATE` row-level lock on Courses row
- [x] Check seats → INSERT Enrollment → UPDATE seats → COMMIT (all atomic)
- [x] If seats = 0 → ROLLBACK → "Course Full" error
- [x] Works correctly even with two simultaneous users

---

## Testing Scenarios (Phase 7 Checklist)

### Provenance Test
1. Log in as `admin01` → Freshman Onboarding → Assign CS101 to `stu03`
2. Log out → Log in as `fac01` → Register for Advisee → Add CS201 for `stu01`
3. Log in as `admin01` → Provenance Search → Search `stu03` and `stu01`
4. ✅ Verify `Action_By_User_ID` shows `admin01` and `fac01` respectively

### Race Condition Test
1. Open Chrome → Log in as `stu01`
2. Open Incognito → Log in as `stu02`
3. Both navigate to Registration → Find `CS401` (1 seat only)
4. Click **Add** simultaneously in both windows
5. ✅ One succeeds, one gets "Course Full" — DB shows `Available_Seats = 0`

---

## Architecture Notes

**Why `SELECT ... FOR UPDATE`?**  
Oracle's `FOR UPDATE` places an exclusive row-level lock. The second transaction
trying to lock the same row will wait (not corrupt). This is more reliable than
application-level checks, which have a TOCTOU race condition.

**Provenance Design**  
`Enrollment.Action_By_User_ID` is a FK to `Users`. This means every row has a
verified actor — you can't insert a fake user ID. The `JOIN` in `get_provenance()`
surfaces the actor's role (ADMIN / FACULTY / STUDENT) automatically.

**Session State Auth**  
Streamlit's `st.session_state` stores `logged_in`, `user_id`, and `role`.
Every page starts with a guard checking `role` and `logged_in`.
The sidebar nav is hidden via CSS so users cannot navigate to unauthorized pages.
# CSE464_Advising_System
