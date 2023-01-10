import os

import disnake
from disnake.ext import commands, tasks
from disnake.ui import Select, View
from disnake import Embed, HTTPException

import requests as r
from bs4 import BeautifulSoup
from random import choice, randint
import asyncio
from AnilistPython import Anilist
import datetime as dt

from dotenv import load_dotenv

from myanimelistAPI import MyAnimeListAPI
from jikan4pyAPI import JikanAPI
from utilities import print_bot, isInteger, jsonOP

# formatting
en_space = " "
invisible_space = "‎"

# Global Variables
load_dotenv()
with open("useragents.txt", 'r') as f:
	HEADERS = [{'User-Agent': header} for header in f.read().splitlines()]

DOMAIN = "https://gogoplay1.com/" # anime ep scraping domain
MAL_DOMAIN = "https://myanimelist.net/anime/"
JSONFILENAME = "series.json" # stores all the tracked anime
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID")) # the discord channel which it will notify

MAL_CLIENT_ID = os.getenv("MAL_CLIENT_ID")
DISCORD_TAG = "@everyone" # Change this to what role it will ping

class aclient(commands.Bot):
	def __init__(self):
		super().__init__(intents=disnake.Intents.default(),
						 command_prefix=commands.when_mentioned)

	async def on_ready(self):
		await self.wait_until_ready()
		await self.change_presence(activity=disnake.Activity(
			type=disnake.ActivityType.watching, name="MahdeenSky"))

		print_bot(
			f"Logged in as {self.user}, Notifying on channel {CHANNEL_ID}")
		scrapeAiringAnime.start()


bot = aclient()
mal_api = MyAnimeListAPI(MAL_CLIENT_ID)
jikan_api = JikanAPI()
anilist_api = Anilist()

jsonOP = jsonOP(JSONFILENAME)
if jsonOP.loadJSON() == {}:
	jsonOP.saveJSON({"series": []})

malID_to_aniListID = {}


def malIDtoAniListID(anime_id):
	"""
	Converts the MAL ID to AniList ID
	using GraphQL
	"""
	if anime_id in malID_to_aniListID:
		return malID_to_aniListID[anime_id]

	query = """query
		($id: Int, $type: MediaType) {
			Media(idMal: $id, type: $type) {
				id}
			}
		"""
	variables = {'id': anime_id, 'type': 'ANIME'}
	url = 'https://graphql.anilist.co'
	response = r.post(url, json={'query': query, 'variables': variables})
	malID_to_aniListID[anime_id] = int(response.json()['data']['Media']['id'])
	return malID_to_aniListID[anime_id]


