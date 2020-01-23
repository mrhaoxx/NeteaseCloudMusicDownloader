#!/usr/bin/python
from urllib import request
from urllib import parse
import urllib.error
from eyed3 import id3
from time import sleep
import ffmpeg
import shutil
import json
import hashlib
import os
import time
import re
# Config
# Api
cloud_music_api = 'http://star-home.top:8000/proxy/glype/browse.php?f=norefer&b=108&u=http%3A%2F%2F163musicapi'
cloud_music_playlist = '510113940'
# Dir
dir_temp="temp/"
dir_end="music/"
# Single File (Merge All Music)
# To be continue ( Mostly not if not neccessary
isgenerateonefile=True
isonefileRandom=True
signalfile="all.mp3"
# Log
islog = True
isverbose = True
isJunkInfo = False


isverbose = islog and isverbose
isJunkinfo = isJunkInfo and isverbose
def id_to_url_type_dict(data_all):
    if isJunkinfo:
        disbar(1,0,"Coventing dict")
    dict = {}
    for x in data_all:
        dict[x['id']] = (x['url'],x['type'],x['md5'])
    return dict
def long_Str_setter(delim,long):
    a = 1;
    b = ""
    while a < long:
        a = a+1;
        b = b + delim
    return b;
def disbar(total,now,msg):   
    if not islog:
        return;    
    print(long_Str_setter(" ",os.get_terminal_size().columns), end="\r")
    print(("{0}% "+(now+1).__str__() + "/" + total.__str__()+ " "+msg).format(round((now + 1) * 100/ total)), end="\r")
    return
def validateTitle(title):
    if isJunkinfo:
        disbar(2,0,"Validating Title")
        print()
    rstr = r"[\·\/\\\:\*\?\"\<\>\|]"
    new_title = re.sub(rstr, "_", title)
    if isJunkinfo:
        disbar(2,1,"Validating Title")
        print()
    return new_title
def getFilename(name,artist,typea):       
    return dir_temp +validateTitle(name)+' - '+validateTitle(artist)+"." + typea;
def GetFileMd5(filename):
    if not os.path.isfile(filename):
        return
    if isverbose:
        a = os.path.getsize(filename)
        n = 0
    myhash = hashlib.md5()
    f = open(filename,'rb')   
    while True:
        b = f.read(8096)
        if isverbose:
            n = n+8096
            disbar(a,n,"[MD5] Calculating")
        if not b :
           break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()
def fetch_api(add):
    if isverbose:
        print("Fetching API:" + add[:25] + " ...")
    f = request.urlopen(cloud_music_api + add);
    
    return f.read().decode('utf-8');
def resolve_json(str):
    return json.loads(str);
def get_playlist(playlist):
    return resolve_json(fetch_api("/playlist/detail?id="+playlist))['playlist'];
def get_tracks_info(plerlist):
    return plerlist['tracks'];
def get_tracks_ids(plerlist):
    return plerlist['trackIds'];
def download(url,save):
    if isverbose:
        print("Downloaded " + url +" to " + save)
    request.urlretrieve(url, save);
    return;

