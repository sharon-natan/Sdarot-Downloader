import requests
from time import sleep
import re
import json
from sys import exit, stderr, stdout
import os
from bs4 import BeautifulSoup

__all__ = ['VERSION', 'SECONDS_TO_WAIT', 'SAVE_LOCATION', 'TIME_TO_WAIT']

VERSION = "1.0.0"
SECONDS_TO_WAIT = 30
SAVE_LOCATION = '%USERPROFILE%\\Downloads\\Sdarot\\'
TIME_TO_WAIT = 20 # Default 20 seconds


####
class Sdarot:

    def __get_title(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        for line in soup.find_all('h1'):
            if line.strong is not None:
                title = line.strong.text
        title = title.split('/')
        for name in title:
            while name[0] == " ":
                name = name[1:]
            while name[-1] == " ":
                name = name[:-1]
            if self.__isEnglish(name):
                title = name
                replace_all = '?:*<>|'
                for char in replace_all:
                    title = title.replace(char, ' ')
                return title
        print("Could not find a title for the series")
        exit()

    def __isEnglish(self, word):
        try:
            word.encode(encoding='utf-8').decode('ascii')
        except UnicodeDecodeError:
            return False
        else:
            return True

    def __banner(self):
        print("SdarotModule Version {0}".format(VERSION))
        print()

    def __getEpisodesList(self, url_of_season):
        list_of_episodes = []
        r = requests.get(url_of_season)
        origin = "https://" + url_of_season.split("/")[2]
        soup = BeautifulSoup(r.content, 'html.parser')
        for line in soup.find_all('a'):
            if "/watch/" in line.get('href') and "/episode/" in line.get('href'):
                episode = origin + line.get('href')
                episode = episode.encode("ascii", "ignore").decode('utf-8')
                list_of_episodes.append(episode)
        return list_of_episodes

    def __isInEpisodeList(self, episode_list, episode_number):
        for episodeLink in episode_list:
            if "/episode/" + str(episode_number) in episodeLink:
                return True
        return False

    def __get_url_info(self, url):
        # Getting Origin from url
        origin = re.search('^((http[s]?):\/)?\/?([\w.-]+)', url).group(0)
        origin = origin.lower()
        url_info = {
            'origin': origin
        }
        # Making Form Data Infromation
        season = url.split('/')[6]
        episode = url.split('/')[8]
        sid = url.split('/')[4].split('-')[0]
        url_info['season'] = season
        url_info['episode'] = episode
        url_info['SID'] = sid
        url_info['url'] = url
        url_info['title'] = self.__get_title(url)
        season = int(season)
        episode = int(episode)
        url_info['file_name'] = "s{season:02d}_e{episode:02d}.mp4".format(season=season, episode=episode)
        return url_info

    def __create_folder_path(self, url_info):
        variable = SAVE_LOCATION.split('%')
        folder = os.getenv(variable[1])
        path = folder + variable[2]  + url_info['title']
        return path

    def __get_token(self, url_info):
        dataForm = {
            'preWatch': True,
            'SID': url_info['SID'],
            'season': url_info['season'],
            'episode': url_info['episode']
        }
        header = {
            'DNT': '1',
            'accept-language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': url_info['origin'],
            'referer': url_info['url'],
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",  # be IE 11.0
        }

        r = requests.post("{}/ajax/watch".format(url_info['origin']), data=dataForm, headers=header)

        if r.status_code == 200:
            # save response cookies (needed to procceed download)
            url_info['cookies'] = r.cookies
            return r.text
        else:
            return False

    def __get_download_url_data(self, url_info):
        dataForm = {
            'watch': True,
            'token': url_info['token'],
            'serie': url_info['SID'],
            'season': url_info['season'],
            'episode': url_info['episode'],
            'type': 'episode'
        }

        header1 = {
            'DNT': '1',
            'accept': '*/*',
            'accept-language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': url_info['origin'],
            'referer': url_info['url'],
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",  # be IE 11.0
        }

        header2 = {
            'DNT': '1',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': url_info['origin'],
            'referer': url_info['url'],
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",  # be IE 11.0
        }

        dataformWatch1 = {
            'vast': True
        }

        # Second and Third Watch POST Requests --- Third is important

        requests.post("{}/ajax/watch".format(url_info['origin']), data=dataformWatch1, headers=header1,
                      cookies=url_info['cookies'])
        watch2 = requests.post("{}/ajax/watch".format(url_info['origin']), data=dataForm, headers=header2,
                               cookies=url_info['cookies'])
        if watch2.status_code == 200:
            return json.loads(watch2.content)
        else:
            return False

    def __create_download_link(self, episode_data, url_info):
        key_of_watch = list(episode_data['watch'])[0]
        requestURL = 'https:' + episode_data['watch'][key_of_watch]
        episode_data['host'] = re.search('^((http[s]?):\/)?\/?([\w.-]+)', requestURL).group(0).split('https://')[-1]
        headers = {
            'DNT': '1',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'identity;q=1, *;q=0',
            'accept-language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Host': episode_data['host'],
            'Range': 'bytes=0-',
            'Referer': url_info['url'],
            'Sec-Fetch-Dest': 'video',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",  # be IE 11.0
        }
        data_form = {
            'token': episode_data['watch'][key_of_watch].split('?token=')[-1].split('&time=')[0],
            'time': episode_data['watch'][key_of_watch].split('?token=')[-1].split('&time=')[-1].split('&uid=')[0],
            'uid': episode_data['watch'][key_of_watch].split('?token=')[-1].split('&time=')[-1].split('&uid=')[-1]
        }
        try:

            linkRequest = requests.get(requestURL, headers=headers, params=data_form, cookies=url_info['cookies'], allow_redirects=True)
            path = self.__create_folder_path(url_info)
            filename = path + '\\' + url_info['file_name']
            open(filename, 'wb').write(linkRequest.content)
        except:
            stdout.write('Failed to generate a download link, try again now... ')
            self.download_episode(url_info['url'])


    def download_episode(self, url):
        self.__banner()
        url_info = self.__get_url_info(url)
        url_info['token'] = self.__get_token(url_info)
        if not url_info['token']:
            stderr.write('[!] Can\'t get token\n')
            stderr.flush()
            exit(2)

        for i in range(SECONDS_TO_WAIT):
            stdout.write('\r[*] Waiting {seconds} seconds... '.format(seconds=SECONDS_TO_WAIT - i - 1))
            stdout.flush()
            sleep(1)
        stdout.write('Done!\n')
        stdout.flush()
        stdout.write('[*] Retrieving download data... \n')
        stdout.flush()
        episode_data = self.__get_download_url_data(url_info)
        keys = list(episode_data.keys())
        if keys[0] == "error":
            stdout.write('[!] There is load on the servers, you will need to wait {0} seconds.\n'.format(TIME_TO_WAIT))
            for i in range(TIME_TO_WAIT):
                stdout.write('\r[*] Waiting {seconds} seconds... '.format(seconds=TIME_TO_WAIT - i - 1))
                stdout.flush()
                sleep(1)
            stdout.write('Done!\n\n')
            stdout.flush()
            self.download_episode(url)
        else:
            if not episode_data:
                stderr.write('[!] Can\'t get download data\n')
                stderr.flush()
                exit(3)

            #Check if download directory exist
            stdout.write("[*] Checking if the save's location is exist... \n")
            path = self.__create_folder_path(url_info)
            print(path)
            if not os.path.isdir(path):
                os.makedirs(path)
                stdout.write("[*] The Directory was created. \n")
            else:
                stdout.write("[*] Directory was existed\n")
            stdout.flush()

            file = path + '\\' + url_info['file_name']
            stdout.write('Downloading now the file {path}\n'.format(path=file))
            self.__create_download_link(episode_data, url_info)

    def download_season(self, url_of_season):
        list_of_episodes = self.__getEpisodesList(url_of_season)
        for episode_url in list_of_episodes:
            url_info = self.__get_url_info(episode_url)
            print("\033[32mDownloading Season {season} Episode {episode}".format(season=url_info['season'], episode=url_info['episode']))
            self.download_episode(episode_url)
            print("\033[32mFinished download Season {season} Episode {episode}\n".format(season=url_info['season'], episode=url_info['episode']))



    def download_range_of_episodes(self, url_of_season, startEpisode, endEpisode):
        if startEpisode > endEpisode:
            print("The start number is bigger then the end number. ")
            exit()
        list_of_episodes = self.__getEpisodesList(url_of_season)
        not_in_list = []
        for episode in range(startEpisode, endEpisode+1):
            if not self.__isInEpisodeList(list_of_episodes, episode):
                not_in_list.append(episode)
        if len(not_in_list) > 0:
            print("There are some episodes that are not in the episode list of the season. The episodes are: \n")
            print(not_in_list)
        else:
            for episode in range(startEpisode, endEpisode+1):
                for episodeLink in list_of_episodes:
                    if "/episode/" + str(episode) in episodeLink:
                        url_info = self.__get_url_info(episodeLink)
                        print("\033[32m Downloading Season {season} Episode {episode}".format(season=url_info['season'], episode=url_info['episode']))
                        self.download_episode(episodeLink)
                        print("\033[32m Finished download Season {season} Episode {episode}".format(season=url_info['season'], episode=url_info['episode']))

    def download_entire_series(self, url_of_series):
        list_of_seasons = []
        r = requests.get(url_of_series)
        origin = "https://" + url_of_series.split("/")[2]
        soup = BeautifulSoup(r.content, 'html.parser')
        for line in soup.find_all('a'):
            if "/season/" in line.get('href') and "/episode/" not in line.get('href'):
                season = origin + line.get('href')
                season = season.encode("ascii", "ignore").decode('utf-8')
                list_of_seasons.append(season)
        for seasonURL in list_of_seasons:
            self.download_season(seasonURL)


def main():
    return None

if __name__ == '__main__':
    main()
