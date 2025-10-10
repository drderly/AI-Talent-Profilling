# LLM Service UI

A modern, feature-rich web UI for managing and interacting with LLM services. Built entirely in **Python** using the **Reflex** framework.

## 🌟 Features

### Admin Dashboard
- **📊 Dashboard**: Overview of system statistics and recent activity
- **🤖 AI Providers**: Manage AI service providers (Ollama, OpenAI, Anthropic, etc.)
- **🧠 AI Models**: Configure and manage AI models
- **📁 AI Types**: Categorize AI capabilities
- **🎨 Media Providers**: Manage media generation services
- **🖼️ Media Models**: Configure media generation models
- **📋 Media Types**: Categorize media capabilities
- **⚙️ Background Jobs**: Monitor async tasks
- **🔑 API Keys**: Manage user API keys
- **📝 Monitoring Logs**: System event logs
- **📈 Performance Metrics**: Track system performance
- **📊 Usage Logs**: Monitor API usage

### Client Dashboard
- **💬 Chat Interface**: 
  - Real-time streaming with SSE support
  - Thinking mode for step-by-step reasoning
  - Browsing mode (placeholder for web search)
  - Attach mode for file uploads
  - Model selector with multiple models
  - Performance metrics display (TTFT, latency, tokens/sec)
  - Context window configuration
- **📁 Projects**: Organize chats into folders
- **📝 System Prompts**: Create and manage custom prompts
- **👤 Profile**: User account management
- **⚙️ Settings**: Configure chat preferences
- **📊 Usage Monitoring**: Track token usage and costs
- **📝 Activity Logs**: View your activity history

### Authentication
- User registration and login
- Password hashing with SHA-256
- Role-based access (Admin/User)
- Session management

## 🚀 Technology Stack

- **Framework**: [Reflex](https://reflex.dev) - Full-stack Python web framework
- **Backend**: FastAPI (via Reflex)
- **Frontend**: React components (via Reflex)
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy
- **Styling**: Tailwind CSS
- **Real-time**: Server-Sent Events (SSE)

## 📋 Prerequisites

- Python 3.10 or higher
- Node.js 16+ (automatically managed by Reflex)
- LLM API service running (see `../llm-api`)
- [Ollama](https://ollama.ai/) or other LLM provider

## 🔧 Installation

### 1. Navigate to the UI directory
```bash
cd apps/llm-ui
```

### 2. Create virtual environment
```bash
python -m venv .venv
```

### 3. Activate virtual environment
**Windows:**
```bash
.venv\Scripts\Activate.ps1  # PowerShell
# or
.venv\Scripts\activate.bat  # CMD
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your configuration
# Notepad .env (Windows) or nano .env (Linux/Mac)
```

### 6. Initialize Reflex
```bash
reflex init
```

This will:
- Install Node.js dependencies
- Set up the `.web` directory
- Prepare the frontend build

### 7. Initialize database
```bash
reflex db init
reflex db migrate
```

## 🎮 Usage

### Start the development server
```bash
reflex run
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

### Create admin user
You'll need to manually create an admin user in the database or use the registration page and then update the `is_admin` field in the database.

**Using Python:**
```python
import reflex as rx
from llm_ui.models import User
from llm_ui.auth import hash_password
from datetime import datetime

with rx.session() as session:
    admin = User(
        email="admin@example.com",
        username="admin",
        password_hash=hash_password("your-secure-password"),
        is_admin=True,
        created_at=datetime.now()
    )
    session.add(admin)
    session.commit()
```

### Production deployment
```bash
# Build for production
reflex export

# Or deploy to Reflex Cloud
reflex deploy
```

## 📁 Project Structure

```
llm-ui/
├── llm_ui/                      # Main application package
│   ├── __init__.py
│   ├── llm_ui.py               # Main app with routes
│   ├── models.py               # Database models
│   ├── auth.py                 # Authentication logic
│   ├── api_client.py           # LLM API client
│   ├── components/             # Reusable UI components
│   │   ├── __init__.py
│   │   └── sidebar.py          # Navigation sidebars
│   ├── pages/                  # Page components
│   │   ├── __init__.py
│   │   ├── auth.py             # Login/Register pages
│   │   ├── chat.py             # Chat interface
│   │   ├── admin.py            # Admin pages
│   │   └── client.py           # Client pages
│   └── states/                 # State management
│       ├── __init__.py
│       ├── chat_state.py       # Chat state
│       └── admin_state.py      # Admin state
├── assets/                      # Static assets
├── rxconfig.py                  # Reflex configuration
├── requirements.txt             # Python dependencies
├── .env.example                # Example environment variables
├── .gitignore
└── README.md
```

## 🔑 Configuration

### Environment Variables

Edit `.env` file:

```env
# LLM API Configuration
LLM_API_URL=http://127.0.0.1:8000
LLM_API_KEY=your-api-key-here

# Database Configuration
DATABASE_URL=sqlite:///llm_ui.db
# For production:
# DATABASE_URL=postgresql://user:password@localhost:5432/llm_ui

# Application Configuration
APP_NAME=LLM Service Dashboard
SECRET_KEY=your-secret-key-here-change-in-production

# Admin Credentials (for initial setup)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-this-password
```

## 🎨 Features in Detail

### Chat Interface
- **Streaming**: Real-time token streaming using SSE
- **Performance Metrics**: Display TTFT, latency, tokens/sec
- **Multiple Models**: Switch between different LLM models
- **Chat History**: Automatic saving to database
- **Advanced Modes**:
  - 🤔 **Thinking Mode**: Shows step-by-step reasoning
  - 🌐 **Browsing Mode**: Web search integration (placeholder)
  - 📎 **Attach Mode**: File upload support (placeholder)

### Admin Features
- **Provider Management**: Add/edit/delete AI providers
- **Model Configuration**: Configure models with custom settings
- **Real-time Monitoring**: Track system performance
- **Usage Analytics**: Monitor token usage and costs

## 🚧 Roadmap

- [ ] Implement file upload (Attach mode)
- [ ] Add web browsing capabilities
- [ ] Implement API key generation UI
- [ ] Add charts for analytics
- [ ] Dark mode support
- [ ] Multi-language support
- [ ] Export chat history
- [ ] Model comparison tool
- [ ] Custom model fine-tuning UI
- [ ] Team collaboration features

## 🐛 Troubleshooting

### Reflex won't start
```bash
# Clear Reflex cache
rm -rf .web
reflex init
```

### Database errors
```bash
# Reset database (WARNING: deletes all data)
rm llm_ui.db
reflex db init
reflex db migrate
```

### Port already in use
```bash
# Change port in rxconfig.py or kill the process using the port
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

### Can't connect to LLM API
- Ensure the LLM API service is running on `http://127.0.0.1:8000`
- Check `LLM_API_URL` in `.env`
- Verify Ollama is running: `ollama serve`

## 📚 Documentation

- [Reflex Documentation](https://reflex.dev/docs/getting-started/introduction/)
- [Reflex Components](https://reflex.dev/docs/library/)
- [LLM API Documentation](../llm-api/README.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License

## 💡 Tips

1. **Development**: Use `reflex run --loglevel debug` for detailed logs
2. **Performance**: In production, use PostgreSQL instead of SQLite
3. **Security**: Always change the default SECRET_KEY in production
4. **Backup**: Regularly backup your database
5. **Updates**: Keep Reflex updated: `pip install --upgrade reflex`

## 🆘 Support

For issues and questions:
- Check the [Reflex Forum](https://forum.reflex.dev)
- Open an issue on GitHub
- Check the Reflex Discord community

---

**Built with ❤️ using Python and Reflex**
