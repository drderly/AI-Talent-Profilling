# 🏗️ LLM UI Architecture

## Overview

LLM UI is a pure Python web application built using **Panel (HoloViz)** that provides a modern, feature-rich interface for interacting with Large Language Models. The architecture follows a modular design with clear separation of concerns.

## Technology Stack

### Frontend (UI Layer)
- **Panel (HoloViz)**: Python-based web framework for creating interactive dashboards
- **Bokeh**: Underlying visualization library used by Panel
- **Material Design**: Design system for consistent UI components
- **Server-Sent Events (SSE)**: Real-time streaming for chat responses

### Backend (Data Layer)
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Default database (production-ready with PostgreSQL/MySQL support)
- **httpx**: Modern async HTTP client for API communication

### Security
- **SHA-256**: Password hashing
- **Session Management**: Custom session handling with timeout
- **Role-Based Access Control (RBAC)**: Admin and User roles

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser (Client)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Panel UI (Bokeh Server)                  │   │
│  │  - Material Design Components                         │   │
│  │  - Real-time Updates via WebSocket                    │   │
│  │  - SSE for Streaming Chat                             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/WebSocket
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Panel Application Server                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    app.py (Main)                        │ │
│  │  - Application State Management                         │ │
│  │  - Routing and Navigation                               │ │
│  │  - Layout Orchestration                                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│  ┌─────────────────┬──────┴────────┬───────────────────┐   │
│  │                 │                │                    │   │
│  ▼                 ▼                ▼                    ▼   │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│ │   Auth   │  │   Chat   │  │  Admin   │  │   User   │    │
│ │ (auth.py)│  │(chat_    │  │(admin_   │  │(user_    │    │
│ │          │  │interface)│  │dashboard)│  │pages.py) │    │
│ │- Login   │  │- Stream  │  │- Manage  │  │- Settings│    │
│ │- Register│  │- History │  │- Monitor │  │- Projects│    │
│ │- Session │  │- Metrics │  │- Users   │  │- Profile │    │
│ └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│      │             │              │              │           │
│      └─────────────┴──────────────┴──────────────┘           │
│                            │                                 │
│  ┌─────────────────────────┴──────────────────────────────┐ │
│  │              Business Logic Layer                       │ │
│  │  ┌──────────────┐        ┌──────────────┐             │ │
│  │  │  LLM Client  │        │    Models    │             │ │
│  │  │(llm_client.py)│        │  (models.py) │             │ │
│  │  │              │        │              │             │ │
│  │  │- API Calls   │        │- Database    │             │ │
│  │  │- Streaming   │        │  Models      │             │ │
│  │  │- Error       │        │- ORM Ops     │             │ │
│  │  │  Handling    │        │- Seed Data   │             │ │
│  │  └──────┬───────┘        └──────┬───────┘             │ │
│  └─────────┼────────────────────────┼─────────────────────┘ │
└────────────┼────────────────────────┼───────────────────────┘
             │                        │
             │                        │
         ┌───┴────────┐         ┌────┴─────┐
         │  LLM API   │         │ Database │
         │  Server    │         │ (SQLite/ │
         │ (FastAPI)  │         │ PostgreSQL)│
         │            │         │          │
         │- /v1/chat  │         │- Users   │
         │- /v1/chat/ │         │- Chats   │
         │  stream    │         │- Models  │
         │- /healthz  │         │- Logs    │
         └────────────┘         └──────────┘
