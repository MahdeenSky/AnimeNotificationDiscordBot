import requests

class MyAnimeListAPI:

    offset = 4
    limit = 1
    fields = ["id", "title", "main_picture", "alternative_titles", "start_date", "end_date", "synopsis", "mean", "rank", "popularity", "num_list_users", "num_scoring_users", "nsfw", "created_at", "updated_at", "media_type", "status", "genres", "my_list_status", "num_episodes", "start_season", "broadcast", "source", "average_episode_duration", "rating", "pictures", "background", "related_anime", "related_manga", "recommendations", "studios", "statistics"]

    def __init__(self, clientID) -> None:
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0', "X-MAL-CLIENT-ID": clientID}


    def _searchAnimeData(self, anime_name: str, limit=limit, offset=offset, fields=fields) -> dict:
        print(f"https://api.myanimelist.net/v2/anime?offset={offset}&q={anime_name}&limit={limit}&fields={','.join(fields)}")
        r = requests.get(f"https://api.myanimelist.net/v2/anime?offset={offset}&q={anime_name}&limit={limit}&fields={','.join(fields)}",
                headers=self.headers
        )
        return r.json()

    def searchAnime(self, anime_name: str, limit=limit, offset=offset, fields=fields) -> list:
        anime_data = self._searchAnimeData(anime_name, limit=limit, offset=offset, fields=fields)
        processed_data = []
        for anime in anime_data["data"]:
            processed_data.append(anime["node"])
        return processed_data

    def searchAnimeByID(self, anime_id: int, fields=fields) -> dict:
        r = requests.get(f"https://api.myanimelist.net/v2/anime/{anime_id}?fields={','.join(fields)}",
                headers=self.headers
        )
        return r.json()

    def searchAnimeByRanking(self, ranking_type: str = "airing", fields=fields) -> dict:
        r = requests.get(f"https://api.myanimelist.net/v2/anime/ranking?ranking_type={ranking_type}&fields={','.join(fields)}",
                headers=self.headers
        )
        return r.json()

    def getAnimeByID(self, anime_id: int, fields=fields) -> dict:
        r = requests.get(f"https://api.myanimelist.net/v2/anime/{anime_id}?fields={','.join(fields)}",
                headers=self.headers
        )
        return r.json()

if __name__ == "__main__":
    import dotenv
    import os
    dotenv.load_dotenv()
    clientID = os.getenv("MAL_CLIENT_ID")
    mal = MyAnimeListAPI(clientID)
    print(mal.getAnimeByID(49470))