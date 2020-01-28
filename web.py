import json
import os

from flask import Flask, jsonify, request, send_file, abort
from werkzeug.utils import secure_filename

import downloader

app = Flask(__name__)

cache_dir = "/cache/"

playlists = {'nums': 0, 'list': {}}

if not os.path.isfile('playlists.json'):
    x = open('playlists.json', "w")
    x.write(json.dumps(playlists))
    x.flush()
    x.close()

hdp = open('playlists.json', "r+")


def save():
    hdp.seek(0)
    hdp.truncate()
    hdp.write(json.dumps(playlists))
    hdp.flush()


@app.route('/')
def index():
    return abort(404)


@app.route('/api/v1/playlist', methods=['POST'])
def create_playlist():
    if not request.json or 'name' not in request.json:
        return jsonify({'code': 400, 'msg': 'Bad Request: No name provided'}), 200
    playlists['list'][playlists['nums'].__str__()] = (
        {'name': request.json['name'], 'musics': {}, 'id': playlists['nums']})
    playlists['nums'] += 1
    save()
    return jsonify(
        {'code': 200, 'msg': 'Successfully added', 'id': str(playlists['nums'] - 1), 'name': request.json['name']}), 200


@app.route('/api/v1/playlist/<int:playlist>/relay163', methods=['POST'])
def relay_playlist(playlist):
    playlist = str(playlist)
    if not request.json or '163list_id' not in request.json:
        return jsonify({'code': 400, 'msg': 'Bad Request: No 163 playlist id provided'}), 200
    if not playlists['list'].__contains__(playlist):
        return jsonify({'code': 404, 'msg': 'Bad Request: Playlist Not Found'}), 200
    t = downloader.Downloader(cache_dir, "http://abcdelf.top:3000", request.json['163list_id'].__str__()).setSV(
        downloader.status, downloader.verbose)
    info = t.run()
    for _x in t.playlist_info.values():
        new = _x.copy()
        downloader.delete(new, 'file')
        downloader.delete(new, 'ly_file')
        playlists['list'][playlist]['musics'][_x['id'].__str__()] = new
    save()
    return jsonify({'code': 200, 'msg': 'Successfully relayed', 'info': info}), 200


@app.route('/api/v1/playlist/<int:playlist>/add', methods=['POST'])
def add_music_playlist(playlist):
    playlist = str(playlist)
    if not request.json or 'id' not in request.json:
        return jsonify({'code': 400, 'msg': 'Bad Request: No music id provided'}), 200
    if not playlists['list'].__contains__(playlist):
        return jsonify({'code': 404, 'msg': 'Bad Request: Playlist Not Found'}), 200
    if request.json['id'].__str__() not in downloader.musics['list']:
        return jsonify({'code': 404, 'msg': 'Music Not Found'}), 200
    new = downloader.musics['list'][request.json['id'].__str__()].copy()
    downloader.delete(new, 'file')
    downloader.delete(new, 'ly_file')
    playlists['list'][playlist]['musics'][request.json['id'].__str__()] = new
    save()
    return jsonify({'code': 200, 'msg': 'Successfully added', 'music': new}), 200


@app.route('/api/v1/playlist/<int:playlist>/remove', methods=['POST'])
def remove_music_playlist(playlist):
    playlist = str(playlist)
    if not request.json or 'id' not in request.json:
        return jsonify({'code': 400, 'msg': 'Bad Request: No music id provided'}), 200
    if not playlists['list'].__contains__(playlist):
        return jsonify({'code': 404, 'msg': 'Playlist Not Found'}), 200
    if request.json['id'].__str__() not in playlists['list'][playlist]['musics']:
        return jsonify({'code': 404, 'msg': 'Music Not Found'}), 200
    downloader.delete(playlists['list'][playlist]['musics'], request.json['id'].__str__())
    save()
    return jsonify({'code': 200, 'msg': 'Successfully removed'}), 200


@app.route('/api/v1/playlist/<int:playlist>', methods=['GET'])
def get_task(playlist):
    playlist = str(playlist)
    if not playlists['list'].__contains__(playlist):
        return jsonify({'code': 404, 'msg': 'Playlist Not Found'}), 200
    return playlists['list'][playlist], 200


@app.route('/api/v1/music/<int:mid>/lyric', methods=['GET'])
def get_lyric(mid):
    mid = str(mid)
    if not downloader.musics['list'].__contains__(mid):
        return jsonify({'code': 404, 'msg': 'Lyric Not Found'}), 200
    if downloader.musics['list'][mid]['status']:
        return send_file(downloader.musics['list'][mid]['ly_file'], mimetype='text/plain'), 200
    return downloader.musics['list'][mid]


@app.route('/api/v1/music/<int:mid>/audio', methods=['GET'])
def get_music_file(mid):
    mid = str(mid)
    if mid not in downloader.musics['list']:
        return jsonify({'code': 404, 'msg': 'Music Not Found'}), 200
    if downloader.musics['list'][mid]['status']:
        return send_file(downloader.musics['list'][mid]['file'],
                         mimetype='audio/' + downloader.musics['list'][mid]['type']), 200
    return downloader.musics['list'][mid]


@app.route('/api/v1/music/<int:mid>', methods=['GET'])
def get_music(mid):
    mid = str(mid)
    if mid not in downloader.musics['list']:
        return jsonify({'code': 404, 'msg': 'Music Not Found'}), 200
    new = downloader.musics['list'][mid].copy()
    downloader.delete(new, 'file')
    downloader.delete(new, 'ly_file')
    return new


@app.route('/api/v1/music/upload', methods=['POST'])
def upload_music():
    if 'info' not in request.form or 'file_audio' not in request.files or 'file_ly' not in request.files:
        return jsonify({'code': 400, 'msg': 'File loss'}), 200
    try:
        data = json.loads(request.form['info'])
    except ValueError:
        return jsonify({'code': 400, 'msg': 'Info type incorrect'}), 200
    if 'name' not in data or 'type' not in data or 'author' not in data or 'album' not in data or '163id' not in data:
        return jsonify({'code': 400, 'msg': 'Info loss'}), 200
    uploaded_file = request.files['file_audio']
    filename = secure_filename(uploaded_file.filename)
    uploaded_file.save(os.path.join(cache_dir, filename))
    uploaded_file_ly = request.files['file_ly']
    filename_ly = secure_filename(uploaded_file_ly.filename)
    uploaded_file_ly.save(os.path.join(cache_dir, filename_ly))
    downloader.musics['list'][downloader.musics['nums'].__str__()] = {
        'status': True,
        'name': data['name'],
        'type': data['type'],
        'file': os.path.join(cache_dir, filename),
        'ly_file': os.path.join(cache_dir, filename_ly),
        'id': downloader.musics['nums'],
        '163id': data['163id'],
        'author': data['author'],
        'album': data['album'],
    }
    if '163id' in data:
        downloader.musics['163map'][data['163id'].__str__()] = downloader.musics['nums'].__str__()
    downloader.musics['nums'] += 1
    downloader.save()
    return jsonify({'code': 200, 'msg': 'Successfully uploaded', 'id': downloader.musics['nums'] - 1}), 200


if __name__ == '__main__':
    playlists = json.load(hdp)
    downloader.musics = json.load(downloader.hdm)
    app.run(debug=True)
