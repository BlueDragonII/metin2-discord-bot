import discord
import asyncio
from datetime import datetime, timedelta
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # wird aus Railway geladen
CHANNEL_INPUT = 1415228079499902976   # metin2-bot eingang
CHANNEL_REMINDER = 1415199079788445757  # metin2 ablauf erinnerung

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

items = []  # Hier speichern wir alle Items mit Ablaufzeit

@client.event
async def on_ready():
    print(f"✅ Bot ist online als {client.user}")
    client.loop.create_task(reminder_loop())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.id != CHANNEL_INPUT:
        return

    try:
        # Erwartetes Format: "Itemname Tage"
        content = message.content.strip()
        name, days_str = content.rsplit(" ", 1)
        days = int(days_str)

        now = datetime.now()
        ablauf = now + timedelta(days=days)

        items.append({
            "name": name,
            "ablauf": ablauf,
            "warn_tag": False,
            "warn_stunde": False
        })

        await message.channel.send(
            f"✅ Reminder gesetzt: **{name}**, Ablauf am {ablauf.strftime('%Y-%m-%d %H:%M')}"
        )
    except Exception as e:
        await message.channel.send(f"❌ Fehler beim Eintragen: {e}")

async def reminder_loop():
    await client.wait_until_ready()
    rc = client.get_channel(CHANNEL_REMINDER)

    while True:
        now = datetime.now()
        for item in items:
            name = item["name"]
            ablauf = item["ablauf"]

            # 1 Tag vorher
            if not item["warn_tag"] and now >= ablauf - timedelta(days=1):
                await rc.send(f"⚠️ **{name}** hat noch 1 Tag verbleibend!")
                item["warn_tag"] = True

            # 1 Stunde vorher
            if not item["warn_stunde"] and now >= ablauf - timedelta(hours=1):
                await rc.send(f"⏰ **{name}** hat noch 1 Stunde verbleibend!")
                item["warn_stunde"] = True

        await asyncio.sleep(3600)  # prüft jede Stunde

client.run(TOKEN)
