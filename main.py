import argparse
import os
import sys
import json
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
from itertools import islice


def main():
    args = parse_arguments()

    if args.playlist:
        games = get_playlist_games_ids(args.playlist)
        create_path(args.playlist.replace(".json", ""))
        report(games, args.playlist.replace(".json", ""))

    if args.playtime:
        games = get_played_games_ids()
        create_path("played")
        report(games, "played")

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


def create_path(name):

    try:
        os.makedirs(os.path.join(os.getcwd(), "report", name, "csv"))
    except FileExistsError:
        pass

    try:
        os.makedirs(os.path.join(os.getcwd(), "report", name, "plots"))
    except FileExistsError:
        pass


def report(games, name):
    df = create_df(games)
    data = calculate(df)
    write_data(data, name)
    draw_plots(data, name)


def create_df(games):

    con = sqlite3.connect("flashpoint.sqlite")
    cur = con.cursor()
    rows = []

    for game in games:
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
    platforms = df.loc[df.publisher != '', "platformName"].value_counts()
    genres = df.loc[df["tagsStr"] != "", "tagsStr"].str.replace(",", ";").str.split("; ").explode().value_counts()

    dates = get_dates(df)
    playtime = get_playtime(df)
    year_platform = get_year_platform(dates)

    data = {
        "developers": developers,
        "publishers": publishers,
        "platforms": platforms,
        "genres": genres,
        "dates": dates,
        "playtime": playtime,
        "year_platform": year_platform
    }

    return data


def get_dates(df):
    df_dates = df.loc[(df.releaseDate != ""), ["title", "releaseDate", "platformName", "library"]].sort_values(by=["releaseDate"])
    df_dates["releaseDate"] = pd.to_datetime(df_dates["releaseDate"], format="mixed").dt.strftime("%Y-%m-%d")     # year-only values get labeled with 1st January.
    
    return df_dates


def get_playtime(df):
    df_playtime = df.loc[(df.releaseDate != ""), ["title", "playtime", "releaseDate", "platformName", "library"]].sort_values(by=["playtime"], ascending=False)
    return df_playtime


def get_year_platform(df_dates):

    df_year_platform = df_dates.copy()
    years = df_year_platform["releaseDate"].astype(str).str[:4]
    df_year_platform[df_year_platform.columns[1]] = years.values
    
    return df_year_platform


def write_data(data, name):
    print("Writing data in CSV format...")

    data = dict(islice(data.items(), 6))
    for field in data:
        data[field].to_csv(f"report/{name}/csv/{field}.csv", index=True, header=True)


def draw_plots(data, name):

    print("Drawing plots...")

    first_set = ["developers", "publishers", "platforms", "genres"]

    for field in first_set:
        create_bar_plot(data[f"{field}"].iloc[:10], f"top_{field}", name)
        create_pie_chart(data[f"{field}"].iloc[:10], f"top_{field}", name)
    
    create_stacked_bar_plot(data["year_platform"], "platform_distribution_by_year", name)


def create_bar_plot(data, title, name):

    sns.set(rc={"figure.figsize":(20,8.27)})
    plot = sns.barplot(x = data.values, y = data.index, orient = "h").set(title = title)
    plt.tight_layout()
    plt.savefig(f"report/{name}/plots/{title}_bar_plot.png")

    plt.figure(clear=True)


def create_pie_chart(data, title, name):

    labels = data.index
    sizes = data.values / data.values.sum() * 100
    plt.pie(sizes, textprops = {"color":"w"})
    labels = [f"{l} - {s:0.1f}%" for l, s in zip(labels, sizes)]
    plt.legend(labels = labels, bbox_to_anchor = (1.6,1), loc = "best")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"report/{name}/plots/{title}_pie_chart.png")

    plt.figure(clear=True)


def create_stacked_bar_plot(data, title, name):
    plot = data.groupby(["releaseDate", "platformName"]).size().unstack().plot(kind = 'bar', stacked = True)
    plt.savefig(f"report/{name}/plots/{title}.png")


if __name__ == "__main__":
    main()
