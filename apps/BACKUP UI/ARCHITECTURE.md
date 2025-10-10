# 🏗️ Architecture Documentation

## System Overview

The LLM UI is a full-stack web application built entirely in Python using the Reflex framework. It provides both an admin dashboard for managing AI services and a client interface for chatting with LLMs.

## Technology Stack

### Frontend
- **Framework**: Reflex (Python-based, compiles to React)
- **UI Components**: Radix UI (via Reflex)
- **Styling**: Tailwind CSS
- **State Management**: Reflex State
- **Real-time**: Server-Sent Events (SSE)

### Backend
- **Framework**: FastAPI (via Reflex)
- **ORM**: SQLAlchemy
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Authentication**: Session-based with password hashing
- **HTTP Client**: httpx (for LLM API communication)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              React Frontend (Generated)               │  │
│  │  - UI Components (Radix)                             │  │
│  │  - State Synchronization                             │  │
│  │  - SSE Event Handling                                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↕ WebSocket/HTTP
┌─────────────────────────────────────────────────────────────┐
│                    Reflex Backend (Python)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   State Management                    │  │
│  │  - AuthState                                         │  │
│  │  - ChatState                                         │  │
│  │  - AdminState                                        │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   FastAPI Routes                      │  │
│  │  - Authentication endpoints                          │  │
│  │  - Admin API endpoints                               │  │
│  │  - Chat API endpoints                                │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  SQLAlchemy ORM                       │  │
│  │  - User, AIProvider, AIModel                        │  │
│  │  - ChatHistory, UsageLog, etc.                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    Database (SQLite/PostgreSQL)              │
└─────────────────────────────────────────────────────────────┘
                              ↕ HTTP/SSE
