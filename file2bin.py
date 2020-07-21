import aiohttp
import socket
from discord.ext import commands


async def make_mystbin(session, text):
    wr = aiohttp.MultipartWriter()
    t = wr.append(text)
    t.set_content_disposition("form-data", name="data")
    t = wr.append_json({"meta": [{"index": 0, "syntax": "python"}]})
    t.set_content_disposition("form-data", name="meta")
    async with session.post("https://mystb.in/api/pastes", data=wr) as resp:
        return "https://mystb.in/" + (await resp.json())["pastes"][0]["id"] + ".py"

bot = commands.Bot(command_prefix="?!")

@bot.command(aliases=["f2b", "f2m", "file2bin"])
async def file2mystbin(ctx):
    async for message in ctx.history(limit=10):
        if message.attachments:
            try:
                text = (await message.attachments[0].read()).decode()
            except UnicodeDecodeError:
                continue
            link = await make_mystbin(bot.session, text)
            await ctx.send(link)
            break
    else:
        await ctx.send("No file in the last 10 messages found.")

async def init():
    bot.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(family=socket.AF_INET))

with open("token.txt") as t:
    token = t.read()

bot.loop.run_until_complete(init())
bot.run(token.strip())
