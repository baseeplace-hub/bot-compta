import os
import json
import discord
from discord.ext import commands
from datetime import datetime

# -------- CONFIG --------
DATA_FILE = "data.json"
SOLDE_DEPART = 0

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# -------- DATA --------
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# -------- EVENTS --------
@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

# -------- COMMANDES --------
@bot.command()
async def test(ctx):
    await ctx.send("Le bot fonctionne ✅")

@bot.command()
async def add(ctx, type, montant: float, *, libelle):
    type = type.lower()
    if type not in ["depense", "recu"]:
        await ctx.send("❌ Utilise `depense` ou `recu`")
        return

    data = load_data()
    data.append({
        "date": datetime.now().strftime("%d/%m/%Y"),
        "type": type,
        "montant": montant,
        "libelle": libelle
    })
    save_data(data)

    await ctx.send(f"✅ {type} ajoutée : {montant}€ — {libelle}")

@bot.command()
async def solde(ctx):
    data = load_data()

    total_recu = sum(x["montant"] for x in data if x["type"] == "recu")
    total_depense = sum(x["montant"] for x in data if x["type"] == "depense")
    solde = SOLDE_DEPART + total_recu - total_depense

    await ctx.send(
        f"💰 **Solde actuel**\n"
        f"Reçus : {total_recu} €\n"
        f"Dépenses : {total_depense} €\n"
        f"➡️ **Solde : {solde} €**"
    )

@bot.command()
async def liste(ctx):
    data = load_data()

    if not data:
        await ctx.send("📭 Aucune transaction")
        return

    message = "📋 **Dernières transactions :**\n"
    for t in data[-10:][::-1]:
        signe = "-" if t["type"] == "depense" else "+"
        message += f'{t["date"]} | {t["type"]} | {signe}{t["montant"]}€ | {t["libelle"]}\n'

    await ctx.send(message)

# -------- RUN --------
bot.run(os.getenv("DISCORD_TOKEN"))
