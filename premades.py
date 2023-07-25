import requests
import steamid_converter.Converter
# local files
from config import settings as cfg
LIST_OF_STEAMIDS = ('76561197982139967', '76561198053393500', '76561197986501211', '76561198378520858', '76561198293126043', '76561198062143237', '76561198136231154', '76561198038784566', '76561198103926498', '76561198860732520')


def steamid64(steamid):
    return steamid_converter.Converter.to_steamID64(str(steamid))


def get_steam_friends(steam_id, api_key):
    steam_id = steamid64(steam_id)  # convert to steamid64 to be safe
    api_url = 'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key=' + api_key + '&relationship=friend&steamid='
    final_api_url = api_url + str(steam_id)
    data_response = requests.get(final_api_url, timeout=2).json()
    try:
        steamids = [friend['steamid'] for friend in data_response['friendslist']['friends']]
    except:
        steamids = []
    return steamids


def remove_nonplayer_from_friendlist(players_on_server, friendlist):
    temp_list = []
    for player in friendlist:
        if player in players_on_server:
            temp_list.append(player)
    return temp_list


# Let's define a helper function that given a player and their friends, finds an existing premade group they belong to
def find_premade_group(player, friends, premade_groups):
    for group in premade_groups:
        if player in group or any(friend in group for friend in friends):
            return group
    return None


def build_dict_for_players(players_on_server):
    done_dict = {}
    for player in players_on_server:
        friendlist = get_steam_friends(player, cfg.steam_api_key)
        clean_fl = remove_nonplayer_from_friendlist(players_on_server, friendlist)
        done_dict.update({player:clean_fl})
    return done_dict


def resolve_steamid_to_name(steamid, api_key):
    response = requests.get(
        'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key='+ api_key + '&steamids=' + steamid)

    data = response.json()

    personaname = data["response"]["players"][0]["personaname"]
    return personaname


def main(server_players):
    premade_groups = []
    steam_key = cfg.steam_api_key
    players_friends = build_dict_for_players(server_players)

    for player, friends in players_friends.items():
        # Find an existing premade group the player or their friends belong to
        group = find_premade_group(player, friends, premade_groups)

        if group is not None:
            # If there's an existing group, add the player and their friends to it
            group.update([player] + friends)
        else:
            # If not, create a new group
            group = set([player] + friends)
            premade_groups.append(group)

    # Filter out groups that are larger than 5 players or smaller than 2 players (as they're not premade groups)
    premade_groups = [group for group in premade_groups if 2 <= len(group)]  # include " <= 5]" if you want max size of5
    premade_group_with_names = [{resolve_steamid_to_name(id, cfg.steam_api_key) for id in group} for group in premade_groups]
    return premade_group_with_names
    # input is list of all players on server, returns a maximum of 4 premade groups


print(main(LIST_OF_STEAMIDS))
