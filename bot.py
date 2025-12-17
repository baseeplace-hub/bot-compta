


import discord
from discord.ext import commands
# import sqlite3
from datetime import datetime

# -------- CONFIG DISCORD --------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------- BASE DE DONNÉES --------
# conn = sqlite3.connect("compta.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    type TEXT,
    montant REAL,
    libelle TEXT
)
""")
conn.commit()

SOLDE_DEPART = 0  # modifie si tu veux (ex: argent déjà sur le compte)

# -------- EVENEMENT --------
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

    cursor.execute(
        "INSERT INTO transactions (date, type, montant, libelle) VALUES (?, ?, ?, ?)",
        (datetime.now().strftime("%d/%m/%Y"), type, montant, libelle)
    )
    conn.commit()

    await ctx.send(f"✅ {type} ajoutée : {montant}€ — {libelle}")

@bot.command()
async def solde(ctx):
    cursor.execute("SELECT SUM(montant) FROM transactions WHERE type='recu'")
    total_recu = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(montant) FROM transactions WHERE type='depense'")
    total_depense = cursor.fetchone()[0] or 0

    solde = SOLDE_DEPART + total_recu - total_depense

    await ctx.send(
        f"💰 **Solde actuel**\n"
        f"Reçus : {total_recu} €\n"
        f"Dépenses : {total_depense} €\n"
        f"➡️ **Solde : {solde} €**"
    )

@bot.command()
async def liste(ctx):
    cursor.execute(
        "SELECT date, type, montant, libelle FROM transactions ORDER BY id DESC LIMIT 10"
    )
    rows = cursor.fetchall()

    if not rows:
        await ctx.send("📭 Aucune transaction enregistrée")
        return

    message = "📋 **Dernières transactions :**\n"
    for date, type, montant, libelle in rows:
        signe = "-" if type == "depense" else "+"
        message += f"{date} | {type} | {signe}{montant}€ | {libelle}\n"

    await ctx.send(message)

# -------- LANCEMENT --------
import os
bot.run(os.getenv("DISCORD_TOKEN"))
