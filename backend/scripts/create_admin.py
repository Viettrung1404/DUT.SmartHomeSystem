#!/usr/bin/env python3
"""
Create an admin user account.

Usage:
    python scripts/create_admin.py [--email admin@demo.local] [--password Admin@123] [--name "Admin User"]
    
Example:
    python scripts/create_admin.py --email admin@demo.local --password Admin@123 --name "Admin User"
"""

import sys
import argparse
from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, str(sys.path[0]))

from src.database.core import engine
from src.entities.user import User
from src.entities.home import Home
from src.entities.home_member import HomeMember
from src.entities.device import Device
from src.entities.device_log import DeviceLog
from src.entities.automation import Automation, AutomationCondition, AutomationAction
from src.entities.energy_log import EnergyLog
from src.entities.security_event import SecurityEvent
from src.entities.todo import Todo

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_admin_user(email: str, password: str, full_name: str) -> bool:
    """Create an admin user in the database."""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if user already exists
        existing_user = session.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ User with email '{email}' already exists!")
            return False
        
        # Create new admin user
        admin_user = User(
            id=uuid.uuid4(),
            email=email,
            full_name=full_name,
            password_hash=get_password_hash(password),
            is_admin=True,
            created_at=datetime.now(timezone.utc)
        )
        
        session.add(admin_user)
        session.commit()
        
        print(f"✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   Name: {full_name}")
        print(f"   ID: {admin_user.id}")
        print(f"\n   You can now login at /login with these credentials:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"\n   Then visit /admin to access the admin dashboard.")
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="Create an admin user account")
    parser.add_argument(
        "--email",
        type=str,
        default="admin@demo.local",
        help="Admin email address (default: admin@demo.local)"
    )
    parser.add_argument(
        "--password",
        type=str,
        default="Admin@123",
        help="Admin password (default: Admin@123)"
    )
    parser.add_argument(
        "--name",
        type=str,
        default="Admin User",
        help="Admin full name (default: Admin User)"
    )
    
    args = parser.parse_args()
    
    print(f"Creating admin user...")
    print(f"  Email: {args.email}")
    print(f"  Name: {args.name}")
    print(f"  Password: {'*' * len(args.password)}")
    print()
    
    success = create_admin_user(args.email, args.password, args.name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
