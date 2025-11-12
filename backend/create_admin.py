"""
Script to create an admin user for Vigil.
Run this script to create a default admin user in the database.
"""
import sys
from app.models import User
from app.core import get_password_hash
from app.db import SessionLocal, Base, engine

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Check if admin user already exists
    existing_user = db.query(User).filter(User.email == "admin@example.com").first()
    if existing_user:
        print("Admin user already exists!")
        sys.exit(0)

    # Create admin user
    admin_user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        is_superuser=True
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    print("Admin user created successfully!")
    print("Email: admin@example.com")
    print("Password: admin123")
    print("\nPlease change the password after first login!")

except Exception as e:
    print(f"Error creating admin user: {e}")
    db.rollback()
    sys.exit(1)
finally:
    db.close()
