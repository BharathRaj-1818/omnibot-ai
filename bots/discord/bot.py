"""
Discord Bot Integration
"""

import os
import discord
from discord.ext import commands
import aiohttp
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# User sessions
user_sessions = {}


@bot.event
async def on_ready():
    """Event: Bot is ready"""
    logger.info(f'✅ {bot.user} is now online!')
    logger.info(f'Connected to {len(bot.guilds)} servers')
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="!help | Multi-Platform AI"
        )
    )


@bot.command(name='start')
async def start(ctx):
    """Start command - Show welcome message"""
    embed = discord.Embed(
        title="🤖 Welcome to OmniBot!",
        description="I'm an intelligent AI chatbot with multiple personalities!",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Personality Modes",
        value="!friendly 😊\n!professional 💼\n!creative ✨",
        inline=True
    )
    
    embed.add_field(
        name="Features",
        value="!image <prompt>\n!translate <text>\n!stats",
        inline=True
    )
    
    embed.add_field(
        name="How to Use",
        value="Just mention me or reply to my messages to chat!\nExample: `@OmniBot tell me a joke`",
        inline=False
    )
    
    embed.set_footer(text="Use !help for more commands")
    
    await ctx.send(embed=embed)


@bot.command(name='friendly')
async def friendly(ctx):
    """Switch to friendly personality"""
    user_id = str(ctx.author.id)
    user_sessions[user_id] = {"personality": "friendly"}
    await ctx.send("😊 Switched to **Friendly** mode! Let's have a casual chat!")


@bot.command(name='professional')
async def professional(ctx):
    """Switch to professional personality"""
    user_id = str(ctx.author.id)
    user_sessions[user_id] = {"personality": "professional"}
    await ctx.send("💼 Switched to **Professional** mode. How may I assist you?")


@bot.command(name='creative')
async def creative(ctx):
    """Switch to creative personality"""
    user_id = str(ctx.author.id)
    user_sessions[user_id] = {"personality": "creative"}
    await ctx.send("✨ Switched to **Creative** mode! Let's explore imaginative ideas!")


@bot.command(name='image')
async def generate_image(ctx, *, prompt: str):
    """Generate an image from text description"""
    
    if not prompt:
        await ctx.send("❌ Please provide an image description!\n**Example:** `!image a sunset over mountains`")
        return
    
    # Send initial message
    msg = await ctx.send("🎨 Generating your image... This may take a moment! ⏳")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/api/generate-image",
                json={
                    "prompt": prompt,
                    "user_id": str(ctx.author.id),
                    "width": 512,
                    "height": 512
                }
            ) as response:
                if response.status == 200:
                    image_data = await response.read()
                    
                    # Send image
                    file = discord.File(fp=io.BytesIO(image_data), filename="generated.png")
                    
                    embed = discord.Embed(
                        title="Generated Image",
                        description=f"**Prompt:** {prompt}",
                        color=discord.Color.purple()
                    )
                    embed.set_image(url="attachment://generated.png")
                    embed.set_footer(text=f"Requested by {ctx.author.name}")
                    
                    await msg.delete()
                    await ctx.send(file=file, embed=embed)
                else:
                    await msg.edit(content="❌ Image generation failed. Please try again!")
    
    except Exception as e:
        logger.error(f"Image generation error: {str(e)}")
        await msg.edit(content="❌ An error occurred during image generation!")


@bot.command(name='translate')
async def translate(ctx, *, text: str):
    """Translate text to English"""
    
    if not text:
        await ctx.send("❌ Please provide text to translate!\n**Example:** `!translate Hola mundo`")
        return
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/api/translate",
                params={
                    "text": text,
                    "source_language": "auto",
                    "target_language": "en"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    embed = discord.Embed(
                        title="Translation",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="Original", value=data["original"], inline=False)
                    embed.add_field(name="Translated", value=data["translated"], inline=False)
                    embed.add_field(name="Language", value=data["source_language"].upper(), inline=True)
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Translation failed!")
    
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        await ctx.send("❌ An error occurred during translation!")


@bot.command(name='stats')
async def stats(ctx):
    """Show bot statistics"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/analytics") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    embed = discord.Embed(
                        title="📊 OmniBot Statistics",
                        color=discord.Color.gold()
                    )
                    
                    embed.add_field(name="Total Conversations", value=data["total_conversations"], inline=True)
                    embed.add_field(name="Total Messages", value=data["total_messages"], inline=True)
                    embed.add_field(name="Images Generated", value=data["total_images_generated"], inline=True)
                    embed.add_field(name="Active Users", value=data["active_users"], inline=True)
                    embed.add_field(name="Popular Mode", value=data["popular_personality"].capitalize(), inline=True)
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Could not fetch statistics!")
    
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        await ctx.send("❌ An error occurred!")


@bot.event
async def on_message(message):
    """Handle incoming messages"""
    # Ignore bot's own messages
    if message.author == bot.user:
        return
    
    # Process commands first
    await bot.process_commands(message)
    
    # Check if bot is mentioned or message is a reply to bot
    if bot.user.mentioned_in(message) or (message.reference and message.reference.resolved.author == bot.user):
        # Get user's personality preference
        user_id = str(message.author.id)
        personality = user_sessions.get(user_id, {}).get("personality", "friendly")
        
        # Clean message content (remove mention)
        content = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        if not content:
            return
        
        # Show typing indicator
        async with message.channel.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{API_BASE_URL}/api/chat",
                        json={
                            "message": content,
                            "user_id": user_id,
                            "personality_mode": personality,
                            "auto_translate": True
                        }
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            bot_response = data.get("response", "I couldn't process that.")
                            
                            # Split long messages
                            if len(bot_response) > 2000:
                                chunks = [bot_response[i:i+2000] for i in range(0, len(bot_response), 2000)]
                                for chunk in chunks:
                                    await message.reply(chunk)
                            else:
                                await message.reply(bot_response)
                        else:
                            await message.reply("❌ Sorry, I encountered an error!")
            
            except Exception as e:
                logger.error(f"Message handling error: {str(e)}")
                await message.reply("❌ Sorry, I'm having connection issues!")


# Import io for image handling
import io


if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        logger.error("❌ DISCORD_BOT_TOKEN not found!")
        logger.info("Please create a .env file with: DISCORD_BOT_TOKEN=your_token_here")
        logger.info("Get your token from https://discord.com/developers/applications")
        exit(1)
    
    logger.info("🚀 Starting Discord Bot...")
    bot.run(DISCORD_BOT_TOKEN)
