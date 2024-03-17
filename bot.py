from discord.ext import commands, tasks
from dataclasses import dataclass
import discord
import random
import datetime
import token_wrapper

BOT_TOKEN = token_wrapper.token

@dataclass
class Session:
    is_active: bool = False
    start_time: int = 0

bot = commands.Bot(command_prefix="!", intents = discord.Intents.all())
session = Session()

SESSION_TIME_REMINDERS = 30

@bot.event
async def on_ready():
    print("Hello! DMAI is ready!")
    #channel = bot.get_channel(CHANNEL_ID)
    #await channel.send("Hello! DMAI is ready!")

# keeps track of the amount of minutes that pass while a session is going on
@tasks.loop(minutes=SESSION_TIME_REMINDERS, count=2)
async def break_reminder(ctx):

    #ignore the first execution of this command
    if break_reminder.current_loop == 0:
        return

    await ctx.send(f"The session has been going on for **{SESSION_TIME_REMINDERS}** minutes for a total of **{SESSION_TIME_REMINDERS * break_reminder.current_loop}** minutes.")


# starting a session to keep track of time
@bot.command()
async def startsession(ctx):
    if session.is_active:
        await ctx.send("A session is already active.")
        return
    
    session.is_active = True
    session.start_time = ctx.message.created_at.astimezone(datetime.timezone(datetime.timedelta(hours=-4)))
    #human_readable_time = ctx.message.created_at.strftime("%I:%M:%S %p")
    break_reminder.start(ctx)
    await ctx.send(f"Session started on {session.start_time.strftime("%B %d at %I:%M:%S %p")}")

# ends a session when called
@bot.command()
async def endsession(ctx):
    if not session.is_active:
        await ctx.send("No session is active!")
        return
    
    session.is_active = False
    end_time = ctx.message.created_at.astimezone(datetime.timezone(datetime.timedelta(hours=-4)))
    duration = end_time - session.start_time

    duration_seconds = duration.total_seconds()
    hours, remainder = divmod(duration_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    human_readable_duration = "{:02} hours, {:02} minutes, and {:02} seconds.".format(int(hours), int(minutes), int(seconds))

    await ctx.send(f"Session ended on {end_time.strftime("%B %d at %I:%M:%S %p")} after {human_readable_duration}")

@bot.command()
async def d20(ctx, *modifiers):
    roller_name = ctx.message.author.display_name
    roll_result = random.randint(1, 20)
    roll_with_mods = dice_roll_mod_math(roll_result, *modifiers)
    
    if roll_result == 20:
        await ctx.send(f":confetti_ball: **{roller_name} rolled a natural 20!** :confetti_ball: With modifiers it becomes a **{roll_with_mods}**")
    elif roll_result == 1:
        await ctx.send(f":skull: **{roller_name} rolled a natural 1...** :skull: With modifiers it becomes a **{roll_with_mods}**")
    else:
        await printrollresults(ctx, roller_name, roll_result, *modifiers)

@bot.command()
async def d12(ctx, *modifiers):
    roller_name = ctx.message.author.display_name
    roll_result = random.randint(1, 12)
    await printrollresults(ctx, roller_name, roll_result, *modifiers)

@bot.command()
async def d10(ctx, *modifiers):
    roller_name = ctx.message.author.display_name
    roll_result = random.randint(1, 10)
    await printrollresults(ctx, roller_name, roll_result, *modifiers)

@bot.command()
async def d8(ctx, *modifiers):
    roller_name = ctx.message.author.display_name
    roll_result = random.randint(1, 8)
    await printrollresults(ctx, roller_name, roll_result, *modifiers)

@bot.command()
async def d6(ctx, *modifiers):
    roller_name = ctx.message.author.display_name
    roll_result = random.randint(1, 6)
    await printrollresults(ctx, roller_name, roll_result, *modifiers)

@bot.command()
async def d4(ctx, *modifiers):
    roller_name = ctx.message.author.display_name
    roll_result = random.randint(1, 4)
    await printrollresults(ctx, roller_name, roll_result, *modifiers)

# rolls multiple dice in NdN format
@bot.command()
async def roll(ctx, dice : str):
    roller_name = ctx.message.author.display_name
    result = rollNdN(dice)
    await ctx.send(f"**{roller_name}** rolled {result}")

@bot.command()
async def showcommands(ctx):
    display_commands = "To use a command, input a '!' before any of the below commands: \n"
    display_commands += "d20 - Roll a d20 \n"
    display_commands += "d12 - Roll a d12 \n"
    display_commands += "d10 - Roll a d10 \n"
    display_commands += "d8 - Roll a d8 \n"
    display_commands += "d6 - Roll a d6 \n"
    display_commands += "d4 - Roll a d4 \n"
    display_commands += "All above dice commands can accept an unlimited number of modifiers to add to the roll \n"
    display_commands += "Example: inputting '!d20 3 8' will roll a d20 and add 3 + 8 to the result \n \n"
    display_commands += "roll [number]d[number] - Rolls multiple dice in NdN format (Ex. !roll 2d20 will roll 2 d20 dice) \n \n"
    display_commands += "startsession - Starts a session to keep track of session time \n"
    display_commands += "endsession - Ends a session and displays the amount of time that the session lasted \n \n"
    display_commands += "showcommands - Shows all of this bot's commands \n"
    await ctx.send(display_commands)

# calculates the total value of a dice roll with modifiers
def dice_roll_mod_math(natural_result, *modifiers):
    if modifiers != None:
        roll_with_mods = natural_result

        for i in modifiers:
            if i.isdigit():
                roll_with_mods += int(i)
            
        return roll_with_mods
    else:
        return -1
    
def rollNdN(dice : str):
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        print('Format has to be in NdN!')
        return

    return ', '.join(str(random.randint(1, limit)) for r in range(rolls))

async def printrollresults(ctx, roller_name, roll_result, *modifiers):
    roll_with_mods = dice_roll_mod_math(roll_result, *modifiers)
    message_str = f"**{roller_name}** rolled a natural **{roll_result}**."
    mod_roll_str = f" With modifiers the total is **{roll_with_mods}**."
    if len(modifiers) != 0: message_str += mod_roll_str
    
    await ctx.send(message_str)

bot.run(BOT_TOKEN)