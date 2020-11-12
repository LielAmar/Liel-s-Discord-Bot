# ========== IMPORTS ==========
import mysql.connector
import time

from discord.utils import get

# ========== UTILS ==========
multiplier = 1

def log(message):
    print(message)

def sort_list(list):
    length = len(list)
    for i in range(0, length):
        for j in range(0, length-i-1):
            if(list[j][2] < list[j +1][2]):
                temp = list[j]
                list[j] = list[j + 1]
                list[j + 1]= temp
    return list

# ========== VARIABLES ==========
db = mysql.connector.connect(host="localhost", user="liel", passwd="D6qOECc7KOPTJ14h", database="bot") # database connection
players = [] # list of players

# ========== CLASSES ==========
class Player:
    def __init__(self, player_id, lvl, total_exp, last_message):
        self.player_id = player_id
        self.lvl = int(lvl)
        self.total_exp = int(total_exp)
        self.last_message = last_message

def get_total_exp(player):
    return int(player.total_exp)

levels = []
def setup_levels(guild):
    global levels
    if len(levels) > 0:
        return levels
    roles = guild.roles
    lvl5plus = get(roles, id=751753513603956797)
    lvl10plus = get(roles, id=751753512903376937)
    lvl15plus = get(roles, id=751753512123236503)
    lvl20plus = get(roles, id=751753510713819146)
    lvl25plus = get(roles, id=751753508411277321)
    lvl30plus = get(roles, id=751753506242822184)
    lvl35plus = get(roles, id=752201885510795356)
    lvl40plus = get(roles, id=752201889445052437)
    lvl45plus = get(roles, id=752201892238458991)
    lvl50plus = get(roles, id=752201894876676118)
    lvl55plus = get(roles, id=752201897078816950)
    lvl60plus = get(roles, id=752202085319180380)

    levels = [(5, lvl5plus),(10, lvl10plus),(15, lvl15plus),(20, lvl20plus),(25, lvl25plus),(30, lvl30plus),(35, lvl35plus),(40, lvl40plus),(45, lvl45plus),(50, lvl50plus),(55, lvl55plus),(60, lvl60plus)]
    return levels

# ========== METHODS ==========
def getPlayer(player_id):
    player = None
    for p in players:
        if(p.player_id == player_id):
            player = p

    if player is not None:
        return player

    player = Player(player_id, getLevelFromDB(player_id), getTotalExpFromDB(player_id), 0)
    players.append(player)
    return player

async def add_exp(discord, member, player, current_time):
    player.total_exp = int(player.total_exp+multiplier)
    player.last_message = current_time

    channel = get(member.guild.channels, id=416654308155719680, type=discord.ChannelType.text)

    while levelUp(player):
        embed = getPlayerStats(discord, member, player, "levelup")
        
        await channel.send(embed=embed)
        await updateRoles(member, player)

def levelUp(player):
    lvl = player.lvl
    if lvl <= 15:
        needed_exp = lvl*lvl + 6*lvl
    elif lvl <= 31:
        needed_exp = 2.5*lvl*lvl - 40.5*lvl+360
    else:
        needed_exp = 4.5*lvl*lvl - 162.5*lvl+2220

    if player.total_exp >= needed_exp:
        player.lvl = player.lvl+1
        log("[PlayerSystem] Leveling up " + str(player.player_id) + " to level: " + str(player.lvl) + " because they have " + str(needed_exp) + " exp...")
        return True
    return False

async def updateRoles(user, player):
    setup_levels(user.guild)
    lvl = player.lvl
    for level in levels:
        if lvl >= level[0]:
            role = level[1];
            if not role in user.roles:
                await user.add_roles(role)

def addPlayerToDB(player_id):
    log("[PlayerSystem] Adding " + str(player_id) + " to the database...")
    cursor = db.cursor()
    cursor.execute("INSERT INTO players (player_id, lvl, total_exp) VALUES (" + str(player_id) + ", 0, 0)")
    db.commit()

def getLevelFromDB(player_id):
    cursor = db.cursor()
    sql = "SELECT lvl FROM players WHERE player_id=" + str(player_id)
    cursor.execute(sql)
    result = cursor.fetchall()

    # If player_id doesn't exists in the database
    if(len(result) == 0):
        addPlayerToDB(player_id)
        return 0

    for lvl in result:
        return int(lvl[0])
    return 0

