import asyncio
import discord
import requests
import os

from dotenv import load_dotenv
from pprint import pprint


load_dotenv()


class DiscordClient(discord.Client):

    IGNORED_USERS = ['Animingle']
    ACCEPTABLE_BANGS = ['!an', '!am', '!animingle']
    ACCEPTABLE_COMMANDS = ['recent', 'help']

    HEADERS = {
        'X-MAL-CLIENT-ID': os.getenv('CLIENT_ID')
    }

    async def on_ready(self):
        print(f"Logged in as user {self.user}")

    async def on_message(self, message):
        command = message.content.split(" ")

        if command[0] not in self.ACCEPTABLE_BANGS:
            return

        if message.author.name in self.IGNORED_USERS:
            return

        error, verified = self._verify_msg(command)

        #if not verified:
        #    await message.channel.send(content=error, mention_author=True)
        #    return

        response = self._process_msg(command)
        pprint(response)
        #await message.channel.send(response)

    def get_recent_anime(self, user, amount):
        req_url= f'https://api.myanimelist.net/v2/users/{user}/animelist?fields=list_status&limit={amount}&sort=anime_start_date'
        resp = requests.get(req_url, headers=self.HEADERS)
        return resp.json()

    def get_all_anime(self, user):
        req_url = f'https://api.myanimelist.net/v2/users/{user}/animelist?fields=list_status&limit=1000&sort=anime_title'
        resp = requests.get(req_url, headers=self.HEADERS)

        res = [ anime['node']['title'] for anime in resp.json()['data'] ]
        return res

    def _verify_msg(self, command):

        if command[1] not in self.ACCEPTABLE_COMMANDS:
            error = "Command doesn't exist. Use <help> to get a list of supported commands. Example !animingle <help>."
            return error, False

        return None, True

    def _process_msg(self, command):
        
        if command[1] == 'recent':
            user = command[2]
            amount = command[3]
            return self.get_recent_anime(user, amount)
        elif command[1] == 'all':
            user = command[2]
            return self.get_all_anime(user)




def main():
    intents = discord.Intents.all()

    dc = DiscordClient(intents=intents)
    dc.run(os.getenv('TOKEN'))


if __name__ == '__main__':
    main()
