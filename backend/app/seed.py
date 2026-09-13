"""
Seed script: creates the first admin and a demo analyst if they don't exist.
Also ensures all database tables exist.

Run once after the database is up:
    python -m app.seed
"""

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import User
from app import models  # noqa: F401  (ensures all models are registered)

SEED_USERS = [
    {
        "email": "admin@momoguard.rw",
        "password": "Admin@1234",
        "full_name": "System Administrator",
        "role": "admin",
    },
    {
        "email": "analyst@momoguard.rw",
        "password": "Analyst@1234",
        "full_name": "MTN Fraud Analyst",
        "role": "analyst",
    },
]


def run():
    # Ensure tables exist before we try to query them
    print("[seed] Ensuring tables exist...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for spec in SEED_USERS:
            existing = db.query(User).filter(User.email == spec["email"]).first()
            if existing:
                print(f"[seed] {spec['email']} already exists — skipping")
                continue
            user = User(
                email=spec["email"],
                password_hash=hash_password(spec["password"]),
                full_name=spec["full_name"],
                role=spec["role"],
            )
            db.add(user)
            print(f"[seed] Created {spec['email']} ({spec['role']})")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()