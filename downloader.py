#!/usr/bin/python
import codecs
import hashlib
import os
import re
import ssl
from urllib import request

import requests
from colorama import Fore, Style

# noinspection PyProtectedMember
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()


def GetFileMd5(filename):
    if not os.path.isfile(filename):
        return
    return hashlib.md5(open(filename, 'rb').read()).hexdigest()


def validateTitle(title):
    rstr = r"[\·\/\\\:\*\?\"\<\>\|]"
    new_title = re.sub(rstr, "_", title)
    return new_title


def id_to_url_type_dict(data_all):
    dicts = {}
    for x in data_all:
        dicts[x['id']] = (x['url'], x['type'], x['md5'])
    return dicts


def empty(*value):
    return


def status(s, n, m):
    if s == 'SUCCESS':
        print(Style.BRIGHT + '[' + Fore.GREEN + 'SUCCESS' + Style.RESET_ALL + Style.BRIGHT + ']', n,
              Fore.YELLOW + m + Style.RESET_ALL)
    if s == 'ERROR':
        print(Style.BRIGHT + '[' + Fore.RED + 'ERROR' + Style.RESET_ALL + Style.BRIGHT + ']', n,
              Fore.MAGENTA + m + Style.RESET_ALL)
    if s == 'CACHED':
        print(
            Style.BRIGHT + '[' + Fore.GREEN + 'SUCCESS' + Fore.WHITE + '][' + Fore.CYAN + 'Cached' + Fore.WHITE + ']'
            + Style.RESET_ALL, Style.DIM + n, Fore.YELLOW + m + Style.RESET_ALL)


def verbose(info):
    print(Style.BRIGHT, info, Style.RESET_ALL)


musics = {}


