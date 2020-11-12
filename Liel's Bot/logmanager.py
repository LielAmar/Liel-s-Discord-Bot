import datetime

def getJoinEmbed(discord, guild, member):
    time = datetime.datetime.now()

    title = 'Member Joined The Server'
    color = discord.Colour.from_rgb(85,255,85)
    desc = "<@" + str(member.id) + "> joined the Server. We are now **" + str(len(guild.members)) + "** members!"

    embed = discord.Embed(description=desc, colour=color)

    embed.set_footer(text = 'Date: ' + str(time))
    return embed

def getLeaveEmbed(discord, guild, member):
    time = datetime.datetime.now()

    title = 'Member Left The Server'
    color = discord.Colour.from_rgb(255,85,85)
    desc = "<@" + str(member.id) + "> left the Server. We are now **" + str(len(guild.members)) + "** members!"

    embed = discord.Embed(description=desc, colour=color)

    embed.set_footer(text = 'Date: ' + str(time))
    return embed

def getMessageEditEmbed(discord, channel, member, before, after):
    time = datetime.datetime.now()

    title = str(member.name) + '#' + str(member.discriminator)
    color = discord.Colour.from_rgb(0,0,130)
    desc = "<@" + str(member.id) + "> has edited a message!"

    embed = discord.Embed(description=desc, colour=color)

    embed.add_field(name = 'From', value = '`' + str(before) + '`', inline = False)
    embed.add_field(name = 'To', value = '`' + str(after) + '`', inline = False)
    embed.add_field(name = 'Channel', value = "<#" + str(channel.id) + ">", inline = False)

    embed.set_footer(text = 'Date: ' + str(time))
    return embed

def getMessageDeleteEmbed(discord, channel, member, msg, delete_by):
    time = datetime.datetime.now()

    title = str(member.name) + '#' + str(member.discriminator)
    color = discord.Colour.from_rgb(130,0,0)
    desc = delete_by + " has deleted a message!"

    embed = discord.Embed(description=desc, colour=color)

    embed.add_field(name = 'Message', value = '`' + str(msg) + '`', inline = False)
    embed.add_field(name = 'Channel', value = "<#" + str(channel.id) + ">", inline = False)
    embed.add_field(name = 'Author', value = "<@" + str(member.id) + ">", inline = False)

    embed.set_footer(text = 'Date: ' + str(time))
    return embed

def getUserRoleAddEmbed(discord, before, after, member):
    time = datetime.datetime.now()

    title = str(member.name) + '#' + str(member.discriminator) + "was updated!"
    desc = "<@" + str(member.id) + "> was updated!"

    updated_roles = ""

    if len(before) > len(after):
        color = discord.Colour.from_rgb(200,0,0)
        embed = discord.Embed(description=desc, colour=color)

        for role in before:
            if not role in after:
                updated_roles = updated_roles + role.name + ", "
        updated_roles = updated_roles[:-2]
        embed.add_field(name = 'Removed Roles', value = '`' + str(updated_roles) + '`', inline = False)
    else:
        color = discord.Colour.from_rgb(0,200,0)
        embed = discord.Embed(description=desc, colour=color)

        for role in after:
            if not role in before:
                updated_roles = updated_roles + role.name + ", "
        updated_roles = updated_roles[:-2]
        embed.add_field(name = 'Given Roles', value = '`' + str(updated_roles) + '`', inline = False)

    embed.set_footer(text = 'Date: ' + str(time))
    return embed
