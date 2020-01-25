#!/usr/bin/python
from urllib import parse
from urllib import request
from urllib import error
from eyed3 import id3
from time import sleep
import shutil
import requests
import json
import hashlib
import os
import time
import re
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()
# Config
# Api
cloud_music_api = 'https://163musicapi.star-home.top:4430'
cloud_music_playlist = '510113940'
# Dir
dir_temp="temp/"
dir_end="music/"
Enable_ORDER = True
Clean_Music_Dir = True
# Log
islog = True
isverbose = False
isJunkInfo = False

import colorama
from colorama import Fore, Style
isverbose = islog and isverbose
isJunkinfo = isJunkInfo and isverbose
def id_to_url_type_dict(data_all):
    dict = {}
    for x in data_all:
        dict[x['id']] = (x['url'],x['type'],x['md5'])
    return dict
def long_Str_setter(delim,long):
    a = 1
    b = ""
    while a < long:
        a = a+1
        b = b + delim
    return b
def disbar(total,now,msg):   
    if not islog:
        return
    print(long_Str_setter(" ",os.get_terminal_size().columns), end="\r")
    print((" {0}% "+(now+1).__str__() + "/" + total.__str__()+ " "+msg).format(round((now + 1) * 100/ total)), end="\r")
    return
def validateTitle(title):
    rstr = r"[\·\/\\\:\*\?\"\<\>\|]"
    new_title = re.sub(rstr, "_", title)
    return new_title
def getFilename(name,artist,typea,id):       
    return dir_temp +validateTitle(name)+' - '+validateTitle(artist)+"."+str(id)+"." + str(typea)
def GetFileMd5(filename):
    if not os.path.isfile(filename):
        return
    try:
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
    except:
        return str(0)
def fetch_api(add):
    if isverbose:
        print("Fetching API:" + add[:25] + "...")
    f = requests.get(cloud_music_api + add,verify=False)
    return f.json()
def resolve_json(str):
    #return json.loads(str)
    return str
def download(url,save):
    if isverbose:
        print("Downloaded " + url +" to " + save)
    request.urlretrieve(url, save)
    return

def download_loop(tracks,trackIds): 
    files = {}
    if islog:
        status_success = 0
        status_failed = 0
        errorinfo = {}
        status_success_cache = 0
        status_success_download = 0
    all = len(tracks)
    i = 0
    s = ""
    for ids in trackIds:
        s = s +"," + str(ids['id'])
    s = s[1:]
    data_all=resolve_json(fetch_api('/song/url?id='+s))['data']
    data=id_to_url_type_dict(data_all)
    for index in range(len(tracks)) :
        name=tracks[index]['name']
        artist = tracks[index]['ar'][0]['name']      
        adl=tracks[index]['al']['name']
        id=tracks[index]['id']
        data_this=data[id]
        ismd5=False
        try:
            disbar(all,i,"[MD5 SUM]"+name)
            if data_this[2] == None or not data_this[2] == GetFileMd5(getFilename(name,artist,data_this[1],id)):
                disbar(all,i,"[CHECK]"+name)
                isavaible=resolve_json(fetch_api('/check/music?id='+str(id)))
                if not isavaible['success']:
                    print(long_Str_setter(" ",os.get_terminal_size().columns), end="\r")
                    print(Style.BRIGHT+'['+Fore.RED + 'ERROR'+Style.RESET_ALL+Style.BRIGHT+']'+name+' ' + isavaible['message'])
                    errorinfo[id]=(name,data_this,isavaible['message'])
                    disbar(all,i,'[ERROR]'+name)
                    status_failed=status_failed+1
                    continue
                disbar(all,i,'[DOWNLOAD]'+name)
                download(data_this[0],getFilename(name,artist,data_this[1],id))
                status_success_download += 1
            else:
                disbar(all,i,'[MD5 PASS]'+name)
                ismd5=True
                status_success_cache += 1
            set_mp3_info(name,artist,getFilename(name,artist,data_this[1],id),adl,data_this[1],all,i,id,index)
        except IOError as d :
            if islog:
                print(long_Str_setter(" ",os.get_terminal_size().columns), end="\r")
                print(Style.BRIGHT+'['+Fore.RED + 'ERROR'+Style.RESET_ALL+Style.BRIGHT+']'+name)
                errorinfo[id]=(name,data_this,d.strerror)
                disbar(all,i,Style.BRIGHT+Fore.RED +'[ERROR]'+name+Style.RESET_ALL)
                status_failed=status_failed+1
        else:
            print(long_Str_setter(" ",os.get_terminal_size().columns), end="\r")
            if not ismd5:
                if islog:
                    print(Style.BRIGHT+'['+Fore.GREEN+'SUCCESS'+Fore.WHITE+']'+name +" "+Fore.YELLOW+str(data_this[1])+Style.RESET_ALL)
            else:
                if islog:
                    print(Style.BRIGHT+'['+Fore.GREEN+'SUCCESS'+Fore.WHITE+']['+Fore.CYAN+'Cached'+Fore.WHITE+']'+Style.RESET_ALL+Style.DIM+name+" "+Fore.YELLOW+str(data_this[1])+Style.RESET_ALL)
            disbar(all,i,'[SUCCESS]'+name+" "+str(data_this[1]))
            files[id]=(name,data_this,dir_end+validateTitle(name)+' - '+validateTitle(artist)+"."+str(data_this[1]))                   
            if islog:
                status_success=status_success+1
        i=i+1
    print(long_Str_setter(" ",os.get_terminal_size().columns), end="\r")
    if islog:
        print(Style.BRIGHT+long_Str_setter("-",os.get_terminal_size().columns))
        print("All " + str(all) + "; "+Fore.GREEN+"Succeed " + str(status_success) +Fore.WHITE+":("+Fore.CYAN+"Cache:"+str(status_success_cache)+Fore.WHITE+","+Fore.GREEN+"Download:"+str(status_success_download) +Fore.WHITE +"); "+Fore.RED+"Failed "+ str(status_failed)+";"+Fore.WHITE)
        if not status_failed == 0:
            print("Error:",Fore.RED,errorinfo,Fore.WHITE)
        if isverbose:
            print("Success:",Fore.GREEN,str(files),Fore.WHITE)
        else:
            print("Success:",Fore.GREEN,str(files)[:25],"....",Fore.WHITE)
    return
