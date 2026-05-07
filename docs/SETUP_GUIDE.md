# 🚀 Setup and Deployment Guide

## Quick Start (5 Minutes)

### Prerequisites Check
```bash
python --version  # Should be 3.9+
node --version    # Should be 16+
npm --version
git --version
```

## Step-by-Step Setup

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd omnibot-ai
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example ../.env
# Edit .env with your configurations (optional for basic testing)

# Initialize database
python -c "from app.models.database import init_db; import asyncio; asyncio.run(init_db())"

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be running at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 3. Frontend Setup (New Terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will open automatically at: `http://localhost:3000`

### 4. Test the Web Interface

1. Open `http://localhost:3000` in your browser
2. Try chatting with the bot
3. Switch personalities (Friendly, Professional, Creative)
4. Try generating an image
5. Test voice input (if your browser supports it)

## Platform Integrations

### Telegram Bot Setup

1. **Get Bot Token:**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` and follow instructions
   - Copy the token you receive

2. **Configure:**
   ```bash
   # Add to .env file
   TELEGRAM_BOT_TOKEN=your_token_here
   ```

3. **Run Bot:**
   ```bash
   cd bots/telegram
   python bot.py
   ```

4. **Test:**
   - Search for your bot on Telegram
   - Send `/start`
   - Start chatting!

### Discord Bot Setup

1. **Create Discord Application:**
   - Go to https://discord.com/developers/applications
   - Click "New Application"
   - Go to "Bot" tab and click "Add Bot"
   - Copy the token
   - Enable "Message Content Intent" under Bot settings

2. **Configure:**
   ```bash
   # Add to .env file
   DISCORD_BOT_TOKEN=your_token_here
   ```

3. **Invite Bot to Server:**
   - Go to OAuth2 > URL Generator
   - Select scopes: `bot`
   - Select permissions: `Send Messages`, `Read Messages`, `Attach Files`
   - Copy the generated URL and open in browser
   - Select your server and authorize

4. **Run Bot:**
   ```bash
   cd bots/discord
   python bot.py
   ```

5. **Test:**
   - Mention your bot: `@YourBot hello`
   - Try commands: `!start`, `!friendly`, `!image sunset`

## Features Testing

### 1. Chat Functionality
```
User: Hello!
Bot: Hello! 👋 I'm OmniBot...
```

### 2. Personality Switching
- Click personality buttons in web interface
- Telegram: `/friendly`, `/professional`, `/creative`
- Discord: `!friendly`, `!professional`, `!creative`

### 3. Image Generation
- Web: Click image icon, enter prompt
- Telegram: `/image a beautiful sunset`
- Discord: `!image a beautiful sunset`

### 4. Multi-Language Support
```
User: Hola, ¿cómo estás?
Bot: (Auto-detects Spanish and responds)
```

### 5. Voice Input (Web Only)
- Click microphone icon
- Allow microphone access
- Speak your message
- Message will be transcribed

## Troubleshooting

### Backend Issues

**Error: "Module not found"**
```bash
# Make sure you're in the virtual environment
# Reinstall dependencies
pip install -r requirements.txt
```

**Error: "Port 8000 already in use"**
```bash
# Kill the process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

**Models downloading slowly:**
- Models will download on first use
- They're cached for future use
- Be patient on first run (~1-2 GB download)

### Frontend Issues

**Error: "npm install fails"**
```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Port 3000 already in use:**
```bash
# Use different port
PORT=3001 npm start
```

### Bot Issues

**Telegram bot not responding:**
- Check token is correct in .env
- Ensure backend is running
- Check bot logs for errors

**Discord bot offline:**
- Verify token is correct
- Check bot has proper permissions
- Ensure Message Content Intent is enabled

## Performance Optimization

### For Low-End Systems

1. **Use smaller models:**
   Edit `backend/app/services/nlp_service.py`:
   ```python
   model_name = "microsoft/DialoGPT-small"  # Instead of medium
   ```

2. **Disable image generation:**
   Comment out image service initialization in `main.py`

3. **Use lightweight services:**
   Replace services with their Lightweight alternatives

### For Production

1. **Use GPU:**
   - Install CUDA
   - Models will automatically use GPU
   - 10-100x faster performance

2. **Use Gunicorn:**
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

3. **Deploy with Docker:**
   ```bash
   docker-compose up -d
   ```

## Deployment Options

### Heroku (Free Tier)
1. Create Heroku account
2. Install Heroku CLI
3. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Railway (Recommended for AI Apps)
1. Connect GitHub repo to Railway
2. Railway auto-detects and deploys
3. Free tier includes 500 hours/month

### Render
1. Connect GitHub repo
2. Select "Web Service"
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### DigitalOcean / AWS / GCP
- Use provided Docker configuration
- Deploy using docker-compose
- Set up reverse proxy (nginx)

## GitHub Repository Setup

```bash
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: OmniBot AI Chatbot"

# Create repo on GitHub and push
git remote add origin <your-repo-url>
git branch -M main
git push -u origin main
```

## Next Steps

1. **Customize Personalities:**
   - Edit `config/personalities.json`
   - Add your own personality modes

2. **Extend Features:**
   - Add more AI capabilities
   - Integrate additional platforms
   - Add database for persistent storage

3. **Improve UI:**
   - Customize React components
   - Add themes
   - Add more interactive features

4. **Scale:**
   - Add Redis for caching
   - Use PostgreSQL instead of SQLite
   - Implement user authentication

## Support

For issues:
1. Check troubleshooting section
2. Review logs in terminal
3. Open issue on GitHub

## License

MIT License - Feel free to use and modify!
