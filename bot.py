from cgitb import reset
from twitchio.ext import commands
import sqlite3
import config as cfg


#CMDS
#Twitch Purge Bot
#- ping
#- chatterarr
#- reset
#- purge

initChannel = ['arainuki']
#https://twitchtokengenerator.com/

create = "CREATE TABLE IF NOT EXISTS chatters (name text not null,channel text not null,time TIMESTAMP DEFAULT CURRENT_TIMESTAMP not null)"
create2 = "CREATE TABLE IF NOT EXISTS counter (counter integer);"
create3 = "INSERT INTO counter(counter) VALUES ('1')"


abfrage = "SELECT * FROM chatters WHERE (time BETWEEN datetime(CURRENT_TIMESTAMP, '-15 minute') and Current_timestamp) and channel = '{}'"
insert = "INSERT INTO chatters (name,channel) VALUES ('{}','{}')"
update = "UPDATE chatters SET time = CURRENT_TIMESTAMP WHERE (name = '{}' and channel = '{}')"
counting = "SELECT COUNT(name) FROM chatters WHERE (name = '{}' and channel = '{}')"


couUp = "UPDATE counter SET counter = counter + 1"
resetCounterStr = "UPDATE counter SET counter = '0'"
getCounter = "SELECT counter from counter"
delete = "DELETE from chatters where channel = '{}'"


conn = sqlite3.connect('chat.db');
print ("Datenbasis wurde erfolgreich eröffnet.");
conn.execute(create)
conn.execute(create2)
conn.execute(create3)


print(conn.execute(abfrage.format("arainuki")).fetchall())
conn.commit()

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=cfg.TOKEN, prefix='?!', initial_channels=initChannel)

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
    
    async def event_message(self, message):
        if message.echo:
            return
        name = message.author.name
        channel = message.channel.name
        print(f"{name} hat folgendes im Channel {channel} geschrieben: {message.content}")
        cursor = conn.execute(counting.format(name,channel))
        zahl = cursor.fetchone()[0]
        print("Zahl test:",zahl)
        mod = message.author.is_mod
        if zahl == 0 and not mod:        
            conn.execute(insert.format(name,channel))
        if zahl > 0 and not mod:
            conn.execute(update.format(name,channel))
        conn.commit()
        result = conn.execute(abfrage.format("arainuki")).fetchall()
        concat = ""
        for entry in result:
            concat = entry[0] + ","+concat
        print(f'Ich habe foldende User registiert:{concat}!')
        await self.handle_commands(message)
   
    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.reply(f'Pong {ctx.author.name}!')

    @commands.command()
    async def content(self, ctx: commands.Context):
        if ctx.author.is_mod or True:
            result = conn.execute(abfrage.format(ctx.channel.name)).fetchall()
            concat = ""
            for entry in result:
                concat = entry[0] + ","+concat
            print(f'Ich habe foldende User registiert:{result}!')
            await ctx.reply(f"Liste: {concat}")
        else:
            await ctx.reply(f'Nope.')
       
    @commands.command()
    async def purge(self, ctx: commands.Context):
        if ctx.author.is_mod:
            result = conn.execute(abfrage.format(ctx.channel.name))
            for entry in result:
                await ctx.send(f'/timeout {entry[0]} 1 Chat-Purge')
                print(entry[0])
                #await ctx.send(f"/delete {entry[0]}")
            conn.execute(delete.format(ctx.channel.name))
            conn.commit()
            await ctx.reply(f'Ausgeführt!')
        else:
            await ctx.reply(f'Nope!')
    
    @commands.command()
    async def counter(self,ctx: commands.Context):
        result = conn.execute(getCounter).fetchone()
        await ctx.send(f"Der aktuelle Counter steht bei {result[0]}.")

    @commands.command()    
    async def addcounter(self,ctx: commands.Context):
        if ctx.author.is_mod:
            conn.execute(couUp)
            conn.commit()
            await ctx.send(f"Der Counter wurde um 1 erhöht.")
        else:
            await ctx.reply(f"Nope")

    @commands.command()    
    async def resetcounter(self,ctx: commands.Context):
        print("resetCounter")
        if not ctx.author.is_mod:
            await ctx.reply(f"Nope.")
        else:
            conn.execute(resetCounterStr)
            conn.commit()
            await ctx.reply(f"Der Counter wurde auf 0 zurückgesetzt.")

try:
    bot = Bot()
    bot.run()
except KeyboardInterrupt:
    print("Schließe Datenbank")
    conn.close()
finally:
    conn.close()