#!/usr/bin/python
import hashlib
import os
import re
# from eyeD3 import id3
import shutil
import ssl
from urllib import request

import requests

# noinspection PyProtectedMember
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()


def GetFileMd5(filename):
    if not os.path.isfile(filename):
        return
    myhash = hashlib.md5()
    f = open(filename, 'rb')
    while True:
        b = f.read(8096)
        if not b:
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()


def validateTitle(title):
    rstr = r"[\·\/\\\:\*\?\"\<\>\|]"
    new_title = re.sub(rstr, "_", title)
    return new_title


def id_to_url_type_dict(data_all):
    dicts = {}
    for x in data_all:
        dicts[x['id']] = (x['url'], x['type'], x['md5'])
    return dicts


class Downloader:
    """Backend of The tools"""
    tmp_dir: str = 'tmp/'
    end_dir: str = 'music/'
    api_url: str = 'https://163musicapi.star-home.top:4430'
    is_order: bool = True
    playlist: str = '510113940'
    callback_progress_BAR = None
    callback_progress_STATUS = None
    callback_progress_VERBOSE = None
    callback_progress_DETAILED = None
    callback_start_list_info = None
    callback_end_list_info = None
    callback_start_download = None
    callback_end_download = None
    status_success: int = 0
    status_failed: int = 0
    error_info: dict = {}
    files: dict = {}
    status_success_cache: int = 0
    status_success_download: int = 0
    tracks: dict = None
    trackIds: dict = None

    def __init__(self, tmp, end, api, iso, pl):
        self.api_url = api
        self.tmp_dir = tmp
        self.end_dir = end
        self.is_order = iso
        self.playlist = pl
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)
        if not os.path.exists(self.end_dir):
            os.mkdir(self.end_dir)

    def setCallBackProgressFunction(self, funcBAR, funcVERBOSE, funcSTATUS, funcDETAILED):
        self.callback_progress_BAR = funcBAR
        self.callback_progress_VERBOSE = funcVERBOSE
        self.callback_progress_STATUS = funcSTATUS
        self.callback_progress_DETAILED = funcDETAILED
        return self

    def setCallBackStatusFunction(self, funcSTARTINFO, funcENDINFO, funcSTARTDOWNLOAD, funcENDDOWNLOAD):
        self.callback_start_download = funcSTARTDOWNLOAD
        self.callback_end_download = funcENDDOWNLOAD
        self.callback_start_list_info = funcSTARTINFO
        self.callback_end_list_info = funcENDINFO
        return self

    def fetch_api(self, add):
        self.callback_progress_VERBOSE("Fetching API:" + add[:50] + "...")
        return requests.get(self.api_url + add, verify=False).json()

    def getFilename(self, name, artist, _type, _id):
        return self.tmp_dir + validateTitle(name) + ' - ' + validateTitle(artist) + "." + str(_id) + "." + str(_type)

    def download(self, url, save):
        self.callback_progress_VERBOSE("Downloading" + str(url) + " to " + str(save))
        request.urlretrieve(str(url), str(save))
        return

    def clear_dir(self):
        shutil.rmtree(self.end_dir)

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
            adl = self.tracks[index]['al']['name']
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
                        continue
                    self.callback_progress_BAR(_all, i, '[DOWNLOAD]' + name)
                    if data_this[0] is None or data_this[1] is None:
                        self.error_info[mid] = (name, data_this, 'API ERROR')
                        self.status_failed += 1
                        self.callback_progress_BAR(_all, i, '[ERROR]' + name)
                        self.callback_progress_STATUS('ERROR', name, 'API ERROR')
                        continue
                    self.download(data_this[0], self.getFilename(name, artist, data_this[1], mid))
                    self.status_success_download += 1
                else:
                    self.callback_progress_BAR(_all, i, '[MD5 PASS]' + name)
                    is_md5 = True
                    self.status_success_cache += 1
                self.set_mp3_info(name, artist, self.getFilename(name, artist, data_this[1], mid), adl, data_this[1],
                                  _all,
                                  i,
                                  mid,
                                  index)
            except IOError as d:
                self.callback_progress_STATUS('ERROR', name, d.strerror)
                self.error_info[mid] = (name, data_this, d.strerror)
                self.callback_progress_BAR(_all, i, '[ERROR]' + name)
                self.status_failed += 1
            else:
                if not is_md5:
                    self.callback_progress_STATUS('SUCCESS', name, str(data_this[1]))
                else:
                    self.callback_progress_STATUS('CACHED', name, str(data_this[1]))
                self.callback_progress_BAR(_all, i, '[SUCCESS]' + name + " " + str(data_this[1]))
                if self.is_order:
                    self.files[mid] = (name, data_this,
                                       self.end_dir + str(index + 1) + "-" + validateTitle(
                                           name) + ' - ' + validateTitle(artist) + "." + str(
                                           data_this[1]))
                else:
                    self.files[mid] = (name, data_this,
                                       self.end_dir + validateTitle(name) + ' - ' + validateTitle(artist) + "." + str(
                                           data_this[1]))
                self.status_success += 1
            i += 1
        self.callback_progress_VERBOSE("All " + str(_all) + "; Succeed " + str(self.status_success) + ":(Cache:" + str(
            self.status_success_cache) + ",Download:" + str(
            self.status_success_download) + "); " + "Failed " + str(
            self.status_failed) + ";")
        self.callback_progress_VERBOSE('End ' + str(self.playlist))
        self.callback_end_download()
        return {'success': self.files, 'failed': self.error_info}

    # noinspection PyUnusedLocal
    def set_mp3_info(self, name, artist, file, adl, music_type, all_musics, i, music_id, index):
        self.callback_progress_BAR(all_musics, i, '[COPY]' + name)
        if self.is_order:
            shutil.copy(file,
                        self.end_dir + str(index + 1) + "-" + validateTitle(name) + ' - ' + validateTitle(
                            artist) + "." +
                        str(music_id) + "." + music_type)
        else:
            shutil.copy(file,
                        self.end_dir + validateTitle(name) + ' - ' + validateTitle(artist) + "." + str(music_id) + "."
                        + music_type)
        # tag = id3.Tag()
        # if self.is_order:
        #     tag.parse(self.end_dir + str(index+1) + "-" + validateTitle(name) + ' - ' + validateTitle(artist)
        #               + "." + str(music_id) + "." + music_type)
        # else:
        #     tag.parse(self.end_dir + validateTitle(name) + ' - ' + validateTitle(artist) + "." + str(music_id) +
        #               "." + music_type)
        # tag.artist = artist
        # tag.title = name
        # tag.album = adl
        # tag.save(encoding='utf-8')
        return

    def run(self):
        self.callback_progress_VERBOSE('Processing ' + str(self.playlist))
        self.callback_start_list_info()
        self.callback_progress_VERBOSE("Getting PlayList")
        get = self.fetch_api("/playlist/detail?id=" + self.playlist)
        if get['code'] is not 200:
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
