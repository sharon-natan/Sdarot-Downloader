# Sdarot-Downloader

A Module that allow you to batch download from the Sdarot website.

#Steps:

1. Adding the py file to the project directory
2. Import the Sdarot-Downloader.py to your code
3. Define Sdarot object
4. Choose whatever you want to download (Episode/ Season/ Series)

and start

** Its will download to your download folder in the folder Sdarot

#Example Define Object

```

import SdarotClass

sdarot = SdarotClass.Sdarot()

```

# Example of Downloading Episode

```
ep = 'https://sdarot.today/watch/973-%D7%91%D7%A8%D7%95%D7%A7%D7%9C%D7%99%D7%9F-%D7%AA%D7%A9%D7%A2-%D7%AA%D7%A9%D7%A2-brooklyn-nine-nine/season/2/episode/1'
sdarot.download_episode(ep)

```

# Example of Downloading Rage of Episodes

```
season = 'https://sdarot.today/watch/973-%D7%91%D7%A8%D7%95%D7%A7%D7%9C%D7%99%D7%9F-%D7%AA%D7%A9%D7%A2-%D7%AA%D7%A9%D7%A2-brooklyn-nine-nine/season/2'
firstEpisode = 5
lastEpisode  = 10
sdarot.download_range_of_episodes(season, firstEpisode, lastEpisode)

```


# Example of Downloading Season

```
season = 'https://sdarot.today/watch/973-%D7%91%D7%A8%D7%95%D7%A7%D7%9C%D7%99%D7%9F-%D7%AA%D7%A9%D7%A2-%D7%AA%D7%A9%D7%A2-brooklyn-nine-nine/season/2'
sdarot.download_season(season)

```

# Example of Downloading Serise

```

series = 'https://sdarot.today/watch/973'
sdarot.download_entire_series(series)

```

