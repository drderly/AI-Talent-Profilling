# 🚀 Quick Start Guide

Get your LLM UI up and running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.10 or higher installed
- [ ] Git installed
- [ ] LLM API service running (see `../llm-api/README.md`)
- [ ] Ollama installed and running (optional, for local models)

## Step-by-Step Setup

### 1️⃣ Navigate to Directory
```bash
cd apps/llm-ui
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv .venv
```

### 3️⃣ Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 4️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- Reflex (web framework)
- httpx (HTTP client)
- SQLAlchemy (database ORM)
- and other dependencies

### 5️⃣ Configure Environment
```bash
# Copy example configuration
cp .env.example .env
```

Edit `.env` file with your settings:
```env
LLM_API_URL=http://127.0.0.1:8000
DATABASE_URL=sqlite:///llm_ui.db
SECRET_KEY=your-secret-key-here
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
```

### 6️⃣ Initialize Reflex
```bash
reflex init
```

This will:
- Download and install Node.js dependencies
- Set up the frontend build system
- Create `.web` directory

**Note:** This may take a few minutes on first run.

### 7️⃣ Initialize Database
```bash
reflex db init
reflex db migrate
```

### 8️⃣ Create Admin User
```bash
python setup.py
```

This will:
- Create an admin user with credentials from `.env`
- Create demo data (AI providers and models)

### 9️⃣ Start the Application
```bash
reflex run
```

The app will be available at:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000

## 🎉 You're Done!

### Login Credentials
- **Email**: admin@example.com (or your configured email)
- **Password**: admin123 (or your configured password)

### First Steps

1. **Login** at http://localhost:3000/login
2. **Change your password** in Profile settings
3. **Configure AI providers** in Admin > AI Providers
4. **Start chatting** in the Chat interface

## 🔧 Common Issues

### "Reflex not found"
```bash
# Make sure virtual environment is activated
pip install reflex
```

### "Port 3000 already in use"
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

### "Can't connect to LLM API"
```bash
# Make sure LLM API is running
cd ../llm-api
python main.py
```

### Database errors
```bash
# Reset database (WARNING: deletes all data)
rm llm_ui.db
reflex db init
reflex db migrate
python setup.py
```

## 📖 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out the [Reflex Documentation](https://reflex.dev/docs)
- Explore the admin dashboard features
- Try the chat interface with different models

## 🆘 Need Help?

- Check the [Reflex Forum](https://forum.reflex.dev)
- Review the [Troubleshooting](#-common-issues) section
- Open an issue on GitHub

---

**Happy coding! 🎉**
