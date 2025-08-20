import os
import sys
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path


load_dotenv(encoding='utf-8')

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


print("�� Working Dir:", os.getcwd())
print("�� ENV_PATH:", Path(__file__).resolve().parent / ".env", "exists:", (Path(__file__).resolve().parent / ".env").exists())



#load_dotenv()
# === 2) Konfiguration aus Environment ===
BOT_TOKEN = (os.getenv("BOTTOKEN") or "").strip()
N8N_WEBHOOK_URL = (os.getenv("N8NWEBHOOKURL") or "").strip()
SHARED_SECRET = (os.getenv("SHAREDSECRET") or "").strip()




# === 3) Checks vor Start ===
if not BOT_TOKEN:
    sys.exit("❌ BOT_TOKEN ist nicht gesetzt. Bitte in .env eintragen.")
if not N8N_WEBHOOK_URL:
    sys.exit("❌ N8N_WEBHOOK_URL ist nicht gesetzt. Bitte in .env eintragen.")

# Token-Format prüfen
parts = BOT_TOKEN.split(".")
if len(parts) != 3:
    sys.exit("❌ Ungültiges Token-Format – im Developer Portal das **Bot Token** kopieren (3 Teile durch Punkte getrennt).")

print("✅ Konfiguration geladen. Bot startet...")

# === 4) Discord Bot Setup ===
intents = discord.Intents.default()
intents.message_content = True  # auch im Dev Portal aktivieren!

bot = commands.Bot(command_prefix="!", intents=intents)

# === 5) Nachrichten-Handler ===
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # Nur Nachrichten, die mit "?" beginnen
    if message.content.lstrip().startswith("?"):
        msg_id = str(message.id)
        print(f"🔹 Sende ID an n8n: {msg_id}")

        payload = {
            "message_id": msg_id,
            "author": str(message.author),
            "content": message.content,
            "channel_id": str(message.channel.id),
            "guild_id": str(message.guild.id) if message.guild else None,
        }

        headers = {"Content-Type": "application/json"}
        if SHARED_SECRET:
            headers["X-Webhook-Secret"] = SHARED_SECRET

        try:
            r = requests.post(N8N_WEBHOOK_URL, json=payload, headers=headers, timeout=10)
            r.raise_for_status()
            print(f"✅ Erfolgreich an n8n gesendet (Status {r.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"❌ Fehler beim Senden an n8n: {e}")

    await bot.process_commands(message)

# === 6) Bot starten ===
bot.run(BOT_TOKEN)
