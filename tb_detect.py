import re
import importlib
import inspect
from dataclasses import dataclass
from typing import List, Tuple

import discord


@dataclass
class Line:
    file: str
    num: str
    cont_name: str
    source: str

@dataclass
class Traceback:
    lines: List[str]
    exc: Tuple[str, str]

    @classmethod
    def from_string(cls, s):
        if not s.startswith("Traceback (most recent call last):\n"):
            return None
        lines = []
        for match in re.finditer(r"  File \"(.*?)\", line (\d+), in (<?[a-zA-Z_][a-zA-Z_0-9]*>?)(?:\n    (.*?))?\n", s):
            lines.append(Line(match.group(1), int(match.group(2)), *match.group(3, 4)))
        if not lines or not (match := re.match("([a-zA-Z_][a-zA-Z_0-9]*?(?:\.[a-zA-Z_][a-zA-Z_0-9]*?)*): (.*)", s[match.end():])):
            return None
        exc = match.group(1, 2)
        return cls(lines, exc)

def parse_possible_traceback(s):
    ss = re.split(r"\n\n(?:During handling of the above exception, another exception occurred|The above exception was the direct cause of the following exception):\n\n", s)
    tbs = []
    for c in ss:
        if (i := c.find("Traceback (most recent call last):")) != -1:
            tb = Traceback.from_string(c[i:])
            if tb is not None:
                tbs.append(tb)
    return tbs

def verify_traceback(tb):
    for line in tb.lines:
        if (i := line.file.replace("\\", "/").find("/discord/")) != -1:
            p = line.file[i+1:].rsplit(".", 1)[0].replace("\\", ".").replace("/", ".")
            lines, _ = inspect.getsourcelines(importlib.import_module(p))
            if lines[line.num-1].strip() != line.source:
                return False
    return True

def full_verify(s):
    tbs = parse_possible_traceback(s)
    return all(map(verify_traceback, tbs))


bot = discord.Client()

@bot.event
async def on_message(message):
    if bot.user in message.mentions:
        if not full_verify(message.content):
            await message.channel.send("Message failed checks. Your discord.py version is likely out of date.")
        elif "help" in message.content:
            await message.channel.send("This bot was made by LyricLy#5695. Use it by pinging the bot and sending a traceback in the same message to check it. For proof of concept purposes only.")

with open("token.txt") as t:
    token = t.read()

bot.run(token.strip())
