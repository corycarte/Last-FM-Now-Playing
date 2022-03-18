import datetime as datetime
from flask import Flask
from flask import render_template

import yaml
import random
import datetime
import shutil

from classes.LastFmApi import LastFmApi as lastfm
from classes.Logger import Logger

app = Flask(__name__)


def get_top_section() -> tuple:
    data = None
    time = random.randint(0, (len(time_frames) - 1))
    stat = random.randint(0, (len(stats) - 1))
    stat_type = stats[stat][0], f' - Last {time_frames[time][0]}' if time > 0 else ' - All Time'

    logger.write_log(message=f'Retrieving {"".join(stat_type)}')

    if stat == 0:
        data = last.process_albums(last.user_get_top_albums(period=time_frames[time][1], limit=stats[stat][1]))
    elif stat == 1:
        data = last.process_artists(last.user_get_top_artists(period=time_frames[time][1], limit=stats[stat][1]))
    else:
        raise ValueError(stat)

    return stat_type, data

@app.route('/')
def index():
    try:
        songs = last.process_songs(last.user_get_recent_tracks(limit=1))

        if songs[0].playing():
            return render_template('current_listen.html', user=last.get_user(), song=songs[0])

        stat_type, top = get_top_section()
        return render_template('recent_tracks.html', user=last.get_user(), scrobbles=last.get_user_scrobbles(), last_song=songs[0], stat=stat_type, data=top)
    except Exception as ex:
        logger.write_log(message=str(ex), level=1)
        return render_template('Error.html')


@app.route('/debug')
def debug():
    try:
        return render_template('debug.html')
    except Exception as ex:
        logger.write_log(message=str(ex), level=1)
        return render_template('Error.html')


logger = Logger(f"{datetime.date.today().strftime('%Y%m%d')}_Site_log.txt")
key = user = None
time_frames = [("All Time", "overall"), ("7 Days", "7day"), ("3 Months", "3month"), ("Month", "1month"), ("6 Months", "6month"), ("12 Months", "12month")]
stats = [("Top Albums", 12), ("Top Artists", 6)] #, ("Top Tags", 4), ("Top Tracks", 12)]

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
    shutil.copyfile('template_config.yaml', 'config.yaml')
    exit(1)

logger.write_log(message='Starting server')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
