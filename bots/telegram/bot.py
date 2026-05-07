"""
Telegram Bot Integration
"""

import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


class TelegramBot:
    """Telegram bot handler"""
    
    def __init__(self, token: str, api_url: str):
        """
        Initialize Telegram bot
        
        Args:
            token: Telegram bot token
            api_url: Backend API URL
        """
        self.token = token
        self.api_url = api_url
        self.app = Application.builder().token(token).build()
        
        # User sessions
        self.user_sessions = {}
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        welcome_message = f"""
🤖 **Welcome to OmniBot, {user.first_name}!**

I'm an AI chatbot with multiple personalities and features:

**Available Commands:**
/start - Show this message
/friendly - Switch to friendly mode 😊
/professional - Switch to professional mode 💼
/creative - Switch to creative mode ✨
/image <prompt> - Generate an image
/translate <text> - Translate text
/voice - Enable voice mode
/help - Show help

Just send me a message to chat! I support multiple languages too!
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
**OmniBot Help**

**Personality Modes:**
• Friendly 😊 - Casual and warm
• Professional 💼 - Formal and structured
• Creative ✨ - Imaginative and expressive

**Features:**
• Multi-language support (auto-detect)
• Image generation from text
• Voice message support
• Context-aware conversations

**Examples:**
• "Tell me a joke"
• "/image a sunset over mountains"
• "/translate Hola mundo"
• Just send a voice message!

Enjoy chatting! 🚀
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def personality_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str):
        """Handle personality switch commands"""
        user_id = str(update.effective_user.id)
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        
        self.user_sessions[user_id]["personality"] = mode
        
        mode_emojis = {
            "friendly": "😊",
            "professional": "💼",
            "creative": "✨"
        }
        
        emoji = mode_emojis.get(mode, "🤖")
        await update.message.reply_text(
            f"{emoji} Switched to **{mode.capitalize()}** mode!",
            parse_mode='Markdown'
        )
    
    async def image_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /image command"""
        if not context.args:
            await update.message.reply_text(
                "Please provide an image description!\n\nExample: `/image a beautiful sunset`",
                parse_mode='Markdown'
            )
            return
        
        prompt = ' '.join(context.args)
        
        await update.message.reply_text("🎨 Generating your image... This may take a moment!")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/api/generate-image",
                    json={
                        "prompt": prompt,
                        "user_id": str(update.effective_user.id)
                    }
                ) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        await update.message.reply_photo(photo=image_data)
                    else:
                        await update.message.reply_text("❌ Image generation failed. Please try again!")
        
        except Exception as e:
            logger.error(f"Image generation error: {str(e)}")
            await update.message.reply_text("❌ An error occurred. Please try again later!")
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        user_id = str(update.effective_user.id)
        message_text = update.message.text
        
        # Get user's personality preference
        personality = self.user_sessions.get(user_id, {}).get("personality", "friendly")
        
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        try:
            # Call backend API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/api/chat",
                    json={
                        "message": message_text,
                        "user_id": user_id,
                        "personality_mode": personality,
                        "auto_translate": True
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        bot_response = data.get("response", "I'm sorry, I couldn't process that.")
                        await update.message.reply_text(bot_response)
                    else:
                        await update.message.reply_text("Sorry, I encountered an error. Please try again!")
        
        except Exception as e:
            logger.error(f"Message handling error: {str(e)}")
            await update.message.reply_text("Sorry, I'm having trouble connecting. Please try again later!")
    
    async def voice_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages"""
        await update.message.reply_text("🎤 Processing your voice message...")
        
        try:
            # Download voice file
            voice_file = await update.message.voice.get_file()
            voice_data = await voice_file.download_as_bytearray()
            
            # Call speech-to-text API
            async with aiohttp.ClientSession() as session:
                form = aiohttp.FormData()
                form.add_field('audio', voice_data, filename='voice.ogg')
                
                async with session.post(
                    f"{self.api_url}/api/speech-to-text",
                    data=form
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        text = data.get("text", "")
                        
                        # Send transcribed text
                        await update.message.reply_text(f"📝 You said: {text}")
                        
                        # Process the message
                        update.message.text = text
                        await self.message_handler(update, context)
                    else:
                        await update.message.reply_text("❌ Could not process voice message!")
        
        except Exception as e:
            logger.error(f"Voice handling error: {str(e)}")
            await update.message.reply_text("❌ Voice processing failed!")
    
    def run(self):
        """Start the bot"""
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        
        # Personality commands
        self.app.add_handler(CommandHandler("friendly", lambda u, c: self.personality_command(u, c, "friendly")))
        self.app.add_handler(CommandHandler("professional", lambda u, c: self.personality_command(u, c, "professional")))
        self.app.add_handler(CommandHandler("creative", lambda u, c: self.personality_command(u, c, "creative")))
        
        # Feature commands
        self.app.add_handler(CommandHandler("image", self.image_command))
        
        # Message handlers
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
        self.app.add_handler(MessageHandler(filters.VOICE, self.voice_handler))
        
        logger.info("🤖 Telegram Bot started!")
        
        # Run the bot
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
        logger.info("Please create a .env file with: TELEGRAM_BOT_TOKEN=your_token_here")
        logger.info("Get your token from @BotFather on Telegram")
        exit(1)
    
    bot = TelegramBot(TELEGRAM_BOT_TOKEN, API_BASE_URL)
    bot.run()
