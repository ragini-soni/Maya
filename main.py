import discord
from discord.ext import commands
import os
import json
import random
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

WARNINGS_FILE = 'warnings.json'

def load_warnings():
    try:
        with open(WARNINGS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_warnings(warnings):
    with open(WARNINGS_FILE, 'w') as f:
        json.dump(warnings, f)

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your server"))

@bot.command()
async def rules(ctx):
    embed = discord.Embed(title="📜 Server Rules", color=discord.Color.blue())
    embed.add_field(name="1. Be Respectful", value="Treat others kindly", inline=False)
    embed.add_field(name="2. No Spam", value="Don't spam messages", inline=False)
    embed.add_field(name="3. No NSFW", value="Keep it clean", inline=False)
    embed.add_field(name="4. Follow Staff", value="Mods have final say", inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    warnings = load_warnings()
    guild = str(ctx.guild.id)
    user = str(member.id)
    
    if guild not in warnings:
        warnings[guild] = {}
    if user not in warnings[guild]:
        warnings[guild][user] = []
    
    warnings[guild][user].append({
        'reason': reason,
        'mod': str(ctx.author),
        'date': str(datetime.now())
    })
    save_warnings(warnings)
    
    await ctx.send(f"⚠️ {member.mention} was warned. Reason: {reason}")
    
    try:
        await member.send(f"You were warned in {ctx.guild.name} for: {reason}")
    except:
        pass

@bot.command()
async def warnings(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    
    warnings = load_warnings()
    guild = str(ctx.guild.id)
    user = str(member.id)
    
    user_warnings = warnings.get(guild, {}).get(user, [])
    count = len(user_warnings)
    
    if count == 0:
        await ctx.send(f"✅ {member.display_name} has no warnings")
    else:
        await ctx.send(f"⚠️ {member.display_name} has {count} warning(s)")

@bot.command()
async def coinflip(ctx):
    result = random.choice(["Heads", "Tails"])
    await ctx.send(f"🪙 **{result}**!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    content = message.content.lower()
    if content in ['hello', 'hi', 'hey']:
        await message.channel.send(f"Hey {message.author.mention}! 👋")
    
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! 🏓 {round(bot.latency * 1000)}ms")

TOKEN = os.environ.get('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("ERROR: No token found!")