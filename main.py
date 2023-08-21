import argparse
import os
import sys
import json
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter


def main():
    set_up()
    args = parse_arguments()

    if args.playlist:
        games = get_playlist_games_ids(args.playlist)
        report(games)

    if args.playtime:
        games = get_played_games_ids()
        report(games)

    print("Done.")


def set_up():

    try:
        os.makedirs(os.path.join(os.getcwd(), "report", "csv"))
    except FileExistsError:
        pass

    try:
        os.makedirs(os.path.join(os.getcwd(), "report", "plots"))
    except FileExistsError:
        pass


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

    print("Getting data...")

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
        print("Error: please provide the database file.")
        sys.exit()
    
    print("Getting data...")

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
    
    print("Calculating stats...")

    developers = df.loc[df.developer != '', "developer"].value_counts()
    publishers = df.loc[df.publisher != '', "publisher"].value_counts()

    dates = get_dates(df)

    data = {
        "developers": developers,
        "publishers": publishers,
        "dates": dates
    }

    return data


def get_dates(df):
    df_dates = df.loc[(df.releaseDate != ""), ["title", "releaseDate", "platformName", "library"]].sort_values(by=["releaseDate"])
    df_dates["releaseDate"] = pd.to_datetime(df_dates["releaseDate"], format="mixed").dt.strftime("%Y-%m-%d")     # year-only values get labeled with 1st January.
    
    return df_dates




def write_data(data):
    print("Writing data in CSV format...")

    for field in data:
        data[field].to_csv(f"report/csv/{field}.csv", index=False, header=True)



def draw_plots(data):

    print("Drawing plots...")

    first_set = ["developers", "publishers", "platforms"]

    for field in first_set:
        create_bar_plot(data[f"{field}"].iloc[:10], f"top_{field}")



def create_bar_plot(data, title):

    sns.set(rc={"figure.figsize":(20,8.27)})
    plot = sns.barplot(x = data.values, y = data.index, orient = "h").set(title = title)
    plt.tight_layout()
    plt.savefig(f"report/plots/{title}_bar_plot.png")
    plt.figure(clear=True)

    labels = data.index
    sizes = data.values / data.values.sum() * 100
    plt.pie(sizes, textprops = {"color":"w"})
    labels = [f"{l} - {s:0.1f}%" for l, s in zip(labels, sizes)]
    plt.legend(labels = labels, bbox_to_anchor = (1.6,1), loc = "best")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"report/plots/{title}_pie_chart.png")

    plt.figure(clear=True)


if __name__ == "__main__":
    main()