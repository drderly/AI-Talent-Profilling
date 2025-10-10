# 🤖 LLM UI - Pure Python Interface

A modern, feature-rich LLM (Large Language Model) chat interface built entirely in Python using **Panel (HoloViz)** - no Node.js, no React, no JavaScript frameworks required!

## ✨ Features

### 🔐 Authentication & User Management
- User registration and login
- Password hashing (SHA-256)
- Session management
- Role-based access control (Admin/User)
- User profiles with avatars

### 💬 Chat Interface
- **Real-time streaming** with Server-Sent Events (SSE)
- Message history with timestamps
- User and AI message bubbles
- Model selector dropdown
- Temperature control (0.0 - 2.0)
- Max tokens configuration
- Context window settings
- Clear chat functionality
- New chat creation
- Thinking mode toggle
- Auto-save chat history
- **Performance metrics display:**
  - Time to First Token (TTFT)
  - Total latency
  - Tokens per second
  - Input/Output token counts

### 🎛️ Admin Dashboard
- **Overview** with statistics cards
  - Total users, chats, API calls, tokens
- **AI Provider Management**
  - Create, edit, delete providers
  - Support for Ollama, OpenAI, Anthropic, etc.
  - API URL and key configuration
  - Active/inactive status toggle
- **AI Model Management**
  - Link models to providers
  - Configure context window and max tokens
  - Activate/deactivate models
- **User Management**
  - View all users
  - User statistics
- **System Prompts Library**
  - Reusable prompt templates
  - Public/private prompts
  - Tags and descriptions
- **Usage Monitoring**
  - Token usage tracking
  - Cost monitoring
  - Conversation statistics

### 📁 Organization
- **Projects** for organizing chats
- **Chat History** with search and filtering
- **System Prompts** library

### ⚙️ Settings
- Default model selection
- Context window configuration
- Temperature settings
- Theme selector (Light/Dark/Auto)
- Language preferences

### 📊 Database Models
- User
- AIProvider
- AIModel
- AIType
- ChatHistory
- Project
- SystemPrompt
- UsageLog
- MonitoringLog
- PerformanceMetric
- BackgroundJob
- APIKey

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- LLM API server running (e.g., the FastAPI Ollama wrapper)

### Installation

1. **Clone the repository:**
```bash
cd apps/llm-ui
```

2. **Create a virtual environment:**
```bash
python -m venv venv
```

3. **Activate the virtual environment:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Create environment file:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your settings
```

6. **Run setup script:**
```bash
python setup.py
```
This will:
- Initialize the database
- Create tables
- Seed initial data (AI types, providers, models, prompts)
- Optionally create an admin user

### Running the Application

**Method 1: Direct Python execution**
```bash
python app.py
```

**Method 2: Panel serve (recommended for development)**
```bash
panel serve app.py --show --autoreload
```

The application will be available at: http://localhost:5006

## 🏗️ Architecture

### Tech Stack
- **UI Framework:** Panel (HoloViz) - Pure Python dashboards
- **Database:** SQLAlchemy with SQLite (easily swappable to PostgreSQL/MySQL)
- **HTTP Client:** httpx for async API calls
- **Authentication:** Custom session management with password hashing
- **Design:** Material Design components

### Project Structure
```
llm-ui/
├── app.py                  # Main application entry point
├── auth.py                 # Authentication and session management
├── models.py               # Database models (SQLAlchemy)
├── chat_interface.py       # Chat UI with streaming
├── admin_dashboard.py      # Admin pages and management
├── user_pages.py           # User settings, projects, profile
├── llm_client.py          # LLM API client
├── setup.py               # Setup and initialization script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
└── FEATURES.md           # Detailed feature checklist
```

## 🔧 Configuration

### Environment Variables

Edit `.env` file:

```env
# Database
DATABASE_URL=sqlite:///./llm_ui.db

# LLM API Configuration
LLM_API_URL=http://127.0.0.1:8000

# Server Configuration
HOST=127.0.0.1
PORT=5006
DEBUG=true

# Session Configuration
SESSION_TIMEOUT_HOURS=24
```

### Database Configuration

By default, SQLite is used. To use PostgreSQL or MySQL:

1. Update `DATABASE_URL` in `.env`:
```env
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/llm_ui

# MySQL
DATABASE_URL=mysql+pymysql://user:password@localhost/llm_ui
```

2. Install appropriate driver:
```bash
# PostgreSQL
pip install psycopg2-binary