```

## Module Structure

### 1. app.py - Main Application
**Responsibilities:**
- Application initialization
- State management
- Routing and navigation
- Layout composition
- Authentication flow

**Key Components:**
- `AppState`: Global application state
- `create_sidebar()`: Navigation sidebar
- `create_main_content()`: Content router
- `create_auth_layout()`: Authentication pages
- `main()`: Entry point

### 2. auth.py - Authentication System
**Responsibilities:**
- User authentication
- Session management
- Password hashing and verification
- Login/Register UI

**Key Components:**
- `SessionManager`: Session lifecycle management
- `AuthState`: Authentication state
- `hash_password()`: SHA-256 hashing
- `verify_password()`: Password validation
- `create_login_page()`: Login UI
- `create_register_page()`: Registration UI

### 3. chat_interface.py - Chat UI
**Responsibilities:**
- Chat conversation display
- Message streaming
- User input handling
- Performance metrics
- Chat history management

**Key Components:**
- `ChatState`: Chat state management
- `ChatMessage`: Message model
- `create_message_bubble()`: Message UI
- `create_chat_interface()`: Main chat layout
- Async message handling with streaming

### 4. admin_dashboard.py - Admin Features
**Responsibilities:**
- Admin dashboard
- Provider management
- Model configuration
- User management
- Usage monitoring

**Key Components:**
- `create_admin_overview()`: Statistics dashboard
- `create_provider_management()`: Provider CRUD
- `create_model_management()`: Model configuration
- `create_users_management()`: User administration
- `create_prompts_library()`: System prompts
- `create_usage_monitoring()`: Usage analytics

### 5. user_pages.py - User Features
**Responsibilities:**
- User settings
- Project management
- Profile display
- Chat history

**Key Components:**
- `create_settings_page()`: User preferences
- `create_projects_page()`: Project organization
- `create_profile_page()`: User profile
- `create_chat_history_page()`: Chat history viewer

### 6. llm_client.py - API Client
**Responsibilities:**
- LLM API communication
- HTTP request handling
- Streaming response processing
- Error handling

**Key Components:**
- `LLMClient`: API client class
- `health_check()`: API health verification
- `chat()`: Non-streaming chat
- `chat_stream()`: Streaming chat with SSE
- `format_messages()`: Message formatting

### 7. models.py - Database Layer
**Responsibilities:**
- Database schema definition
- ORM models
- Database initialization
- Data seeding

**Key Models:**
- `User`: User accounts
- `AIProvider`: LLM service providers
- `AIModel`: Available models
- `AIType`: Model categories
- `ChatHistory`: Conversation storage
- `Project`: Chat organization
- `SystemPrompt`: Reusable prompts
- `UsageLog`: Usage tracking
- `MonitoringLog`: System logs
- `PerformanceMetric`: Performance data
- `BackgroundJob`: Job tracking
- `APIKey`: API key management

## Data Flow

### 1. Authentication Flow

```
User Input (Login)
    ↓
AuthState.login()
    ↓
Query User from Database
    ↓
Verify Password Hash
    ↓
SessionManager.create_session()
    ↓
Update AuthState
    ↓
Trigger UI Update
    ↓
Redirect to Main App
```

### 2. Chat Message Flow

```
User Types Message
    ↓
ChatState.send_message_async()
    ↓
Add User Message to State
    ↓
Format Messages for API
    ↓
LLMClient.chat_stream()
    ↓
HTTP POST to /v1/chat/stream
    ↓
Receive SSE Events
    ↓
Update Assistant Message in Real-time
    ↓
Display Performance Metrics
    ↓
Save Chat to Database
    ↓
Update UI
```

### 3. Admin Management Flow

```
Admin Opens Provider Management
    ↓
Query AIProviders from Database
    ↓
Display in Tabulator Widget
    ↓
Admin Creates New Provider
    ↓
Validate Form Input
    ↓
Create AIProvider Record
    ↓
Save to Database
    ↓
Show Success Notification
    ↓
Refresh Table
```

## State Management

### Application State Hierarchy

```
AppState (Global)
  ├── current_page: str
  └── AuthState
      ├── is_authenticated: bool
      ├── session_id: str
      ├── username: str
      ├── email: str
      └── role: UserRole

ChatState (Per Chat)
  ├── messages: List[ChatMessage]
  ├── is_streaming: bool
  ├── selected_model: str
  ├── temperature: float
  ├── max_tokens: int
  └── performance_metrics: dict
```

### State Synchronization

Panel uses **reactive parameters** for state management:
- Changes to state automatically trigger UI updates
- Bidirectional data binding with widgets
- Observer pattern for component updates

```python
# Example: Temperature slider linked to state
temperature_slider.link(chat_state, value="temperature")

# Watcher for state changes
chat_state.param.watch(update_ui, "messages")
```

## Database Schema

### Core Tables

**users**
- id (PK)
- username (unique)
- email (unique)
- password_hash
- role (enum: USER, ADMIN)
- is_active
- created_at, updated_at

**ai_providers**
- id (PK)
- name
- ai_type_id (FK → ai_types)
- api_url
- api_key
- is_active
- created_at, updated_at

**ai_models**
- id (PK)
- name
- provider_id (FK → ai_providers)
- model_id
- context_window
- max_tokens
- is_active
- created_at, updated_at

**chat_histories**
- id (PK)
- user_id (FK → users)
- project_id (FK → projects)
- model_id (FK → ai_models)
- title
- messages (JSON)
- temperature, max_tokens, context_window
- created_at, updated_at

### Relationships

```
User 1──N ChatHistory
User 1──N Project
User 1──N UsageLog

AIProvider 1──N AIModel
AIType 1──N AIProvider

