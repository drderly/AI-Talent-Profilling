"""Setup script for creating initial admin user."""
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import after loading env
import reflex as rx
from llm_ui.models import User
from llm_ui.auth import hash_password


def create_admin_user():
    """Create an admin user from environment variables."""
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    
    print("🚀 Creating admin user...")
    print(f"   Email: {admin_email}")
    
    try:
        with rx.session() as session:
            # Check if admin already exists
            existing_admin = session.exec(
                User.select().where(User.email == admin_email)
            ).first()
            
            if existing_admin:
                print("⚠️  Admin user already exists!")
                print(f"   Username: {existing_admin.username}")
                print(f"   Email: {existing_admin.email}")
                return
            
            # Create new admin user
            admin = User(
                email=admin_email,
                username="admin",
                password_hash=hash_password(admin_password),
                is_admin=True,
                created_at=datetime.now()
            )
            
            session.add(admin)
            session.commit()
            
            print("✅ Admin user created successfully!")
            print(f"   Username: admin")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
            print("\n⚠️  IMPORTANT: Change the password after first login!")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")


def create_demo_data():
    """Create demo data for testing."""
    print("\n🎨 Creating demo data...")
    
    try:
        from llm_ui.models import AIProvider, AIModel
        
        with rx.session() as session:
            # Check if data already exists
            existing_providers = session.exec(AIProvider.select()).all()
            if existing_providers:
                print("⚠️  Demo data already exists!")
                return
            
            # Create Ollama provider
            ollama = AIProvider(
                name="Ollama",
                api_url="http://127.0.0.1:11434",
                provider_type="ollama",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(ollama)
            session.commit()
            
            # Create some models
            models = [
                AIModel(
                    name="smollm2:1.7b",
                    display_name="SmolLM 2 (1.7B)",
                    provider_id=ollama.id,
                    model_type="text",
                    context_window=4096,
                    max_tokens=2048,
                    is_active=True,
                    created_at=datetime.now()
                ),
                AIModel(
                    name="mistral:7b-instruct",
                    display_name="Mistral 7B Instruct",
                    provider_id=ollama.id,
                    model_type="text",
                    context_window=8192,
                    max_tokens=4096,
                    is_active=True,
                    created_at=datetime.now()
                ),
            ]
            
            for model in models:
                session.add(model)
            
            session.commit()
            
            print("✅ Demo data created successfully!")
            print(f"   Provider: Ollama")
            print(f"   Models: {len(models)}")
            
    except Exception as e:
        print(f"❌ Error creating demo data: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("LLM UI Setup")
    print("=" * 50)
    
    # Create admin user
    create_admin_user()
    
    # Create demo data
    create_demo_data()
    
    print("\n" + "=" * 50)
    print("Setup complete! 🎉")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Start the application: reflex run")
    print("2. Open browser: http://localhost:3000")
    print("3. Login with admin credentials")
    print("=" * 50)
