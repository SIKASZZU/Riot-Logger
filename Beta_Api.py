import requests


class RiotAPI:
    def __init__(self, api_key: str, region: str):
        self.api_key = api_key
        self.region = region
        self.base_urls = {
            "ranked": f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-puuid/",
            "account": "https://europe.api.riotgames.com",
            "summoner": f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/",
            "icon": 'http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/',
            # replace 'TIER' with apex tier
            "apex": f"https://{self.region}.api.riotgames.com/lol/league/v4/TIERleagues/by-queue/RANKED_SOLO_5x5"
        }
        self.headers = {"X-Riot-Token": self.api_key}

    def check_key_validation(self):
        if self.get_puuid('ZØDIACSIGNCAŃCER', 'EUW'):
            return True
        return False

    @staticmethod
    def _handle_response(response, key):
        if response.status_code == 200:
            return response.json().get(key)
        print(f"Error {response.status_code}: {response.json()}")
        return None

    # puuid by submitted gameName and tagLine
    def get_puuid(self, game_name: str, tagline: str):
        url = f"{self.base_urls['account']}/riot/account/v1/accounts/by-riot-id/{game_name}/{tagline}"
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response, "puuid")

    # ranked info by puuid
    def get_ranked_data(self, puuid: str):
        url = f"{self.base_urls['ranked']}{puuid}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.json()}")
            return {}

        for entry in response.json():
            if entry['queueType'] == 'RANKED_SOLO_5x5':
                tier = entry['tier'].capitalize()
                data = {
                    'tier': tier,
                    'rank': entry['rank'],  # will be 'I' for Master+
                    'lp': entry['leaguePoints'],
                    'wins': entry['wins'],
                    'losses': entry['losses'],
                    'winrate': round(
                        entry['wins'] / (entry['wins'] + entry['losses']) * 100
                    ),
                    'hotStreak': entry['hotStreak']
                }

                # Apex tiers need ladder position
                if tier in ("Master", "Grandmaster", "Challenger"):
                    position = self.get_apex_position(puuid, tier)
                    data["ladderRank"] = position

                return data

        return {}

    def get_icon_id(self, puuid):
        url = f"{self.base_urls['summoner']}{puuid}" 
        response = requests.get(url, headers=self.headers) 
        # iconID = data.get('profileIconId')
        return self._handle_response(response, 'profileIconId')

    def get_player_data(self, game_name: str, tagline: str):

        puuid = self.get_puuid(game_name, tagline)
        if not puuid:
            print(f"Could not retrieve PUUID.->{game_name}#{tagline}")
            return {}

        iconID = self.get_icon_id(puuid)
        ranked_info = self.get_ranked_data(puuid)
        ranked_info.update({
            'iconID': iconID
        })

        return ranked_info

    def get_apex_league(self, tier: str):
        tier = tier.lower()
        url = self.base_urls['apex'].replace('TIER', tier)
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response, 'entries')

    def get_apex_position(self, puuid: str, tier: str):
        entries = self.get_apex_league(tier)
        if not entries:
            return None

        # Sort by LP (desc), wins (desc)
        entries.sort(
            key=lambda x: (x["leaguePoints"], x["wins"]),
            reverse=True
        )

        for index, player in enumerate(entries, start=1):
            if player["puuid"] == puuid:
                return index

        return None

def get_data(game_name: str, tagline: str, riot_api: RiotAPI) -> dict:
    return riot_api.get_player_data(game_name, tagline)

def get_puuid(game_name: str, tagline: str, riot_api: RiotAPI) -> str:
    url = f"{riot_api.base_urls['account']}/riot/account/v1/accounts/by-riot-id/{game_name}/{tagline}"
    response = requests.get(url, headers=riot_api.headers)
    return riot_api._handle_response(response, "puuid")

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv('getenv.env')
    api_key = os.getenv('api_key')
    if not api_key:
        raise ValueError("API key not found.")

    print()
    # info who you want to test with
    gameName = 'g h c a p o t b'
    tagLine = 'FF333'
    region = 'EUW1'
    riotApi = RiotAPI(api_key, region)
    data = get_data(gameName, tagLine, riotApi)
    print(data)