"""
Setup script for LLM UI application
Initializes database and creates default admin user
"""
import sys
import os
from getpass import getpass
from models import init_db, get_session, seed_data, User, UserRole
from auth import hash_password

def setup_database():
    """Initialize database and seed data"""
    print("🔧 Initializing database...")
    
    # Initialize database
    engine = init_db()
    print("✅ Database tables created")
    
    # Seed initial data
    db = get_session()
    seed_data(db)
    print("✅ Initial data seeded")
    db.close()
    
    return True

def create_admin_user():
    """Create admin user"""
    print("\n👤 Create Admin User")
    print("-" * 40)
    
    db = get_session()
    
    try:
        # Check if admin exists
        existing_admin = db.query(User).filter_by(role=UserRole.ADMIN).first()
        if existing_admin:
            print(f"⚠️  Admin user already exists: {existing_admin.username}")
            create_new = input("Create another admin? (y/n): ").lower()
            if create_new != 'y':
                return True
        
        # Get admin details
        username = input("Username: ").strip()
        if not username:
            print("❌ Username cannot be empty")
            return False
        
        email = input("Email: ").strip()
        if not email or '@' not in email:
            print("❌ Invalid email")
            return False
        
        # Check if user exists
        existing = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing:
            print("❌ Username or email already exists")
            return False
        
        password = getpass("Password: ")
        if len(password) < 6:
            print("❌ Password must be at least 6 characters")
            return False
        
        confirm = getpass("Confirm Password: ")
        if password != confirm:
            print("❌ Passwords do not match")
            return False
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        
        print(f"✅ Admin user '{username}' created successfully!")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {str(e)}")
        return False
    finally:
        db.close()

def main():
    """Main setup function"""
    print("=" * 50)
    print("🤖 LLM UI - Setup Script")
    print("=" * 50)
    print()
    
    # Setup database
    if not setup_database():
        print("❌ Database setup failed")
        sys.exit(1)
    
    # Create admin user
    print()
    create_admin = input("Create admin user now? (y/n): ").lower()
    if create_admin == 'y':
        if not create_admin_user():
            print("⚠️  Admin user creation failed, but you can create one later")
    
    print()
    print("=" * 50)
    print("✅ Setup completed successfully!")
    print("=" * 50)
    print()
    print("To start the application, run:")
    print("  python app.py")
    print()
    print("Or with Panel serve:")
    print("  panel serve app.py --show --autoreload")
    print()

if __name__ == "__main__":
    main()