def set_mp3_info(name,artist,file,adl,type,all,i,id,index): 
    if isJunkInfo:
        disbar(1,0,"Setting up mp3 info")
        print()
    disbar(all,i,'[COPY]'+name)
    if Enable_ORDER:
        shutil.copy(file,dir_end+str(index)+"-"+validateTitle(name)+' - '+validateTitle(artist)+"."+str(id)+"."+type)
    else:
        shutil.copy(file,dir_end+validateTitle(name)+' - '+validateTitle(artist)+"."+str(id)+"."+type)
    tag = id3.Tag()
    if Enable_ORDER:
        tag.parse(dir_end+str(index)+"-"+validateTitle(name)+' - '+validateTitle(artist)+"."+str(id)+"."+type)
    else:
        tag.parse(dir_end+validateTitle(name)+' - '+validateTitle(artist)+"."+str(id)+"."+type)        
    tag.artist = artist        
    tag.title = name
    tag.album=adl   
    tag.save(encoding='utf-8')
    return

def main():
    if islog:
        print(Style.BRIGHT+"Getting PlayList",end=' ')
    get = resolve_json(fetch_api("/playlist/detail?id="+cloud_music_playlist))['playlist']
    if islog:
        if not isverbose:
            print(str(get)[:50],"...")
        else:
            print(str(get))
    if islog:
        print("Getting Tracks",end=' ')
    tracks = get['tracks']
    if islog:
        if not isverbose:
            print(str(tracks)[:50],"...")
        else:
            print(str(tracks))
    if islog:
        print("All " + str(len(tracks)) + " musics" )    
    tracksIds = get['trackIds']
    if islog:
        print(Style.BRIGHT+long_Str_setter("-",os.get_terminal_size().columns))
        print("Starting download"+Style.RESET_ALL)
    download_loop(tracks,tracksIds)
    if islog:
        print(Style.BRIGHT+long_Str_setter("-",os.get_terminal_size().columns)+Style.RESET_ALL)
    return

if isverbose:
    disbar(5,0,"Lauching")
    print()
if Clean_Music_Dir:
    shutil.rmtree(dir_end)
if not os.path.exists(dir_temp):
    os.mkdir(dir_temp)
if not os.path.exists(dir_end):
    os.mkdir(dir_end)
if islog:
    print(Style.BRIGHT+long_Str_setter("-",os.get_terminal_size().columns))
    print("    NeteaseCloudMusic Downloader     ")
    print("               Powered by haoxingxing")
    print(Style.BRIGHT+long_Str_setter("-",os.get_terminal_size().columns))
    print(Fore.CYAN+"Api:" + cloud_music_api+Fore.WHITE)
    print(Fore.YELLOW+"PlayListId:" + cloud_music_playlist.__str__()+Fore.WHITE)
    print(Style.BRIGHT+long_Str_setter("-",os.get_terminal_size().columns)+Style.RESET_ALL)
main()
