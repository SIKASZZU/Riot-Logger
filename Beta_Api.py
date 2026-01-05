import requests


class RiotAPI:
    def __init__(self, api_key: str, region: str):
        self.api_key = api_key
        self.region = region
        self.base_urls = {
            "ranked": f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-puuid/",
            "account": "https://europe.api.riotgames.com",
            "summoner": f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/",
            "icon": 'http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/'
        }
        self.headers = {"X-Riot-Token": self.api_key}

    # puuid by submitted gameName and tagLine
    def get_puuid(self, game_name: str, tagline: str):
        url = f"{self.base_urls['account']}/riot/account/v1/accounts/by-riot-id/{game_name}/{tagline}"
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response, "puuid")

    # ranked info by puuid
    def get_ranked_data(self, puuid: str):
        url = f"{self.base_urls['ranked']}{puuid}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            ranked_data = response.json()
            for entry in ranked_data:
                if entry['queueType'] == 'RANKED_SOLO_5x5':
                    tier, rank, lp = entry['tier'], entry['rank'], entry['leaguePoints']
                    wins, losses = entry['wins'], entry['losses']
                    hotStreak = entry['hotStreak']
                    winrate = round((wins / (wins + losses)) * 100, 1)
                    return {
                        'tier': tier,
                        'rank': rank,
                        'lp': lp,
                        'wins': wins,
                        'losses': losses,
                        'winrate': winrate,
                        'hotStreak': hotStreak,
                        }
            return None
        else:
            print(f"Error {response.status_code}: {response.json()}")
            return None

    def get_icon_id(self, puuid):
        url = f"{self.base_urls['summoner']}{puuid}" 
        response = requests.get(url, headers=self.headers) 
        # iconID = data.get('profileIconId')
        return self._handle_response(response, 'profileIconId')

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

        iconID = self.get_icon_id(puuid)
        ranked_info = self.get_ranked_data(puuid)

        ranked_info.update({
            'iconID': iconID
        })

        return ranked_info


def get_data(game_name, tagline, region, api_key):
    riot_api = RiotAPI(api_key, region)
    return riot_api.get_player_data(game_name, tagline)

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv('getenv.env')
    api_key = os.getenv('api_key')
    if not api_key:
        raise ValueError("API key not found.")

    print()
    data = get_data('TwTv RiverSanzu', '0000', 'EUN1', api_key)
    print(data)