def timeTillNextEpisode(anime_id):
	"""
	Returns the time till the next episode of the anime airs
	"""
	query = """query ($id: Int) {
					Media(idMal: $id, type: ANIME) {
						id
						nextAiringEpisode {
						timeUntilAiring
						}
					}
				}
	"""
	variables = {'id': anime_id, 'type': 'ANIME'}
	url = 'https://graphql.anilist.co'
	data = r.post(url, json={'query': query, 'variables': variables}).json()

	time_data = data['data']['Media']['nextAiringEpisode']
	if time_data is not None:
		seconds = time_data['timeUntilAiring']
	else:
		return {"days": 0,
				"hours": 0,
				"minutes": 0,
				"seconds": 0,
				"total_seconds": 0,
				"isNull": True}

	time = dt.timedelta(seconds=seconds)
	return {"days": time.days,
			"hours": time.seconds//3600,
			"minutes": (time.seconds//60) % 60,
			"seconds": time.seconds % 60,
			"total_seconds": seconds,
			"isNull": False}


def isAnimeAiring(anime_id, api="mal"):
	"""
	Checks if the anime is airing
	using the MyAnimeList API (atleast more updated then the Jikan API due to less caching)
	"""
	if api == "mal":
		try:
			result = mal_api.getAnimeByID(anime_id)
			return (result['status'] != "finished_airing")
		except Exception as e:
			print_bot(
				f"Error: Mal API ID check failed, so switching to Jikan API.\n'{e}'")
			result = jikan_api.getAnimeByID(anime_id)
			return result["status"] != "Finished Airing"
	else:
		result = jikan_api.getAnimeByID(anime_id)
		return result["status"] != "Finished Airing"


def episodeEmbedCard(anime_id, episode_number, video_link, airing=True):
	"""
	Creates an embed card for the episode
	"""
	anime = jikan_api.getAnimeByID(anime_id)

	description = f"Episode {episode_number}"
	if not airing:
		description += " (Final Episode)"

	embed = Embed(title=anime['title'],
				  description=description, color=0x00ff00)
	embed.set_thumbnail(url=anime['images']['jpg']['image_url'])
	embed.set_footer(text="by MahdeenSky")
	embed.set_image(url=anime['images']['jpg']['image_url'])
	embed.add_field(name="MyAnimeList",
					value=f"[Link](https://myanimelist.net/anime/{anime_id})", inline=False)
	embed.add_field(name="Episode", value=f"[Link]({video_link})", inline=True)
	return embed


def animeListEmbedCard(anime_series):
	"""
	Creates an embed card for the anime list
	"""
	embed = Embed(title="Currently Tracking Anime", color=0xff0000)
	embed.set_footer(text="by MahdeenSky")

	fields = []
	for anime in anime_series:
		anime_name, episode_number, anime_id = anime
		mal_anime_link = MAL_DOMAIN + str(anime_id)

		nextEpTime = timeTillNextEpisode(anime_id)
		if nextEpTime["isNull"]:
			time = "N/A"
		elif nextEpTime["days"] == 0 and nextEpTime["hours"] == 0 and nextEpTime["minutes"] == 0:
			time = f"{nextEpTime['seconds']} seconds"
		elif nextEpTime["days"] == 0 and nextEpTime["hours"] == 0:
			time = f"{nextEpTime['minutes']} minutes"
		elif nextEpTime["days"] == 0:
			time = f"{nextEpTime['hours']} hours and {nextEpTime['minutes']} minutes"
		else:
			time = f"{nextEpTime['days']} days, {nextEpTime['hours']} hours and {nextEpTime['minutes']} minutes"

		episode_field = f"Episode {episode_number}" if episode_number != - \
			1 else "Episode Did Not Air"
		episode_field += "\n" + f"Airing in {time}"
		episode_field += "\n" + f"[anime]({mal_anime_link})"
		fields.append((anime_name, episode_field, nextEpTime["total_seconds"]))

	fields.sort(key=lambda x: x[2])
	for anime_name, episode_field, _ in fields:
		embed.add_field(name=anime_name, value=episode_field, inline=True)
	return embed


def animeSelectionEmbedCards(animes):
	embeds = [Embed(title="Which Anime to Add?", color=0xffff00)]
	anime_titles = [anime["title"] for anime in animes]
	longest_title_length = max([len(title) for title in anime_titles])
	for i, title in enumerate(anime_titles, 1):
		embed = Embed(url=f"https://www.lol{i}.com", color=0xff00ff)
		space_length = longest_title_length - len(title) + title.count(":")
		embed.add_field(name=f"{i}.\n{title}"+space_length*en_space+invisible_space, value=invisible_space, inline=False)
		embed.set_thumbnail(animes[i-1]["images"]["jpg"]["image_url"])
		embeds.append(embed)
	return embeds

def animeDeletionEmbedCard(anime_titles):
	embed = Embed(title="Which Anime to Remove?", color=0xfff000)
	for i, title in enumerate(anime_titles, 1):
		embed.add_field(name=f"{i}. {title}", value=invisible_space, inline=False)
	return embed


@bot.slash_command(description="Adds an anime to the list")
async def addanime(interaction: disnake.CommandInteraction, name: str):
	print_bot(f"Adding New Anime")
	animes = jikan_api.searchAnime(anime_name=name)
	anime_titles = [anime["title"] for anime in animes]
	print_bot(f"Querying for '{name}'")
	print_bot(f"Choices are: '{', '.join(anime_titles)}'")
	options = [disnake.SelectOption(label=i, value=i-1)
			   for i in range(1, len(anime_titles)+1)]
	select = Select(placeholder="", options=options)

	async def my_callback(interaction: disnake.CommandInteraction):
		selectedAnime = anime_titles[int(select.values[0])]
		anime_id = jikan_api.getAnimeIDByName(anime_name=selectedAnime)
		registered_series = jsonOP.loadJSON()["series"]

		if all(selectedAnime not in registeredanime for registeredanime in registered_series):
			registered_series.append([selectedAnime, -1, anime_id])
			jsonOP.saveJSON({"series": registered_series})
			print_bot(f"Added '{selectedAnime}' to the list")
			await interaction.send(f"Added {selectedAnime} to the list")
		else:
			print_bot(f"{selectedAnime} is already in the list")
			await interaction.send(f"{selectedAnime} is already in the list")

	select.callback = my_callback
	view = View()
	view.add_item(select)

	await interaction.send("Which Anime To Add?", view=view, embeds=animeSelectionEmbedCards(animes), delete_after=30)


@bot.slash_command(description="Removes an anime from the list")
async def removeanime(interaction: disnake.CommandInteraction):
	print_bot(f"Removing Anime")
	anime_titles = [anime[0] for anime in jsonOP.loadJSON()["series"]]
	print_bot(f"Choices are: '{', '.join(anime_titles)}'")
	options = [disnake.SelectOption(label=i, value=i-1)
			   for i in range(1, len(anime_titles)+1)]
	select = Select(placeholder="", options=options)

	async def my_callback(interaction: disnake.CommandInteraction):
		selectedAnime = anime_titles[int(select.values[0])]
		current_series = jsonOP.loadJSON()["series"]

		for i, anime in enumerate(current_series):
			if anime[0] == selectedAnime:
				current_series.pop(i)
				jsonOP.saveJSON({"series": current_series})
				print_bot(f"Removed '{selectedAnime}' from the list")
				await interaction.send(f"Removed {selectedAnime} from the list")
				return

		print_bot(f"{selectedAnime} is not in the list")
		await interaction.send(f"{selectedAnime} is not in the list")

	select.callback = my_callback
	view = View()
	view.add_item(select)

	await interaction.send("Which Anime to Remove?", view=view, embed=animeDeletionEmbedCard(anime_titles), delete_after=30)


@bot.slash_command(description="Shows the current tracked anime list")
async def listanime(interaction: disnake.CommandInteraction):
	try:
		await interaction.response.defer()
	except:
		print_bot("Defer failed")
		await interaction.followup.send("Error, please try again.")
		return

	try:
		print_bot(f"Listing Anime")
		current_series = jsonOP.loadJSON()["series"]
		if len(current_series) == 0:
			print_bot("No anime found in list")
			await interaction.send("You are not tracking any anime.")
			return
	except Exception as e:
		print(e)
		await interaction.followup.send("Error occured, please try again.")
		return

	await interaction.followup.send(embed=animeListEmbedCard(current_series))

@bot.slash_command(description="Select Channel to Announce New Episodes using Channel ID")
async def setchannel(interaction: disnake.CommandInteraction):
	executed_channel = interaction.channel_id
	try:
		with open(".env", 'r') as f:
			env = f.read().split("\n")

		with open(".env", 'w') as f:
			for i, line in enumerate(env):
				if line.startswith("DISCORD_CHANNEL_ID"):
					env[i] = f"DISCORD_CHANNEL_ID={executed_channel}"
					break
			f.write("\n".join(env))
			CHANNEL_ID = executed_channel
	except Exception as e:
		await interaction.send(f"{e}\nError occured, please try again.")
		return

	print_bot(f"Notification Channel set to {executed_channel}")
	await interaction.send(f"Notification Channel set to {executed_channel}")


@bot.slash_command(description="Help information for every command")
async def help(interaction: disnake.CommandInteraction):
	embed = disnake.Embed(title="Commands", color=0xf0000f)
	embed.add_field(name="/addanime", value="Adds an anime to the list", inline=False)
	embed.add_field(name="/removeanime", value="Removes an anime from the list", inline=False)
	embed.add_field(name="/listanime", value="Shows the current tracked anime list", inline=False)
	embed.add_field(name="/setchannel", value="Sets the channel to notify new episodes in", inline=False)
	embed.add_field(name="/help", value="Help information for every command", inline=False)
	await interaction.send(embed=embed)

@tasks.loop(count=1)
async def scrapeAiringAnime():
	"""
	Scrapes the GogoPlay website for airing anime
	"""
	while True:
		try:
			res = r.get(DOMAIN, headers=choice(HEADERS))
			soup = BeautifulSoup(res.text, "html.parser")
			episodes = soup.findAll("div", {"class": "name"})
		except HTTPException as e:
			print(e)
			# os.system("kill 1")

		for i, episode in enumerate(episodes):
			registeredAnime = jsonOP.loadJSON()["series"]
			episode_text = episode.text.strip().lower()
			for index, [anime, episode_number_db, anime_id] in enumerate(registeredAnime):
				if anime.lower() in episode_text:
					episode_number = episode_text.split("episode ")[-1]
					if str(episode_number_db) != str(episode_number):
						registeredAnime[index][1] = int(episode_number) if isInteger(
							episode_number) else float(episode_number)

						link = episodes[i].parent.get("href")
						video_link = scrapeVideo(DOMAIN + link)

						airing = isAnimeAiring(anime_id)

						print_bot(
							f"Anime '{anime}' has aired a new episode: {episode_number}")
						await notify(anime, anime_id, episode_number, video_link, airing)

						if not airing:
							registeredAnime.pop(index)
							jsonOP.saveJSON({"series": registeredAnime})
							print_bot(
								f"Anime '{anime}' is no longer airing at episode {episode_number_db}")
						else:
							jsonOP.saveJSON({"series": registeredAnime})

						break

		# airing anime check incase the program didn't run for a while and passed over the final episode
		for index, [anime, _, anime_id] in enumerate(registeredAnime):
			airing = isAnimeAiring(anime_id, api="jikan")
			# rate limit of 3 requests per second
			await asyncio.sleep(0.34)
			if not airing:
				registeredAnime.pop(index)
				jsonOP.saveJSON({"series": registeredAnime})
				episode_number = mal_api.getAnimeByID(anime_id)["num_episodes"]
				print_bot(
					f"Anime '{anime}' is no longer airing at episode '{episode_number}'")

		await asyncio.sleep(randint(300, 600)) # 5-10 minutes


def scrapeVideo(link):
	"""
	Scrapes the video link from the GogoPlay website
	"""
	res = r.get(link, headers=choice(HEADERS))
	soup = BeautifulSoup(res.text, "html.parser")
	# get the attribute called "src" from the iframe tag
	video_link = soup.find("iframe").get("src")
	return "https://" + video_link.lstrip("/")


async def notify(anime_name, anime_id, episode_number, video_link, airing=True):
	"""
	Notifies on Discord when an anime has aired a new episode
	"""
	message = DISCORD_TAG + f" {anime_name} Episode {episode_number}"
	try:
		channel = bot.get_channel(CHANNEL_ID)
		await channel.send(message, embed=episodeEmbedCard(anime_id, episode_number, video_link, airing))
	except Exception as e:
		print(f"{e}\nFailed to get Channel/Send Notification")

# keep_alive()
bot.run(os.getenv('BOT_API_KEY'))
