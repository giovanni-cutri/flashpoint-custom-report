# flashpoint-custom-report
Get a detailed report on the Flashpoint games included in a playlist or for those that you have played.

The custom report consists in data in CSV format, bar plots and pie charts about developers, publishers, genres, platforms, release dates and playtime or the games.

## Dependencies

All the necessary libraries are listed in the *requirements.txt* file.

You can install them by running:

```
pip install -r requirements.txt
```

## Usage

- Run *main.py* with at least one of the following arguments:

```
-pl [PLAYLIST], --playlist [PLAYLIST]         the filename of the playlist with the games you want a report about
-pt, --playtime                               get the report about all the games you have played in Flashpoint
```

- You will need to provide the *flashpoint.sqlite* file by copying it inside the directory where the script is located.
    - You can find the said file inside the *Data* folder in your Flashpoint local copy.
- If you choose the report for the games of a playlist, you will need to provide the playlist file by copying it inside the directory where the script is located.
    - You can export the playlist file from Flashpoint itself.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/giovanni-cutri/flashpoint-custom-report/blob/main/LICENSE) file for details.
