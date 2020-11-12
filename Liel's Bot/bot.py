# ========== IMPORTS ==========
import hypixelmanager
import ticketmanager
import playermanager
import eventmanager
import logmanager

import utils
import lists

import requests
import discord
import random
import time

from discord.ext import commands, tasks
from discord.utils import get

# ========== SETUPS ==========
intents = discord.Intents().all()
client = commands.Bot(command_prefix = "!", intents=intents)
client.remove_command("help")

# ========== UTILS ==========
version = '1.1'
fish_times = 0

general_channels = ['606541782607724560', '416654308155719680', '717681883550318612']
private_channels = []

# ========== GENERAL ==========
# When the bot is ready
@client.event
async def on_ready():
    utils.log("General", "Starting up the bot")

    general_loop.start()
    users_update.start()

    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="over the server :)"))

# ========== EVENTS ==========
# Updates the users and saves them to the database every 10 minutes
@tasks.loop(minutes=10)
async def users_update():
    length = str(len(playermanager.players))
    utils.log("PlayerSystem", "Saving " + length + " players to the database...")

    for player in playermanager.players:
        playermanager.saveToSQL(player)
        utils.log("PlayerSystem", "Saved player id: " + str(player.player_id))

    playermanager.players = []
    utils.log("PlayerSystem", "Saved " + length + " players to the database!")

# Re-setting the variable fish_times to 0 every 24 hours to let players use it again!
@tasks.loop(hours=24)
async def general_loop():
    fish_times = 0
    utils.log("General", "Resetting the fish_times variable!")

# ========== Events ==========
# - Events channel message
# - Adding XP to the player
# - Tickets system
@client.event
async def on_message(message):
    if message.author.bot == True:
        await client.process_commands(message)
        return

    channel_id = str(message.channel.id)

    # ========== Ticket System ==========
    if channel_id == '730792324530962533':
        if('~new' in message.content) or ('!new' in message.content):
            guild = message.channel.guild
            member = message.author

            if not await ticketmanager.create_ticket(guild, member):
                channel = get(guild.channels, id=416654308155719680, type=discord.ChannelType.text)
                await channel.send('❌ <@' + str(member.id) + '>, you cannot create another support ticket yet!')
        await message.delete()
        return

    player = playermanager.getPlayer(message.author.id)

    # ========== Events System ==========
    if eventmanager.event_phase == 1:
        if eventmanager.check_answer(message):
            eventmanager.event_phase = 0
            player.total_exp = int(player.total_exp+(2*playermanager.multiplier))
            await message.channel.send("כל הכבוד " + message.author.name + "!" + "\nהתשובה הנכונה היא: " + str(eventmanager.event_math_answer) + " ואתה זכית ב-" + str(2*playermanager.multiplier) + " אקספיי על תשובה נכונה!")
            utils.log("EventSystem", "Ending Event. Winner is " + str(message.author.name) + "!")

    # ========== Level System ==========
    if any(x in channel_id for x in general_channels):
        current_time = time.time()
        isTimeoutExpired = current_time-player.last_message

        if isTimeoutExpired > 60:
            await playermanager.add_exp(discord, message.author, player, current_time)
            utils.log("PlayerSystem", "Adding " + str(playermanager.multiplier) + " exp to " + str(player.player_id))


    await client.process_commands(message)

