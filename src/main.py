import asyncio
import discord
import requests
import os

import sqlite3

from dotenv import load_dotenv

from constants import ACCEPTABLE_BANGS, ACCEPTABLE_COMMANDS, HEADERS, IGNORED_USERS


load_dotenv()


class DiscordClient(discord.Client):

    async def on_ready(self):
        print(f"Logged in as user {self.user}")

    async def on_message(self, message):
        command = message.content.split(" ")

        if command[0] not in ACCEPTABLE_BANGS:
            return

        if message.author.name in IGNORED_USERS:
            return

        error, verified = verify_msg(command)

        if not verified:
            await message.channel.send(content=error, mention_author=True)
            return

        response = process_msg(command)
        await message.channel.send(response)


def get_recent_anime(user, amount):
    output_string = f"Top {amount} recent anime:\n"
    req_url= f'https://api.myanimelist.net/v2/users/{user}/animelist?fields=list_status&limit={amount}&sort=anime_start_date'
    resp = requests.get(req_url, headers=HEADERS)
    resp = resp.json().get('data')

    for anime in resp:
        output_string += anime['node']['title'] + '\n'

    return output_string


def get_all_anime(user):
    req_url = f'https://api.myanimelist.net/v2/users/{user}/animelist?fields=list_status&limit=1000&sort=anime_title'
    resp = requests.get(req_url, headers=HEADERS)

    res = [ anime['node']['title'] for anime in resp.json()['data'] ]
    return res


def get_user_summary(user):
    """ Returns a summary of user infor

        Username:

        Total Anime Watched:
        Completed:
        Ongoing:
        Dropped:
        Upcomming:
    """
    req_url = f'https://api.myanimelist.net/v2/users/{user}/animelist?fields=list_status&limit=1000&sort=anime_title'
    resp = requests.get(req_url, headers=HEADERS)
    resp = resp.json()
    resp_data = resp.get('data')

    completed = 0
    watching = 0
    dropped = 0
    upcomming = 0
    other = 0

    for anime in resp_data:
        if anime['list_status']['status'] == 'watching':
            watching += 1
        elif anime['list_status']['status'] == 'completed':
            completed += 1
        elif anime['list_status']['status'] == 'dropped':
            dropped += 1
        elif anime['list_status']['status'] == 'plan_to_watch':
            upcomming += 1
        else:
            other += 1

    summary_result = f"Anime Watched: {len(resp_data)} \nCompleted: {completed} \nOngoing: {watching} \nDropped: {dropped} \nUpcomming: {upcomming} \nOther: {other}"

    return summary_result


def verify_msg(command):

    if command[1] not in ACCEPTABLE_COMMANDS:
        error = "Command doesn't exist. Use <help> to get a list of supported commands. Example !animingle <help>."
        return error, False

    return None, True


def process_msg(command):
    
    if command[1] == 'recent':
        user = command[2]
        amount = command[3]
        return get_recent_anime(user, amount)

    elif command[1] == 'all':
        user = command[2]
        return get_all_anime(user)

    elif command[1] == 'summary':
        user = command[2]
        return get_user_summary(user)


def setup_database():
    con = sqlite3.connect("animingle.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS Users(name)")
    cur.execute("CREATE TABLE IF NOT EXISTS Anime(name)")
    cur.execute("CREATE TABLE IF NOT EXISTS WatchStatus(user_id, anime_id, name, status, last_updated)")


def main():

    setup_database()

    intents = discord.Intents.all()

    dc = DiscordClient(intents=intents)
    dc.run(os.getenv('TOKEN'))


if __name__ == '__main__':
    main()
