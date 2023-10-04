import csv
from datetime import datetime
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

HISTORY_FILE = "lp_history.csv"
UP_ARROW = ":arrow_upper_right:"
RIGHT_ARROW = ":arrow_right:"
DOWN_ARROW = ":arrow_lower_right:"


def get_league(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json().get("entries")


def log_to_csv(cutoff_challenger, cutoff_grandmaster, region):
    fieldnames = ["timestamp", "rank", "cutoff", "region"]

    # Create file if it doesn't exist and write header
    if not os.path.isfile(HISTORY_FILE):
        with open(HISTORY_FILE, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

    # Append new data
    with open(HISTORY_FILE, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "rank": "challenger",
                "cutoff": cutoff_challenger,
                "region": region,
            }
        )
        writer.writerow(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "rank": "grandmaster",
                "cutoff": cutoff_grandmaster,
                "region": region,
            }
        )


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

challenger_cutoff = new_challenger_players[-1].get("leaguePoints") + 1
grandmaster_cutoff = new_gm_players[-1].get("leaguePoints") + 1


def main():
    webhook = {
        "username": "Blitzcrank Bot",
        "avatar_url": "https://prod.api.assets.riotgames.com/public/v1/asset/lol/13.18.1/CHAMPION/53/ICON",
        "embeds": [
            {
                "title": "Ranked cutoffs for NA",
                "fields": [
                    {
                        "name": "Current Challenger Cutoff",
                        "value": f"{challenger_cutoff} LP",
                        "inline": False,
                    },
                    # {
                    #     'name': "3 Hour History",
                    #     'value': f"700 LP {UP_ARROW} 720 LP",
                    #     'inline': True,
                    # },
                    # {
                    #     'name': "1 Day History",
                    #     'value': f"715 LP {RIGHT_ARROW} 720 LP",
                    #     'inline': True,
                    # },
                    # {
                    #     'name': "7 Day History",
                    #     'value': f"760 LP {DOWN_ARROW} 720 LP",
                    #     'inline': True,
                    # },
                    {
                        "name": "Current Grandmaster Cutoff",
                        "value": f"{grandmaster_cutoff} LP",
                        "inline": False,
                    },
                    # {
                    #     'name': "3 Hour History",
                    #     'value': f"700 LP {UP_ARROW} 720 LP",
                    #     'inline': True,
                    # },
                    # {
                    #     'name': "1 Day History",
                    #     'value': f"715 LP {RIGHT_ARROW} 720 LP",
                    #     'inline': True,
                    # },
                    # {
                    #     'name': "7 Day History",
                    #     'value': f"760 LP {DOWN_ARROW} 720 LP",
                    #     'inline': True,
                    # },
                ],
                "footer": {
                    "text": f"Updated {datetime.now().strftime('%b %d %Y • %H:%M')}",
                    "icon_url": "https://i.imgur.com/0XC49UU.png",
                },
            },
        ],
    }
    log_to_csv(challenger_cutoff, grandmaster_cutoff, "na1")
    webhook = requests.post(DISCORD_WEBHOOK, json=webhook)
    print(webhook)


if __name__ == "__main__":
    main()
