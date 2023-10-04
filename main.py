import sqlite3
from datetime import datetime, timedelta
import os
import requests
from dotenv import load_dotenv

# Load enviroment variables from .env file
load_dotenv()

API_KEY = os.environ["API_KEY"]
DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

# https://support-leagueoflegends.riotgames.com/hc/en-us/articles/4405776545427-Master-Grandmaster-and-Challenger-The-Apex-Tiers
# TODO Add region selection and change this automatically
NUM_CHALL_PLAYERS = 300
NUM_GM_PLAYERS = 700

# Discord emojis equivalent (but better looking) to ↗→↘ respectively
UP_ARROW = ":arrow_upper_right:"
RIGHT_ARROW = ":arrow_right:"
DOWN_ARROW = ":arrow_lower_right:"

# SQLite Database File
HISTORIC_FILE = "test_history.db"


def setup_db(database_file):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS league_lp_trends (
        id INTEGER PRIMARY KEY,
        time timestamp NOT NULL,
        rank TEXT NOT NULL,
        cutoff_rank INTEGER NOT NULL,
        region TEXT NOT NULL
    )
    """
    )

    conn.commit()
    conn.close()


setup_db(HISTORIC_FILE)


def get_league(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json().get("entries")


def insert_data(rank: str, cutoff_rank: int, region="NA"):
    timestamp = datetime.now()

    conn = sqlite3.connect(HISTORIC_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
    INSERT INTO league_lp_trends (time, rank, cutoff_rank, region)
    VALUES (?, ?, ?, ?)
    """,
        (timestamp, rank, cutoff_rank, region),
    )

    conn.commit()
    conn.close()


def get_historical_data(rank: str, hours: int, hours_back: int, region="NA"):
    # We are looking to fetch rank data between the range of hours ± hours_back to
    # try and get an accurate average in the timeframe.
    earliest_time = datetime.now() - timedelta(hours=hours + hours_back)
    latest_time = datetime.now() - timedelta(hours=hours - hours_back)

    conn = sqlite3.connect(HISTORIC_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT time, cutoff_rank FROM league_lp_trends 
    WHERE rank = ? AND region = ? AND time >= ? AND time <= ?
    ORDER BY time ASC
    """,
        (rank, region, earliest_time, latest_time),
    )

    data_points = cursor.fetchall()
    conn.close()

    # If data is unavailable or we are missing more than 75% of the data points. Since
    # data should be ingested every hour, we can assume there should be hours_back * 2 points
    # If the script runs late, we could in theory miss up to 75% of the data hence we check less than
    if not data_points or len(data_points) < hours_back / 2:
        # We return None to indicate lack of data.
        return None

    cutoff_ranks = [point[1] for point in data_points]

    # Calculate the average cutoff from the collected data
    avg_cutoff = sum(cutoff_ranks) / len(cutoff_ranks)

    return avg_cutoff


def generate_embed(rank, current_cutoff, region="NA"):
    intervals = [
        # Hour we collect around, ± hours, embed text
        (3, 1, "3 Hour History"),
        (24, 3, "1 Day History"),
        (168, 24, "7 Day History"),
    ]

    embeds = []

    for hours, hours_back, name in intervals:
        oldest = get_historical_data(rank, hours, hours_back, region)

        if oldest is None:
            value = "UNAVAILABLE"
        else:
            if abs(current_cutoff - oldest) <= 15:
                value = f"{round(oldest)} LP {RIGHT_ARROW} {current_cutoff} LP"
            elif current_cutoff > oldest:
                value = f"{round(oldest)} LP {UP_ARROW} {current_cutoff} LP"
            else:
                value = f"{round(oldest)} LP {DOWN_ARROW} {current_cutoff} LP"

        embeds.append({"name": name, "value": value, "inline": True})

    return embeds


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

new_challenger_players = apex_players[0:NUM_CHALL_PLAYERS]
new_gm_players = apex_players[NUM_CHALL_PLAYERS : NUM_GM_PLAYERS + NUM_CHALL_PLAYERS]

challenger_cutoff = new_challenger_players[-1].get("leaguePoints") + 1
grandmaster_cutoff = new_gm_players[-1].get("leaguePoints") + 1


def main():
    insert_data("challenger", challenger_cutoff)
    insert_data("grandmaster", grandmaster_cutoff)

    challenger_embeds = generate_embed("challenger", challenger_cutoff)
    grandmaster_embeds = generate_embed("grandmaster", grandmaster_cutoff)
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
                    }
                ]
                + challenger_embeds
                + [
                    {
                        "name": "Current Grandmaster Cutoff",
                        "value": f"{grandmaster_cutoff} LP",
                        "inline": False,
                    }
                ]
                + grandmaster_embeds,
                "footer": {
                    "text": f"Updated {datetime.now().strftime('%b %d %Y • %H:%M')}",
                    "icon_url": "https://i.imgur.com/0XC49UU.png",
                },
            },
        ],
    }

    webhook = requests.post(DISCORD_WEBHOOK, json=webhook)


if __name__ == "__main__":
    main()
