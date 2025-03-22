import requests


class RiotAPI:
    def __init__(self, api_key: str, region: str):
        self.api_key = api_key
        self.region = region
        self.base_urls = {
            "account": "https://europe.api.riotgames.com",
            "summoner": f"https://{region}.api.riotgames.com"
        }
        self.headers = {"X-Riot-Token": self.api_key}

    def get_puuid(self, game_name: str, tagline: str):
        url = f"{self.base_urls['account']}/riot/account/v1/accounts/by-riot-id/{game_name}/{tagline}"
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response, "puuid")

    def get_summoner_id(self, puuid: str):
        url = f"{self.base_urls['summoner']}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response, "id")

    def get_ranked_data(self, summoner_id: str):
        url = f"{self.base_urls['summoner']}/lol/league/v4/entries/by-summoner/{summoner_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            ranked_data = response.json()
            for entry in ranked_data:
                if entry['queueType'] == 'RANKED_SOLO_5x5':
                    tier, rank, lp = entry['tier'], entry['rank'], entry['leaguePoints']
                    wins, losses = entry['wins'], entry['losses']
                    winrate = round((wins / (wins + losses)) * 100, 1)
                    return (tier, rank, lp), (wins, losses, winrate)
            return None
        else:
            print(f"Error {response.status_code}: {response.json()}")
            return None

    @staticmethod
    def _handle_response(response, key):
        if response.status_code == 200:
            return response.json().get(key)
        print(f"Error {response.status_code}: {response.json()}")
        return None

    def get_player_data(self, game_name: str, tagline: str):
        puuid = self.get_puuid(game_name, tagline)
        if not puuid:
            print("Could not retrieve PUUID.")
            return None

        summoner_id = self.get_summoner_id(puuid)
        if not summoner_id:
            print("Could not retrieve Summoner ID.")
            return None

        ranked_info = self.get_ranked_data(summoner_id)
        if ranked_info:
            rank, winrate = ranked_info
            tier, rank, lp = rank
            wins, losses, winrate = winrate

            rank = tier, f"{tier} {rank} - {lp} LP"
            winrate = f"{wins}W/{losses}L - {winrate}% WR"

        else:
            winrate = None
            rank = None

        return rank, winrate


def get_data(game_name, tagline, region, api_key):
    riot_api = RiotAPI(api_key, region)
    return riot_api.get_player_data(game_name, tagline)

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv('riot_api_key')
    if not api_key:
        raise ValueError("API key not found. Check your .env file.")

    data = get_data('revert conq zzzz', 'mrcha', 'EUW1', api_key)
    print(data)