"""
backend/setup_db.py
ERP-007 FIX: Admin credentials come from environment variables only.
No hardcoded email, username, or password.

Usage:
  # Interactive first-run (prompts for credentials):
  python setup_db.py

  # Non-interactive (CI/Docker first-run):
  ADMIN_EMAIL=admin@yourcompany.com \
  ADMIN_USERNAME=admin \
  ADMIN_PASSWORD=<generated_strong_password> \
  python setup_db.py

  # Skip admin creation entirely (tables only):
  python setup_db.py --tables-only
"""
import os
import sys
import secrets
import string
import getpass
import argparse
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------------
# Bootstrap path so this runs from the backend/ directory
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.models.base import Base
from app.models.user import User
from app.models.security import UserRole, Permission, Role, RolePermission
from app.services.auth import get_password_hash


def generate_strong_password(length: int = 24) -> str:
    """Generate a cryptographically strong password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        # Ensure it meets complexity requirements
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()" for c in password)
        if has_upper and has_lower and has_digit and has_special:
            return password


def validate_password(password: str) -> tuple[bool, str]:
    """Returns (is_valid, error_message)."""
    if len(password) < 12:
        return False, "Password must be at least 12 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    if not any(c in "!@#$%^&*()" for c in password):
        return False, "Password must contain at least one special character (!@#$%^&*())"
    return True, ""


def get_admin_credentials() -> tuple[str, str, str]:
    """
    Resolve admin credentials in priority order:
      1. Environment variables (ADMIN_EMAIL, ADMIN_USERNAME, ADMIN_PASSWORD)
      2. Interactive prompt (if running in a TTY)
      3. Fatal error if neither is available
    """
    email = os.environ.get("ADMIN_EMAIL", "").strip()
    username = os.environ.get("ADMIN_USERNAME", "").strip()
    password = os.environ.get("ADMIN_PASSWORD", "").strip()

    # All three provided via env — use them directly
    if email and username and password:
        is_valid, err = validate_password(password)
        if not is_valid:
            print(f"[ERROR] ADMIN_PASSWORD is too weak: {err}", file=sys.stderr)
            sys.exit(1)
        print("[INFO] Using admin credentials from environment variables.")
        return email, username, password

    # Partial env — don't silently accept incomplete config
    if any([email, username, password]) and not all([email, username, password]):
        missing = [k for k, v in {
            "ADMIN_EMAIL": email,
            "ADMIN_USERNAME": username,
            "ADMIN_PASSWORD": password,
        }.items() if not v]
        print(
            f"[ERROR] Partial admin env vars set. Missing: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)

    # No env vars — try interactive
    if not sys.stdin.isatty():
        print(
            "[ERROR] No admin credentials in environment and not running interactively.\n"
            "Set ADMIN_EMAIL, ADMIN_USERNAME, and ADMIN_PASSWORD environment variables.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Interactive prompt
    print("\n" + "=" * 60)
    print("  TOP WorX — First-Run Admin Setup")
    print("=" * 60)
    print("No admin account found. Creating first administrator.\n")

    email = input("Admin email address: ").strip()
    if not email or "@" not in email:
        print("[ERROR] Invalid email address.", file=sys.stderr)
        sys.exit(1)

    username = input("Admin username (no spaces): ").strip()
    if not username or " " in username:
        print("[ERROR] Invalid username.", file=sys.stderr)
        sys.exit(1)

    suggested = generate_strong_password()
    print(f"\nSuggested strong password: {suggested}")
    print("(Press Enter to use suggested, or type your own)\n")

    while True:
        password = getpass.getpass("Admin password: ").strip()
        if not password:
            password = suggested
            print("[INFO] Using suggested password.")
            break
        is_valid, err = validate_password(password)
        if is_valid:
            confirm = getpass.getpass("Confirm password: ").strip()
            if password == confirm:
                break
            print("[ERROR] Passwords do not match. Try again.")
        else:
            print(f"[ERROR] {err}. Try again.")

    print("\n" + "=" * 60)
    print("⚠️  IMPORTANT: Save these credentials NOW before continuing.")
    print(f"  Email:    {email}")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print("=" * 60)
    input("\nPress Enter to confirm you have saved the credentials... ")

    return email, username, password


def create_tables(engine) -> None:
    """Create all tables if they don't exist."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    Base.metadata.create_all(bind=engine)

    new_tables = [
        t for t in inspect(engine).get_table_names() if t not in existing_tables
    ]
    if new_tables:
        print(f"[INFO] Created tables: {', '.join(new_tables)}")
    else:
        print("[INFO] All tables already exist.")


def seed_default_roles(db) -> None:
    """Create the four default system roles if they don't exist."""
    default_roles = [
        ("admin", "System Administrator — full access"),
        ("manager", "Module Manager — read/write within assigned modules"),
        ("staff", "Staff — standard operational access"),
        ("viewer", "Viewer — read-only access"),
    ]
    for name, description in default_roles:
        existing = db.query(Role).filter(Role.name == name).first()
        if not existing:
            db.add(Role(name=name, description=description))
    db.commit()
    print("[INFO] Default roles ensured.")


def create_admin_user(db, email: str, username: str, password: str) -> None:
    """Create the admin user if they don't already exist."""
    existing_email = db.query(User).filter(User.email == email).first()
    existing_user = db.query(User).filter(User.username == username).first()

    if existing_email or existing_user:
        print(f"[INFO] Admin user already exists (email={email}). Skipping creation.")
        return

    admin = User(
        email=email,
        username=username,
        full_name="System Administrator",
        hashed_password=get_password_hash(password),
        role=UserRole.ADMIN,
        is_active=True,
        is_superuser=True,
    )
    db.add(admin)
    db.commit()
    print(f"[INFO] Admin user created: {username} <{email}>")


def main() -> None:
    parser = argparse.ArgumentParser(description="TOP WorX database setup")
    parser.add_argument(
        "--tables-only",
        action="store_true",
        help="Only create tables, skip admin user creation",
    )
    args = parser.parse_args()

    print(f"[INFO] Connecting to database: {settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}")

    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 1. Create tables
    create_tables(engine)

    if args.tables_only:
        print("[INFO] --tables-only flag set. Skipping admin creation.")
        return

    db = SessionLocal()
    try:
        # 2. Seed roles
        seed_default_roles(db)

        # 3. Check if any superuser exists — skip if so
        existing_superuser = db.query(User).filter(User.is_superuser == True).first()
        if existing_superuser:
            print(
                f"[INFO] Superuser already exists ({existing_superuser.email}). "
                "Skipping admin creation."
            )
            return

        # 4. Get credentials and create admin
        email, username, password = get_admin_credentials()
        create_admin_user(db, email, username, password)

    finally:
        db.close()

    print("[INFO] Database setup complete.")


if __name__ == "__main__":
    main()
