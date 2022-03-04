from flask import Flask
from flask import render_template

import requests
import yaml
import datetime as DT

from classes.LastFmApi import LastFmApi as lastfm
from classes.Logger import Logger

app = Flask(__name__)


@app.route('/')
def index():
    songs = last.user_get_recent_tracks(limit=10)
    if '@attr' in songs[0] and songs[0]['@attr']['nowplaying']:
        logger.write_log(f'Return now playing info')
        return render_template('current_listen.html',
                               artist=songs[0]['artist']['#text'],
                               song=songs[0]['name'],
                               image=songs[0]['image'][2]['#text'],
                               image_alt=songs[0]['album']['#text'])

    return render_template('recent_tracks.html', songs=songs, count=len(songs))


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
    app.run(debug=True)
