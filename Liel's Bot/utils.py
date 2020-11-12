# Log a message to the console
def log(prefix, message):
    print("[" + prefix + "] " + message)

# Load the bot's profile picture
async def loadPFP(client):
   pfp_path = "/home/liel/bot/pfps/gray.png"
   fp = open(pfp_path, 'rb')
   pfp = fp.read()
   await client.user.edit(password=None, avatar=pfp)
