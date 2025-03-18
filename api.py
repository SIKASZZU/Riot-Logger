import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv('riot_api_key')  # TODO: pane oma api key faili .env

if not api_key:
    raise ValueError("API key not found. Check your .env file.")

game_name = 'pegla'
tagline = 'eune'
region = 'eun1'  # Use 'eun1' for EUNE players

# Function to get PUUID
def get_puuid(game_name: str, tagline: str, api_key: str):
    url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tagline}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('puuid')
    else:
        print(f"Error {response.status_code}: {response.json()}")
        return None

# Function to get Summoner ID from PUUID
def get_summoner_id(puuid: str, api_key: str, region: str):
    url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('id')  # Summoner ID
    else:
        print(f"Error {response.status_code}: {response.json()}")
        return None

# Function to get ranked data from Summoner ID
def get_ranked_data(summoner_id: str, api_key: str, region: str):
    url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        ranked_data = response.json()
        for entry in ranked_data:
            if entry['queueType'] == 'RANKED_SOLO_5x5':
                tier = entry['tier']
                rank = entry['rank']
                lp = entry['leaguePoints']
                wins = entry['wins']
                losses = entry['losses']
                winrate = round((wins / (wins + losses)) * 100, 1)
                return f"{tier} {rank} - {lp} LP ({winrate}% WR)"
        return "No ranked data found."
    else:
        print(f"Error {response.status_code}: {response.json()}")
        return None

# Main execution
puuid = get_puuid(game_name, tagline, api_key)
if puuid:
    summoner_id = get_summoner_id(puuid, api_key, region)
    if summoner_id:
        ranked_info = get_ranked_data(summoner_id, api_key, region)
        print(f"Ranked Info: {ranked_info}" if ranked_info else "Could not retrieve rank.")
    else:
        print("Could not retrieve Summoner ID.")
else:
    print("Could not retrieve PUUID.")
