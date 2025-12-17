import os
import json
import discord
from discord import app_commands
from datetime import datetime

# -------- CONFIG --------
DATA_FILE = "data.json"
SOLDE_DEPART = 0

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

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
@client.event
async def on_ready():
    await tree.sync()
    print(f"Connecté en tant que {client.user}")

# -------- SLASH COMMANDS --------

@tree.command(name="depense", description="Ajouter une dépense")
@app_commands.describe(
    montant="Montant de la dépense",
    libelle="Ex: macdo, essence, loyer..."
)
async def depense(interaction: discord.Interaction, montant: float, libelle: str):
    data = load_data()
    data.append({
        "date": datetime.now().strftime("%d/%m/%Y"),
        "type": "depense",
        "montant": montant,
        "libelle": libelle
    })
    save_data(data)

    await interaction.response.send_message(
        f"💸 Dépense ajoutée : **-{montant}€** — {libelle}",
        ephemeral=True
    )

@tree.command(name="recu", description="Ajouter un revenu")
@app_commands.describe(
    montant="Montant reçu",
    libelle="Ex: salaire, remboursement..."
)
async def recu(interaction: discord.Interaction, montant: float, libelle: str):
    data = load_data()
    data.append({
        "date": datetime.now().strftime("%d/%m/%Y"),
        "type": "recu",
        "montant": montant,
        "libelle": libelle
    })
    save_data(data)

    await interaction.response.send_message(
        f"💰 Reçu ajouté : **+{montant}€** — {libelle}",
        ephemeral=True
    )

@tree.command(name="solde", description="Afficher le solde")
async def solde(interaction: discord.Interaction):
    data = load_data()

    total_recu = sum(x["montant"] for x in data if x["type"] == "recu")
    total_depense = sum(x["montant"] for x in data if x["type"] == "depense")
    solde = SOLDE_DEPART + total_recu - total_depense

    await interaction.response.send_message(
        f"💰 **Solde actuel**\n"
        f"Reçus : {total_recu} €\n"
        f"Dépenses : {total_depense} €\n"
        f"➡️ **Solde : {solde} €**",
        ephemeral=True
    )

@tree.command(name="liste", description="Voir les transactions")
async def liste(interaction: discord.Interaction):
    data = load_data()

    if not data:
        await interaction.response.send_message("📭 Aucune transaction", ephemeral=True)
        return

    message = "📋 **Transactions :**\n"
    for i, t in enumerate(data, start=1):
        signe = "-" if t["type"] == "depense" else "+"
        message += f"{i}. {t['date']} | {t['type']} | {signe}{t['montant']}€ | {t['libelle']}\n"

    await interaction.response.send_message(message, ephemeral=True)

# -------- RUN --------
client.run(os.getenv("DISCORD_TOKEN"))
