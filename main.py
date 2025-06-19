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
    ACCEPTABLE_COMMANDS = ['recent', 'help', 'all', 'summary']

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

        if not verified:
            await message.channel.send(content=error, mention_author=True)
            return

        response = self._process_msg(command)
        #pprint(response)
        await message.channel.send(response)

    def get_recent_anime(self, user, amount):
        output_string = f"Top {amount} recent anime:\n"
        req_url= f'https://api.myanimelist.net/v2/users/{user}/animelist?fields=list_status&limit={amount}&sort=anime_start_date'
        resp = requests.get(req_url, headers=self.HEADERS)
        resp = resp.json().get('data')

        for anime in resp:
            output_string += anime['node']['title'] + '\n'

        return output_string

    def get_all_anime(self, user):
        req_url = f'https://api.myanimelist.net/v2/users/{user}/animelist?fields=list_status&limit=1000&sort=anime_title'
        resp = requests.get(req_url, headers=self.HEADERS)

        res = [ anime['node']['title'] for anime in resp.json()['data'] ]
        return res

    def get_user_summary(self, user):
        """ Returns a summary of user infor

            Username:

            Total Anime Watched:
            Completed:
            Ongoing:
            Dropped:
            Upcomming:
        """
        req_url = f'https://api.myanimelist.net/v2/users/{user}/animelist?fields=list_status&limit=1000&sort=anime_title'
        resp = requests.get(req_url, headers=self.HEADERS)
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

        summary = {
            'total_anime_watched': len(resp_data),
            'completed': completed,
            'ongoing': watching,
            'dropped': dropped,
            'upcomming': upcomming,
            'other': other
        }

        summary_result = f"Anime Watched: {summary['total_anime_watched']} \nCompleted: {completed} \nOngoing: {watching} \nDropped: {dropped} \nUpcomming: {upcomming} \nOther: {other}"

        return summary_result

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
        elif command[1] == 'summary':
            user = command[2]
            return self.get_user_summary(user)


def main():
    intents = discord.Intents.all()

    dc = DiscordClient(intents=intents)
    dc.run(os.getenv('TOKEN'))


if __name__ == '__main__':
    main()
