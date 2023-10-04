import sqlite3
from main import setup_db
from datetime import datetime, timedelta
import random

DATABASE_FILE = "test_history.db"
# Connect to the database
conn = sqlite3.connect(DATABASE_FILE)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS league_lp_trends")

conn.commit()

setup_db(DATABASE_FILE)

# Number of simulated data points
NUM_DATA_POINTS = 96  # 4 days worth of data

# Simulated data generation for challenger rank
# Using random numbers to simulate LP fluctuations.
initial_challenger_lp = 700
challenger_lps = [
    initial_challenger_lp + random.randint(-10, 5) for _ in range(NUM_DATA_POINTS)
]

# Date 4 days back from now
start_time = datetime.now() - timedelta(days=4)

# Insert data into the database
for i in range(NUM_DATA_POINTS):
    timestamp = start_time + timedelta(minutes=60 * i)
    rank = "challenger"
    cutoff_rank = challenger_lps[i]
    region = "NA"
    cursor.execute(
        """
    INSERT INTO league_lp_trends (time, rank, cutoff_rank, region)
    VALUES (?, ?, ?, ?)
    """,
        (timestamp, rank, cutoff_rank, region),
    )

# Full 8 days data for grandmaster
NUM_DATA_POINTS_8DAYS = 168 + 24  # 8 days worth of data, every hour
initial_gm_lp = 500
gm_lps = [initial_gm_lp + random.randint(-10, 10) for _ in range(NUM_DATA_POINTS_8DAYS)]
start_time_8days = datetime.now() - timedelta(days=8)

for i in range(NUM_DATA_POINTS_8DAYS):
    timestamp = start_time_8days + timedelta(hours=1 * i)
    rank = "grandmaster"
    cutoff_rank = gm_lps[i]
    region = "NA"
    cursor.execute(
        """
    INSERT INTO league_lp_trends (time, rank, cutoff_rank, region)
    VALUES (?, ?, ?, ?)
    """,
        (timestamp, rank, cutoff_rank, region),
    )

# Commit and close
conn.commit()
conn.close()

print("Test data populated!")
