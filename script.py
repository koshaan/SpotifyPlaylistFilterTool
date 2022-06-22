import configparser
import sys
import argparse
import os
import requests
import json

def getSongsInList(playlistid):
    list = [] 
    total = requests.get("https://api.spotify.com/v1/playlists/{}?fields=tracks(total)".format(playlistid), headers=headers).json()['tracks']['total']
    print("songs in playlist: " + str(total))
    for offset in range(0, total, 100):
        new_endpoint = (endpoint + "/tracks?fields=items(track(name%2Cid))&offset={}").format(playlistid, offset)
        print("attempting request: " + str(new_endpoint))
        tracks = requests.get(new_endpoint, headers=headers).json()
        for item in tracks["items"]:
            list.append(item["track"])
    return list

input("This tool cannot perform any actions on local files. Sorry. Continue?")


config = configparser.RawConfigParser()
config.read('config.config')

parser = argparse.ArgumentParser(description='spotify delete one playlist from another')
parser.add_argument("-t", "--token", help="token for spotify account", type=str, default=config['info']['token'])
parser.add_argument("-o", "--originalid", help="playlist id of the one to keep songs from", type=str, default=config['info']['originalid'])
parser.add_argument("-d", "--deleteid", help="playlist id of the one to delete occurences of", type=str, default=config['info']['deleteid'])
parser.add_argument("-u", "--userid", help="user id of spotify account", type=str, default=config['info']['userid'])

args = parser.parse_args().__dict__

token = args["token"]
original_playlist = args["originalid"]
deleter_playlist = args["deleteid"]
userid = args["userid"]

for elem in args.items():
    if elem[1] == "default":
        print(elem[0] + " cannot be left as default.")
        exit()

endpoint = "https://api.spotify.com/v1/playlists/{}"
headers = {"Authorization": "Bearer " + token}

try:
    if requests.get("https://api.spotify.com/v1/artists/6GTwMrB4u3hwcUyc9sU1UL", headers=headers).json()['name'] != "The Minds Of 99":
        print("Error occured in spotify API")
        exit()
except Exception as e:
    print("Error in alive check, token probrably expired")

originalList = getSongsInList(original_playlist)
deleteList = getSongsInList(deleter_playlist)

print("checking lengths on playlists. should match numbers printed earlier.")
print(len(originalList), len(deleteList))

print("intersecting playlists")
original_ids = list(map(lambda x: str(x["id"]), originalList))
delete_ids = list(map(lambda x: str(x["id"]), deleteList))

intersection = list(set(original_ids) & set(delete_ids)) 
only_left = [x for x in original_ids if x not in intersection]
print(str(len(only_left)) + " songs left")

print("creating new playlist for the remaining " + str(len(only_left)) + " songs")
create_playlist_body = {
  "name": "filtered playlist✨",
  "description": "filtered playlist based on two others",
  "public": "false"
}

new_playlist_id = requests.post("https://api.spotify.com/v1/users/{}/playlists".format(userid), headers=headers, json=create_playlist_body).json()["id"]

spotify_track_list = list(map(lambda x: "spotify:track:" + str(x), only_left))

def divide_chunks(l, n):
    for i in range(0, len(l), n): 
        yield l[i:i + n]

divided_list = list(divide_chunks(spotify_track_list, 90))

for sublist in divided_list:
    track_string = ','.join(sublist)
    requests.post("https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(new_playlist_id, track_string), headers=headers)

print("All done. check out the playlist at: ")
print("https://open.spotify.com/playlist/{}".format(new_playlist_id))
input("close?")