def getPlayerStats(discord, user, player, type):
    if type == 'levelup':
        title = ' Leveled Up!'
        desc = 'Congratulations <@' + str(user.id) + '>, you have leveled up!'
    else:
        title = ' Stats'
        desc = 'These are your stats, <@' + str(user.id) + '> :)'

    lvl = player.lvl
    if lvl <= 15:
        needed_exp = lvl*lvl + 6*lvl
    elif lvl <= 31:
        needed_exp = 2.5*lvl*lvl - 40.5*lvl+360
    else:
        needed_exp = 4.5*lvl*lvl - 162.5*lvl+2220

    if lvl <= 5:
        rank = "Red"
        color = discord.Colour.from_rgb(255,85,85)
    elif lvl <= 10:
        rank = "Gold"
        color = discord.Colour.from_rgb(255,170,0)
    elif lvl <= 15:
        rank = "Lime"
        color = discord.Colour.from_rgb(85,255,85)
    elif lvl <= 20:
        rank = "Yellow"
        color = discord.Colour.from_rgb(255,255,85)
    elif lvl <= 25:
        rank = "Pink"
        color = discord.Colour.from_rgb(255,85,255)
    elif lvl <= 30:
        rank = "White"
        color = discord.Colour.from_rgb(245,245,245)
    elif lvl <= 35:
        rank = "Blue"
        color = discord.Colour.from_rgb(85,85,255)
    elif lvl <= 40:
        rank = "Green"
        color = discord.Colour.from_rgb(0,170,0)
    elif lvl <= 45:
        rank = "Dark Red"
        color = discord.Colour.from_rgb(170,0,0)
    elif lvl <= 50:
        rank = "Cyan"
        color = discord.Colour.from_rgb(0,170,170)
    elif lvl <= 55:
        rank = "Purple"
        color = discord.Colour.from_rgb(170,0,170)
    elif lvl <= 60:
        rank = "Gray"
        color = discord.Colour.from_rgb(170,170,170)
    else:
        rank = "Black"
        color = discord.Colour.from_rgb(0,0,0)

    embed = discord.Embed(description=desc, colour=color)
    embed.set_author(name= str(user.name) + title, icon_url = 'https://lielamar.com/cdn/numbers/' + str(lvl) + '.png', url = 'https://lielamar.com/')
    embed.set_thumbnail(url = user.avatar_url)
    # embed.set_image(url = 'https://lielamar.com/cdn/numbers/' + str(lvl) + '.png')
    embed.add_field(name = 'Your level', value = lvl, inline = False)
    embed.add_field(name = 'Your rank', value = rank, inline = False)
    embed.add_field(name = 'Total experience', value = str(player.total_exp) + "xp", inline = False)
    embed.add_field(name = 'Experience needed for next Level', value = str(needed_exp-player.total_exp) + "xp", inline = False)
    embed.set_footer(text = '❤️ The bot was made by LielAmar')
    return embed

def getLeaderboard(client, discord, page):
    cursor = db.cursor()
    sql = "SELECT * FROM players"
    cursor.execute(sql)
    result = sort_list(cursor.fetchall())

    if(page*5 > len(result)):
        page = 1

    embed = discord.Embed(description="Page " + str(page) + "/" + str(round(len(result)/5)), colour=discord.Colour.from_rgb(255,170,0))
    embed.set_author(name="Levels Leaderboard")

    counter = (page-1)*5
    while counter < page*5:
        user = client.get_user(int(result[counter][0]))

        if user is None:
            embed.add_field(name = str(counter+1) + ". " + result[counter][0], value = "Level: " + str(result[counter][1]) + ", Exp: " + str(result[counter][2]), inline = False)
        else:
            embed.add_field(name = str(counter+1) + ". " + user.name, value = "Level: " + str(result[counter][1]) + ", Exp: " + str(result[counter][2]), inline = False)

        counter = counter+1

    embed.set_footer(text = '❤️ The bot was made by LielAmar')
    return embed

def getTotalExpFromDB(player_id):
    cursor = db.cursor()
    sql = "SELECT total_exp FROM players WHERE player_id=" + str(player_id)
    cursor.execute(sql)
    result = cursor.fetchall()

    # If player_id doesn't exists in the database
    if(len(result) == 0):
        addPlayerToDB(player_id)
        return 0

    for total_exp in result:
        return str(total_exp[0])
    return 0

def saveToSQL(player):
    log("[PlayerSystem] Updating " + str(player.player_id) + ". Setting lvl to " + str(player.lvl) + ", total_exp to " + str(player.total_exp) + "...")
    cursor = db.cursor()
    cursor.execute("UPDATE players SET lvl={0}, total_exp={1} WHERE player_id={2}".format(str(player.lvl), str(player.total_exp), str(player.player_id)))
    db.commit()
