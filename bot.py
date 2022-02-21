from twitchio.ext import commands
import sqlite3
import config as cfg


#CMDS
#Twitch Purge Bot
#- ping
#- chatterarr
#- reset
#- purge

counterINT = 0
initChannel = ['arainuki']
#https://twitchtokengenerator.com/?code=17ld9c5vqcitalrldvfeqptaa76shw&scope=chat%3Aread+chat%3Aedit&state=frontend%7CREE0amFmd1ZYcFhrTzVEZ01HQzhxUT09

create = "CREATE TABLE IF NOT EXISTS chatters (name text not null,channel text not null,time TIMESTAMP DEFAULT CURRENT_TIMESTAMP not null)"
abfrage = "SELECT * FROM chatters WHERE (time BETWEEN datetime(CURRENT_TIMESTAMP, '-15 minute') and Current_timestamp)"
insert = "INSERT INTO chatters (name,channel) VALUES ('{}','{}')"
update = "UPDATE chatters SET time = CURRENT_TIMESTAMP WHERE (name = '{}' and channel = '{}')"
delete = ""
counting = "SELECT COUNT(name) FROM chatters WHERE (name = '{}' and channel = '{}')"

conn = sqlite3.connect('chat.db');
print ("Datenbasis wurde erfolgreich eröffnet.");
curser = conn.execute(create)
conn.commit()
#curser = conn.execute("select datetime(CURRENT_TIMESTAMP, '-15 minute')")
#curser = conn.execute("SELECT * FROM chatters")
curser = conn.execute(abfrage.format(initChannel[0]))
for row in curser:
    print(row)

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=cfg.TOKEN, prefix='?1?', initial_channels=initChannel)

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
        a = message.author.is_mod
        if zahl == 0 and not a:
            conn.execute(insert.format(name,channel))
        if zahl > 0 and not a:
            conn.execute(update.format(name,channel))
            
        conn.commit()
        await self.handle_commands(message)
   
    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.reply(f'Pong {ctx.author.name}!')

    @commands.command()
    async def chatterarr(self, ctx: commands.Context):
        if ctx.author.is_mod:
            result = conn.execute(abfrage.format(ctx.channel.name)).fetchall()

            await ctx.reply(f'Ich habe foldende User registiert:{result}!')
        else:
            await ctx.reply(f'Ich glaube das darf ich dir nicht verraten.')

    @commands.command()
    async def reset(self, ctx: commands.Context):
        if ctx.author.is_mod:
            await ctx.reply(f'OK!')
        else:
            await ctx.reply(f'Nope')
       
    @commands.command()
    async def purge(self, ctx: commands.Context):
        if ctx.author.is_mod:
            result = conn.execute(abfrage.format(ctx.channel.name))
            for entry in result:
                await ctx.send(f'/timeout {entry} 1 Chat-Purge')
            await ctx.reply(f'Ausgeführt!')
        else:
            await ctx.reply(f'Nope!')
    
    @commands.command()
    async def counter(self,ctx: commands.Context):
        await ctx.send(f"Der aktuelle Counter steht bei {counterINT}.")

    @commands.command()    
    async def addcounter(self,ctx: commands.Context):
        global counterINT
        if ctx.author.is_mod:
            counterINT = counterINT+1
            await ctx.send(f"Der Counter wurde um 1 erhöht.")
        else:
            await ctx.reply(f"Nope")

    @commands.command()    
    async def resetcounter(self,ctx: commands.Context):
        global counterINT
        if not ctx.author.is_mod:
            await ctx.reply(f"Nope")
        else:
            counterINT = 0
            await ctx.reply(f"Der Counter wurde auf 0 zurückgesetzt.")

try:
    bot = Bot()
    bot.run()
except KeyboardInterrupt:
    print("Schließe Datenbank")
    curser.close()
    conn.close()
finally:
    curser.close()
    conn.close()