# # database.py
# # ─────────────────────────────────────────────────────────────
# # Oracle DB bridge for the Student Advising Portal.
# # Uses positional bind variables (:1, :2 ...) throughout to
# # avoid ORA-01745 reserved-word conflicts in thin mode.
# # ─────────────────────────────────────────────────────────────

# import oracledb
# oracledb.defaults.fetch_lobs = False

# import pandas as pd
# import streamlit as st
# from contextlib import contextmanager

# # ── Connection config ────────────────────────────────────────
# DB_USER = "system"
# DB_PASS = "system"
# DB_DSN  = "localhost:1521/XE"

# # oracledb.init_oracle_client()   ← keep commented out (thin mode)


# database.py
# ─────────────────────────────────────────────────────────────
# Oracle DB bridge for the Student Advising Portal.
# Uses positional bind variables (:1, :2 ...) throughout to
# avoid ORA-01745 reserved-word conflicts in thin mode.
# ─────────────────────────────────────────────────────────────

# import oracledb
# # oracledb.defaults.fetch_lobs = False

# import os
# from dotenv import load_dotenv
# import pandas as pd
# import streamlit as st
# from contextlib import contextmanager

# # Load environment variables from the .env file
# load_dotenv()

# # ── Connection config ────────────────────────────────────────
# # Securely fetch credentials from the environment
# DB_USER = os.getenv("FREESQL_USER")
# DB_PASS = os.getenv("FREESQL_PASS")

# # Reconstruct the DSN format provided by FreeSQL
# DB_HOST = os.getenv("FREESQL_HOST", "db.freesql.com")
# DB_PORT = os.getenv("FREESQL_PORT", "1521")
# DB_SERVICE = os.getenv("FREESQL_SERVICE", "23ai_mb9q7")

# DB_DSN  = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"

# oracledb.init_oracle_client()  # ← keep commented out (thin mode)

import oracledb
import os
import urllib.request
import zipfile
import pandas as pd
import streamlit as st
from contextlib import contextmanager
from dotenv import load_dotenv
import platform
import shutil
import sys

oracledb.defaults.fetch_lobs = False
load_dotenv()

# ── Environment Variables ────────────────────────────────────
DB_USER = os.getenv("FREESQL_USER")
DB_PASS = os.getenv("FREESQL_PASS")
DB_HOST = os.getenv("FREESQL_HOST", "db.freesql.com")
DB_PORT = os.getenv("FREESQL_PORT", "1521")
DB_SERVICE = os.getenv("FREESQL_SERVICE", "23ai_mb9q7")
DB_DSN  = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"

# ── Oracle Instant Client Auto-Installer for Streamlit ───────
# def setup_oracle_client():
#     # Define where the folder will live in Streamlit Cloud
#     client_dir = os.path.join(os.getcwd(), "instantclient_21_13")
    
#     # If the folder doesn't exist, download and unzip it
#     if not os.path.exists(client_dir):
#         with st.spinner("Downloading Oracle Client dependencies (first run only)..."):
#             # Official Oracle URL for Linux Basic Lite client
#             url = "https://download.oracle.com/otn_software/linux/instantclient/2113000/instantclient-basiclite-linux.x64-21.13.0.0.0dbru.zip"
#             zip_path = "instantclient.zip"
            
#             # Download the zip file
#             urllib.request.urlretrieve(url, zip_path)
            
#             # Extract the zip file
#             with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#                 zip_ref.extractall(os.getcwd())
                
#             # Clean up the zip file to save space
#             os.remove(zip_path)
            
#     # Initialize Thick mode using the downloaded folder
#     try:
#         oracledb.init_oracle_client(lib_dir=client_dir)
#     except oracledb.ProgrammingError:
#         # Catch the error if init_oracle_client has already been called
#         pass

# def setup_oracle_client():
#     system = platform.system() 
#     client_dir = os.path.join(os.getcwd(), "instantclient_21_13")
    
#     # If the folder doesn't exist, download the correct version for the OS
#     if not os.path.exists(client_dir):
        
