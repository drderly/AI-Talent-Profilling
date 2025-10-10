"""Development helper script."""
import sys
import subprocess
import os


def check_venv():
    """Check if virtual environment is activated."""
    if sys.prefix == sys.base_prefix:
        print("⚠️  Virtual environment is not activated!")
        print("\nPlease activate it first:")
        print("  Windows: .venv\\Scripts\\Activate.ps1")
        print("  Linux/Mac: source .venv/bin/activate")
        return False
    return True


def check_env_file():
    """Check if .env file exists."""
    if not os.path.exists(".env"):
        print("⚠️  .env file not found!")
        print("\nPlease create it:")
        print("  cp .env.example .env")
        return False
    return True


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🚀 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} completed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        return False


def main():
    """Main development helper."""
    print("=" * 60)
    print("LLM UI Development Helper")
    print("=" * 60)
    
    # Check prerequisites
    if not check_venv():
        sys.exit(1)
    
    if not check_env_file():
        sys.exit(1)
    
    print("\n📋 Available commands:")
    print("1. Install dependencies")
    print("2. Initialize Reflex")
    print("3. Initialize database")
    print("4. Run setup (create admin + demo data)")
    print("5. Start development server")
    print("6. Export for production")
    print("7. Clean build files")
    print("8. Run all setup steps (2-4)")
    print("0. Exit")
    
    choice = input("\n👉 Enter your choice (0-8): ").strip()
    
    if choice == "1":
        run_command("pip install -r requirements.txt", "Installing dependencies")
    
    elif choice == "2":
        run_command("reflex init", "Initializing Reflex")
    
    elif choice == "3":
        run_command("reflex db init", "Initializing database")
        run_command("reflex db migrate", "Running migrations")
    
    elif choice == "4":
        run_command("python setup.py", "Running setup script")
    
    elif choice == "5":
        print("\n🚀 Starting development server...")
        print("   Frontend: http://localhost:3000")
        print("   Backend: http://localhost:8000")
        print("\nPress Ctrl+C to stop\n")
        subprocess.run("reflex run", shell=True)
    
    elif choice == "6":
        run_command("reflex export", "Exporting for production")
    
    elif choice == "7":
        print("\n🧹 Cleaning build files...")
        if os.path.exists(".web"):
            import shutil
            shutil.rmtree(".web")
            print("✅ Cleaned .web directory")
        print("✅ Clean complete!")
    
    elif choice == "8":
        print("\n🔄 Running full setup...")
        if run_command("reflex init", "Initializing Reflex"):
            if run_command("reflex db init", "Initializing database"):
                if run_command("reflex db migrate", "Running migrations"):
                    run_command("python setup.py", "Running setup script")
        print("\n✅ Full setup complete!")
        print("\nYou can now run: reflex run")
    
    elif choice == "0":
        print("\n👋 Goodbye!")
    
    else:
        print("\n❌ Invalid choice!")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
