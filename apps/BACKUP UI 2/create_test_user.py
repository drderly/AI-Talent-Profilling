"""
Quick script to create a test user
"""
from models import get_session, User, UserRole, init_db
from auth import hash_password

def create_test_user():
    """Create a test admin user with default credentials"""
    print("=" * 50)
    print("🔧 Creating Test User")
    print("=" * 50)
    print()
    
    # Initialize database
    init_db()
    
    db = get_session()
    try:
        # Check if any admin user exists
        existing_admin = db.query(User).filter_by(username="admin").first()
        if existing_admin:
            print("⚠️  An admin user already exists!")
            print()
            print("Existing Admin User:")
            print(f"  Username: {existing_admin.username}")
            print(f"  Email:    {existing_admin.email}")
            print()
            print("💡 Use the email and password you set during setup.py")
            print("   If you forgot the password, run: del llm_ui.db && python setup.py")
            return
        
        # Check if test user already exists
        existing = db.query(User).filter_by(email="admin@test.com").first()
        if existing:
            print("⚠️  Test user already exists!")
            print()
            print("Test User Credentials:")
            print("  Email:    admin@test.com")
            print("  Password: admin123")
            print()
            print("Try logging in with these credentials.")
            return
        
        # Create test user
        test_user = User(
            username="admin",
            email="admin@test.com",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(test_user)
        db.commit()
        
        print("✅ Test user created successfully!")
        print()
        print("Test User Credentials:")
        print("  Email:    admin@test.com")
        print("  Password: admin123")
        print()
        print("🚀 You can now login with these credentials!")
        print("   Open http://localhost:5006 and use the credentials above")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
    print()
    print("=" * 50)
