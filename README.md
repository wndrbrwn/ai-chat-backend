# AI Chat Backend

A session-based AI chat backend built with **FastAPI, SQLite, and OpenRouter**.

This project provides RESTful APIs for AI conversations, persistent chat history, and session management. Conversation history is stored in SQLite and remains available after server restarts.

## Tech Stack

- **Language:** Python
- **Backend:** FastAPI
- **Database:** SQLite
- **LLM API:** OpenRouter (accessed through the OpenAI Python SDK)
- **AI Model:** `openrouter/free`
- **API Documentation:** Swagger UI

## Features

- **AI Chat:** Generate AI responses using the OpenRouter API.
- **Session Management:** Maintain separate conversation histories using session IDs.
- **Persistent Storage:** Store conversation history in SQLite, preserving data across server restarts.
- **Conversation Context:** Send the most recent 6 messages as context to the AI.
- **Atomic Message Storage:** Save user messages and AI responses within a single database transaction.
- **Input Validation:** Reject empty or whitespace-only session IDs and questions.
- **Error Handling:** Return appropriate HTTP status codes for invalid requests, missing sessions, and AI service failures.
- **Automated Tests:** pytest tests for database functions and the /ask endpoint (AI calls are mocked).

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check server availability |
| GET | `/hello` | Return a greeting using a name query parameter |
| POST | `/message` | Receive a simple message |
| POST | `/ask` | Send a question to the AI and receive a response |
| GET | `/sessions` | Retrieve the list of stored session IDs |
| DELETE | `/sessions/{session_id}` | Delete all messages belonging to a session |

## Project Structure

```text
ai-chat-backend/
├── main.py
├── database.py
├── requirements.txt
├── README.md
└── .gitignore
```

The SQLite database file (`chat_history.db`) and virtual environment (`.venv`) are generated locally and excluded from version control.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/wndrbrwn/ai-chat-backend.git
cd ai-chat-backend
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure the API key

Set your OpenRouter API key as an environment variable.

Windows PowerShell:

```powershell
$env:OPENROUTER_API_KEY="your_openrouter_api_key"
```

Replace the placeholder with your own API key. This setting applies only to the current terminal window, so set it again whenever you open a new one.

**Never commit your actual API key to the repository.**

### 5. Start the server

```powershell
python -m uvicorn main:app --reload
```

### 6. Access the API documentation

Open the following URL in your browser:

http://127.0.0.1:8000/docs

Swagger UI provides an interactive interface for testing the API endpoints.

### 7. Run the tests

```powershell
python -m pytest
```

The tests use a temporary SQLite database and mock the AI call, so they do not touch `chat_history.db` or call OpenRouter. No API key is required to run them.

## Database Design

The project uses SQLite to store individual chat messages.

**chat_messages**

| Column | Type | Description |
|---|---|---|
| message_id | INTEGER | Unique message identifier |
| session_id | TEXT | Conversation session identifier |
| role | TEXT | Message sender (`user` or `assistant`) |
| content | TEXT | Message content |

Each message is stored as a separate row. Session histories are retrieved using the `session_id` column.

## Limitations

- The project currently uses the OpenRouter free model endpoint. Model availability and response quality may vary.
- Session identification is handled through client-provided session IDs.
- No authentication or user account system is currently implemented.
- The project is currently designed as a local development application.

## Project Goals

This project is part of my ongoing learning journey in Python backend development and AI application development.

The goal is to build practical experience in REST API development, LLM integration, database management, and backend application design.