#         if system == "Linux":
#             url = "https://download.oracle.com/otn_software/linux/instantclient/2113000/instantclient-basiclite-linux.x64-21.13.0.0.0dbru.zip"
#         elif system == "Windows":
#             url = "https://download.oracle.com/otn_software/nt/instantclient/2113000/instantclient-basiclite-windows.x64-21.13.0.0.0dbru.zip"
#         elif system == "Darwin":
#             url = "https://download.oracle.com/otn_software/mac/instantclient/2113000/instantclient-basiclite-macos.x64-21.13.0.0.0dbru.zip"
#         else:
#             st.error(f"Unsupported Operating System: {system}")
#             return
            
#         with st.spinner(f"Downloading Oracle Client for {system} (first run only)..."):
#             zip_path = "instantclient.zip"
            
#             urllib.request.urlretrieve(url, zip_path)
#             with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#                 zip_ref.extractall(os.getcwd())
#             os.remove(zip_path)
            
#         # --- THE LINUX SYMLINK FIX ---
#         if system == "Linux":
#             so_file = os.path.join(client_dir, "libclntsh.so")
#             target_file = os.path.join(client_dir, "libclntsh.so.21.1")
            
#             # If the shortcut file is tiny (broken by zipfile), replace it with the real file
#             if os.path.exists(so_file) and os.path.getsize(so_file) < 100:
#                 os.remove(so_file)
#                 shutil.copy(target_file, so_file)
#             # -----------------------------
            
#     # Initialize Thick mode
#     try:
#         oracledb.init_oracle_client(lib_dir=client_dir)
#     except oracledb.ProgrammingError:
#         pass

# def setup_oracle_client():
#     system = platform.system() 
#     client_dir = os.path.join(os.getcwd(), "instantclient_21_13")
    
#     # 1. Download if missing
#     if not os.path.exists(client_dir):
#         if system == "Linux":
#             url = "https://download.oracle.com/otn_software/linux/instantclient/2113000/instantclient-basiclite-linux.x64-21.13.0.0.0dbru.zip"
#         elif system == "Windows":
#             url = "https://download.oracle.com/otn_software/nt/instantclient/2113000/instantclient-basiclite-windows.x64-21.13.0.0.0dbru.zip"
#         elif system == "Darwin":
#             url = "https://download.oracle.com/otn_software/mac/instantclient/2113000/instantclient-basiclite-macos.x64-21.13.0.0.0dbru.zip"
#         else:
#             st.error(f"Unsupported Operating System: {system}")
#             return
            
#         with st.spinner(f"Downloading Oracle Client for {system} (first run only)..."):
#             zip_path = "instantclient.zip"
#             urllib.request.urlretrieve(url, zip_path)
#             with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#                 zip_ref.extractall(os.getcwd())
#             os.remove(zip_path)
            
#     # 2. --- THE BULLETPROOF LINUX SYMLINK FIX ---
#     # We run this every time, just in case a file is still broken
#     if system == "Linux" and os.path.exists(client_dir):
#         for filename in os.listdir(client_dir):
#             filepath = os.path.join(client_dir, filename)
            
#             # If a file is tiny (< 50 bytes), Python likely extracted a shortcut as plain text
#             if os.path.isfile(filepath) and os.path.getsize(filepath) < 50:
#                 try:
#                     # Read the text inside (it usually contains the name of the real file)
#                     with open(filepath, 'r') as f:
#                         target_name = f.read().strip()
                    
#                     target_path = os.path.join(client_dir, target_name)
                    
#                     # If the text points to a real, large library file in the folder, copy it!
#                     if os.path.exists(target_path) and os.path.getsize(target_path) > 100:
#                         os.remove(filepath)
#                         shutil.copy(target_path, filepath)
#                 except Exception:
#                     pass # Ignore standard tiny files that aren't broken shortcuts
#     # ---------------------------------------------
            
#     # 3. Initialize Thick mode
#     try:
#         oracledb.init_oracle_client(lib_dir=client_dir)
#     except oracledb.ProgrammingError:
#         pass # Catch if it's already initialized by a previous Streamlit run

