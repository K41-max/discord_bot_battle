import discord
import os
import asyncio
import requests
import base64
import time
import sys
from bs4 import BeautifulSoup

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
    channel = client.get_channel(1236954659554459648)

    async def get_data(username, password):
        headers = {'Authorization': 'Basic ' + base64.b64encode(f"{username}:{password}".encode()).decode()}
        response = requests.get('https://yukibbs-server.onrender.com/battle/admin', headers=headers)
        return response.content

    async def main():
        username = 'admin'
        password = 'gafa074256Pass'
        last_number = None

        while True:
            html_content = await get_data(username, password)

            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find('table')

            if table:
                rows = table.find_all('tr')
                if len(rows) > 1:
                    second_row = rows[1]
                    first_cell_second_row = second_row.find('td')
                    current_number = first_cell_second_row.text.strip()

                    if last_number is not None and current_number != last_number:
                        last_cell_second_row = second_row.find_all('td')[-1]
                        last_cell_content = last_cell_second_row.get_text(separator="\n").strip()

                        await channel.send(f"\n\n```{last_cell_content}```\n")

                    last_number = current_number

            else:
                print("No table found in the response.")

            await asyncio.sleep(2)

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

