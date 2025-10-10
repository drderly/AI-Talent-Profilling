# 🔧 Troubleshooting Guide

## Login Issues

### Problem: Can't Login / Invalid Email or Password

#### Solution 1: Check if Users Exist

Run the diagnostic script:
```bash
python check_users.py
```

This will:
- Show all users in the database
- Indicate if no users exist
- Offer to create an admin user

#### Solution 2: Create a Test User

Run the quick test user creation script:
```bash
python create_test_user.py
```

This creates a test admin account:
- **Email**: `admin@test.com`
- **Password**: `admin123`

#### Solution 3: Run Full Setup

If you haven't run setup yet:
```bash
python setup.py
```

This will:
- Initialize the database
- Seed default data
- Prompt you to create an admin user

#### Solution 4: Reset Database

If database is corrupted:
```bash
# Windows
del llm_ui.db
python setup.py

# Linux/Mac
rm llm_ui.db
python setup.py
```

### Common Login Mistakes

1. **Wrong Email Format**
   - ❌ Using username instead of email
   - ✅ Use the full email (e.g., `admin@test.com`)

2. **Password Case Sensitive**
   - Passwords are case-sensitive
   - Make sure Caps Lock is off

3. **Account Not Active**
   - Check if `is_active` is True in database
   - Run `python check_users.py` to verify

## Database Issues

### Problem: Database Not Found

**Error**: `no such table: users`

**Solution**:
```bash
python setup.py
```

### Problem: Database Locked

**Error**: `database is locked`

**Solution**:
```bash
# Stop the application
# Then delete and recreate database
del llm_ui.db  # Windows
rm llm_ui.db   # Linux/Mac
python setup.py
```

## Application Won't Start

### Problem: Module Not Found

**Error**: `ModuleNotFoundError: No module named 'panel'`

**Solution**:
```bash
# Make sure virtual environment is activated
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Option 1: Change port in .env
PORT=5007

# Option 2: Kill the process using port 5006
# Windows
netstat -ano | findstr :5006
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5006 | xargs kill -9
```

### Problem: Import Error

**Error**: `cannot import name 'X' from 'Y'`

**Solution**:
```bash
# Reinstall all dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt --upgrade
```

## Connection Issues

### Problem: Can't Connect to LLM API

**Error**: Connection refused / API not responding

**Solution**:
```bash
# Check if LLM API is running
curl http://localhost:8000/healthz

# If not running, start it
cd ../llm-api
python main.py
```

**Update API URL** in `.env`:
```env
LLM_API_URL=http://127.0.0.1:8000
```

### Problem: CORS Errors

If you see CORS errors in browser console:

**Solution**: Make sure both UI and API are running on same machine or configure CORS in the API.

## UI Issues

### Problem: Blank Page / White Screen

**Solutions**:
1. Check browser console for errors (F12)
2. Clear browser cache
3. Try a different browser
4. Restart the application

### Problem: Streaming Not Working

**Symptoms**: Messages don't appear in real-time

**Solutions**:
1. Check if LLM API supports streaming
2. Verify `/v1/chat/stream` endpoint is working
3. Check browser console for WebSocket errors

### Problem: UI Not Updating

**Solution**:
```bash
# Run with autoreload
panel serve app.py --show --autoreload
```

## Performance Issues

### Problem: Slow Response

**Solutions**:
1. Check LLM API response time
2. Reduce model size
3. Lower max_tokens setting
4. Use PostgreSQL instead of SQLite for production

### Problem: High Memory Usage

**Solutions**:
1. Clear old sessions
2. Limit chat history length
3. Restart application periodically

## Development Issues

### Problem: Changes Not Reflected

**Solution**:
```bash
# Use autoreload during development
panel serve app.py --show --autoreload --dev
```

### Problem: Database Schema Changed

**Solution**:
```bash
# Option 1: Delete and recreate
del llm_ui.db
python setup.py

# Option 2: Use migrations (advanced)
# Install alembic
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "changes"
alembic upgrade head
```

## Quick Diagnostics

### Run Full Diagnostic

```bash
# 1. Check users
python check_users.py

# 2. Create test user if needed
python create_test_user.py

# 3. Verify LLM API
curl http://localhost:8000/healthz

# 4. Check if database exists
# Windows: dir llm_ui.db
# Linux/Mac: ls -la llm_ui.db
```

### Verify Installation

```python
# test_install.py
import sys
print(f"Python: {sys.version}")

try:
    import panel as pn
    print(f"✅ Panel: {pn.__version__}")
except:
    print("❌ Panel not installed")

try:
    import sqlalchemy
    print(f"✅ SQLAlchemy: {sqlalchemy.__version__}")
except:
    print("❌ SQLAlchemy not installed")

try:
    import httpx
    print(f"✅ httpx: {httpx.__version__}")
except:
    print("❌ httpx not installed")

print("\n✅ All core dependencies installed!")
```

Run: `python test_install.py`

## Getting More Help

### Enable Debug Mode

Edit `.env`:
```env
DEBUG=true
```

This will show detailed error messages.

### Check Logs

Look for error messages in the terminal where you ran the application.

### Common Error Messages

1. **"Invalid email or password"**
   - User doesn't exist OR wrong password
   - Run `python check_users.py`

2. **"Account is inactive"**
   - User exists but `is_active=False`
   - Update database or create new user

3. **"Email and password are required"**
   - Form fields are empty
   - Make sure you filled both fields

4. **"Username or email already exists"**
   - During registration
   - Try a different username/email or login instead

## Still Having Issues?

1. **Delete everything and start fresh**:
```bash
# Stop the application
# Delete database
del llm_ui.db  # or rm llm_ui.db

# Recreate virtual environment
# Windows
rmdir /s venv
python -m venv venv
venv\Scripts\activate

# Linux/Mac
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Reinstall
pip install -r requirements.txt
python setup.py
python app.py
```

2. **Check file permissions**: Make sure you have write permissions in the directory

3. **Try a different database**: Use PostgreSQL instead of SQLite

4. **Verify Python version**: Requires Python 3.9+
```bash
python --version
```

## Quick Reference: Common Commands

```bash
# Check users in database
python check_users.py

# Create test user (admin@test.com / admin123)
python create_test_user.py

# Full setup with admin creation
python setup.py

# Start application
python app.py

# Start with autoreload (development)
panel serve app.py --show --autoreload

# Reset database
del llm_ui.db && python setup.py  # Windows
rm llm_ui.db && python setup.py   # Linux/Mac

# Check if port is available
netstat -ano | findstr :5006  # Windows
lsof -i :5006                 # Linux/Mac
```

---

**Most Common Fix**: If you can't login, run:
```bash
python create_test_user.py
```

Then login with:
- Email: `admin@test.com`
- Password: `admin123`
