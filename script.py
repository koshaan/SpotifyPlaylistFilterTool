import configparser
import sys
import argparse
import os

config = configparser.RawConfigParser()
config.read('config.config')

parser = argparse.ArgumentParser(description='spotify delete one playlist from another')
parser.add_argument("-t", "--token", help="token for spotify account", type=str, default=config['info']['token'])
parser.add_argument("-o", "--originalid", help="playlist id of the one to keep songs from", type=str, default=config['info']['originalid'])
parser.add_argument("-d", "--deleteid", help="playlist id of the one to delete occurences of", type=str, default=config['info']['deleteid'])

args = parser.parse_args().__dict__

token = args["token"]

for elem in args.items():
    if elem[1] == "default":
        print(elem[0] + " cannot be left as default.")
        exit(420)

print("found token: " + str(token))