def setup_oracle_client():
    system = platform.system() 
    client_dir = os.path.join(os.getcwd(), "instantclient_21_13")
    
    # 1. Download if missing
    if not os.path.exists(client_dir):
        if system == "Linux":
            url = "https://download.oracle.com/otn_software/linux/instantclient/2113000/instantclient-basiclite-linux.x64-21.13.0.0.0dbru.zip"
        elif system == "Windows":
            url = "https://download.oracle.com/otn_software/nt/instantclient/2113000/instantclient-basiclite-windows.x64-21.13.0.0.0dbru.zip"
        elif system == "Darwin":
            url = "https://download.oracle.com/otn_software/mac/instantclient/2113000/instantclient-basiclite-macos.x64-21.13.0.0.0dbru.zip"
        else:
            st.error(f"Unsupported Operating System: {system}")
            return
            
        with st.spinner(f"Downloading Oracle Client for {system} (first run only)..."):
            zip_path = "instantclient.zip"
            urllib.request.urlretrieve(url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(os.getcwd())
            os.remove(zip_path)
            
    # 2. Linux Symlink Repair (Fixing Python's zipfile bug)
    if system == "Linux" and os.path.exists(client_dir):
        for filename in os.listdir(client_dir):
            filepath = os.path.join(client_dir, filename)
            if os.path.isfile(filepath) and os.path.getsize(filepath) < 50:
                try:
                    with open(filepath, 'r') as f:
                        target_name = f.read().strip()
                    target_path = os.path.join(client_dir, target_name)
                    if os.path.exists(target_path) and os.path.getsize(target_path) > 100:
                        os.remove(filepath)
                        shutil.copy(target_path, filepath)
                except Exception:
                    pass
                    
    # 3. --- THE LINUX LD_LIBRARY_PATH JEDI MIND TRICK ---
    if system == "Linux":
        current_ld = os.environ.get("LD_LIBRARY_PATH", "")
        # If our client folder isn't in the system path yet...
        if client_dir not in current_ld:
            # Add it to a fresh copy of the environment
            env = os.environ.copy()
            env["LD_LIBRARY_PATH"] = f"{client_dir}:{current_ld}" if current_ld else client_dir
            
            # Restart the process, but explicitly call 'streamlit run' this time!
            os.execve(
                sys.executable, 
                [sys.executable, "-m", "streamlit", "run", sys.argv[0]], 
                env
            )
    # -----------------------------------------------------
            
    # 4. Initialize Thick mode
    try:
        if system == "Linux":
            # On Linux, Oracle strictly forbids passing lib_dir.
            # It will automatically find the files using the LD_LIBRARY_PATH we just injected!
            oracledb.init_oracle_client()
        else:
            # Windows and Mac are perfectly happy using lib_dir
            oracledb.init_oracle_client(lib_dir=client_dir)
    except oracledb.ProgrammingError:
        pass # Catch if it's already initialized by a previous Streamlit UI rerun

# Run the setup before creating the pool
setup_oracle_client()

@st.cache_resource(show_spinner=False)
def get_pool():
    return oracledb.create_pool(
        user=DB_USER,
        password=DB_PASS,
        dsn=DB_DSN,
        min=1,
        max=5,
        increment=1,
    )


@contextmanager
def get_conn():
    pool = get_pool()
    conn = pool.acquire()
    try:
        yield conn
    finally:
        pool.release(conn)


# ─────────────────────────────────────────────────────────────
# Core helpers  (positional params as list)
# ─────────────────────────────────────────────────────────────

def run_query(sql: str, params: list = None) -> pd.DataFrame:
    """Execute a SELECT and return a DataFrame. params is a list."""
    params = params or []
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            cols = [c[0].lower() for c in cur.description]
            rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


def execute_dml(sql: str, params: list = None) -> int:
    """Execute INSERT / UPDATE / DELETE, auto-commit. params is a list."""
    params = params or []
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rowcount = cur.rowcount
        conn.commit()
    return rowcount


# ─────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────

def get_user(user_id: str) -> dict | None:
    df = run_query(
        "SELECT user_id, password AS pwd, role FROM Users WHERE user_id = :1",
        [user_id],
    )
    if df.empty:
        return None
    row = df.iloc[0]
    return {"user_id": row["user_id"], "password_hash": row["pwd"], "role": row["role"]}


# ─────────────────────────────────────────────────────────────
# STUDENT queries
# ─────────────────────────────────────────────────────────────

def get_student_profile(student_id: str) -> dict | None:
    df = run_query(
        """
        SELECT s.student_id, s.name, s.email, s.department,
               s.semester, s.cgpa, s.credits_completed,
               f.name AS advisor_name, f.department AS advisor_dept
        FROM   Students s
        LEFT JOIN Faculty f ON s.advisor_id = f.faculty_id
        WHERE  s.student_id = :1
        """,
        [student_id],
    )
    return df.iloc[0].to_dict() if not df.empty else None


def get_advising_window_for_student(credits: int) -> pd.DataFrame:
    return run_query(
        """
        SELECT schedule_id, label, start_time, end_time
        FROM   Advising_Schedules
        WHERE  target_role  = 'STUDENT'
          AND  min_credits <= :1
          AND  max_credits >= :2
        ORDER BY min_credits DESC
        FETCH FIRST 1 ROW ONLY
        """,
        [credits, credits],
    )


def get_faculty_advising_window() -> pd.DataFrame:
    return run_query(
        """
        SELECT schedule_id, label, start_time, end_time
        FROM   Advising_Schedules
        WHERE  target_role = 'FACULTY'
        ORDER BY start_time DESC
        FETCH FIRST 1 ROW ONLY
        """
    )


def get_available_courses() -> pd.DataFrame:
    return run_query(
        """
        SELECT course_code, title, credits, department,
               max_seats, available_seats
        FROM   Courses
        WHERE  available_seats > 0
        ORDER BY course_code
        """
    )


def get_all_courses() -> pd.DataFrame:
    return run_query(
        "SELECT course_code, title, credits, department, max_seats, available_seats FROM Courses ORDER BY course_code"
    )


def get_student_enrollments(student_id: str) -> pd.DataFrame:
    return run_query(
        """
        SELECT e.enrollment_id, e.course_code, c.title, c.credits,
               e.status, e.action_date, e.action_by_user_id
        FROM   Enrollment e
        JOIN   Courses c ON e.course_code = c.course_code
        WHERE  e.student_id = :1
        ORDER BY e.action_date DESC
        """,
        [student_id],
    )


def get_active_enrollment(student_id: str, course_code: str) -> pd.DataFrame:
    df = run_query(
        """
        SELECT enrollment_id, status FROM Enrollment
        WHERE  student_id  = :1
          AND  course_code = :2
        ORDER BY action_date DESC
        FETCH FIRST 1 ROW ONLY
        """,
        [student_id, course_code],
    )
    return df if not df.empty and df.iloc[0]['status'] == 'ENROLLED' else pd.DataFrame()


# ─────────────────────────────────────────────────────────────
# CONCURRENCY ENGINE  (SELECT ... FOR UPDATE)
# ─────────────────────────────────────────────────────────────

def enroll_student(student_id: str, course_code: str, actor_id: str) -> tuple[bool, str]:
    with get_conn() as conn:
        try:
            with conn.cursor() as cur:
                # 1. Row-level lock
                cur.execute(
                    "SELECT available_seats FROM Courses WHERE course_code = :1 FOR UPDATE",
                    [course_code],
                )
                row = cur.fetchone()
                if row is None:
                    conn.rollback()
                    return False, "Course not found."

                available = row[0]

                # 2. Already enrolled?
                cur.execute(
                    """
                    SELECT status FROM Enrollment
                    WHERE  student_id  = :1
                      AND  course_code = :2
                    ORDER BY action_date DESC
                    FETCH FIRST 1 ROW ONLY
                    """,
                    [student_id, course_code],
                )
                row_status = cur.fetchone()
                if row_status and row_status[0] == 'ENROLLED':
                    conn.rollback()
                    return False, "Student is already enrolled in this course."

                # 3. Seat check
                if available <= 0:
                    conn.rollback()
                    return False, "Course is full - no seats remaining."

                # 4. Insert provenance record
                cur.execute(
                    """
                    INSERT INTO Enrollment
                           (student_id, course_code, status, action_date, action_by_user_id)
                    VALUES (:1, :2, 'ENROLLED', SYSTIMESTAMP, :3)
                    """,
                    [student_id, course_code, actor_id],
                )

                # 5. Decrement seat
                cur.execute(
                    "UPDATE Courses SET available_seats = available_seats - 1 WHERE course_code = :1",
                    [course_code],
                )

            conn.commit()
            return True, f"Successfully enrolled in {course_code}."

        except Exception as e:
            conn.rollback()
            return False, f"Database error: {e}"


def drop_course(student_id: str, course_code: str, actor_id: str) -> tuple[bool, str]:
    with get_conn() as conn:
        try:
            with conn.cursor() as cur:
                # Lock course row
                cur.execute(
                    "SELECT available_seats FROM Courses WHERE course_code = :1 FOR UPDATE",
                    [course_code],
                )
                if cur.fetchone() is None:
                    conn.rollback()
                    return False, "Course not found."

                # Verify enrolled
                cur.execute(
                    """
                    SELECT status FROM Enrollment
                    WHERE  student_id  = :1
                      AND  course_code = :2
                    ORDER BY action_date DESC
                    FETCH FIRST 1 ROW ONLY
                    """,
                    [student_id, course_code],
                )
                row_status = cur.fetchone()
                if not row_status or row_status[0] != 'ENROLLED':
                    conn.rollback()
                    return False, "Student is not enrolled in this course."

                # Insert DROP provenance record
                cur.execute(
                    """
                    INSERT INTO Enrollment
                           (student_id, course_code, status, action_date, action_by_user_id)
                    VALUES (:1, :2, 'DROPPED', SYSTIMESTAMP, :3)
                    """,
                    [student_id, course_code, actor_id],
                )

                # Restore seat
                cur.execute(
                    "UPDATE Courses SET available_seats = available_seats + 1 WHERE course_code = :1",
                    [course_code],
                )

            conn.commit()
            return True, f"Successfully dropped {course_code}."

        except Exception as e:
            conn.rollback()
            return False, f"Database error: {e}"


# ─────────────────────────────────────────────────────────────
# FACULTY queries
# ─────────────────────────────────────────────────────────────

def get_advisees(faculty_id: str) -> pd.DataFrame:
    return run_query(
        """
        SELECT student_id, name, email, department,
               semester, cgpa, credits_completed
        FROM   Students
        WHERE  advisor_id = :1
        ORDER BY name
        """,
        [faculty_id],
    )


def get_faculty_profile(faculty_id: str) -> dict | None:
    df = run_query(
        "SELECT faculty_id, name, department FROM Faculty WHERE faculty_id = :1",
        [faculty_id],
    )
    return df.iloc[0].to_dict() if not df.empty else None


# ─────────────────────────────────────────────────────────────
# ADMIN queries
# ─────────────────────────────────────────────────────────────

def get_all_schedules() -> pd.DataFrame:
    return run_query(
        """
        SELECT schedule_id, target_role, min_credits, max_credits,
               start_time, end_time, label
        FROM   Advising_Schedules
        ORDER BY target_role, min_credits
        """
    )


def create_schedule(target_role, min_credits, max_credits, start_time, end_time, label):
    execute_dml(
        """
        INSERT INTO Advising_Schedules
               (target_role, min_credits, max_credits, start_time, end_time, label)
        VALUES (:1, :2, :3, :4, :5, :6)
        """,
        [target_role, min_credits, max_credits, start_time, end_time, label],
    )


def update_schedule(schedule_id, start_time, end_time, label):
    execute_dml(
        """
        UPDATE Advising_Schedules
        SET    start_time = :1, end_time = :2, label = :3
        WHERE  schedule_id = :4
        """,
        [start_time, end_time, label, schedule_id],
    )


def delete_schedule(schedule_id):
    execute_dml(
        "DELETE FROM Advising_Schedules WHERE schedule_id = :1",
        [schedule_id],
    )


def get_freshmen() -> pd.DataFrame:
    return run_query(
        """
        SELECT student_id, name, department, semester
        FROM   Students
        WHERE  credits_completed = 0
        ORDER BY name
        """
    )


def get_provenance(student_id: str) -> pd.DataFrame:
    return run_query(
        """
        SELECT e.enrollment_id,
               e.student_id,
               s.name           AS student_name,
               e.course_code,
               c.title          AS course_title,
               e.status,
               e.action_date,
               e.action_by_user_id,
               u.role           AS actor_role
        FROM   Enrollment e
        JOIN   Students s ON e.student_id        = s.student_id
        JOIN   Courses  c ON e.course_code       = c.course_code
        JOIN   Users    u ON e.action_by_user_id = u.user_id
        WHERE  e.student_id = :1
        ORDER BY e.action_date DESC
        """,
        [student_id],
    )


def get_all_students_summary() -> pd.DataFrame:
    return run_query(
        """
        SELECT s.student_id, s.name, s.department, s.semester,
               s.cgpa, s.credits_completed, s.advisor_id,
               f.name AS advisor_name
        FROM   Students s
        LEFT JOIN Faculty f ON s.advisor_id = f.faculty_id
        ORDER BY s.name
        """
    )