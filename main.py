import argparse
import os
import sys
import json
import sqlite3


def main():
    args = parse_arguments()

    if args.playlist:
        games = get_playlist_games_ids(args.playlist)
        report(games)
        
    if args.playtime:
        games = get_played_games_ids()
        report(games)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-pl", "--playlist", help="the filename of the playlist with the games you want a report about")
    parser.add_argument("-pt", "--playtime", help="get the report about all the games you have played in Flashpoint", action="store_true")
    args = parser.parse_args()
    if not args.playlist and not args.playtime:
        parser.error("Please add at least one the available parameters.")
    return args


def get_playlist_games_ids(playlist):

    if not os.path.exists(playlist):
        sys.exit("Invalid filename.")

    f = open(playlist) 
    playlist = json.load(f)
    f.close()
    games = playlist["games"]
    ids = []
    for game in games:
        ids.append(game["gameId"])

    return ids


def get_played_games_ids():

    if not os.path.isfile("flashpoint.sqlite"):
        print("Error: please provide the database file")
        sys.exit()

    con = sqlite3.connect("flashpoint.sqlite")
    cur = con.cursor()
    res = cur.execute('SELECT id FROM game WHERE playtime > 0')
    ids = []
    for game in res.fetchall():
        id = game[0]
        ids.append(id)
    
    return ids


def report(games):
    print("HHEHHEHEH")


if __name__ == "__main__":
    main()