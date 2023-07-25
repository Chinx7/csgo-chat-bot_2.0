import requests
import steamid_converter.Converter

#local files
from config import settings as cfg
from info import get_players_and_map

def steamid64(steamid):
    return steamid_converter.Converter.to_steamID64(str(steamid))

def get_faceit_elo(player):
    player = steamid64(player)  # convert to steamid64 to be safe
    url = 'https://open.faceit.com/data/v4/players?game=csgo&game_player_id=' + player  # 76561198053393500
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer ' + cfg.faceit_api_key
    }

    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        country = data["country"]
        faceit_elo = data["games"]["csgo"]["faceit_elo"]
        game_player_name = data["games"]["csgo"]["game_player_name"]
        return country, faceit_elo, game_player_name
    else:
        print(f'Request failed with status code {response.status_code}')
        return "N/A", "N/A", "N/A"

def main(server_player):
    temp_dict = {}
    for player in server_player:
        temp_dict.update({player:get_faceit_elo(player)})
    return temp_dict

def test_func():
    playersAndMap = get_players_and_map()
    players = playersAndMap[0]
    return main(players)

print(test_func())