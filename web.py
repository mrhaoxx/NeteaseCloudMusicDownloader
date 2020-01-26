from flask import Flask, jsonify, request, send_file

from downloader import Downloader, musics, status, verbose

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello, World!"


playlists = {}


@app.route('/api/v1/playlist', methods=['POST'])
def create_playlist():
    if not request.json or not 'id' in request.json:
        return jsonify({'code': 400, 'msg': 'Bad Request: No id provided'}), 200
    if playlists.__contains__(request.json['id']):
        return jsonify({'code': 200, 'msg': 'Successfully updated', 'info': playlists[request.json['id']].run()}), 200
    new_downloader = Downloader("/cache/", "http://abcdelf.top:3000", request.json['id']).setSV(status, verbose)
    t = new_downloader.run()
    playlists[request.json['id']] = new_downloader
    return jsonify({'code': 200, 'msg': 'Successfully added', 'info': t}), 200


@app.route('/api/v1/playlist/<int:task_id>', methods=['GET'])
def get_task(task_id):
    if not playlists.__contains__(str(task_id)):
        return jsonify({'code': 404, 'msg': 'Playlist Not Found'}), 200
    return {'musics': playlists[str(task_id)].playlist_info}, 200


@app.route('/api/v1/music_lyric/<int:mid>', methods=['GET'])
def get_lyric(mid):
    if not musics.__contains__(mid):
        return jsonify({'code': 404, 'msg': 'Lyric Not Found'}), 200
    if musics[mid]['status']:
        return send_file(musics[mid]['ly_file'], mimetype='text/plain'), 200
    return musics[mid]


@app.route('/api/v1/music_file/<int:mid>', methods=['GET'])
def get_music(mid):
    if not musics.__contains__(mid):
        return jsonify({'code': 404, 'msg': 'Music Not Found'}), 200
    if musics[mid]['status']:
        return send_file(musics[mid]['file'], mimetype='audio/' + musics[mid]['type']), 200
    return musics[mid]


if __name__ == '__main__':
    app.run(debug=True)
