import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_league(url):
    response = requests.get(url)
    if response.ok:
        return response.json().get('entries')

API_KEY = os.environ['API_KEY']
WEBHOOK = os.environ['DISCORD_WEBHOOK']
challengers = "https://na1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key=" + API_KEY
grandmasters = "https://na1.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key=" + API_KEY
masters = "https://na1.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?api_key=" + API_KEY

chall = get_league(challengers)
gm = get_league(grandmasters)
masters = get_league(masters)

apex_players = chall + gm + masters
apex_players.sort(key=lambda x: x['leaguePoints'], reverse=True)
new_challenger_players = apex_players[0:300]
new_gm_players = apex_players[300:1000]

def main():
    content = f'''Cutoff for Challenger in NA is currently >= {new_challenger_players[-1].get('leaguePoints') + 1} LP
Cutoff for Grandmaster in NA is currently >= {new_gm_players[-1].get('leaguePoints') + 1} LP'''
    requests.post(WEBHOOK, {'content': content})

if __name__ == "__main__":
    main()