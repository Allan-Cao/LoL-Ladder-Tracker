# LoL-Ladder-Tracker

---

## Introduction
This project is a Python script that tracks the LP (League Points) cutoffs for Challenger and Grandmaster ranks in League of Legends. It fetches data from Riot Games' API, stores it in an SQLite database, and posts updates to a Discord channel via webhooks. The code is designed with modularity and efficiency in mind, utilizing SQLite for lightweight, serverless, and self-contained SQL database management.

---

## Setup and Installation

1. Clone the repository.
    ```bash
    git clone https://github.com/Allan-Cao/LoL-Ladder-Tracker.git
    ```
2. Navigate to the project directory.
    ```bash
    cd LoL-Ladder-Tracker
    ```
3. Create a virtual environment.
    ```bash
    py -m venv venv
    ```
4. Activate the virtual environment.
    - On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    - On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
5. Install the required packages.
    ```bash
    pip install -r requirements.txt
    ```
6. Rename `env.example` to `.env` and fill in your Riot API key and [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).
    ```env
    API_KEY=Your-API-Key
    DISCORD_WEBHOOK=Your-Webhook-URL
    ```

---

## Usage
Run the script.
```bash
python main.py
```
This will populate the SQLite database and post the current LP cutoffs to the specified Discord channel.

For automated hourly updates, consider using `crontab` on a Unix-based system.
```bash
crontab -e
```
Add the following line to schedule the script to run every hour.
```bash
0 * * * * /path/to/python /path/to/LoL-Ladder-Tracker/main.py
```
Please note that you will also have to modify the `HISTORIC_FILE` variable to be an absolute path for crontab to run correctly.

---

## License

This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License. See the LICENSE file for more information.