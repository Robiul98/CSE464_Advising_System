"""
generate_hashes.py
──────────────────
Run this ONCE to generate the bcrypt hashes needed in the SQL seed data.
Usage:  python generate_hashes.py

Copy the printed hashes into 1_schema_and_seed.sql
"""

import bcrypt

passwords = {
    "admin01":   "admin123",
    "fac01":     "faculty123",
    "fac02":     "faculty123",
    "stu01":     "student123",
    "stu02":     "student123",
    "stu03":     "student123",
}

print("=" * 70)
print("BCRYPT HASHES  —  paste into 1_schema_and_seed.sql")
print("=" * 70)
for user_id, plain in passwords.items():
    hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
    print(f"\n-- {user_id} / {plain}")
    print(f"-- {hashed}")

print("\n")
print("SQL INSERT snippet (copy-paste ready):")
print("-" * 70)
for user_id, plain in passwords.items():
    hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
    role   = "ADMIN" if "admin" in user_id else ("FACULTY" if "fac" in user_id else "STUDENT")
    print(f"INSERT INTO Users VALUES ('{user_id}', '{hashed}', '{role}');")
