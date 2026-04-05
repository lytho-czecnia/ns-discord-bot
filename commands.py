import discord
import nationstates as ns
import json
import tkinter as tk
import asyncio
import threading

api = ns.Nationstates("Discord-NationStates bot",enable_beta=True)

class Messages:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.messages: list[discord.message.Message] = []
        self.authors:list[discord.Member] = []
        self.message_label = tk.Label(self.master, text="")
        self.message_label.grid(row=0,column=0,columnspan=3)
    
    def add_message(self, message: discord.message.Message, author:discord.Member):
        self.messages.append(message)
        self.authors.append(author)
        self.refresh()
    
    def remove_message(self, ind=0):
        self.messages.pop(ind)
        self.authors.pop(ind)
        self.refresh()
    
    def refresh(self):
        if len(self.messages)==0:
            self.master.title("No more messages!")
            self.message_label.config(text="")
            global disable
            disable()
        else:
            self.master.title(f"NEW MESSAGE! {len(self.messages)} messages to verify!")
            self.message_label.config(text=f'{self.authors[0].display_name} has asked to send the message: {self.messages[0].content.removeprefix("!post")}')
            global enable
            enable()
        self.master.after(100,self.refresh)


def enable():
    global accept, deny
    accept.enable()
    deny.enable()

def disable():
    global accept, deny
    accept.disable()
    deny.disable()


class judgeButton:
    def __init__(self, master, text, command,bcol,c, loop,r=1,fcol="black"):
        self.master = master
        self.loop = loop
        self.command = command
        self.button = tk.Button(self.master, text=text,command=lambda :self.run_command(),foreground=fcol,background=bcol,width=20)
        self.button.grid(row=r,column=c)

    def run_command(self):
        global message_box
        asyncio.run_coroutine_threadsafe(self.command(message_box.messages[0]),self.loop)
        message_box.remove_message()
    
    def enable(self):
        self.button.config(state="normal")
    
    def disable(self):
        self.button.config(state="disabled")

def start_gui(loop, msg, auth):
    global verify_window, message_box, accept, deny
    try:
        message_box.add_message(msg,auth) # type:ignore
    except:
        verify_window = tk.Tk()
        message_box = Messages(verify_window)
        empty_label = tk.Label(verify_window,width=20)
        empty_label.grid(row=1,column=1)
        accept = judgeButton(verify_window, "Accept", accepted_message, "lime", 0, loop)
        deny = judgeButton(verify_window, "Deny", denied_message, "red", 2, loop)
        message_box.add_message(msg,auth)
        verify_window.mainloop()

with open("tokens.json") as json_file:
    tokens: dict[str,dict[str,dict[str,str]]] = json.load(json_file)

ns_password = tokens['NationStates']['Bot']['password']
ns_username = tokens['NationStates']['Bot']['username']
bot = api.nation(ns_username,ns_password)

del tokens

with open("valid_users.json") as json_file:
    users: dict[str,list[int]] = json.load(json_file)

valid_roles = users['roles']
authenticated_users = users['users']

send_message = lambda message, channel: channel.send(message)
async def send_hi (author, channel ):
    '''Sends the word "hi", followed by the message'''
    await send_message(f"Hello {author}!", channel)

async def help(message: discord.message.Message):
    '''Provides documentation and example usage of all functions'''
    out = ''
    if message.content == "!help":
        out = '# Full list of commands:\n - '+'\n - '.join(command_prefixes) + '\n\nUse `!help (command)` to find out more about a specific command!'
    elif (message.content.removeprefix("!help ") in command_prefixes):
        out += f" # HELP: {message.content.removeprefix("!help !")}\n"
        out += commands[command_prefixes.index(message.content.removeprefix("!help "))].__doc__
    elif ("!"+message.content.removeprefix("!help ") in command_prefixes):
        out += f" # HELP: {message.content.removeprefix("!help ")}\n"
        out += commands[command_prefixes.index("!" + message.content.removeprefix("!help "))].__doc__
    if out != '':
        await send_message(out,message.channel)

async def mirror (contents, channel): 
    '''Sends the contents of the message which was sent in'''
    await send_message(contents,channel)

async def post_to_rmb(message: discord.message.Message, author:discord.Member):
    '''Attempts to post using the bot account linked to this discord bot.'''
    is_message_allowed = any(author.get_role(valid_role) != None and valid_role == author.get_role(valid_role).id for valid_role in valid_roles) #type: ignore
    if author.id in authenticated_users:
        bot.send_rmb("nisatian_testing_range",message.content.removeprefix("!post").replace("’","'"))
        await message.reply("Message sent without approval (user was in list of authenticated users)!")
    elif is_message_allowed:
        loop = asyncio.get_running_loop()
        await message.reply("Message has been sent for approval.")
        threading.Thread(target=start_gui, args=(loop,message,author), daemon=True).start()
    else:
        await message.reply(f"Nice try, {author}, but only real_darkxgaming can send messages through me!!")


async def accepted_message(message: discord.message.Message):
    await message.reply("Message has been approved. Sending!")
    bot.send_rmb("nisatian_testing_range",message.content.removeprefix("!post").replace("’","'"))

async def denied_message(message: discord.message.Message):
    await message.reply("Message has been denied. Sorry!")



commands = [help,send_hi, mirror,post_to_rmb]
command_prefixes = ["!help","!hi","!mirror","!post"]