Project 1──N ChatHistory
AIModel 1──N ChatHistory
```

## Security Architecture

### Authentication
- **Password Hashing**: SHA-256 with no salt (consider upgrading to bcrypt)
- **Session Management**: In-memory session store with timeout
- **Session Timeout**: 24 hours default

### Authorization
- **Role-Based Access Control (RBAC)**
  - USER: Access to chat, projects, settings
  - ADMIN: Additional access to admin dashboard, user management

### Input Validation
- Form validation on client side
- Server-side validation in state handlers
- SQL injection prevention via SQLAlchemy ORM

### Best Practices for Production
1. Use bcrypt or Argon2 for password hashing
2. Implement CSRF protection
3. Use HTTPS for all communication
4. Add rate limiting
5. Store sessions in Redis or database
6. Add audit logging
7. Implement API key rotation

## Communication Protocols

### WebSocket (Panel ↔ Browser)
- Real-time UI updates
- Bidirectional communication
- Parameter synchronization
- Event handling

### Server-Sent Events (SSE) (Panel ↔ LLM API)
- Unidirectional streaming
- Chat response tokens
- Performance metrics
- Done signal with metadata

### HTTP/REST (Panel ↔ LLM API)
- Health checks
- Non-streaming chat
- Model queries

## Performance Considerations

### Optimization Strategies

1. **Database**
   - Use connection pooling
   - Index frequently queried columns
   - Lazy loading for relationships
   - Consider PostgreSQL for production

2. **UI Updates**
   - Batch message updates
   - Virtual scrolling for long chats
   - Debounce user input
   - Lazy load chat history

3. **Streaming**
   - Efficient SSE parsing
   - Minimal per-token overhead
   - Async/await for non-blocking I/O

4. **Caching**
   - Cache model lists
   - Cache system prompts
   - Session caching

### Resource Usage

- **Memory**: ~50-200MB per user session
- **Database**: Grows with chat history
- **Network**: Streaming keeps connection open

## Deployment Architecture

### Development

```
Local Machine
├── Panel Server (port 5006)
├── LLM API (port 8000)
└── SQLite Database (file)
```

### Production

```
┌─────────────────────────────────────┐
│         Nginx (Reverse Proxy)        │
│         - SSL Termination            │
│         - Load Balancing             │
└─────────────┬───────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────┐         ┌────▼───┐
│ Panel  │         │ Panel  │
│ Server │   ...   │ Server │
│   #1   │         │   #N   │
└───┬────┘         └────┬───┘
    │                   │
    └─────────┬─────────┘
              │
    ┌─────────▼─────────┐
    │   PostgreSQL DB   │
    │   - Primary       │
    │   - Replicas      │
    └───────────────────┘
```

## Extension Points

### Adding New AI Providers

1. Add provider configuration in admin dashboard
2. Create provider entry in database
3. Add models for the provider
4. LLM client handles communication

### Adding New Features

1. **New Page**: Create page function, add to navigation
2. **New Widget**: Use Panel components library
3. **New Database Table**: Add model to models.py, run migrations
4. **New API Endpoint**: Extend LLMClient

### Plugin Architecture (Future)

Consider implementing:
- Plugin loader system
- Event hooks for extensions
- Custom widget registration
- Theme plugins

## Testing Strategy

### Unit Tests
- Test state management logic
- Test database models
- Test authentication functions
- Test API client methods

### Integration Tests
- Test full authentication flow
- Test chat message flow
- Test admin operations
- Test database transactions

### E2E Tests
- Use Playwright or Selenium
- Test user workflows
- Test admin workflows
- Test error scenarios

## Monitoring and Logging

### Application Monitoring
- Performance metrics collection
- Usage log tracking
- Error logging
- Health checks

### Database Monitoring
- Query performance
- Connection pool stats
- Table sizes
- Index usage

### User Activity
- Login events
- Chat creation
- Token usage
- Error occurrences

## Scalability Considerations

### Horizontal Scaling
- Stateless Panel servers
- Shared session storage (Redis)
- Database connection pooling
- Load balancer required

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Use caching layers
- Upgrade to PostgreSQL

### Bottlenecks
- Database I/O
- LLM API latency
- WebSocket connections
- Session storage

## Future Architecture Improvements

1. **Microservices**: Separate chat, admin, auth services
2. **Message Queue**: Async job processing (Celery/RQ)
3. **Caching Layer**: Redis for sessions and frequently accessed data
4. **CDN**: Static asset delivery
5. **Containerization**: Docker/Kubernetes deployment
6. **API Gateway**: Unified API management
7. **Observability**: OpenTelemetry integration

---

**Architecture Version**: 1.0
**Last Updated**: 2025-10-08
**Target**: Pure Python Implementation with Panel (HoloViz)
