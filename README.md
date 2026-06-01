# 🤖 OmniBot

A student project implementing conversational AI with a React frontend and FastAPI backend.

## Overview

OmniBot supports chat, voice, translation, and image generation. The backend uses FastAPI, async SQLAlchemy, and Hugging Face models. The frontend is built with React and connects to the backend via REST.

## Features

- Conversational chat powered by Transformers
- Speech-to-Text using Whisper
- Text-to-Speech via gTTS
- Translation and language detection
- Image generation support
- Personality modes: Friendly, Professional, Creative
- Conversation analytics and local storage

## Tech Stack

- Python 3.9+
- FastAPI
- SQLAlchemy + SQLite
- React
- Axios
- Transformers / Torch
- Whisper
- gTTS

## Structure

```
omnibot-ai/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # API entrypoint
│   │   ├── models/            # Database models and schemas
│   │   ├── services/          # AI and utility services
│   │   └── utils/             # Personality and analytics helpers
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React frontend
│   ├── src/                   # Source files
│   └── package.json           # Node dependencies
├── bots/                      # Chat platform integrations
├── docs/                      # Documentation
├── docker-compose.yml         # Docker compose setup
├── Dockerfile.backend         # Backend Dockerfile
├── .env.example               # Environment template
└── LICENSE                    # MIT License
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- pip and npm
- Git

### Setup

```bash
git clone https://github.com/BharathRaj-1818/omnibot-ai.git
cd omnibot-ai
```

### Backend

```bash
cd backend
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

### Environment

```bash
copy .env.example .env   # Windows
# or
cp .env.example .env    # macOS/Linux
```

Update `.env` with your settings.

## Run Locally

### Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm start
```

Open the app at `http://localhost:3000`.

## Notes

- The backend initializes the database automatically.
- Image generation may require a capable machine or GPU.
- Configure `.env` for optional bot tokens and API keys.

## Project URL

https://github.com/BharathRaj-1818/omnibot-ai
