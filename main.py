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
    """Load all custom autoresponder triggers"""
    try:
        with open(AUTORESPONDER_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_autoresponder(data):
    """Save autoresponder triggers"""
    with open(AUTORESPONDER_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ========== BOT EVENTS ==========
@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    print(f'Serving {len(bot.guilds)} server(s)')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="for custom triggers 👀"
    ))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # ===== AUTO-RESPONDER SYSTEM (MIMU STYLE) =====
    # Check if message is from a server (not DMs)
    if message.guild:
        guild_id = str(message.guild.id)
        autoresponder_data = load_autoresponder()
        
        # Check if this guild has any autoresponders
        if guild_id in autoresponder_data:
            content_lower = message.content.lower()
            
            # Loop through all triggers for this server
            for trigger, response in autoresponder_data[guild_id].items():
                if trigger in content_lower:
                    await message.channel.send(response)
                    break  # Only trigger once per message
    
    # ===== PROCESS COMMANDS (must be at the end) =====
    await bot.process_commands(message)

# ========== AUTORESPONDER MANAGEMENT COMMANDS ==========
@bot.group(name='autoresponder', aliases=['ar'], invoke_without_command=True)
async def autoresponder(ctx):
    """Manage custom autoresponders (like Mimu)"""
    embed = discord.Embed(
        title="🤖 Autoresponder Commands",
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
    """Add a new autoresponder trigger-response pair"""
    guild_id = str(ctx.guild.id)
    data = load_autoresponder()
    
    if guild_id not in data:
        data[guild_id] = {}
    
    # Add the new trigger-response
    data[guild_id][trigger.lower()] = response
    save_autoresponder(data)
    
    embed = discord.Embed(
        title="✅ Autoresponder Added",
        color=discord.Color.green()
    )
    embed.add_field(name="Trigger", value=f"`{trigger}`", inline=True)
    embed.add_field(name="Response", value=response, inline=True)
    await ctx.send(embed=embed)

@autoresponder.command(name='remove', aliases=['rm', 'delete'])
@commands.has_permissions(manage_messages=True)
async def ar_remove(ctx, *, trigger: str):
    """Remove an autoresponder trigger"""
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
    """List all autoresponders in this server"""
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
        await ctx.send("📭 No autoresponders set in this server yet!")

@autoresponder.command(name='clear')
@commands.has_permissions(administrator=True)
async def ar_clear(ctx):
    """Clear ALL autoresponders (admin only)"""
    guild_id = str(ctx.guild.id)
    data = load_autoresponder()
    
    if guild_id in data:
        del data[guild_id]
        save_autoresponder(data)
        await ctx.send("🗑️ All autoresponders cleared!")
    else:
        await ctx.send("📭 No autoresponders to clear.")

# ========== RULES COMMAND WITH CUSTOM FLOWER EMOJIS ==========
@bot.command()
async def rules(ctx):
    """Post server rules with custom flower emojis"""
    
    # Your flower emojis
    flower1 = "<:831009762262515742:831009762262515742>"
    flower2 = "<:831009762124627998:831009762124627998>"
    flower3 = "<:831009761897349130:831009761897349130>"
    flower4 = "<:831009762258452501:831009762258452501>"
    
    embed = discord.Embed(
        title=f"{flower1}{flower2} **SERVER RULES** {flower3}{flower4}",
        description="Please read all rules carefully. Breaking them may result in warnings, mutes, or bans.",
        color=0xFFB6C1  # Soft pink to match flower vibes
    )
    
    # Rule 1
    embed.add_field(
        name=f"{flower1} **1. Be Respectful** {flower1}",
        value="• Treat everyone with kindness.\n• No hate speech, bullying, harassment, or toxicity.\n• Discrimination based on skin color, race, religion, nationality, gender, orientation, or appearance will not be tolerated.",
        inline=False
    )
    
    # Rule 2
    embed.add_field(
        name=f"{flower2} **2. No Spamming** {flower2}",
        value="• Avoid flooding the chat.\n• No excessive caps, repeated messages, or emoji spam.",
        inline=False
    )
    
    # Rule 3
    embed.add_field(
        name=f"{flower3} **3. Keep It SFW** {flower3}",
        value="• No NSFW content, sexual topics, or inappropriate jokes.\n• No gore, graphic, disturbing, or harmful content — including AI-generated images or videos that are violent, shocking, or hard to watch.\n• This is a safe space for everyone.",
        inline=False
    )
    
    # Rule 4
    embed.add_field(
        name=f"{flower4} **4. No Self-Promotion** {flower4}",
        value="• Do not advertise servers, socials, products, or anything else without permission from staff.",
        inline=False
    )
    
    # Rule 5
    embed.add_field(
        name=f"{flower1} **5. Use the Correct Channels** {flower1}",
        value="• Post in the right channel so everything stays organized and easy to find.",
        inline=False
    )
    
    # Rule 6
    embed.add_field(
        name=f"{flower2} **6. Protect Privacy** {flower2}",
        value="• Never share your own or anyone else's personal information (age, location, school, photos, social media, etc.) without clear consent.",
        inline=False
    )
    
    # Rule 7
    embed.add_field(
        name=f"{flower3} **7. Stay Safe Online** {flower3}",
        value="• Do not click unknown or suspicious links.\n• Don't download files from strangers.\n• If something feels off, report it to staff immediately.",
        inline=False
    )
    
    # Rule 8
    embed.add_field(
        name=f"{flower4} **8. No Doxxing or Forced Reveals** {flower4}",
        value="• Posting someone's photos, personal details, private messages, or forcing face reveals without clear consent = instant ban.",
        inline=False
    )
    
    # Rule 9
    embed.add_field(
        name=f"{flower1}{flower2} **9. No Inappropriate Relationships Involving Minors** {flower3}{flower4}",
        value="• Romantic or sexual interactions involving minors, age-gaps that violate platform rules, or any behavior that makes minors uncomfortable are strictly prohibited and will result in immediate action.",
        inline=False
    )
    
    # Rule 10
    embed.add_field(
        name=f"{flower1} **10. Respect Staff Decisions** {flower1}",
        value="• Moderators and admins have the final say.\n• Publicly arguing, disrespecting, or bypassing punishments will not be tolerated.",
        inline=False
    )
    
    # Rule 11
    embed.add_field(
        name=f"{flower2}{flower3} **11. Have Fun & Stay Positive!** {flower4}{flower1}",
        value="• This is a chill and safe space — spread good vibes and enjoy your time here 💖",
        inline=False
    )
    
    # Important Notice
    embed.add_field(
        name=f"{flower4} **⚠️ Important** {flower1}",
        value="All members must also follow **[Discord Community Guidelines](https://discord.com/guidelines)** and **[Terms of Service](https://discord.com/terms)**. Breaking platform-wide rules may result in reports and permanent bans.",
        inline=False
    )
    
    # Footer
    embed.set_footer(
        text=f"{flower2} {ctx.guild.name} • Rules last updated {flower3}",
        icon_url=ctx.guild.icon.url if ctx.guild.icon else None
    )
    embed.timestamp = datetime.now()
    
    await ctx.send(embed=embed)

# ========== WARN COMMANDS ==========
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
    embed.add_field(name="Total Warnings", value=str(len(warnings[guild_id][user_id])), inline=True)
    await ctx.send(embed=embed)
    
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

@bot.command()
async def ping(ctx):
    """Check if bot is alive"""
    await ctx.send(f"Pong! 🏓 Latency: {round(bot.latency * 1000)}ms")

# Run the bot
TOKEN = os.environ.get('DISCORD_TOKEN')
if TOKEN is None:
    print("ERROR: DISCORD_TOKEN not found!")
    print("Please set it in your hosting dashboard")
else:
    bot.run(TOKEN)