┌─────────────────────────────────────────────────────────────┐
│                    LLM API Service (FastAPI)                 │
│  - /v1/chat (non-streaming)                                 │
│  - /v1/chat/stream (SSE streaming)                          │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    Ollama / LLM Provider                     │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
llm-ui/
├── llm_ui/                          # Main package
│   ├── __init__.py
│   ├── llm_ui.py                   # App definition & routes
│   ├── models.py                   # Database models (SQLAlchemy)
│   ├── auth.py                     # Authentication logic
│   ├── api_client.py               # LLM API client
│   │
│   ├── components/                 # Reusable UI components
│   │   ├── __init__.py
│   │   └── sidebar.py              # Admin & client sidebars
│   │
│   ├── pages/                      # Page components
│   │   ├── __init__.py
│   │   ├── auth.py                 # Login/Register pages
│   │   ├── chat.py                 # Chat interface
│   │   ├── admin.py                # Admin pages
│   │   └── client.py               # Client pages
│   │
│   └── states/                     # State management
│       ├── __init__.py
│       ├── chat_state.py           # Chat state & logic
│       └── admin_state.py          # Admin state & logic
│
├── assets/                          # Static assets
├── .web/                           # Generated frontend (git-ignored)
├── rxconfig.py                     # Reflex configuration
├── requirements.txt                # Python dependencies
├── setup.py                        # Setup script
├── dev.py                          # Development helper
├── .env                            # Environment variables
├── .gitignore
├── README.md
├── QUICKSTART.md
└── ARCHITECTURE.md (this file)
```

## Data Models

### User Management
- **User**: User accounts with authentication
  - email, username, password_hash
  - is_admin, created_at, last_login

### AI Configuration
- **AIProvider**: AI service providers (Ollama, OpenAI, etc.)
  - name, api_url, api_key, provider_type
  - is_active, created_at, updated_at

- **AIModel**: AI models configuration
  - name, display_name, provider_id
  - model_type, context_window, max_tokens
  - is_active, created_at

- **AIType**: AI categories/types
  - name, description, icon

### Media Configuration
- **MediaProvider**: Media generation providers
- **MediaModel**: Media generation models
- **MediaType**: Media categories

### Chat & Usage
- **ChatHistory**: Saved conversations
  - user_id, project_id, model_name
  - messages (JSON), title
  - created_at, updated_at

- **Project**: Folder organization for chats
  - user_id, name, description, icon

- **SystemPrompt**: Custom prompts library
  - user_id, name, prompt
  - is_public, tags

- **UsageLog**: Token usage tracking
  - user_id, model_name
  - input_tokens, output_tokens, total_tokens
  - cost, duration, created_at

### System Management
- **BackgroundJob**: Async task tracking
  - job_id, job_type, status, progress
  - result, error, timestamps

- **APIKey**: User API key management
  - key_name, api_key, user_id
  - is_active, expires_at, last_used

- **MonitoringLog**: System event logs
  - log_level, log_type, message
  - user_id, metadata, created_at

- **PerformanceMetric**: Performance tracking
  - metric_name, metric_value
  - model_name, endpoint, created_at

## State Management

### AuthState
Manages user authentication and session:
- Login/logout functionality
- User registration
- Session persistence
- Role-based access control

### ChatState
Manages chat interface:
- Message history
- Streaming responses (SSE)
- Model selection
- Advanced modes (thinking, browsing, attach)
- Performance metrics tracking
- Chat history persistence

### AdminState
Manages admin operations:
- Dashboard statistics
- Provider CRUD operations
- Model management
- System monitoring

## Data Flow

### Chat Flow (Streaming)
1. User types message → ChatState.current_input
2. User clicks send → ChatState.send_message()
3. Message added to ChatState.messages
4. API call to LLM API via api_client.chat_stream()
5. SSE events streamed back
6. ChatState.current_response updated token-by-token
7. Frontend re-renders on state change
8. Final metrics received and displayed
9. Chat saved to database

### Admin Provider Management Flow
1. Admin opens AI Providers page
2. AIProviderState.load_providers() fetches from DB
3. Admin fills form → AIProviderState.form_* fields
4. Admin clicks save → AIProviderState.save_provider()
5. Database updated via SQLAlchemy
6. Providers list refreshed
7. Success message displayed

## Security

### Authentication
- Passwords hashed using SHA-256
- Session-based authentication
- Role-based access control (admin/user)

### API Communication
- HTTPS recommended for production
- API keys stored encrypted in database
- Environment variables for sensitive config

### Best Practices
- Never commit `.env` file
- Change default SECRET_KEY in production
- Use strong passwords
- Regular security updates

## Performance Considerations

### Database
- SQLite for development (single file, easy setup)
- PostgreSQL recommended for production
- Indexes on frequently queried fields

### Frontend
- React components compiled by Reflex
- State changes trigger efficient re-renders
- SSE for real-time updates

### Chat Streaming
- httpx AsyncClient for non-blocking I/O
- Server-Sent Events for efficient streaming
- Token-by-token updates for smooth UX

## Deployment

### Development
```bash
reflex run
```
- Hot reload enabled
- Debug mode active
- SQLite database

### Production
```bash
reflex export
```
- Optimized build
- No hot reload
- Production database (PostgreSQL)

### Reflex Cloud
```bash
reflex deploy
```
- Automatic deployment
- Managed infrastructure
- SSL certificates included

## Extensibility

### Adding New Pages
1. Create page component in `llm_ui/pages/`
2. Add route in `llm_ui/llm_ui.py`
3. Add sidebar link if needed

### Adding New State
1. Create state class inheriting from `rx.State`
2. Define state variables and methods
3. Import and use in page components

### Adding New Models
1. Define model in `llm_ui/models.py`
2. Run `reflex db migrate`
3. Create state management if needed

### Custom Components
1. Create component in `llm_ui/components/`
2. Define props and rendering logic
3. Import and use in pages

## Testing Strategy

### Manual Testing
- User registration and login
- Chat functionality with streaming
- Admin CRUD operations
- Database persistence

### Automated Testing (Future)
- Unit tests for state methods
- Integration tests for API calls
- E2E tests with Playwright

## Monitoring

### Logs
- Application logs in console
- Database query logs (debug mode)
- Error tracking

### Metrics
- Performance metrics in database
- Usage statistics
- System health checks

## Future Enhancements

### Planned Features
- File upload support
- Web browsing integration
- Dark mode
- Multi-language support
- Advanced analytics
- Team collaboration
- Model fine-tuning UI

### Technical Debt
- Add comprehensive error handling
- Implement retry logic for API calls
- Add request caching
- Optimize database queries
- Add automated tests

## Contributing

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions
- Keep functions small and focused

### Git Workflow
- Feature branches for new features
- PR review before merge
- Semantic versioning

---

**Last Updated**: 2025-10-07