# - Verification system
# - Tickets system
@client.event
async def on_raw_reaction_add(payload):
    member = payload.member
    channel = get(client.get_guild(payload.guild_id).channels, id=payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    if member.bot == True:
        return

    channel_id = str(message.channel.id)

    if str(message.id) == '761016602538803201':
        rank = get(member.guild.roles, id=761016664816353291)
        await member.add_roles(rank)

    # ========== Verification System ==========
    if str(channel.id) == '717646683529543781':
        rank = get(member.guild.roles, id=598634332608921600)

        embed = discord.Embed(description = '**' + member.name + '** just joined the server. We wish you a lovely stay!', colour = discord.Colour.green())
        channel = get(member.guild.channels, id=620617060770119695, type=discord.ChannelType.text)

        await channel.send(embed=embed)
        await member.add_roles(rank)

        utils.log("MemberSystem", "Verified user: " + member.name + "!")

    # ========== Ticket System ==========
    if channel_id == '730792324530962533':
        guild = channel.guild

        if not await ticketmanager.create_ticket(guild, member):
            channel = get(guild.channels, id=416654308155719680, type=discord.ChannelType.text)
            await channel.send('❌ <@' + str(member.id) + '>, you cannot create another support ticket yet!')

        await message.remove_reaction(message.reactions[0].emoji, member)
        return

@client.event
async def on_raw_reaction_remove(payload):
    member = payload.member
    channel = get(client.get_guild(payload.guild_id).channels, id=payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    if member is None:
        return

    if member.bot == True:
        return

    if str(message.id) == '761016602538803201':
        rank = get(member.guild.roles, id=761016664816353291)
        await member.remove_roles(rank)

# When a player leaves the server
@client.event
async def on_member_remove(member):
    embed = discord.Embed(description = '**' + member.name + '** just left the server. We hope to see you again soon!', colour = discord.Colour.red())
    channel = get(member.guild.channels, id=620617060770119695, type=discord.ChannelType.text)

    await channel.send(embed=embed)

    # ========== Logging Systen ==========
    embed = logmanager.getLeaveEmbed(discord, member.guild, member)
    channel = get(member.guild.channels, id=723956704676675694, type=discord.ChannelType.text)

    await channel.send(embed=embed)

# ========== LOGS ==========
@client.event
async def on_member_join(member):
    embed = logmanager.getJoinEmbed(discord, member.guild, member)
    channel = get(member.guild.channels, id=723956704676675694, type=discord.ChannelType.text)

    await channel.send(embed=embed)

@client.event
async def on_message_edit(before, after):
    if before.author.bot == True:
        return

    embed = logmanager.getMessageEditEmbed(discord, before.channel.guild, before.channel, before.author, before.content, after.content)
    channel = get(before.channel.guild.channels, id=723956704676675694, type=discord.ChannelType.text)

    await channel.send(embed=embed)

@client.event
async def on_message_edit(before, after):
    if before.author.bot == True:
        return

    embed = logmanager.getMessageEditEmbed(discord, before.channel, before.author, before.content, after.content)
    channel = get(before.channel.guild.channels, id=723956704676675694, type=discord.ChannelType.text)

    await channel.send(embed=embed)

@client.event
async def on_message_delete(message):
    if message.author.bot == True:
        return

    async for deleted_message in message.guild.audit_logs(action=discord.AuditLogAction.message_delete, limit=1):
        delete_by = "{0.user}".format(deleted_message)

    embed = logmanager.getMessageDeleteEmbed(discord, message.channel, message.author, message.content, delete_by)
    channel = get(message.channel.guild.channels, id=723956704676675694, type=discord.ChannelType.text)

    await channel.send(embed=embed)

@client.event
async def on_member_update(before, after):
    if before.bot == True:
        return

    if before.roles != after.roles:
        embed = logmanager.getUserRoleAddEmbed(discord, before.roles, after.roles, before)
        channel = get(before.guild.channels, id=723956704676675694, type=discord.ChannelType.text)

        await channel.send(embed=embed)

# ========== Private Channels ==========
@client.event
async def on_voice_state_update(member, before, after):
    if (not before is None) and (not before.channel is None):
        if str(before.channel.category_id) == '746994318945943622':
            if (not str(before.channel.id) == '749604499882115142') and (not str(before.channel.id) == '749920270059438090'):
                if len(before.channel.members) == 0:
                    await before.channel.delete()

    if (not after is None) and (not after.channel is None):
        if str(after.channel.id) == '749604499882115142':

            player = playermanager.getPlayer(member.id)
            if player.lvl < 7:
                msg = '<@' + str(member.id) + '> You must be level 7+ to create a private channel. Use !stats to view your current level!'
                embed = discord.Embed(description = msg, colour = discord.Colour.from_rgb(255,255,102))
                channel = get(member.guild.channels, id=416654308155719680, type=discord.ChannelType.text)

                await channel.send(embed=embed)
                await member.move_to(None)
                return

            channel = await after.channel.guild.create_voice_channel(member.name + "'s channel", overwrites=None, category=after.channel.category, reason="Temporary private channel", user_limit=1)
            await member.move_to(channel, reason=None)

            private_channels.append((str(member.id), str(channel.id)))
            channel = get(member.guild.channels, id=416654308155719680, type=discord.ChannelType.text)

            msg = '<@' + str(member.id) + '> we created a new private channel for you!\n• !vclimit <number> to change the user limit\n• !vcmove @<Member> to move them to your channel\n• !vckick @<Member> to kick them out of your channel\n• !vcdelete to delete the channel'
            embed = discord.Embed(description = msg, colour = discord.Colour.from_rgb(255,255,102))
            await channel.send(embed=embed)

# ========== Errors ==========
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Hey! You missed some arguments. Check your command again ^^")
        return
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("What were you trying to do? This command does not exists!")
        return
    if isinstance(error, commands.errors.BadArgument):
        await ctx.send("Bad Argument! If you tagged a player, make sure they exists!")
        return
    raise error

# ========== General Commands ==========
@client.command()
async def help(context):
    msg = "**General Commands**\n• !help - The help command\n• !version - The version command\n• !yt - Liel's Youtube Channel\n• !twitter - Liel's Twitter Account\n• !quote - Get a lovely quote\n" + "\n**Levels Commands**\n• !stats - View your current stats\n• !vclimit - change your channel's user limit (level 7+)\n• !vcmove - move someone to your private channel (level 7+)\n• !vckick - kick someone from your private channel (level 7+)\n• !vcdelete - delete your channel (level 7+)\n" + "\n**Hypixel Related**\n• !hypixel - View your general Hypixel Stats"
    embed = discord.Embed(description = msg, colour = discord.Colour.from_rgb(255,255,102))
    await context.send(embed=embed)

@client.command()
async def version(context):
    msg = "My Version is **Release " + version + "**"
    embed = discord.Embed(description = msg, colour = discord.Colour.from_rgb(255,170,0))
    await context.send(embed=embed)

@client.command()
async def yt(context):
    msg = "**Liel's Youtube Channel**\nhttps://www.youtube.com/channel/UCK9c8Rixqzy7LqG8eBDy9Fg"
    embed = discord.Embed(description = msg, colour = discord.Colour.from_rgb(255,0,0))
    await context.send(embed=embed)

@client.command()
async def twitter(context):
    msg = "**Liel's Twitter Account**\nhttps://twitter.com/ItsLielAmar"
    embed = discord.Embed(description = msg, colour = discord.Colour.from_rgb(0,172,238))
    await context.send(embed=embed)

@client.command()
async def quote(context):
    await context.send("\"" + random.choice(lists.quotes) + "\"")

@client.command()
async def admin(context):
    await context.send("\"" + random.choice(lists.admin) + "\"")

@client.command()
async def pokemon(context):
    await context.send("gotta catch 'em all")

@client.command()
async def shekel(context, target : discord.Member):
    await context.send(target.name + ' קח שקל')

@client.command()
async def shnekel(context, target : discord.Member):
    await context.send(target.name + ' קח שנקל')

@client.command()
async def amit(context):
    await context.send(random.choice(lists.amit))

@client.command()
async def roi(context):
    await context.send(random.choice(lists.roi))

@client.command()
async def gal(context):
    await context.send(random.choice(lists.gal))

@client.command()
async def nadav(context):
    await context.send(random.choice(lists.nadav))

@client.command()
async def raz(context):
    await context.send(random.choice(lists.raz))

@client.command()
async def yuval(context):
    await context.send(random.choice(lists.yuval))

@client.command()
async def liel(context):
    await context.send(random.choice(lists.liel))

@client.command()
async def dag(context):
    global fish_times
    if fish_times > 2:
        await context.send("We cannot DAG anymore! :fishing_pole_and_fish:")
        return
    for i in range(0, 5):
        fish_times = fish_times+1
        await context.send(':fish:')
        time.sleep(1)

@client.command()
async def kaboom(context):
    num = random.randint(0, 10)
    with open("images/kaboom/" + str(num) + '.gif', 'rb') as f:
        picture = discord.File(f)
        await context.message.channel.send(file=picture)
        return

@client.command()
async def hypixel(context, ign):
    sender = context.message.author
    channel = context.message.channel
    timestamp = str(int(time.time()))
    response = requests.get('https://api.mojang.com/users/profiles/minecraft/' + ign + '?at=' + timestamp)

    if response.status_code == 200:
        utils.log('Hypixel', 'Successfuly conntected to Mojang with the IGN ' + ign)

        try:
            uuid = hypixelmanager.analyzeUUIDFromMojang(response.text)
            p = hypixelmanager.hypixel.Player(uuid)

            if p is None:
                utils.log('Hypixel', 'Player not found on Hypixel ' + ign)
                await context.send("Couldn't find a player called " + ign)
            else:
                embed = hypixelmanager.getPlayerStats(discord, p, uuid, response)
                await context.send(embed=embed)
        except Exception as e:
            print(e)
            await context.send("Couldn't find a player called " + ign)
    elif response.status_code == 404:
        utils.log('Hypixel', 'Could not connect to Mojang with the IGN ' + ign)
        await context.send('Could not connect to Mojang with the IGN ' + ign)

# ========== Leveling Commands ==========
@client.command()
async def stats(context):
    player = None
    for p in playermanager.players:
        if(p.player_id == context.message.author.id):
            player = p

    if(player == None):
        player = playermanager.getPlayer(context.message.author.id)
        playermanager.players.append(player)

    embed = playermanager.getPlayerStats(discord, context.message.author, player, "stats")
    await context.message.channel.send(embed=embed)

@client.command()
async def leaderboard(context, page: int):
    if((page is None) or (int(page) < 1)):
        page = '1'

    embed = playermanager.getLeaderboard(client, discord, int(page))
    await context.message.channel.send(embed=embed)

# ========== Private Channel Commands ==========
@client.command()
async def vclimit(context, user_limit: int):
    member = context.message.author

    if member.voice.channel is None:
        await context.send("You are not in a voice channel!")
        return

    pc_id = member.voice.channel.id

    channel = None

    for pc in private_channels:
        if(pc[0] == str(member.id) and pc[1] == str(pc_id)):
            channel = get(member.guild.channels, id=pc_id, type=discord.ChannelType.voice)
            if channel is not None:
                break

    if channel is None:
        roles = [get(member.guild.roles, id=723658114741829723), get(member.guild.roles, id=597006943831195648)]
        for role in roles:
            if role in member.roles:
                channel = member.voice.channel

    if channel is not None:
        if((int(user_limit) < 1) or (int(user_limit) > 99)):
            user_limit = '2'
        await channel.edit(user_limit=int(user_limit))
        await context.send("User limit changed to: " + str(user_limit) + "!")
        return
    else:
        await context.send("We either couldn't find your channel/you don't have permissions in this channel.")
        return

@client.command()
async def vcmove(context, target : discord.Member):
    member = context.message.author

    if member.voice.channel is None:
        await context.send("You are not in a voice channel!")
        return

    if (target.voice.channel is None) or (str(target.voice.channel.id) != '749920270059438090'):
        await context.send("The targeted player is not in the the 'Waiting' Voice Channel!")
        return

    pc_id = member.voice.channel.id

    channel = None

    for pc in private_channels:
        if(pc[0] == str(member.id) and pc[1] == str(pc_id)):
            channel = get(member.guild.channels, id=pc_id, type=discord.ChannelType.voice)
            if channel is not None:
                break

    if channel is None:
        roles = [get(member.guild.roles, id=723658114741829723), get(member.guild.roles, id=597006943831195648)]
        for role in roles:
            if role in member.roles:
                channel = member.voice.channel

    if channel is not None:
        await target.move_to(channel, reason=None)
        return
    else:
        await context.send("We either couldn't find your channel/you don't have permissions in this channel.")
        return

@client.command()
async def vckick(context, target : discord.Member):
    member = context.message.author

    if member.voice.channel is None:
        await context.send("You are not in a voice channel!")
        return

    if (target.voice.channel is None) or (str(target.voice.channel.id) != str(member.voice.channel.id)):
        await context.send("The targeted player is not in your channel!")
        return

    pc_id = member.voice.channel.id

    channel = None

    for pc in private_channels:
        if(pc[0] == str(member.id) and pc[1] == str(pc_id)):
            channel = get(member.guild.channels, id=pc_id, type=discord.ChannelType.voice)
            if channel is not None:
                break

    if channel is None:
        roles = [get(member.guild.roles, id=723658114741829723), get(member.guild.roles, id=597006943831195648)]
        for role in roles:
            if role in member.roles:
                channel = member.voice.channel

    if channel is not None:
        await target.move_to(get(member.guild.channels, id=749920270059438090, type=discord.ChannelType.voice), reason=None)
        return
    else:
        await context.send("We either couldn't find your channel/you don't have permissions in this channel.")
        return

@client.command()
async def vcdelete(context):
    member = context.message.author

    if member.voice.channel is None:
        await context.send("You are not in a voice channel!")
        return

    pc_id = member.voice.channel.id

    channel = None

    for pc in private_channels:
        if(pc[0] == str(member.id) and pc[1] == str(pc_id)):
            channel = get(member.guild.channels, id=pc_id, type=discord.ChannelType.voice)
            if channel is not None:
                break

    if channel is None:
        roles = [get(member.guild.roles, id=723658114741829723), get(member.guild.roles, id=597006943831195648)]
        for role in roles:
            if role in member.roles:
                channel = member.voice.channel

    if channel is not None:
        await channel.delete()
        await context.send("Deleted your private channel!")
        return
    else:
        await context.send("We either couldn't find your channel/you don't have permissions in this channel.")
        return

# ========== Staff Commands ==========
def isStaff(context):
    member = context.message.author
    staff_roles = [get(context.message.author.guild.roles, id=597006943831195648), get(context.message.author.guild.roles, id=723658114741829723), get(context.message.author.guild.roles, id=751469916221079608), get(context.message.author.guild.roles, id=751476841029828670)]

    for role in staff_roles:
        for prole in member.roles:
            if role.id == prole.id:
                return True
    return False

def isManager(context):
    member = context.message.author
    manager_roles = [get(context.message.author.guild.roles, id=597006943831195648)]

    for role in manager_roles:
        for pRole in member.roles:
            if role.id == pRole.id:
                return True
    return False

# Supporter Command
# Shows a list of staff commands
@client.command()
async def shelp(context):
    if not isStaff(context):
        return

    if (str(context.message.channel.category_id) != '720258181871173642'):
        return

    msg = "**Staff Commands**\n• !shelp - The staff help command\n• !close - Closes a ticket (works only in the support category)\n• !shutup <time> - Mutes the channel for X seconds\n• !givexp <Player> <XP> - Gives XP xp to the player Player\n• !forcesave - Forcesaves the leaderboard\n• !xpmultiplier <multiplier> - Changes the XP multiplier\n• !slap - Kicks everyone in your channel to different channels\n• !pull - Pulls everyone to your channel!"
    embed = discord.Embed(description = msg, colour = discord.Colour.from_rgb(255,255,102))
    await context.send(embed=embed)

# Supporter Command
# Closes a ticket
@client.command()
async def close(context):
    if not isStaff(context):
        return

    channel = context.message.channel
    if not await ticketmanager.close_ticket(channel):
        await context.send("This is not a ticket channel!")

# Supporter Command
# Mutes the chat for arg(time) seconds
@client.command()
async def shutup(context, seconds: int):
    if not isStaff(context):
        return

    if seconds > 30:
        if not isManager(context):
            seconds = 30

    if seconds > 120:
        seconds = 120

    channel = context.message.channel
    await channel.set_permissions(get(context.message.guild.roles, name='@everyone'), send_messages=False)
    await channel.set_permissions(get(context.message.guild.roles, id=598634332608921600), send_messages=False)
    await context.send("Channel muted for " + str(seconds) + " seconds!")
    time.sleep(seconds)
    await channel.set_permissions(get(context.message.guild.roles, name='@everyone'), send_messages=True)
    await channel.set_permissions(get(context.message.guild.roles, id=598634332608921600), send_messages=True)

# Manager Command
# Gives xp to the selected player
@client.command()
async def givexp(context, target : discord.Member, amount: int):
    if not isManager(context):
        return

    if amount <= 0:
        amount = 1

    player = playermanager.getPlayer(target.id)
    player.total_exp = int(player.total_exp+int(amount))

    while playermanager.levelUp(player) == True:
        channel = get(target.guild.channels, name='〔🤖〕bots', type=discord.ChannelType.text)
        embed = playermanager.getPlayerStats(discord, target, player, "levelup")
        await channel.send(embed=embed)
        await playermanager.updateRoles(target, player)

    await context.message.channel.send("given xp to the player")

# Manager Command
# Forcesaves the leaderboard
@client.command()
async def forcesave(context):
    if not isManager(context):
        return

    for player in playermanager.players:
        playermanager.saveToSQL(player)
    await context.message.channel.send("forcesaved")

# Manager Command
# Changes the XP multiplier
@client.command()
async def xpmultiplier(context, multiplier: int):
    if not isManager(context):
        return

    playermanager.multiplier = multiplier
    await context.message.channel.send("changed the XP multiplier to " + str(multiplier))
    return

# Manager Command
# Starts a quickmath question
@client.command()
async def quickmath(context):
    if not isManager(context):
        return

    channel = context.message.channel

    type = random.randint(1, 1)
    eventmanager.event_type = type
    if type == 1:
        utils.log("[EventSystem] Starting an event...")
        eventmanager.event_phase = 1
        sign = random.randint(1, 4)
        if sign == 1:
            a = random.randint(1, 1000)
            b = random.randint(1, 1000)
            eventmanager.event_math_answer = int(int(a)+int(b))
            await channel.send("`איוונט:` מה הפתרון לבעיית המתמטיקה הבאה?" + "\n`" + str(a) + "+" + str(b) + "`")
        elif sign == 2:
            a = random.randint(1, 1000)
            b = random.randint(1, 1000)
            if b > a:
                c = a
                a = b
                b = c
            eventmanager.event_math_answer = int(int(a)-int(b))
            await channel.send("`איוונט:` מה הפתרון לבעיית המתמטיקה הבאה?" + "\n`" + str(a) + "-" + str(b) + "`")
        elif sign == 3:
            a = random.randint(1, 250)
            b = random.randint(1, 250)
            eventmanager.event_math_answer = int(int(a)*int(b))
            await channel.send("`איוונט:` מה הפתרון לבעיית המתמטיקה הבאה?" + "\n`" + str(a) + "*" + str(b) + "`")
        elif sign == 4:
            a = random.randint(1, 250)
            b = random.randint(1, 250)
            while b%a != 0:
                b = random.randint(1, 35)
            if b > a:
                c = a
                a = b
                b = c
            eventmanager.event_math_answer = int(int(a)/int(b))
            await channel.send("`איוונט:` מה הפתרון לבעיית המתמטיקה הבאה?" + "\n`" + str(a) + "/" + str(b) + "`")

# Manager Command
# Slaps everyone out of your room to different rooms
@client.command()
async def slap(context):
    if not isManager(context):
        return

    member = context.message.author

    if member.voice.channel is None:
        await context.message.channel.send("You are not in a channel!")
        return

    voice_channels = get(member.guild.categories, id=598627960248991809)
    amount_of_players = len(member.voice.channel.members)

    for player in member.voice.channel.members:
        if player.id == member.id:
            continue

        await player.move_to(random.choice(voice_channels.channels), reason=None)

    await channel.send("<@" + str(member.id) + " has slapped " + str(amount_of_players) + " players out of their channel!")

# Manager Command
# Pulls everyone to your channel
@client.command()
async def pull(context):
    if not isManager(context):
        return

    member = context.message.author
    amount_of_players = 0

    if member.voice.channel is None:
        await context.message.channel.send("You are not in a channel!")
        return

    for channel in member.guild.channels:
        if isinstance(channel, discord.VoiceChannel):
            for player in channel.members:
                amount_of_players = amount_of_players+1
                await player.move_to(member.voice.channel, reason=None)

    await channel.send("<@" + str(member.id) + " has pulled " + str(amount_of_players) + " players to their channel!")

client.run('<Token>')
