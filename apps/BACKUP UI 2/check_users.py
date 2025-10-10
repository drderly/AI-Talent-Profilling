"""
Diagnostic script to check users in database
"""
from models import get_session, User, init_db
from auth import hash_password

def check_users():
    """Check if users exist in database"""
    print("=" * 50)
    print("🔍 Checking Database Users")
    print("=" * 50)
    print()
    
    try:
        db = get_session()
        users = db.query(User).all()
        
        print(f"Total users found: {len(users)}")
        print()
        
        if not users:
            print("❌ No users found in database!")
            print()
            print("💡 Solutions:")
            print("1. Run: python setup.py")
            print("2. Or create a user manually with this script")
            print()
            
            create = input("Create an admin user now? (y/n): ").lower()
            if create == 'y':
                create_admin_user(db)
        else:
            print("✅ Users in database:")
            print()
            for user in users:
                print(f"  Username: {user.username}")
                print(f"  Email:    {user.email}")
                print(f"  Role:     {user.role.value.upper()}")
                print(f"  Active:   {'Yes' if user.is_active else 'No'}")
                print(f"  Created:  {user.created_at}")
                print()
            
            print("💡 To login, use one of the emails and passwords above")
            print("   (You should know the password you set during setup)")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()
        print("💡 Try running: python setup.py")

def create_admin_user(db):
    """Create an admin user"""
    print()
    print("👤 Create Admin User")
    print("-" * 40)
    
    try:
        from models import UserRole
        
        username = input("Username: ").strip()
        if not username:
            print("❌ Username cannot be empty")
            return
        
        email = input("Email: ").strip()
        if not email or '@' not in email:
            print("❌ Invalid email")
            return
        
        # Check if user exists
        existing = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing:
            print("❌ Username or email already exists")
            return
        
        from getpass import getpass
        password = getpass("Password: ")
        if len(password) < 6:
            print("❌ Password must be at least 6 characters")
            return
        
        confirm = getpass("Confirm Password: ")
        if password != confirm:
            print("❌ Passwords do not match")
            return
        
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
        
        print()
        print(f"✅ Admin user '{username}' created successfully!")
        print(f"   Email: {email}")
        print(f"   You can now login with these credentials")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating user: {str(e)}")

if __name__ == "__main__":
    check_users()
    print()
    print("=" * 50)
    input("Press Enter to exit...")
