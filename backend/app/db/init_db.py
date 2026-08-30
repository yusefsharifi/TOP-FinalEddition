"""Database initialization — creates default admin user."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base_class import Base
from app.models.auth_enhanced import User, UserStatus, Role, UserRole
from app.services.auth import get_password_hash

async def init_db(db: AsyncSession) -> None:
    """Initialize the database with default data."""
    try:
        # Create default admin role if it doesn't exist
        role_r = await db.execute(select(Role).where(Role.code == "admin"))
        admin_role = role_r.scalar_one_or_none()
        if not admin_role:
            admin_role = Role(
                code="admin",
                name="Administrator",
                name_fa="مدیر سیستم",
                role_type="system",
                level=1,
                data_scope="all",
            )
            db.add(admin_role)
            await db.flush()

        # Create default admin user
        user_r = await db.execute(select(User).where(User.email == "admin@topworx.com"))
        admin = user_r.scalar_one_or_none()
        if not admin:
            admin = User(
                email="admin@topworx.com",
                first_name="System",
                last_name="Administrator",
                hashed_password=get_password_hash("admin123!@#"),
                status=UserStatus.ACTIVE,
                email_verified=True,
            )
            db.add(admin)
            await db.flush()

            # Assign admin role
            user_role = UserRole(user_id=admin.id, role_id=admin_role.id)
            db.add(user_role)
            await db.commit()
            print("Created admin user: admin@topworx.com")
        else:
            await db.commit()

    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise