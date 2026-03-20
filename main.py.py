from bs4 import BeautifulSoup
import os
import json
import datetime
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import aiohttp

load_dotenv()
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
}

user_info_path = r"./user_info.json"

# dictionary to store loops per user
loops = {}

async def fetch_product(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")
    price = soup.find("span", class_="a-price-whole")
    decimal = soup.find("span", class_="a-price-fraction")
    title = soup.find("span", class_="a-size-large product-title-word-break")

    if price is None or decimal is None or title is None:
        price = soup.find("span", class_="a-price-whole")
        decimal = soup.find("span", class_="a-price-decimal")
        title = soup.find("span", id="productTitle")

    price_str = price.get_text(strip=True).replace(",", "").replace("\u202f", "")
    decimal_str = decimal.get_text(strip=True)
    price_float = float(f"{price_str}.{decimal_str}")
    title_text = title.get_text(strip=True)

    return price_float, title_text


async def check_price(ctx):
    username = ctx.author.display_name
    user = ctx.author
    dm = await user.create_dm()

    # load JSON file
    if os.path.exists(user_info_path):
        try:
            with open(user_info_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    user_entries = [e for e in data if e.get("pseudo") == username]

    price_float, title_text = await fetch_product(url)

    entry = {
        "url": url,
        "prix": price_float,
        "pseudo": username,
        "titre": title_text
    }

    # if no entry, send DM and add it
    if len(user_entries) == 0:
        data.append(entry)
        with open(user_info_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        await dm.send(f"On va tracker le prix pour le produit : {title_text} qui est actuellement à {price_float}€")
        return

    # add new entry
    data.append(entry)
    with open(user_info_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    # group by pseudo + url + title
    user_entries = [e for e in data if e["pseudo"] == username]
    groups = {}

    for element in user_entries:
        key = (element["pseudo"], element["url"], element["titre"])
        groups.setdefault(key, []).append(element)

    # compare if at least two entries exist
    for key, elements in groups.items():
        if len(elements) >= 2:
            last = elements[-1]
            previous = elements[-2]

            last_price = last["prix"]
            previous_price = previous["prix"]
            title2 = last["titre"]

            if previous_price > last_price:
                await dm.send(f"Le produit '{title2}' a baissé : {previous_price} → {last_price}€")
            elif previous_price < last_price:
                await dm.send(f"Le produit '{title2}' a monté : {previous_price} → {last_price}€")
            else:
                await dm.send(f"Le produit '{title2}' n'a pas changé : {last_price}€")


@bot.command()
async def url(ctx, *, text):
    global url
    url = text

    if "https://www.amazon.fr" in url or "https://amzn.eu" in url:
        await ctx.send(f"URL stockée : {url}")
    else:
        await ctx.send("Met une URL Amazon valide.")


@bot.command()
async def get(ctx):
    username = ctx.author.display_name

    if username in loops and loops[username].is_running():
        await ctx.send("Le tracking est déjà lancé pour toi.")
        return

    # create loop for this user
    @tasks.loop(hours=3)
    async def loop():
        await check_price(ctx)

    loops[username] = loop
    loop.start()
    await ctx.send("Tracking lancé. Le bot va vérifier le prix toutes les 15 secondes.")


print("Lancement du bot...")
bot.run(os.getenv("DISCORD_TOKEN"))