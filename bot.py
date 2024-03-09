import time, random, json, asyncio, threading
from math import modf
from numpy import median
from ping3 import ping as ping_url
from disnake import Intents, Message, TextChannel, ApplicationCommandInteraction
from disnake.ext import commands

from detection import *
from format import *
from request import *

with open("settings.json", "r", encoding="utf-8") as file:
    data = json.load(file)
claiming_channels: list = data["claiming_channels"]
emoticons: list = data["emoticons"]
facts: list = data["facts"]


def automatic_header():
    global cookie
    while True:
        time.sleep(5)
        asyncio.run(update_headers(cookie))

bot = commands.InteractionBot(intents=Intents.all())

def split(data: list) -> int:
    for item in data:
        if item.isdigit():
            return item
    return 0

@bot.event
async def on_ready():
    global username, user_id, start_time, end_time
    channel: TextChannel = bot.get_channel(1209903087544827994)

    await channel.send(f"succesfully loaded as **{username}** *({user_id})* in `{round(end_time - start_time, 3)}s`!")

@bot.event
async def on_message(msg: Message):
    global username, user_id, headers, cookie
    if msg.channel.id in claiming_channels:
        group_id: int = 0
        if "roblox.com/groups" in msg.content:
            group_id: int = split(msg.content.split("/"))
        
        if msg.embeds:
            embed = msg.embeds[0]

            if "roblox.com/groups" in embed.url:
                group_id: int = split(embed.url.split("/"))
            elif "roblox.com/groups" in embed.description:
                group_id: int = split(embed.description.split("/"))
            else:
                for field in embed.fields:
                    if "roblox.com/groups" in field.value:
                        group_id: int = split(field.value.split("/"))
                    elif "roblox.com/groups" in field.name:
                        group_id: int = split(field.name.split("/"))

        if group_id != 0:
            join_req, claim_req, time = await claim(group_id, headers)
            generate_text(f"trying to claim `{group_id}`", 0)
            channel: TextChannel = bot.get_channel(1209903087544827994)

            if join_req.status_code == 200:
                if claim_req.status_code == 200:
                    await shout(group_id, f"ggwp claimed by @mehhovcki in `{time}s`", headers)
                    generate_text(f"succesfully **claimed** `{group_id}` in `{time}s`!", 0)
                    await check_group(group_id, time, channel)
                else:
                    if claim_req.status_code in [400, 500, 403]:
                        await leave(group_id, user_id, headers)
                        await channel.send( f"succesfully **failed** to claim `{group_id}`, someone got it faster :( *[{time}]*" )
                        generate_text(f"succesfully **failed** claimed `{group_id}` in `{time}s` :( [claimed already]", 0) 
                    elif claim_req.status_code == 429:
                        await channel.send( f"succesfully **failed** to claim `{group_id}`, got ratelimit *(wompwomp)* :( *[{time}]*" )
                        generate_text(f"succesfully **failed** claimed `{group_id}` in `{time}s` :( [ratelimit]", 0)
                    username, user_id, cookie, headers = await account_switch(bot)
            else:
                if join_req.status_code == 403:
                    await channel.send( f"succesfully **failed** to claim `{group_id}`, account got full / captcha!! *[{time}]*" )
                    generate_text(f"succesfully **failed** claimed `{group_id}` in `{time}s` :( [full/captcha]", 0)
                    username, user_id, cookie, headers = await account_switch(bot)
                elif join_req.status_code == 429:
                    await channel.send( f"faled to claim `{group_id}`, ratelimit :( *[{time}]*" )
                    generate_text(f"succesfully **failed** claimed `{group_id}` in `{time}s` :( [ratelimit]", 0)
                    username, user_id, cookie, headers = await account_switch(bot)


@bot.slash_command(name="ping", description="🏓 Ping.. Pong.. Ping.. Pong")
async def ping(ctx: ApplicationCommandInteraction):
    global username, user_id
    await ctx.send(f"# Pong! `{random.choice(emoticons)}` \nMy latency is `{round(bot.latency * 1000)}ms`\nAutoclaiming as `{username}` *`({user_id})`* \n\n> **Random Fact:** {random.choice(facts)}")

@bot.slash_command(name="response", description="⏰ Response time from roblox.com or groups.roblox.com!")
@commands.cooldown(1, 30, commands.BucketType.user)
async def response(ctx: ApplicationCommandInteraction, action: str = commands.Param(name="action", choices=["roblox.com", "groups.roblox.com"])):
    responses: list = []
    ips: list = {"roblox.com": "128.116.95.4", "groups.roblox.com": "128.116.123.4"}
    await ctx.send(f"```\nC:\\Users\\Alexander $ ping {action}\n\n$ Sending requests to {action} [{ips[action]}]```", ephemeral=True)

    for i in range(4):
        time: float = ping_url(action)

        fractional, _ = modf(time)
        result = str(fractional)[2:5]

        responses.append(int(result))

        await ctx.edit_original_response(content=f"```\nC:\\Users\\Alexander $ ping {action}\n\n$ Sending requests to {action} [{ips[action]}]\n\n$ [Request #{i + 1}] bytes=32 time={result}ms TTL=51\n$ Trying again in 2 seconds...```")
        await asyncio.sleep(2)
    await ctx.edit_original_message(content=f"```\nC:\\Users\\Alexander $ ping {action}\n\n$ Sending requests to {action} [{ips[action]}]\n\n$ Answer from {ips[action]}: bytes=32 time={responses[0]}ms TTL=51\n$ Answer from {ips[action]}: bytes=32 time={responses[1]}ms TTL=51\n$ Answer from {ips[action]}: bytes=32 time={responses[2]}ms TTL=51\n$ Answer from {ips[action]}: bytes=32 time={responses[3]}ms TTL=51\n\n$ Statistics Ping for {ips[action]}: \n$     Packets: sent = 4, received = 4, losed = 0\n      (0% loss)\n$     Minimum = {min(responses)}ms, Maximum = {max(responses)}ms, Average = {median(responses)}ms```")

@response.error
async def on_error(ctx: ApplicationCommandInteraction, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("Sorry, you can use this command only 1 time every 30 seconds. 🤷‍♂️", ephemeral=True   )

@bot.slash_command(name="finder", description="🔎 Add, or remove groups from finder")
async def finder(ctx: ApplicationCommandInteraction, channel: TextChannel, action: str = commands.Param(name="action", choices=["add", "remove"])):
    global claiming_channels
    if not ctx.author.id in [bot.owner.id, 1137484045501092012]:
        return await ctx.send(f"Sorry, {ctx.author.mention}, you cannot use this command.")

    if action == "add":
        if channel.id in claiming_channels:
            return await ctx.send(f"You cannot add channel {channel.mention} twice!")

        claiming_channels.append(channel.id)
    else:
        if not channel.id in claiming_channels:
            return await ctx.send(f"You cannot remove channel {channel.mention}, because it wasnt added!")
        claiming_channels.remove(channel.id)

    data["claiming_channels"] = claiming_channels
    with open("settings.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    claiming_channels = data["claiming_channels"]
    await ctx.send(f"Succesfully added, or removed channel `{channel.id}` from finder.")

start_time: float = time.time()
username, user_id, cookie, headers = asyncio.run(account_switch(bot))
threading.Thread(target=automatic_header).start()
end_time: float = time.time()

os.system("cls")
generate_logo()

texts = [
    "=======================================",
    f"succesfully loaded as `{username}` ({user_id})!",
    f"took {round(end_time - start_time, 3)} seconds to load everything",
    f"claiming from {len(claiming_channels)} channels"
]

for text in texts:
    generate_text(text, 0)


bot.run("")