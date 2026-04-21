-- ============================================================
-- STUDENT ADVISING PORTAL — ORACLE DDL + SEED DATA
-- Run this file in SQLPlus:  @1_schema_and_seed.sql
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- STEP 0: Clean slate (run safely even on first run)
-- ────────────────────────────────────────────────────────────

SET DEFINE OFF

BEGIN
    FOR t IN (
        SELECT table_name FROM user_tables
        WHERE table_name IN (
            'ENROLLMENT','STUDENTS','FACULTY',
            'COURSES','ADVISING_SCHEDULES','USERS'
        )
    ) LOOP
        EXECUTE IMMEDIATE 'DROP TABLE ' || t.table_name || ' CASCADE CONSTRAINTS';
    END LOOP;
END;
/

-- ────────────────────────────────────────────────────────────
-- STEP A: USERS  (root identity table for all roles)
-- ────────────────────────────────────────────────────────────
CREATE TABLE Users (
    User_ID      VARCHAR2(20)  PRIMARY KEY,
    Password     VARCHAR2(255) NOT NULL,          -- bcrypt hash stored here
    Role         VARCHAR2(10)  NOT NULL
        CHECK (Role IN ('ADMIN','FACULTY','STUDENT'))
);

-- ────────────────────────────────────────────────────────────
-- STEP B: ADVISING_SCHEDULES
-- ────────────────────────────────────────────────────────────
CREATE TABLE Advising_Schedules (
    Schedule_ID  NUMBER        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    Target_Role  VARCHAR2(10)  NOT NULL CHECK (Target_Role IN ('STUDENT','FACULTY')),
    Min_Credits  NUMBER(5,0)   DEFAULT 0,
    Max_Credits  NUMBER(5,0)   DEFAULT 9999,
    Start_Time   TIMESTAMP     NOT NULL,
    End_Time     TIMESTAMP     NOT NULL,
    Label        VARCHAR2(100)
);

-- ────────────────────────────────────────────────────────────
-- STEP C: COURSES
-- ────────────────────────────────────────────────────────────
CREATE TABLE Courses (
    Course_Code      VARCHAR2(15)  PRIMARY KEY,
    Title            VARCHAR2(100) NOT NULL,
    Credits          NUMBER(2,0)   NOT NULL,
    Department       VARCHAR2(50),
    Max_Seats        NUMBER(4,0)   NOT NULL,
    Available_Seats  NUMBER(4,0)   NOT NULL,
    CONSTRAINT chk_seats CHECK (Available_Seats >= 0 AND Available_Seats <= Max_Seats)
);

-- ────────────────────────────────────────────────────────────
-- STEP D: FACULTY
-- ────────────────────────────────────────────────────────────
CREATE TABLE Faculty (
    Faculty_ID   VARCHAR2(20)  PRIMARY KEY,
    Name         VARCHAR2(100) NOT NULL,
    Department   VARCHAR2(50),
    CONSTRAINT fk_faculty_user FOREIGN KEY (Faculty_ID) REFERENCES Users(User_ID)
);

-- ────────────────────────────────────────────────────────────
-- STEP E: STUDENTS
-- ────────────────────────────────────────────────────────────
CREATE TABLE Students (
    Student_ID        VARCHAR2(20)   PRIMARY KEY,
    Name              VARCHAR2(100)  NOT NULL,
    Email             VARCHAR2(100),
    Department        VARCHAR2(50),
    Semester          NUMBER(2,0),
    CGPA              NUMBER(4,2)    DEFAULT 0.00,
    Credits_Completed NUMBER(5,0)    DEFAULT 0,
    Advisor_ID        VARCHAR2(20),
    CONSTRAINT fk_student_user    FOREIGN KEY (Student_ID) REFERENCES Users(User_ID),
    CONSTRAINT fk_student_advisor FOREIGN KEY (Advisor_ID) REFERENCES Faculty(Faculty_ID)
);

-- ────────────────────────────────────────────────────────────
-- STEP F: ENROLLMENT  (core provenance table)
-- ────────────────────────────────────────────────────────────
CREATE TABLE Enrollment (
    Enrollment_ID     NUMBER         GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    Student_ID        VARCHAR2(20)   NOT NULL,
    Course_Code       VARCHAR2(15)   NOT NULL,
    Status            VARCHAR2(10)   NOT NULL CHECK (Status IN ('ENROLLED','DROPPED')),
    Action_Date       TIMESTAMP      DEFAULT SYSTIMESTAMP NOT NULL,
    Action_By_User_ID VARCHAR2(20)   NOT NULL,             -- provenance: who clicked
    CONSTRAINT fk_enroll_student FOREIGN KEY (Student_ID)        REFERENCES Students(Student_ID),
    CONSTRAINT fk_enroll_course  FOREIGN KEY (Course_Code)       REFERENCES Courses(Course_Code),
    CONSTRAINT fk_enroll_actor   FOREIGN KEY (Action_By_User_ID) REFERENCES Users(User_ID)
);

-- Useful index for provenance queries
CREATE INDEX idx_enroll_student ON Enrollment(Student_ID);
CREATE INDEX idx_enroll_actor   ON Enrollment(Action_By_User_ID);

-- ============================================================
-- SEED DATA
-- Passwords below are bcrypt hashes of the plaintext shown
-- in the comment.  To log in use the plaintext passwords.
--
--   admin01   → password: admin123
--   fac01     → password: faculty123
--   fac02     → password: faculty123
--   stu01     → password: student123
--   stu02     → password: student123
--   stu03     → password: student123  (0 credits — freshman)
-- ============================================================

