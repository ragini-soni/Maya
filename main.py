@bot.command()
@commands.is_owner()
async def only_me_command(ctx):
    await ctx.send("Only the bot owner can use this!")
import discord
from discord.ext import commands
import os
import json
import random
from datetime import datetime
import asyncio
from discord import app_commands

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

# File paths
WARNINGS_FILE = 'warnings.json'
AUTORESPONDER_FILE = 'autoresponder.json'

# ========== HELPER FUNCTIONS ==========
def load_warnings():
    try:
        with open(WARNINGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_warnings(warnings):
    with open(WARNINGS_FILE, 'w') as f:
        json.dump(warnings, f, indent=4)

def load_autoresponder():
    try:
        with open(AUTORESPONDER_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_autoresponder(data):
    with open(AUTORESPONDER_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ========== RULES EMBED FUNCTION ==========
def create_rules_embed(guild):
    """Create rules embed - FILL WITH YOUR OWN RULES"""
    
    embed = discord.Embed(
        title="📜 **SERVER RULES**",
        description="Please read all rules carefully. Breaking them may result in warnings, mutes, or bans.",
        color=0xFFB6C1  # Soft pink - change if you want
    )
    
    # ===== TYPE YOUR RULES HERE =====
    # Just copy-paste these blocks and fill in YOUR rules
    
    embed.add_field(
        name="🔹 **1. [YOUR RULE TITLE]**",
        value="• [Your rule details here]\n• [More points if needed]",
        inline=False
    )
    
    embed.add_field(
        name="🔹 **2. [YOUR RULE TITLE]**",
        value="• [Your rule details here]",
        inline=False
    )
    
    embed.add_field(
        name="🔹 **3. [YOUR RULE TITLE]**",
        value="• [Your rule details here]",
        inline=False
    )
    
    embed.add_field(
        name="🔹 **4. [YOUR RULE TITLE]**",
        value="• [Your rule details here]",
        inline=False
    )
    
    embed.add_field(
        name="🔹 **5. [YOUR RULE TITLE]**",
        value="• [Your rule details here]",
        inline=False
    )
    
    # Add more fields as needed - just copy this pattern:
    # embed.add_field(
    #     name="🔹 **[NUMBER]. [TITLE]**",
    #     value="• [Details]",
    #     inline=False
    # )
    
    embed.set_footer(
        text=f"{guild.name} • Rules",
        icon_url=guild.icon.url if guild.icon else None
    )
    embed.timestamp = datetime.now()
    
    return embed

# ========== BOT EVENTS ==========
@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    print(f'Serving {len(bot.guilds)} server(s)')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="for custom triggers 👀"
    ))
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"❌ Error syncing slash commands: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # ===== AUTO-RESPONDER SYSTEM (MIMU STYLE) =====
    if message.guild:
        guild_id = str(message.guild.id)
        autoresponder_data = load_autoresponder()
        
        if guild_id in autoresponder_data:
            content_lower = message.content.lower()
            
            # Check each trigger
            for trigger, response in autoresponder_data[guild_id].items():
                if trigger in content_lower:
                    await message.channel.send(response)
                    break
    
    await bot.process_commands(message)

# ========== RULES COMMAND ==========
@bot.command()
async def rules(ctx):
    """Post server rules"""
    embed = create_rules_embed(ctx.guild)
    embed.set_footer(text=f"Requested by {ctx.author.name} • Rules")
    await ctx.send(embed=embed)

# ========== SETUP RULES COMMAND (Posts to #rules channel) ==========
@bot.command()
@commands.has_permissions(administrator=True)
async def setrules(ctx):
    """Set up permanent rules in #rules channel"""
    
    # Find rules channel
    rules_channel = None
    for channel in ctx.guild.text_channels:
        if channel.name.lower() in ['rules', '📜rules', 'rule', 'server-rules']:
            rules_channel = channel
            break
    
    if not rules_channel:
        await ctx.send("❌ Please create a channel named #rules first!")
        return
    
    # Create embed
    embed = create_rules_embed(ctx.guild)
    
    # Clear old bot messages
    async for message in rules_channel.history(limit=20):
        if message.author == bot.user:
            await message.delete()
    
    # Post new rules
    await rules_channel.send(embed=embed)
    await ctx.send(f"✅ Rules updated in {rules_channel.mention}!")

# ========== WARN COMMAND WITH DESI STYLE ==========
@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    """Warn a user (mods only) - with desi style!"""
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
    
    # FUNNY DESI WARNING MESSAGE
    desi_messages = [
        "**CHHI CHHI!** Rules rules todte tum kese insaan ho?! 😤",
        "**AREY YAAR!** Rules todi? Sharam karo! 🫵😂",
        "**OYE!** Rule book phaad diya kya? ⚠️",
        "**NAINON MEIN KATAR!** Warning mil gayi ab sambhal! 💀",
        "**CHALO JI!** Ek warning register ho gayi! 📝",
        "**BHAI BHAI!** Rules yaad rakho thoda! 🤦‍♂️"
    ]
    
    embed = discord.Embed(
        title="⚠️ **USER WARNED!**",
        description=f"{member.mention} ko warning mil gayi!",
        color=discord.Color.orange()
    )
    embed.add_field(name="**Reason:**", value=f"`{reason}`", inline=False)
    embed.add_field(name="**Moderator:**", value=ctx.author.mention, inline=True)
    embed.add_field(name="**Total Warnings:**", value=str(len(warnings[guild_id][user_id])), inline=True)
    embed.add_field(name="**Desi Message:**", value=random.choice(desi_messages), inline=False)
    embed.set_footer(text=f"Warning #{warning['warning_id']} • Chhi chhi! 👀")
    
    await ctx.send(embed=embed)
    
    # Try to DM the user
    try:
        dm_message = f"**⚠️ You were warned in {ctx.guild.name}!**\n**Reason:** {reason}\n\n*{random.choice(['Rules yaad rakho! 📜', 'Agli baar mat karna! 👀', 'Chhi chhi!'])}*"
        await member.send(dm_message)
    except:
        pass

# ========== WARNINGS COMMAND ==========
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
        embed.description = "✅ Clean record! No warnings!"
    
    await ctx.send(embed=embed)

# ========== AUTORESPONDER MANAGEMENT COMMANDS ==========
@bot.group(name='autoresponder', aliases=['ar'], invoke_without_command=True)
async def autoresponder(ctx):
    """Manage custom autoresponders"""
    embed = discord.Embed(
        title="🤖 **Autoresponder Commands**",
        description="Manage your custom trigger-response pairs",
        color=discord.Color.blue()
    )
    embed.add_field(name="`!ar add <trigger> <response>`", value="Add a new autoresponder", inline=False)
    embed.add_field(name="`!ar remove <trigger>`", value="Remove an autoresponder", inline=False)
    embed.add_field(name="`!ar list`", value="Show all autoresponders", inline=False)
    embed.add_field(name="`!ar clear`", value="Clear ALL autoresponders (admin only)", inline=False)
    await ctx.send(embed=embed)

@autoresponder.command(name='add')
@commands.has_permissions(manage_messages=True)
async def ar_add(ctx, trigger: str, *, response: str):
    """Add a new autoresponder"""
    guild_id = str(ctx.guild.id)
    data = load_autoresponder()
    
    if guild_id not in data:
        data[guild_id] = {}
    
    data[guild_id][trigger.lower()] = response
    save_autoresponder(data)
    
    embed = discord.Embed(
        title="✅ Autoresponder Added!",
        color=discord.Color.green()
    )
    embed.add_field(name="Trigger", value=f"`{trigger}`", inline=True)
    embed.add_field(name="Response", value=response, inline=True)
    await ctx.send(embed=embed)

@autoresponder.command(name='remove', aliases=['rm', 'delete'])
@commands.has_permissions(manage_messages=True)
async def ar_remove(ctx, *, trigger: str):
    """Remove an autoresponder"""
    guild_id = str(ctx.guild.id)
    data = load_autoresponder()
    
    if guild_id in data and trigger.lower() in data[guild_id]:
        del data[guild_id][trigger.lower()]
        save_autoresponder(data)
        await ctx.send(f"✅ Removed trigger: `{trigger}`")
    else:
        await ctx.send(f"❌ Trigger `{trigger}` not found!")

@autoresponder.command(name='list')
async def ar_list(ctx):
    """List all autoresponders"""
    guild_id = str(ctx.guild.id)
    data = load_autoresponder()
    
    if guild_id in data and data[guild_id]:
        embed = discord.Embed(
            title=f"📋 Autoresponders in {ctx.guild.name}",
            color=discord.Color.purple()
        )
        
        for trigger, response in data[guild_id].items():
            embed.add_field(
                name=f"Trigger: {trigger}",
                value=f"➜ {response[:50]}{'...' if len(response) > 50 else ''}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("📭 No autoresponders set yet!")

@autoresponder.command(name='clear')
@commands.has_permissions(administrator=True)
async def ar_clear(ctx):
    """Clear ALL autoresponders"""
    guild_id = str(ctx.guild.id)
    data = load_autoresponder()
    
    if guild_id in data:
        del data[guild_id]
        save_autoresponder(data)
        await ctx.send("🗑️ All autoresponders cleared!")
    else:
        await ctx.send("📭 No autoresponders to clear.")

# ========== FUN COMMANDS ==========
@bot.command()
async def coinflip(ctx):
    """Flip a coin"""
    result = random.choice(["Heads", "Tails"])
    responses = [
        f"🪙 **{result}**!",
        f"Coin says... **{result}**! 🎲",
        f"**{result}**! Kismat! ✨"
    ]
    await ctx.send(random.choice(responses))

@bot.command()
async def ping(ctx):
    """Check if bot is alive"""
    latency = round(bot.latency * 1000)
    responses = [
        f"Pong! 🏓 `{latency}ms`",
        f"Zinda hoon! `{latency}ms` 🤖",
        f"Active! `{latency}ms` ⚡"
    ]
    await ctx.send(random.choice(responses))

# ========== SLASH COMMANDS ==========
@bot.tree.command(name="say", description="Send a message through Maya")
@app_commands.describe(
    channel="The channel to send the message to",
    message="What you want Maya to say"
)
async def say_command(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ You need `Manage Messages` permission!", ephemeral=True)
        return
    
    await channel.send(f"**{interaction.user.name} says:** {message}")
    await interaction.response.send_message(f"✅ Message sent to {channel.mention}!", ephemeral=True)

@bot.tree.command(name="dm", description="Send a DM through Maya")
@app_commands.describe(
    user="The user to DM",
    message="What you want Maya to say"
)
async def dm_command(interaction: discord.Interaction, user: discord.User, message: str):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ You need `Manage Messages` permission!", ephemeral=True)
        return
    
    try:
        await user.send(f"**{interaction.user.name} (via Maya):** {message}")
        await interaction.response.send_message(f"✅ DM sent to {user.name}!", ephemeral=True)
    except:
        await interaction.response.send_message(f"❌ Couldn't DM {user.name}!", ephemeral=True)

# ========== RUN THE BOT ==========
TOKEN = os.environ.get('DISCORD_TOKEN')
if TOKEN is None:
    print("ERROR: DISCORD_TOKEN not found!")
    print("Please set it in your hosting dashboard")
else:
    bot.run(TOKEN)