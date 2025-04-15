import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests
import os

# Load environment variables from .env file
load_dotenv()

# Get tokens from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
HUGGINGFACE_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')

# Create intents
intents = discord.Intents.default()
intents.message_content = True  # Allow the bot to read message content

# Create the bot instance with intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Hugging Face API URL
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print("Bot is ready!")

# Command: /hi
@bot.tree.command(name="hi", description="Say hello!")
async def hi(interaction: discord.Interaction):
    await interaction.response.send_message("Hello! I'm EcoFriend!")

# Event: When the bot reads a message
@bot.event
async def on_message(message):
    # Prevent bot from replying to itself
    if message.author == bot.user:
        return

    # Send the user's message to Hugging Face API to get a response
    payload = {"inputs": message.content}
    response = requests.post(HUGGINGFACE_API_URL, headers=HEADERS, json=payload)
    data = response.json()

    try:
        reply = data[0]['generated_text']
    except:
        reply = "Sorry, I couldn't get a response right now!"

    # Send the AI-generated reply
    await message.channel.send(reply)

bot.run(DISCORD_TOKEN)

