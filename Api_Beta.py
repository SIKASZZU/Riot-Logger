import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv('riot_api_key')  # TODO: Ensure your API key is in the .env file

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
        # Handle client-side errors (4xx) and server-side errors (5xx)
        if response.status_code >= 400 and response.status_code < 500:
            return f"Client [{response.status_code}]"
        elif response.status_code >= 500 and response.status_code < 600:
            return f"Server [{response.status_code}]"
        else:
            return f"Error {response.status_code} - Unknown error"

# Function to get Summoner ID from PUUID
def get_summoner_id(puuid: str, api_key: str, region: str):
    url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('id')  # Summoner ID
    else:
        # Handle client-side errors (4xx) and server-side errors (5xx)
        if response.status_code >= 400 and response.status_code < 500:
            return f"Client [{response.status_code}]"
        elif response.status_code >= 500 and response.status_code < 600:
            return f"Server [{response.status_code}]"
        else:
            return f"Error {response.status_code} - Unknown error"

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
                # Return the rank and winrate as separate strings
                rank_str = f"{tier} {rank} - {lp} LP"
                winrate_str = f"{wins}W/{losses}L - {winrate}% WR"
                return rank_str, winrate_str
        return "No ranked data found."
    else:
        # Handle client-side errors (4xx) and server-side errors (5xx)
        if response.status_code >= 400 and response.status_code < 500:
            return f"Client [{response.status_code}]"
        elif response.status_code >= 500 and response.status_code < 600:
            return f"Server [{response.status_code}]"
        else:
            return f"Error {response.status_code} - Unknown error"

# Main execution
puuid = get_puuid(game_name, tagline, api_key)
if isinstance(puuid, str) and puuid.startswith("Client") or puuid.startswith("Server"):
    print(puuid)  # Print the error message
else:
    summoner_id = get_summoner_id(puuid, api_key, region)
    if isinstance(summoner_id, str) and summoner_id.startswith("Client") or summoner_id.startswith("Server"):
        print(summoner_id)  # Print the error message
    else:
        ranked_info = get_ranked_data(summoner_id, api_key, region)
        if isinstance(ranked_info, str) and ranked_info.startswith("Client") or ranked_info.startswith("Server"):
            print(ranked_info)  # Print the error message
        else:
            # Unpack the tuple into rank and winrate strings
            rank, winrate = ranked_info
            print(f"Ranked Info: {rank}, {winrate}")
