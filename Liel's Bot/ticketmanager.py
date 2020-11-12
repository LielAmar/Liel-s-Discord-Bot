# ========== IMPORTS ==========
import random
import time

from discord.utils import get

# ========== SETUPS ==========
ticket_cooldown = []

# ========== METHODS ==========
async def create_ticket(guild, member):
    for cooldown_member in ticket_cooldown:
        if (cooldown_member[0] == member.id):
            if (time.time()-cooldown_member[1]) < 3600:
                return False

    staff_roles = [get(guild.roles, id=597006943831195648), get(guild.roles, id=723658114741829723), get(guild.roles, id=751469916221079608), get(guild.roles, id=751476841029828670)]

    id = random.randint(0, 1000000)
    name = 'ticket-' + str(id)

    ticket = await guild.create_text_channel(name)
    # ticket = get(guild.channels, name=name, type=discord.ChannelType.text)
    await ticket.edit(category=get(guild.categories, id=730794905487540284))

    await ticket.set_permissions(get(guild.roles, name='@everyone'), read_messages=False)
    await ticket.set_permissions(member, read_messages=True, send_messages=True)
    for role in staff_roles:
        await ticket.set_permissions(role, read_messages=True, send_messages=True)

    await ticket.send('✔️ <@' + str(member.id) + '>, your support ticket has been created! <@&' + str(staff_roles[1].id) + '>')

    # ticket_cooldown
    # tuple = (member.id, int(round(time.time() * 1000)))
    ticket_cooldown.append((member.id, time.time() * 1000))
    return True

async def close_ticket(channel):
    if str(channel.category.id) != '730794905487540284':
        return False

    # messages = []
    # last_message = channel.last_message
    #
    # while last_message is not None:
    #     messages.insert(0, last_message.author.name + ": " + last_message.content)
    #
    #     last_message.delete()
    #     last_message = channel.last_message

    # with open('/tickets/' + channel.name + '.txt', 'w+') as f:
    #     for item in messages:
    #         f.write("%s\n" % messages)

    await channel.delete()
    return True