class Downloader:
    """Backend of The tools"""
    tmp_dir: str = 'cache/'
    api_url: str = 'https://163musicapi.star-home.top:4430'
    callback_progress_BAR = empty
    callback_progress_STATUS = empty
    callback_progress_VERBOSE = empty
    callback_progress_DETAILED = empty
    callback_start_list_info = empty
    callback_end_list_info = empty
    callback_start_download = empty
    callback_end_download = empty
    status_success: int = 0
    status_failed: int = 0
    error_info: dict = {}
    files: dict = {}
    status_success_cache: int = 0
    status_success_download: int = 0
    tracks: dict = None
    trackIds: dict = None
    status: str = ""
    is_ready = False
    playlist_info: dict = {}

    def __init__(self, tmp, api, pl):
        self.api_url = api
        self.tmp_dir = tmp
        self.playlist = pl

    def setSV(self, fuuncS, funcV):
        self.callback_progress_STATUS = fuuncS
        self.callback_progress_VERBOSE = funcV
        return self

    def fetch_api(self, add):
        self.callback_progress_VERBOSE("Fetching API:" + add[:50] + "...")
        return requests.get(self.api_url + add, verify=False).json()

    def getFilename(self, name, artist, _type, _id):
        return self.tmp_dir + validateTitle(name) + ' - ' + validateTitle(artist) + "." + str(_id) + "." + str(_type)

    def download(self, url, save):
        self.callback_progress_VERBOSE("Downloading " + str(url) + " to " + str(save))
        request.urlretrieve(str(url), str(save))
        return

    def download_loop(self):
        self.callback_start_download()
        _all = len(self.tracks)
        i = 0
        s = ""
        for ids in self.trackIds:
            s = s + "," + str(ids['id'])
        s = s[1:]
        data_all = self.fetch_api('/song/url?id=' + s)['data']
        data = id_to_url_type_dict(data_all)
        for index in range(_all):
            name = self.tracks[index]['name']
            artist = self.tracks[index]['ar'][0]['name']
            mid = self.tracks[index]['id']
            data_this = data[mid]
            is_md5 = False
            try:
                self.callback_progress_BAR(_all, i, "[MD5 SUM]" + name)
                if data_this[2] is None or not data_this[2] == GetFileMd5(
                        self.getFilename(name, artist, data_this[1], mid)):
                    self.callback_progress_BAR(_all, i, "[CHECK]" + name)
                    is_available = self.fetch_api('/check/music?id=' + str(mid))
                    if not is_available['success']:
                        self.callback_progress_STATUS('ERROR', name, is_available['message'])
                        self.error_info[mid] = (name, data_this, is_available['message'])
                        self.callback_progress_BAR(_all, i, '[ERROR]' + name)
                        self.status_failed += 1
                        musics[mid] = {
                            'status': False,
                            'name': name,
                            'msg': is_available['message']
                        }
                        self.playlist_info[index] = {
                            'status': musics[mid],
                            'author': self.tracks[index]['ar'],
                            'id': mid,
                            'name': name,
                            'album': self.tracks[index]['al'],
                        }
                        continue
                    self.callback_progress_BAR(_all, i, '[DOWNLOAD]' + name)
                    if data_this[0] is None or data_this[1] is None:
                        self.error_info[mid] = (name, data_this, 'API ERROR')
                        self.status_failed += 1
                        self.callback_progress_BAR(_all, i, '[ERROR]' + name)
                        self.callback_progress_STATUS('ERROR', name, 'API ERROR')
                        musics[mid] = {
                            'status': False,
                            'name': name,
                            'msg': 'API ERROR'
                        }
                        self.playlist_info[index] = {
                            'status': musics[mid],
                            'author': self.tracks[index]['ar'],
                            'id': mid,
                            'name': name,
                            'album': self.tracks[index]['al'],
                        }
                        continue
                    self.download(data_this[0], self.getFilename(name, artist, data_this[1], mid))
                    self.callback_progress_BAR(_all, i, '[LYRIC]' + name)
                    lyric = self.fetch_api('/lyric?id=' + str(mid))
                    f = codecs.open(self.getFilename(name, artist, 'lrc', mid), 'w', "utf-8")
                    try:
                        f.write(lyric['lrc']['lyric'])
                    except KeyError:
                        f.write("")
                    f.close()
                    self.status_success_download += 1
                else:
                    self.callback_progress_BAR(_all, i, '[MD5 PASS]' + name)
                    is_md5 = True
                    self.status_success_cache += 1
            except IOError as d:
                self.callback_progress_STATUS('ERROR', name, d.strerror)
                self.error_info[mid] = (name, data_this, d.strerror)
                self.callback_progress_BAR(_all, i, '[ERROR]' + name)
                self.status_failed += 1
                musics[mid] = {
                    'status': False,
                    'name': name,
                    'msg': d.strerror
                }
                self.playlist_info[index] = {
                    'status': musics[mid],
                    'author': self.tracks[index]['ar'],
                    'id': mid,
                    'name': name,
                    'album': self.tracks[index]['al'],
                }
            else:
                if not is_md5:
                    self.callback_progress_STATUS('SUCCESS', name, str(data_this[1]))
                else:
                    self.callback_progress_STATUS('CACHED', name, str(data_this[1]))
                musics[mid] = {
                    'status': True,
                    'name': name,
                    'type': data_this[1],
                    'file': self.getFilename(name, artist, data_this[1], mid),
                    'ly_file': self.getFilename(name, artist, 'lrc', mid),
                }
                self.playlist_info[index] = {
                    'status': musics[mid],
                    'author': self.tracks[index]['ar'],
                    'id': mid,
                    'name': name,
                    'album': self.tracks[index]['al'],
                }
                self.files[mid] = (name, data_this, musics[mid])
                self.callback_progress_BAR(_all, i, '[SUCCESS]' + name + " " + str(data_this[1]))
                self.status_success += 1
            i += 1
        self.callback_progress_VERBOSE("All " + str(_all) + "; Succeed " + str(self.status_success) + ":(Cache:" + str(
            self.status_success_cache) + ",Download:" + str(
            self.status_success_download) + "); " + "Failed " + str(
            self.status_failed) + ";")
        self.callback_progress_VERBOSE('End ' + str(self.playlist))
        self.callback_end_download()
        return {'success': self.files, 'failed': self.error_info}

    def run(self):
        self.status_success: int = 0
        self.status_failed: int = 0
        self.error_info: dict = {}
        self.files: dict = {}
        self.status_success_cache: int = 0
        self.status_success_download: int = 0
        self.tracks: dict = None
        self.trackIds: dict = None
        self.status: str = ""
        self.is_ready = False
        self.playlist_info: dict = {}
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
        self.callback_progress_VERBOSE('Processing ' + str(self.playlist))
        self.callback_start_list_info()
        self.callback_progress_VERBOSE("Getting PlayList")
        get = self.fetch_api("/playlist/detail?id=" + self.playlist)
        if get['code'] != 200:
            self.callback_progress_VERBOSE('Error ' + get['msg'])
            return {}
        get = get['playlist']
        self.callback_progress_DETAILED('playlist', get)
        self.callback_progress_VERBOSE("Getting Tracks")
        self.tracks = get['tracks']
        self.callback_progress_DETAILED('tracks', self.tracks)
        self.callback_progress_VERBOSE("All " + str(len(self.tracks)) + " musics")
        self.trackIds = get['trackIds']
        self.callback_end_list_info()
        self.callback_progress_VERBOSE("Starting download")
        return self.download_loop()
