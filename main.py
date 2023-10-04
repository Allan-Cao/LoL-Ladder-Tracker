import os
import requests
from dotenv import load_dotenv

# Load enviroment variables from .env file
load_dotenv()

API_KEY = os.environ["API_KEY"]
DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

# https://support-leagueoflegends.riotgames.com/hc/en-us/articles/4405776545427-Master-Grandmaster-and-Challenger-The-Apex-Tiers
NUM_CHALL_PLAYERS = 300
NUM_GM_PLAYERS = 700


def get_league(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json().get("entries")


challengerleagues = (
    "https://na1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key="
    + API_KEY
)
grandmasterleagues = (
    "https://na1.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key="
    + API_KEY
)
masterleagues = (
    "https://na1.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?api_key="
    + API_KEY
)

challenger_players = get_league(challengerleagues)
grandmaster_players = get_league(grandmasterleagues)
master_players = get_league(masterleagues)

apex_players = challenger_players + grandmaster_players + master_players
apex_players.sort(key=lambda x: x["leaguePoints"], reverse=True)

# After bracket update, the top 300 players in NA
new_challenger_players = apex_players[0:NUM_CHALL_PLAYERS]
new_gm_players = apex_players[NUM_CHALL_PLAYERS : NUM_GM_PLAYERS + NUM_CHALL_PLAYERS]


def main():
    content = f"""Cutoff for Challenger in NA is currently >= {new_challenger_players[-1].get('leaguePoints') + 1} LP
Cutoff for Grandmaster in NA is currently >= {new_gm_players[-1].get('leaguePoints') + 1} LP"""
    print(content)
    # requests.post(DISCORD_WEBHOOK, {'content': content})


if __name__ == "__main__":
    main()
