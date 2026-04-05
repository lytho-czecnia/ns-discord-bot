import discord
import json
import commands as cmds
from commands import commands, command_prefixes
from inspect import signature as sig
parameters = lambda function: list(sig(function).parameters)
parameter_count = lambda function: len(sig(function).parameters)

with open("tokens.json") as json_file:
    tokens: dict[str,dict[str,dict[str,str]]] = json.load(json_file)

discord_bot_token = tokens['Discord']['Bot']['Token']

del tokens

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(command_prefix="!", intents=intents) #type: ignore


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message: discord.message.Message):
    if message.author == client.user:
        return
    for command, prefix in zip(commands, command_prefixes):
        if message.content.startswith(prefix):
            needed_parameters = parameters(command)
            parameters_in: dict = dict()
            for parameter in needed_parameters:
                match parameter:
                    case "author":
                        value = message.author
                    case "channel":
                        value = message.channel
                    case "contents":
                        value = message.content.removeprefix(prefix)
                    case "message":
                        value = message
                    case _:
                        value = ''
                if value != '':
                    parameters_in[parameter] = value
            await command(**parameters_in)

client.run(discord_bot_token)
