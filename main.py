import argparse
import os
import sys
import json
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def main():
    args = parse_arguments()

    if args.playlist:
        games = get_playlist_games_ids(args.playlist)
        report(games)

    if args.playtime:
        games = get_played_games_ids()
        report(games)

    print("Done.")


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
    df = create_df(games)
    data = calculate(df)
    write_data(data)
    draw_plots(data)


 


def create_df(games):

    con = sqlite3.connect("flashpoint.sqlite")
    cur = con.cursor()
    rows = []

    for game in games:
        print(game)
        row = cur.execute('SELECT * FROM game WHERE id = ?', (game,)).fetchall()[0]
        rows.append(row)
   
    con.row_factory = sqlite3.Row
    columns = con.execute('SELECT * FROM game').fetchone().keys()
    df = pd.DataFrame(rows, columns=columns)

    return df


def calculate(df):
    top_developers = df.loc[df.developer != '', "developer"].value_counts()[:10]
    top_publishers = df.loc[df.publisher != '', "publisher"].value_counts()[:10]


    data = {
        "top_developers": top_developers,
        "top_publishers": top_publishers
    }


def write_data(data):
    print("W")


def draw_plots(data):

    top_developers = data["top_developers"]
    sns.set(rc={"figure.figsize":(20,8.27)})
    plot = sns.barplot(x = top_developers.values, y = top_developers.index, orient = "h").set(title = "Top ten developers distribution")
    plt.tight_layout()
    plt.savefig(f"report/plots/top_developers_bar_plot.png")
    plt.figure(clear=True)

    labels = top_developers.index
    sizes = top_developers.values / top_developers.values.sum() * 100
    plt.pie(sizes, textprops = {"color":"w"})
    labels = [f"{l} - {s:0.1f}%" for l, s in zip(labels, sizes)]
    plt.legend(labels = labels, bbox_to_anchor = (1.6,1), loc = "best")
    plt.title("Top ten developers distribution")
    plt.tight_layout()
    plt.savefig(f"report/plots/top_developers_pie_chart.png")

    plt.figure(clear=True)

    top_publishers = data["top_publishers"]
    plot = sns.barplot(x = top_publishers.values, y = top_publishers.index, orient = "h").set(title = "Top ten publishers distribution")
    plt.tight_layout()
    plt.savefig(f"report/plots/top_publishers_bar_plot.png")
    plt.figure(clear=True)

    labels = top_publishers.index
    sizes = top_publishers.values / top_publishers.values.sum() * 100
    plt.pie(sizes, textprops = {"color":"w"})
    labels = [f"{l} - {s:0.1f}%" for l, s in zip(labels, sizes)]
    plt.legend(labels = labels, bbox_to_anchor = (1.6,1), loc = "best")
    plt.title("Top ten publishers distribution")
    plt.tight_layout()
    plt.savefig(f"report/plots/top_publishers_pie_chart.png")

    plt.figure(clear=True)


if __name__ == "__main__":
    main()