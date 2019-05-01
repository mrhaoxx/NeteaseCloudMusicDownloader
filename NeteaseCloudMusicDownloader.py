#!/usr/bin/python
from urllib import request
from urllib import parse
from eyed3 import id3
from time import sleep
import shutil
import json
import hashlib
import os
import _thread
import time
import re
cloud_music_api = 'http://haoxx.imwork.net:3000' # 收起你对这个IP的想法
cloud_music_playlist = '510113940'
def id_to_url_type_dict(data_all):
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
    print(long_Str_setter(" ",os.get_terminal_size().columns), end="\r")
    print(("{0}% "+(now+1).__str__() + "/" + total.__str__()+ " "+msg).format(round((now + 1) * 100/ total)), end="\r")
    return
def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"
    new_title = re.sub(rstr, "_", title)
    return new_title
def getFilename(name,artist,type):       
    return 'temp/'+validateTitle(name)+' - '+validateTitle(artist)+".mp3";
def GetFileMd5(filename):
    if not os.path.isfile(filename):
        return
    myhash = hashlib.md5()
    f = open(filename,'rb')   
    while True:
        b = f.read(8096)
        if not b :
           break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()
def fetch_api(add):
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
    request.urlretrieve(url, save);
    return;

def download_loop(tracks,trackIds): 
    status_success = 0;
    status_failed = 0;
    all = len(tracks);
    errorinfo = {};
    i = 0;
    s = "";
    for ids in trackIds:
        s = s +"," + str(ids['id']);
    s = s[1:];
    data_all=resolve_json(fetch_api('/song/url?id='+s))['data'];  
    data=id_to_url_type_dict(data_all)
    for index in range(len(tracks)) :
        name=tracks[index]['name'];
        artist = tracks[index]['ar'][0]['name'];      
        adl=tracks[index]['al']['name'];
        id=tracks[index]['id'];
        data_this=data[id];
        ismd5=False;
        try:
            disbar(all,i,"[MD5 Calculating]"+name)
            if not data_this[2] == GetFileMd5(getFilename(name,artist,data_this[1])):
                disbar(all,i,'[Download]'+name)
                download(data_this[0],getFilename(name,artist,data_this[1]));
            else:
                disbar(all,i,'[MD5 PASS]'+name)
                ismd5=True;
                sleep(0.1)
            set_mp3_info(name,artist,getFilename(name,artist,data_this[1]),adl,data_this[1]);
            disbar(all,i,'[Processed]"'+name+'"')
        except:
            print(long_Str_setter(" ",os.get_terminal_size().columns), end="\r")
            print('[ERROR]'+name);
            errorinfo[id]=(name);
            disbar(all,i,'[ERROR]'+name)
            sleep(0.5)
            status_failed=status_failed+1;
            pass
        else:
            print(long_Str_setter(" ",os.get_terminal_size().columns), end="\r")
            if not ismd5:
                print('[SUCCESS]'+name);
            else:
                print('[SUCCESS][Cached]'+name);
            disbar(all,i,'[SUCCESS]'+name)
            status_success=status_success+1;
        i=i+1;
    print();
    print(long_Str_setter("-",os.get_terminal_size().columns))
    print("All " + str(all) + "; Succeed " + str(status_success) + "; Failed "+ str(status_failed))
    if not status_failed == 0:
        print("Error Music:",errorinfo);
    return;
def set_mp3_info(name,artist,file,adl,type): 
    shutil.copy(file,"music/")
    tag = id3.Tag()
    tag.parse("music/"+validateTitle(name)+' - '+validateTitle(artist)+"."+type);    
    tag.artist = artist;        
    tag.title = name;
    tag.album=adl;   
    tag.save(encoding='utf-8');
    return;
def main():
    get = get_playlist(cloud_music_playlist);
    tracks = get_tracks_info(get);
    list = "";
    print("All " + str(len(tracks)) + " musics" )    
    tracksIds = get_tracks_ids(get);
    print(long_Str_setter("-",os.get_terminal_size().columns))
    download_loop(tracks,tracksIds);
    print(long_Str_setter("-",os.get_terminal_size().columns))
    return;

if not os.path.exists('temp'):
    os.mkdir('temp')
if not os.path.exists('music'):
    os.mkdir('music')
print(long_Str_setter("-",os.get_terminal_size().columns))
print("    NeteaseCloudMusic Downloader     ")
print("               Powered by haoxingxing")
print(long_Str_setter("-",os.get_terminal_size().columns))
print("Api:" + cloud_music_api)
print("PlayListId:" + cloud_music_playlist.__str__())
print(long_Str_setter("-",os.get_terminal_size().columns))
main();