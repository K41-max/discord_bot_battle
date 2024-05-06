import discord
import os
import asyncio
import requests
import base64
import json
import time
import sys

client = discord.Client(intents=discord.Intents.default())

discord_token = os.environ['DISCORD_TOKEN']

LOCK_FILE_PATH = "/tmp/discord_bot.lock"

def acquire_lock():
    try:
        if os.path.exists(LOCK_FILE_PATH):
            print("Another instance is already running. Exiting.")
            sys.exit(0)
        
        with open(LOCK_FILE_PATH, "w") as lockfile:
            lockfile.write(str(os.getpid()))
    except Exception as e:
        print("Error acquiring lock:", e)
        sys.exit(1)

def release_lock():
    try:
        os.remove(LOCK_FILE_PATH)
    except Exception as e:
        print("Error releasing lock:", e)

acquire_lock()

async def send_message():
    channel = client.get_channel(1217993869275168811)

    async def get_data(username, password):
        headers = {'Authorization': 'Basic ' + base64.b64encode(f"{username}:{password}".encode()).decode()}
        response = requests.get('https://yukibbs-server.onrender.com/bbs/admin', headers=headers)
        return response.json()

    async def main():
        username = 'admin'
        password = 'gafa074256Pass'
        last_number = None

        while True:
            data = await get_data(username, password)

            if 'main' in data:
                main_section = data['battle']
                if main_section and len(main_section) > 0:
                    current_number = int(main_section[0]['number'])

                    if last_number is not None and current_number == last_number:
                        await asyncio.sleep(2)
                        continue

                    info = main_section[0].get('info', 'null')
                    await channel.send(f"\n\nnumber:{current_number}\nname:{main_section[0]['name']}\nmessage:{main_section[0]['message']}\ninfo:{info}\n")

                    last_number = current_number

            else:
                print("No 'main' section found in the response.")

            await asyncio.sleep(2.1)

    try:
        await main()
    except Exception as e:
        print("An error occurred:", e)
        release_lock()
        os.execv(sys.executable, ['python'] + sys.argv)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    await send_message()

    release_lock()

client.run(discord_token)
