from flask import Flask
from flask import render_template

import requests
import yaml
import datetime as DT
import json

from classes.LastFmApi import LastFmApi as lastfm
from classes.Logger import Logger
from classes.SongInfo import Song

app = Flask(__name__)

def process_songs(songs) -> list:
    res = []

    for song in songs:
        try:
            s = Song()
            s.set_song_info(artist=song['artist']['#text'], track=song['name'], album=song['album']['#text'])
            s.set_image(song['image'][3]['#text'])

            if '@attr' in song and song['@attr']['nowplaying']:
                s.set_playing(True)

            track = json.loads(last.get_track_info(track=s.get_track(), artist=s.get_artist(), user=last.get_user()))

            if 'error' not in track:
                s.set_listens(track['track']['userplaycount'])
                s.set_love(track['track']['userloved'] == 1)
            else:
                print(f'Track error: {s.get_track()} -> {track["message"]}')

            res.append(s)
        except Exception as ex:
            print(ex)

    return res

@app.route('/')
def index():
    try:
        songs = last.process_songs(last.user_get_recent_tracks(limit=1))

        if songs[0].playing():
            return render_template('current_listen.html', user=last.get_user(), song=songs[0])

        top_albums = last.process_albums(last.user_get_top_albums(limit=12, period='7day'))

        return render_template('recent_tracks.html', user=last.get_user(), scrobbles=last.get_user_scrobbles(), last_song=songs[0], count=len(songs), top_albums=top_albums)
    except Exception as ex:
        print(f'index: {ex}')
        return render_template('Error.html')


@app.route('/debug')
def debug():
    res = process_songs(last.user_get_recent_tracks(limit=4))

    return render_template('debug.html', debug=json.dumps(res))


logger = Logger('log.txt')
key = user = None

try:
    logger.write_log(message="Loading config.yaml")
    with open('config.yaml', "r") as stream:
        conf = yaml.safe_load(stream)
        key = conf["api_key"]
        user = conf["user_name"]

    last = lastfm(key)
    last.set_user(user)
except Exception as ex:
    logger.write_log(message=str(ex), level=1)

logger.write_log(message='Starting server')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
