# ========== IMPORTS ==========
import hypixel
import json
import utils

from datetime import datetime

# ========== SETUPS ==========
hypixel.setKeys(['<key>'])

# ========== UTILS ==========
def analyzeUUIDFromMojang(text):
    uuidText = text.split("\",\"")[1]
    uuid = uuidText.split("\"")[2]

    return uuid

# ========== METHODS ==========
def getPlayerStats(discord, p, uuid, response):
    data = json.loads(json.dumps(p.JSON))

    if str(p.getGuildID()) == 'None':
        guild = 'None'
    else:
        guild = str(hypixel.Guild(p.getGuildID()).JSON)[int(str(hypixel.Guild(p.getGuildID()).JSON).index('name')):int(str(hypixel.Guild(p.getGuildID()).JSON).index('name'))+28].split('\'')[2]

    rank = str(p.getRank()).split('\'')[5]

    if "mcVersionRp" in data:
        version = data["mcVersionRp"]
    else:
        version = "1.8.9"

    karma = data["karma"]

    firstLogin = str(datetime.fromtimestamp(int(data["firstLogin"]) / 1e3)).split(".")[0]

    if "currentGadget" in data:
        currentGadget = data["currentGadget"]
    else:
        currentGadget = "None"

    if "currentPet" in data:
        currentPet = data["currentPet"]
    else:
        currentPet = "None"

    discordName = "idk man"
    if "socialMedia" in data:
        if "links" in data["socialMedia"]:
            if "DISCORD" in data["socialMedia"]["links"]:
                discordName = data["socialMedia"]["links"]["DISCORD"]
            else:
                discordName = "None"

    # rank
    # rank = str(p.getRank()).split('\'')[5]

    # guild
    # if str(p.getGuildID()) == 'None':
    #     guild = 'None'
    # else:
    #     guild = str(hypixel.Guild(p.getGuildID()).JSON)[int(str(hypixel.Guild(p.getGuildID()).JSON).index('name')):int(str(hypixel.Guild(p.getGuildID()).JSON).index('name'))+28].split('\'')[2]

    # version
    # version = str(p.JSON)[int(str(p.JSON).index('mcVersionRp')):int(str(p.JSON).index('mcVersionRp'))+28].split('\'')[2]

    # first login
    # firstLoginText = str(p.JSON)[int(str(p.JSON).index('firstLogin')):int(str(p.JSON).index('firstLogin'))+28].split('\'')[1]
    # firstLoginText = firstLoginText.split(' ')[1]
    # firstLoginText = firstLoginText.split(',')[0]
    # date = datetime.fromtimestamp(int(firstLoginText) / 1e3)
    # date = str(date).split('.')[0]

    title = "[" + rank + "] " + str(p.getName())
    desc = " "

    if rank == "VIP":
        color = discord.Colour.from_rgb(85,255,85)
    elif rank == "VIP+":
        color = discord.Colour.from_rgb(85,255,85)
    elif rank == "MVP":
        color = discord.Colour.from_rgb(85,255,255)
    elif rank == "MVP+":
        color = discord.Colour.from_rgb(85,255,255)
    elif rank == "MVP++":
        color = discord.Colour.from_rgb(255,170,0)
    elif rank == "Builder":
        color = discord.Colour.from_rgb(0,170,170)
    elif rank == "YouTube":
        color = discord.Colour.from_rgb(255,85,85)
    elif rank == "Helper":
        color = discord.Colour.from_rgb(85,85,255)
    elif rank == "Moderator":
        color = discord.Colour.from_rgb(0,170,0)
    elif rank == "Admin":
        color = discord.Colour.from_rgb(170,0,0)
    else:
        color = discord.Colour.from_rgb(170,170,170)

    embed = discord.Embed(description=desc, colour=color)
    embed.set_author(name = title, icon_url = 'https://hypixel.net/favicon-32x32.png', url = 'https://hypixel.net/')
    embed.set_thumbnail(url = 'https://visage.surgeplay.com/head/' + uuid)

    embed.add_field(name = 'IGN', value = '`' + str(p.getName()) + '`', inline = True)
    embed.add_field(name = 'Rank', value = '`' + str(rank) + '`', inline = True)
    if guild == 'None':
        embed.add_field(name = 'Guild', value = '`' + str(guild) + '`', inline = True)
    else:
        embed.add_field(name = 'Guild', value = '[' + str(guild) + '](https://hypixel.net/guilds/' + str(guild) + ')', inline = True)
    embed.add_field(name = 'Level', value = '`' + str(int(float(p.getLevel()*100))/100) + '`', inline = True)
    embed.add_field(name = 'Version', value = '`' + str(version) + '`', inline = True)
    embed.add_field(name = "First Login", value = '`' + str(firstLogin) + '`', inline = True)
    embed.add_field(name = "Discord", value = '`' + str(discordName) + '`')
    embed.add_field(name = "Gadget", value = '`' + str(currentGadget) + '`', inline = True)
    embed.add_field(name = "Pet", value = '`' + str(currentPet) + '`', inline = True)
    embed.add_field(name = "Karma", value = '`' + str("{:,}".format(karma)) + '`', inline = True)

    embed.set_image(url = 'https://visage.surgeplay.com/full/512/' + uuid + '.png')
    embed.set_footer(text = '❤️ The bot was made by LielAmar')
    return embed