def download_loop(tracks,trackIds): 
    files = {}
    if islog:
        status_success = 0;
        status_failed = 0;
        errorinfo = {};
    all = len(tracks);
    i = 0;
    s = "";
    for ids in trackIds:
        s = s +"," + str(ids['id']);
    s = s[1:];
    data_all=resolve_json(fetch_api('/song/url?id='+s))['data'];  
    data=id_to_url_type_dict(data_all)
    for index in range(len(tracks)) :
        name=tracks[index]['name']
        artist = tracks[index]['ar'][0]['name']      
        adl=tracks[index]['al']['name']
        id=tracks[index]['id']
        isavaible=resolve_json(fetch_api('/check/music?id='+str(id)))
        data_this=data[id]
        ismd5=False
        if( not isavaible['success']):
            print(isavaible['message'])
            pass
        try:
            disbar(all,i,"[MD5]"+name)
            if not data_this[2] == GetFileMd5(getFilename(name,artist,data_this[1])):
                disbar(all,i,'[Download]'+name)
                download(data_this[0],getFilename(name,artist,data_this[1]));
            else:
                disbar(all,i,'[MD5 PASS]'+name)
                ismd5=True;
                if islog:
                    sleep(0.1)
            set_mp3_info(name,artist,getFilename(name,artist,data_this[1]),adl,data_this[1],all,i);
            disbar(all,i,'[Processed]"'+name+'"')
        except IOError as d :
            print(d.strerror)
            if islog:
                print(long_Str_setter(" ",os.get_terminal_size().columns), end="\r")
                print('[ERROR]'+name);
                errorinfo[id]=(name);
                disbar(all,i,'[ERROR]'+name)
                status_failed=status_failed+1;
        except urllib.error.HTTPError as e:  # 此时是HTTPError
            print(e.code)
        else:
            print(long_Str_setter(" ",os.get_terminal_size().columns), end="\r")
            if not ismd5:
                if islog:
                    print('[SUCCESS]'+name);
            else:
                if islog:
                    print('[SUCCESS][Cached]'+name);
            disbar(all,i,'[SUCCESS]'+name)
            files[len(files)]=dir_end+validateTitle(name)+' - '+validateTitle(artist)+".mp3";                   
            if islog:
                status_success=status_success+1;
        i=i+1;
    if islog:
        print();
        print(long_Str_setter("-",os.get_terminal_size().columns))
        print("All " + str(all) + "; Succeed " + str(status_success) + "; Failed "+ str(status_failed))
        if not status_failed == 0:
            print("Error Music:",errorinfo);
    #mergemp3s(files)
    return;
def set_mp3_info(name,artist,file,adl,type,all,i): 
    if isJunkInfo:
        disbar(1,0,"Setting up mp3 info")
        print()
    disbar(all,i,'[Copying]'+name)
    shutil.copy(file,dir_end)
    tag = id3.Tag()
    tag.parse(dir_end+validateTitle(name)+' - '+validateTitle(artist)+"."+type);    
    tag.artist = artist;        
    tag.title = name;
    tag.album=adl;   
    tag.save(encoding='utf-8');
    return;
def mergemp3s(files):
    #ffmpeg -i "concat:${files:1}" -loglevel panic -c:a copy -c:v copy -f s16le -ar 22.05k -ac 1 ${MusicDir}/all.wav
    streamlist={}
    for path in files:
        streamlist[len(streamlist)]=ffmpeg.input(path);
    ffmpeg.concat(ffmpeg.input(files[0]),ffmpeg.input(files[1])).output("test.wav").run();
    print(t);
    return
def main():
    if isverbose:
        disbar(5,1,"Getting PlayList")
        print()
    get = get_playlist(cloud_music_playlist);
    if isverbose:
        disbar(5,2,"Getting Tracks")
        print()
    tracks = get_tracks_info(get);
    list = "";
    if islog:
        print("All " + str(len(tracks)) + " musics" )    
    if isverbose:
        disbar(5,2,"Getting TrackIds")
        print()
    tracksIds = get_tracks_ids(get);
    if islog:
        print(long_Str_setter("-",os.get_terminal_size().columns))
    if isverbose:
        disbar(5,3,"Starting download")
        print()
    download_loop(tracks,tracksIds);
    if islog:
        print(long_Str_setter("-",os.get_terminal_size().columns))
    if isverbose:
        disbar(5,4,"Done")
        print()
    return;

if isverbose:
    disbar(5,0,"Lauching")
    print()
if not os.path.exists(dir_temp):
    os.mkdir(dir_temp)
if not os.path.exists(dir_end):
    os.mkdir(dir_end)
if islog:
    print(long_Str_setter("-",os.get_terminal_size().columns))
    print("    NeteaseCloudMusic Downloader     ")
    print("               Powered by haoxingxing")
    print(long_Str_setter("-",os.get_terminal_size().columns))
    print("Api:" + cloud_music_api)
    print("PlayListId:" + cloud_music_playlist.__str__())
    print(long_Str_setter("-",os.get_terminal_size().columns))
main();