# MySQL
pip install pymysql
```

## 📚 Usage

### Creating an Account

1. Navigate to the login page
2. Click "Register here"
3. Fill in username, email, and password
4. Click "Register"
5. Return to login and sign in

### Using the Chat Interface

1. **Select a Model:** Choose from available AI models
2. **Adjust Settings:** 
   - Temperature: Controls randomness (0.0 = deterministic, 2.0 = very random)
   - Max Tokens: Maximum response length
3. **Enable Thinking Mode:** For step-by-step reasoning
4. **Type Message:** Enter your prompt
5. **Send:** Watch the AI respond in real-time with streaming

### Admin Features

Admins have access to:
- **Provider Management:** Add Ollama, OpenAI, Anthropic endpoints
- **Model Configuration:** Configure available models
- **User Management:** View and manage users
- **Monitoring:** Track usage and performance

### Managing Projects

1. Navigate to "Projects" from sidebar
2. Create new projects to organize chats
3. Assign chats to projects

### System Prompts

Use pre-configured prompts for common tasks:
- General Assistant
- Code Assistant
- Writing Assistant
- Custom prompts (create your own)

## 🔌 API Integration

The UI connects to your LLM API server. Ensure the API has these endpoints:

- `GET /healthz` - Health check
- `POST /v1/chat` - Non-streaming chat
- `POST /v1/chat/stream` - Streaming chat (SSE)

See the included FastAPI Ollama wrapper in `apps/llm-api/` for reference.

## 🎨 Customization

### Adding New Pages

1. Create page function in appropriate module
2. Add navigation button in `create_sidebar()` in `app.py`
3. Add page handler in `update_content()` in `app.py`

### Custom Themes

Edit styles in components:
```python
styles={
    "background": "#f5f5f5",
    "padding": "20px",
    "border-radius": "8px"
}
```

## 🧪 Development

### Running in Development Mode

```bash
panel serve app.py --show --autoreload --dev
```

### Database Migrations

For schema changes, consider using Alembic:

```bash
# Initialize
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## 🐛 Troubleshooting

### Database Issues

**Problem:** Database locked
```bash
# Solution: Close all connections and restart
rm llm_ui.db
python setup.py
```

### Connection Issues

**Problem:** Cannot connect to LLM API
```bash
# Solution: Verify API is running
curl http://localhost:8000/healthz

# Check .env configuration
LLM_API_URL=http://127.0.0.1:8000
```

### Import Errors

**Problem:** Module not found
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## 📈 Performance

### Optimization Tips

1. **Use PostgreSQL** for production (faster than SQLite)
2. **Enable caching** for frequently accessed data
3. **Limit chat history** display (paginate old messages)
4. **Use connection pooling** for database

### Streaming Performance

The SSE streaming provides:
- **Low latency:** Tokens appear as generated
- **Responsive UI:** Non-blocking interface
- **Metrics tracking:** Real-time performance data

## 🔒 Security

### Best Practices

1. **Change default secrets** in production
2. **Use HTTPS** for production deployment
3. **Enable CORS** restrictions
4. **Regular updates** of dependencies
5. **Database backups** regularly

### Password Security

- Passwords hashed with SHA-256
- No plaintext storage
- Session timeout after 24 hours

## 🚀 Deployment

### Production Deployment

1. **Use a production WSGI server:**
```bash
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:5006
```

2. **Set up reverse proxy (nginx):**
```nginx
location / {
    proxy_pass http://localhost:5006;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

3. **Use environment variables:**
```bash
export DATABASE_URL=postgresql://...
export DEBUG=false
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python setup.py

CMD ["panel", "serve", "app.py", "--port", "5006", "--address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t llm-ui .
docker run -p 5006:5006 llm-ui
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional AI provider integrations
- Enhanced UI components
- Performance optimizations
- Testing coverage
- Documentation

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Panel (HoloViz)** - Amazing Python dashboard framework
- **SQLAlchemy** - Powerful ORM
- **FastAPI** - Modern API framework (for backend)

## 📞 Support

For issues and questions:
- Check the FEATURES.md for implementation status
- Review troubleshooting section
- Open an issue on GitHub

## 🗺️ Roadmap

See FEATURES.md for detailed feature status and roadmap.

**High Priority:**
- File upload support
- Web browsing integration
- Dark mode implementation
- Mobile responsive design
- Export chat functionality

**Medium Priority:**
- Multi-user chat rooms
- Prompt templates library
- Model comparison tool
- Advanced analytics

**Future:**
- Plugin system
- Voice input/output
- Multi-language support
- Native mobile apps

---

**Built with ❤️ using 100% Python - No JavaScript Required!**
