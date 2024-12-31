# -*- coding: utf-8 -*-
"""
Created on Sat Dec 28 11:46:02 2024

@author: Thomas Guan
"""
import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import datetime
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

reacted_users = {}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord')

games = ["overwatch", "valorant", "rivals", "marvel", "marvel rivals"]

async def send_reminder(message):
    global reacted_users
    reacted_users = reacted_users.get(message.id)
    if reacted_users and 'users' in reacted_users:
        for user_id in reacted_users['users']:
            user = await bot.fetch_user(user_id)
            try:
                if user:
                    await user.send("Time to play!")
                    print(f"Reminder sent to {user.id}")
            except discord.Forbidden:
                print(f"Cannot send DM to {user.id}, womp womp")
    else:
        print("No users to send reminders to.")

# Command to start the reminder process
@bot.command(name="Play", description="Reminder for gaming")
async def play(ctx, game: str, time: str):
    global reacted_users
    if game.lower() not in games:
        await ctx.send("Unknown Game. Please use !add command to add game (This is not implemented lol)")
        return

    try:
        reminder_time = datetime.datetime.strptime(time, '%H:%M')
    except ValueError:
        await ctx.send("Please use the correct format: '!play game HH:MM'.")
        return

    now = datetime.datetime.now()
    print(now)

    if reminder_time <= now:
        await ctx.send("The time is in the past... ONWARDS AYOSHIMA!")
        reminder_time = reminder_time.replace(day=now.day, month=now.month, year=now.year)
    
    scheduler = AsyncIOScheduler()
    message = await ctx.send(f"Please react to play {game} at {time} Sail Standard Time(SST)! 👍")
    await message.add_reaction("👍")
    reacted_users[message.id] = {'game': game, 'time': time, 'users': []}
    await reaction_collection(message)
    scheduler.add_job(send_reminder, 'date', run_date=reminder_time, args=[message])
    await ctx.send(f"Reminder set for {reminder_time}")
    scheduler.start()

@bot.command()
async def reaction_collection(message):
    global reacted_users

    def check(reaction, user):
        return str(reaction.emoji) == "👍" and not user.bot

    if message.id not in reacted_users:
        reacted_users[message.id] = {'users': []}

    print('Collecting reactions...')
    
    while len(reacted_users[message.id]['users']) < 5:
        try:
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=5.0)
            if user.id not in reacted_users[message.id]['users']:
                reacted_users[message.id]['users'].append(user.id)
                print(f"Added {user.id} to the list")
        except asyncio.TimeoutError:
            break


bot.run(TOKEN)
