# Anime Notification Discord Bot

This is an Anime Discord bot that is built using the disnake library and it's using the Anilist, MyAnimeListAPI, JikanAPI libraries. It allows you to track anime airing episodes and notified when a new episode releases, or keep track of the anime you are watching, and displays how long it will take a new episode to come out.

<img src="screenshots/discordss.png" />

### Features

- Notifies on Discord when the next episode of an anime airs
- Ability to track multiple anime
- Lists information about every anime's airing time/how long for the next episode to come out.
- Gives you the link to watch the episode right from discord.
- Easy to use

### Prerequisites

You will need to have the following:
- Linux/MacOS
- Python 3.7 or later
- [PIP](https://pip.pypa.io/en/stable/installing/) to install the required libraries

### Installation

1. Clone the repository
```
git clone https://github.com/MahdeenSky/AnimeNotificationDiscordBot
```
2. Navigate to the project directory
```
cd AnimeNotificationDiscordBot
```
3. Install the required libraries
```
pip install -r requirements.txt
```
4. Create a .env file in the folder and set the following variables, which should look like: (you can put your channel ID if you know, but it is  not required)
  - BOT_API_KEY is your discord bot token which you can get by following [this](https://www.writebots.com/discord-bot-token/) (it is the token)
  - DISCORD_CHANNEL_ID represents the channel which the bot will notify you about new episodes. (you dont have to set it manually, ignore it)
  - MAL_CLIENT_ID is to use the MAL API, which you can get from [here](https://myanimelist.net/blog.php?eid=835707). Just following Step 0.
```
BOT_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
DISCORD_CHANNEL_ID=XXXXXXXXXXXXX
MAL_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```
5. Invite the bot to your discord server (you can skip this if you follow the article to get your `BOT_API_KEY` for discord) and run the bot.
```
python3 main.py
```
6. Do the following discord slash command to set the notification channel (where you'll get notified of new eps):
```
/setchannel
```

### Usage

The bot has several commands that can be used to interact with it. You can view all the commands by typing `/help` in the Discord channel where the bot is running.

### Contributing

Feel free to submit pull requests and raise issues on the Github page.

Note:

- the bot is designed to be run 24/7 in order to scrape every so often, so if you don't have a dedicated server, you can use [replit](https://docs.replit.com/tutorials/build-basic-discord-bot-python#creating-a-repl-and-installing-our-discord-dependencies) (However, you will need to put your tokens from the .env file into replit Secrets, and upload each file onto the replit repository.
- the bot is using scraping to get anime episode airing information, so if any issues with the scraping please let me know.
- feel free to modify and use the code according to your usecase.

