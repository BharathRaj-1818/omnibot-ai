# 🤖 OmniBot - Multi-Platform Conversational AI

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)

An intelligent, multi-platform conversational AI chatbot with NLP capabilities, image generation, voice support, and multi-language processing. Built with 100% free and open-source tools.

## ✨ Features

- 🧠 **Advanced NLP** - Powered by Hugging Face Transformers
- 🎨 **Image Generation** - Stable Diffusion integration via Hugging Face
- 🎤 **Voice Message Support** - Speech-to-Text and Text-to-Speech
- 🌍 **Multi-Language** - Support for 100+ languages
- 🎭 **Customizable Personalities** - Switch between Friendly, Professional, and Creative modes
- 💬 **Multi-Platform** - Web, Telegram, Discord, WhatsApp
- 📊 **Analytics Dashboard** - Track conversations and user engagement
- 🧠 **Context Memory** - Remembers conversation history
- 🔒 **Privacy First** - All data stored locally, no third-party tracking

## 🏗️ Architecture

```
omnibot-ai/
├── backend/           # FastAPI backend server
│   ├── app/
│   │   ├── models/    # Database models
│   │   ├── routes/    # API endpoints
│   │   ├── services/  # Core AI services
│   │   └── utils/     # Utility functions
├── frontend/          # React web interface
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
├── bots/             # Platform integrations
│   ├── telegram/
│   ├── discord/
│   └── whatsapp/
├── config/           # Configuration files
├── docs/             # Documentation
└── tests/            # Unit and integration tests
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- pip and npm
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/omnibot-ai.git
cd omnibot-ai
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your configurations
```

5. **Initialize Database**
```bash
cd backend
python init_db.py
```

### Running the Application

**Backend (Terminal 1):**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm start
```

**Telegram Bot (Terminal 3):**
```bash
cd bots/telegram
python bot.py
```

Access the web interface at: `http://localhost:3000`

## 🔧 Configuration

### Personality Modes

Edit `config/personalities.json` to customize bot behaviors:

- **Friendly**: Casual, uses emojis, tells jokes
- **Professional**: Formal, structured responses
- **Creative**: Imaginative, storytelling focused

### API Keys (All Free Tier)

Get your free API keys from:
- **Hugging Face**: https://huggingface.co/settings/tokens
- **Telegram**: https://t.me/BotFather
- **Discord**: https://discord.com/developers/applications

## 📚 API Documentation

Once running, visit:
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Core Endpoints

```
POST /api/chat              - Send message to chatbot
POST /api/generate-image    - Generate images from text
POST /api/speech-to-text    - Convert voice to text
POST /api/text-to-speech    - Convert text to voice
GET  /api/analytics         - Get conversation analytics
POST /api/personality       - Switch personality mode
```

## 🌐 Platform Integration

### Telegram Bot
1. Create bot via @BotFather
2. Add token to `.env`
3. Run `python bots/telegram/bot.py`

### Discord Bot
1. Create application at Discord Developer Portal
2. Add token to `.env`
3. Run `python bots/discord/bot.py`

### WhatsApp (Twilio)
1. Sign up for Twilio free account
2. Get WhatsApp sandbox credentials
3. Run `python bots/whatsapp/bot.py`

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## 📊 Technologies Used

### Backend
- **FastAPI** - High-performance web framework
- **Transformers** - Hugging Face NLP models
- **SQLAlchemy** - Database ORM
- **Whisper** - Speech recognition
- **gTTS** - Text-to-speech
- **Diffusers** - Image generation

### Frontend
- **React** - UI library
- **TailwindCSS** - Styling
- **Axios** - HTTP client
- **React Router** - Navigation
- **Recharts** - Analytics visualization

### AI Models (All Free)
- **DialoGPT** - Conversational AI
- **BLIP** - Image captioning
- **Stable Diffusion** - Image generation
- **Whisper** - Speech recognition
- **MarianMT** - Translation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Hugging Face for amazing open-source models
- FastAPI and React communities
- All contributors and users

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Email: your.email@example.com

---

**Made with ❤️ for the AI Community**
