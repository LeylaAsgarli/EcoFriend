import discord
from discord.ext import commands
from discord import app_commands
import requests
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HUGGINGFACE_API_TOKEN = os.getenv("HF_TOKEN")

# Create intents
intents = discord.Intents.default()
intents.message_content = True

# Create the bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# HuggingFace API setup
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user.name}")

@bot.tree.command(name="hi", description="Say hello!")
async def hi(interaction: discord.Interaction):
    await interaction.response.send_message("Hello! I'm EcoFriend Bot! 🌿")

@bot.tree.command(name="ask", description="Ask EcoFriend something!")
@app_commands.describe(message="What do you want to ask?")
async def ask(interaction: discord.Interaction, message: str):
    await interaction.response.defer()
    payload = {"inputs": message}
    response = requests.post(HUGGINGFACE_API_URL, headers=HEADERS, json=payload)
    data = response.json()
    try:
        reply = data[0]['generated_text']
    except:
        reply = "Sorry, I couldn't get a response right now!"
    await interaction.followup.send(reply)

bot.run(DISCORD_TOKEN)
