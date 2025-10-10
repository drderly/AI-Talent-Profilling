# 🚀 Quick Start Guide

Get your LLM UI up and running in **5 minutes**!

## Prerequisites

- Python 3.9+ installed
- LLM API server running (e.g., at http://localhost:8000)

## Windows Quick Start

### Option 1: One-Click Start (Easiest)

1. **Double-click** `start.bat`
2. Wait for automatic setup
3. Create admin account when prompted
4. Application opens at http://localhost:5006

### Option 2: Manual Setup

```cmd
# 1. Create virtual environment
python -m venv venv

# 2. Activate
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
python setup.py

# 5. Run application
python app.py
```

## Linux/Mac Quick Start

### Option 1: Shell Script

```bash
# Make executable
chmod +x start.sh

# Run
./start.sh
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
python setup.py

# 5. Run application
python app.py
```

## First Time Setup

### 1. Create Admin Account

During `python setup.py`, you'll be prompted:

```
👤 Create Admin User
----------------------------------------
Username: admin
Email: admin@example.com
Password: ******
Confirm Password: ******

✅ Admin user 'admin' created successfully!
```

### 2. Configure Environment (Optional)

Edit `.env` file if needed:

```env
# Default configuration works out of the box
LLM_API_URL=http://127.0.0.1:8000
PORT=5006
```

### 3. Start the Application

```bash
python app.py
```

Or with Panel serve:

```bash
panel serve app.py --show --autoreload
```

## First Login

1. **Open browser**: http://localhost:5006
2. **Login** with your admin credentials
3. **Start chatting**!

## Quick Tour

### Chat Interface

1. **Select Model**: Choose from dropdown
2. **Adjust Temperature**: 0.0 (deterministic) to 2.0 (creative)
3. **Type Message**: Enter your prompt
4. **Send**: Watch AI respond in real-time!

### Admin Dashboard (Admin Only)

1. Click **🎛️ Admin Dashboard** in sidebar
2. View statistics
3. Manage providers and models
4. Monitor usage

### Settings

1. Click **⚙️ Settings** in sidebar
2. Set default model
3. Configure preferences
4. Choose theme

## Common Tasks

### Add a New AI Provider

1. Go to **Admin Dashboard** → **Providers** tab
2. Click **➕ New Provider**
3. Fill in details:
   - Name: "My Ollama"
   - Type: "LLM"
   - API URL: "http://localhost:11434"
4. Click **💾 Save**

### Create a Project

1. Click **📁 Projects** in sidebar
2. Click **➕ New Project**
3. Name your project
4. Add description and icon

### Use System Prompts

1. Click **📝 Prompts** in sidebar
2. Browse available prompts:
   - General Assistant
   - Code Assistant
   - Writing Assistant
3. Click to use in chat

## Troubleshooting

### Issue: Can't connect to LLM API

**Solution:**
```bash
# Check if API is running
curl http://localhost:8000/healthz

# If not, start your LLM API first
```

### Issue: Database error

**Solution:**
```bash
# Delete database and recreate
rm llm_ui.db
python setup.py
```

### Issue: Port already in use

**Solution:**
```bash
# Change port in .env
PORT=5007

# Or specify when running
panel serve app.py --port 5007
```

### Issue: Module not found

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## Development Mode

For auto-reload during development:

```bash
panel serve app.py --show --autoreload --dev
```

Features:
- ✅ Auto-reload on file changes
- ✅ Debug mode enabled
- ✅ Detailed error messages

## Production Deployment

### Using Gunicorn (Linux)

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn app:app --workers 4 --bind 0.0.0.0:5006
```

### Using Docker

```bash
# Build image
docker build -t llm-ui .

# Run container
docker run -p 5006:5006 llm-ui
```

## Configuration Tips

### Connect to Different LLM API

Edit `.env`:
```env
LLM_API_URL=http://your-api-server:8000
```

### Use PostgreSQL Instead of SQLite

1. Install driver:
```bash
pip install psycopg2-binary
```

2. Update `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost/llm_ui
```

### Enable Debug Mode

Edit `.env`:
```env
DEBUG=true
```

## Next Steps

- ✅ **Explore Features**: Check FEATURES.md for full feature list
- ✅ **Read Documentation**: See README.md for detailed info
- ✅ **Understand Architecture**: Read ARCHITECTURE.md
- ✅ **Customize**: Modify styles and add features

## Getting Help

### Common Questions

**Q: How do I add more models?**
A: Go to Admin Dashboard → Models tab

**Q: Can I use OpenAI/Anthropic APIs?**
A: Yes! Add them as providers in Admin Dashboard

**Q: Is this production-ready?**
A: For internal use, yes. For public internet, add security enhancements.

**Q: Can I customize the UI?**
A: Absolutely! Edit the .py files to modify layouts and styles.

### Resources

- **Documentation**: README.md
- **Features**: FEATURES.md
- **Architecture**: ARCHITECTURE.md
- **Panel Docs**: https://panel.holoviz.org/

## Quick Reference

### File Structure

```
llm-ui/
├── app.py              # Main app (START HERE)
├── auth.py             # Login/Register
├── chat_interface.py   # Chat UI
├── admin_dashboard.py  # Admin features
├── user_pages.py       # User pages
├── llm_client.py       # API client
├── models.py           # Database
└── setup.py            # Setup script
```

### Key Commands

```bash
# Setup
python setup.py

# Run
python app.py

# Dev mode
panel serve app.py --show --autoreload

# Production
gunicorn app:app --workers 4
```

### Default Credentials

After running `setup.py`, use the credentials you created.

Example:
- Username: `admin`
- Password: `your-password`

---

**🎉 You're ready to go! Happy chatting!**

For more help, see README.md or open an issue.
