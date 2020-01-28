# APIs

## Playlist

#### /api/v1/playlist

*TO CREATE A PLAYLIST*

- **POST**
- {
  - name: string
- }

- **RETURN**
- {
  - code: int {200,400} *status
  - msg: string         *readable status string
  - id: string(if 200)  *the id of playlist
- }

return example  
```json
{
  "code": 200,
  "id": "3",
  "msg": "Successfully added",
  "name": "Test"
}
```

#### /api/v1/playlist/<playlist_id:int>
*TO GET DETAIL OF A PLAYLIST*

- **GET**
- **RETURN**
- {
  - code: int {200,404} *status
  - msg: string(if 404)         *readable status string
  - data: json(if 200)  *the playlist
- }

- data{
  - id: int *id of playlist
  - musics: json *musics
  - name: string *name of playlist
- }

- musics{
  - key>*id of music*
  - value> *music info*
- }

return example
```json  
{
  "code": 200,
  "data": {
    "id": 1,
    "musics": {
    "0":{
        "163id": 31680125,
        "album": {
          "name": "飛鳥ものがたり"
        },
        "author": [
          {
            "name": "天地雅楽"
          }
        ],
        "id": 0,
        "name": "飛鳥ものがたり",
        "status": true,
        "type": "mp3"
    },
    "name": "Test"
  }
}
```

#### /api/v1/playlist/<playlist_id:int>/add
*ADD MUSIC TO PLAYLIST*

- **POST**
- JSON{id:int}

#### /api/v1/playlist/<playlist_id:int>/remove
*REMOVE MUSIC FROM PLAYLIST*

- **POST**
- JSON{id:int}


## MUSIC
#### /api/v1/music/upload
*UPLOAD A MUSIC*

- **POST FORM FILE+JSON**
- FILE: **FILE** file_audio
- FILE: **FILE** file_ly
- JSON: **FORM DATA** info

info example:
```json
{
    "name":"TestSONGNAME",
    "type":"flacSONGTYPE",
    "author":[
        {
            "name":"testARTIST"
        }
        ],
    "album":{
        "name":"testALBUM"
        },
    "163id":-1//(if not a 163 music)
}
```



#### /api/v1/music/<music_id:int>
*TO GET DETAIL OF A MUSIC*

- **GET**
- **RETURN**
- {
  - code: int {200,404} *status
  - msg: string(if 404)         *readable status string
  - data: json(if 200)  *the detail of music
- }

return example:
```json
{
  "code": 200,
  "data": {
    "163id": 31680126,
    "album": {
      "name": "飛鳥ものがたり"
    },
    "author": [
      {
        "name": "天地雅楽"
      }
    ],
    "id": 1,
    "name": "壬申ノ乱",
    "status": true,
    "type": "mp3"
  }
}
```

#### /api/v1/music/<music_id:int>/audio
*TO GET AUDIO FILE OF A MUSIC*
- **GET**
- **RETURN**
- *json or file*
- {
  - code:int {-,404}
  - msg:string (if 404)
- }
- **or**
- _FILE OF AUDIO_

#### /api/v1/music/<music_id:int>/lyric
*TO GET lyric FILE OF A MUSIC*
- **GET**
- **RETURN**
- *json or file*
- {
  - code:int {-,404}
  - msg:string (if 404)
- }
- **or**
- _LYRIC OF AUDIO_