-- ── Users ───────────────────────────────────────────────────
INSERT INTO Users VALUES ('admin01', '$2b$12$jkpf.N3xMwJau0nTbf0HA.uzDf4qpWpgIxY.uSyBrOqwcNVNMQsye', 'ADMIN');
INSERT INTO Users VALUES ('fac01', '$2b$12$jQygdWxCAJTxg7uwCLI6fee3laiKeba7eCgZJaHZsHoHwswGXLstm', 'FACULTY');
INSERT INTO Users VALUES ('fac02', '$2b$12$mbQlv0l3YmvGyFp7GuWcJ.8EXD6xIAUGh3KnwcHdF38DFphTrmLRe', 'FACULTY');
INSERT INTO Users VALUES ('stu01', '$2b$12$/2mn1S0DYunuHLdB5i5sje8a4/wX3JeYNgtcPyagpAZCOPTHEwEMm', 'STUDENT');
INSERT INTO Users VALUES ('stu02', '$2b$12$zzzD4swycvndyZVV207F9eOZaYwtwF9.lQOQ44ZVjnvnX7Gs3xuY2', 'STUDENT');
INSERT INTO Users VALUES ('stu03', '$2b$12$KYmi3OGESzPJmG7TnA1fkOVsVpcAoUL0yYlVegOVguulV4IVENTBG', 'STUDENT');


-- ── Faculty ─────────────────────────────────────────────────
INSERT INTO Faculty VALUES ('fac01', 'Dr. Amina Rahman',  'Computer Science');
INSERT INTO Faculty VALUES ('fac02', 'Prof. Karim Hossain','Electrical Engineering');

-- ── Students ────────────────────────────────────────────────
-- stu01 → Senior (90 credits), stu02 → Sophomore (45 credits), stu03 → Freshman (0 credits)
INSERT INTO Students VALUES ('stu01','Rafi Ahmed',   'rafi@uni.edu',  'Computer Science',     8, 3.75, 90, 'fac01');
INSERT INTO Students VALUES ('stu02','Nadia Islam',  'nadia@uni.edu', 'Computer Science',     4, 3.20, 45, 'fac01');
INSERT INTO Students VALUES ('stu03','Tanvir Hasan', 'tanvir@uni.edu','Electrical Engineering',1, 0.00,  0, 'fac02');

-- ── Courses ─────────────────────────────────────────────────
-- CS401 intentionally has only 1 seat → perfect for concurrency demo
INSERT INTO Courses VALUES ('CS101', 'Introduction to Programming',       3, 'Computer Science',      30, 28);
INSERT INTO Courses VALUES ('CS201', 'Data Structures & Algorithms',      3, 'Computer Science',      25, 20);
INSERT INTO Courses VALUES ('CS301', 'Database Management Systems',       3, 'Computer Science',      20, 15);
INSERT INTO Courses VALUES ('CS401', 'Advanced Machine Learning',         3, 'Computer Science',      10,  1);
INSERT INTO Courses VALUES ('EE201', 'Circuit Theory & Electronics',      3, 'Electrical Engineering', 25, 22);

-- Fix ORA-00904 error — Courses table has no 6th column here; let me fix:
-- (already correct above — 7 columns match the DDL)

-- ── Advising Schedules ──────────────────────────────────────
-- NOTE: Adjust these dates to straddle TODAY when you run the seed
--       so that the time-gating feature is testable immediately.
--
-- Window 1: SENIORS (60+ credits)  — earliest access
INSERT INTO Advising_Schedules (Target_Role, Min_Credits, Max_Credits, Start_Time, End_Time, Label)
VALUES ('STUDENT', 60, 9999,
        SYSTIMESTAMP - INTERVAL '2' DAY,
        SYSTIMESTAMP + INTERVAL '5' DAY,
        'Senior Registration Window');

-- Window 2: SOPHOMORES / JUNIORS (11-59 credits)
INSERT INTO Advising_Schedules (Target_Role, Min_Credits, Max_Credits, Start_Time, End_Time, Label)
VALUES ('STUDENT', 11, 59,
        SYSTIMESTAMP - INTERVAL '1' DAY,
        SYSTIMESTAMP + INTERVAL '5' DAY,
        'Junior/Sophomore Registration Window');

-- Window 3: FRESHMEN (0-10 credits) — latest access (admin override used for 0-credit)
INSERT INTO Advising_Schedules (Target_Role, Min_Credits, Max_Credits, Start_Time, End_Time, Label)
VALUES ('STUDENT', 0, 10,
        SYSTIMESTAMP + INTERVAL '1' DAY,
        SYSTIMESTAMP + INTERVAL '5' DAY,
        'Freshman Registration Window');

-- Window 4: FACULTY global advising window
INSERT INTO Advising_Schedules (Target_Role, Min_Credits, Max_Credits, Start_Time, End_Time, Label)
VALUES ('FACULTY', 0, 9999,
        SYSTIMESTAMP - INTERVAL '1' DAY,
        SYSTIMESTAMP + INTERVAL '3' DAY,
        'Faculty Advising Window');

COMMIT;

-- ── Verify ──────────────────────────────────────────────────
SELECT 'Users'              AS tbl, COUNT(*) AS row_count FROM Users
UNION ALL
SELECT 'Faculty',                   COUNT(*)              FROM Faculty
UNION ALL
SELECT 'Students',                  COUNT(*)              FROM Students
UNION ALL
SELECT 'Courses',                   COUNT(*)              FROM Courses
UNION ALL
SELECT 'Advising_Schedules',        COUNT(*)              FROM Advising_Schedules
UNION ALL
SELECT 'Enrollment',                COUNT(*)              FROM Enrollment;
