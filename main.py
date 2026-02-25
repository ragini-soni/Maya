import discord
from discord.ext import commands
import os
import json
import random
from datetime import datetime

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

# File for storing warnings
WARNINGS_FILE = 'warnings.json'

def load_warnings():
    try:
        with open(WARNINGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_warnings(warnings):
    with open(WARNINGS_FILE, 'w') as f:
        json.dump(warnings, f, indent=4)

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    print(f'Serving {len(bot.guilds)} server(s)')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="your server 👀"
    ))

@bot.command()
async def rules(ctx):
    """Post server rules"""
    embed = discord.Embed(
        title="📜 Server Rules",
        description="Please follow these rules to keep our community safe!",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="1. Be Respectful", 
        value="Treat others how you want to be treated", 
        inline=False
    )
    embed.add_field(
        name="2. No Spam", 
        value="Don't spam messages, mentions, or DMs", 
        inline=False
    )
    embed.add_field(
        name="3. No NSFW", 
        value="Keep all content family-friendly", 
        inline=False
    )
    embed.add_field(
        name="4. Follow Staff", 
        value="Moderators' decisions are final", 
        inline=False
    )
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    """Warn a user (mods only)"""
    warnings = load_warnings()
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)
    
    if guild_id not in warnings:
        warnings[guild_id] = {}
    if user_id not in warnings[guild_id]:
        warnings[guild_id][user_id] = []
    
    warning = {
        'reason': reason,
        'mod': str(ctx.author),
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'warning_id': len(warnings[guild_id][user_id]) + 1
    }
    warnings[guild_id][user_id].append(warning)
    save_warnings(warnings)
    
    embed = discord.Embed(
        title="⚠️ User Warned",
        description=f"{member.mention} has been warned",
        color=discord.Color.orange()
    )
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
    embed.add_field(
        name="Total Warnings", 
        value=str(len(warnings[guild_id][user_id])), 
        inline=True
    )
    await ctx.send(embed=embed)
    
    # Try to DM the user
    try:
        await member.send(f"You were warned in **{ctx.guild.name}** for: {reason}")
    except:
        pass

@bot.command()
async def warnings(ctx, member: discord.Member = None):
    """Check warnings for a user"""
    if member is None:
        member = ctx.author
        
    warnings = load_warnings()
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)
    
    embed = discord.Embed(
        title=f"Warnings for {member.display_name}",
        color=discord.Color.purple()
    )
    
    if (guild_id in warnings and 
        user_id in warnings[guild_id] and 
        warnings[guild_id][user_id]):
        
        for w in warnings[guild_id][user_id]:
            embed.add_field(
                name=f"Warning #{w['warning_id']} - {w['date']}",
                value=f"**Reason:** {w['reason']}\n**By:** {w['mod']}",
                inline=False
            )
        embed.set_footer(text=f"Total: {len(warnings[guild_id][user_id])} warnings")
    else:
        embed.description = "This user has no warnings! ✅"
    
    await ctx.send(embed=embed)

@bot.command()
async def coinflip(ctx):
    """Flip a coin"""
    result = random.choice(["Heads", "Tails"])
    await ctx.send(f"🪙 **{result}**!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    content = message.content.lower()
    
    # Auto-responder
    greetings = ['hello', 'hi', 'hey', 'sup']
    if any(greet in content for greet in greetings):
        await message.channel.send(f"Hey {message.author.mention}! 👋")
    
    thanks = ['thanks', 'thank you', 'thx']
    if any(word in content for word in thanks):
        if 'maya' in content or 'bot' in content:
            await message.channel.send("You're welcome! 😊")
    
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    """Check if bot is alive"""
    await ctx.send(f"Pong! 🏓 Latency: {round(bot.latency * 1000)}ms")

# Run the bot
TOKEN = os.environ.get('DISCORD_TOKEN')
if TOKEN is None:
    print("ERROR: DISCORD_TOKEN not found!")
    print("Please set it in Koyeb dashboard")
else:
    bot.run(TOKEN)