import requests
import json
import datetime
import time

from . import SongInfo
from . import Logger

API_ROOT = "https://ws.audioscrobbler.com/2.0/"

class LastFmApi_Error(Exception):
    def __init__(self, message="An error occurred in the call to LastFM"):
        self.message = message
        super().__init__(self.message)


class LastFmApi:

    _user = None
    _api_key = None
    _logger = None

    def __init__(self, api_key: str):
        self._api_key = api_key

    def _make_api_request(self, endpoint: str) -> requests.Request():
        return requests.get(endpoint)

    def _write_log(self, message: str, logger: Logger.Logger = None) -> None:
        if logger:
            logger.write_log(message=message)
        else:
            print(message)

    # User commands
    def set_user(self, user: str):
        print(f'Setting current user to {user}')
        self._user = user

    def get_user(self) -> str:
        return self._user

    def get_user_scrobbles(self) -> int:
        try:
            endpoint = f'{API_ROOT}/?method=user.getinfo&user={self._user}&api_key={self._api_key}&format=json'
            res = self._make_api_request(endpoint)

            if res.status_code == 200:
                tmp = json.loads(res.text)
                return int(tmp['user']['playcount'])
            else:
                raise(LastFmApi_Error(message=f'LastFm response {res.status_code}'))
        except Exception as ex:
            raise (LastFmApi_Error(message=f'LastFM API Error {ex}'))

    def user_get_recent_tracks(self, limit:int=None, page:int=None, from_date:datetime=None, to_date:datetime=None, extended:bool = False) -> list:
        base_endpoint = API_ROOT + '?method=user.getrecenttracks&user={user_name}&api_key={key}&format=json'.format(user_name=self._user, key=self._api_key)
        tracklist = []
        current_page = total_pages = 1

        try:
            if limit:
                base_endpoint += f'&limit={limit}'

            if from_date:
                base_endpoint += f'&from={int(time.mktime(from_date.timetuple()))}'

            if to_date:
                base_endpoint += f'&to={int(time.mktime(to_date.timetuple()))}'

            if extended:
                base_endpoint += f'&extended=1'

            res = requests.get(base_endpoint)

            if res.status_code == 200:
                tmp = json.loads(res.text)

                current_page = int(tmp['recenttracks']['@attr']['page'])
                total_pages = int(tmp['recenttracks']['@attr']['totalPages'])
                tracklist += tmp['recenttracks']['track']

                while current_page < total_pages and len(tracklist) < limit:
                    current_page += 1

                    req_endpoint = base_endpoint + '&page={}'.format(current_page)
                    response = requests.get(req_endpoint)

                    if response.status_code == 200:
                        tmp = json.loads(response.text)
                        tracklist += tmp['recenttracks']['track']
            else:
                raise LastFmApi_Error(message=f'LastFM error {res.status_code}')

            return tracklist
        except Exception as ex:
            raise LastFmApi_Error(message=str(ex))

    def user_get_top_albums(self, period: str = None, limit: int=None):
        endpoint = API_ROOT + f'?method=user.gettopalbums&user={self._user}&api_key={self._api_key}&format=json'

        if period:
            endpoint += f'&period={period}'

        if limit:
            endpoint += f'&limit={limit}'

        res = self._make_api_request(endpoint)

        if res.status_code == 200:
            res = json.loads(res.text)
            return res['topalbums']['album']

        raise LastFmApi_Error(message=f'LastFM error {res.status_code}')


    def user_get_top_artists(self, period: str = None, limit: int = None):
        endpoint = API_ROOT + f'?method=user.gettopartists&user={self._user}&api_key={self._api_key}&format=json'

        if period:
            endpoint += f'&period={period}'

        if limit:
            endpoint += f'&limit={limit}'

        res = self._make_api_request(endpoint)

        if res.status_code == 200:
            res = json.loads(res.text)
            return res['topartists']['artist']

        raise LastFmApi_Error(message=f'LastFM error {res.status_code}')

    # Track commands
    def get_track_info(self, track: str=None, artist: str=None, mbid: str=None, user: str=None, autocorrect:bool=True, limit:int=None) -> dict:
        req_endpoint = API_ROOT + f'?method=track.getInfo&api_key={self._api_key}'
        if not mbid and not (track and artist):
            raise LastFmApi_Error("Either mbid or track/artist required")
        
        if mbid:
            req_endpoint += f'&mbid={mbid}'
        else:
            req_endpoint += f'&track={track}&artist={artist}'

        req_endpoint += '&autocorrect=1' if autocorrect else f'&autocorrect=0'

        if user:
            req_endpoint += f'&user={user}'

        if limit:
            req_endpoint += f'&limit={limit}'

        req_endpoint += '&format=json'
        res = self._make_api_request(req_endpoint)

        if res.status_code == 200:
            return json.loads(res.text)

        raise LastFmApi_Error(message=f'LastFM error {res.status_code}')

    # Utilities
    def process_albums(self, albums: list) -> list:
        res = []

        for album in albums:
            try:
                a = SongInfo.Album()
                a.set_artist(album['artist']['name'])
                a.set_album(album['name'])
                a.set_image(album['image'][3]['#text'])
                res.append(a)
            except Exception as ex:
                print(f'LastFmApi.process_albums: {ex}')

        return res

    def process_songs(self, songs: list) -> list:
        res = []

        for song in songs:
            try:
                s = SongInfo.Song()
                s.set_song_info(artist=song['artist']['#text'], track=song['name'], album=song['album']['#text'])
                s.set_image(song['image'][3]['#text'])

                if '@attr' in song and song['@attr']['nowplaying']:
                    s.set_playing(True)

                track = self.get_track_info(track=s.get_track(), artist=s.get_artist(), user=self._user)

                if 'error' not in track:
                    s.set_listens(track['track']['userplaycount'])
                    s.set_love(track['track']['userloved'] == 1)
                else:
                    print(f'Track error: {s.get_track()} -> {track["message"]}')

                res.append(s)
            except Exception as ex:
                print(f'LastFmApi.process_songs: {ex}')

        return res

    def process_artists(self, artists: list) -> list:
        res = []

        for artist in artists:
            a = SongInfo.Artist()
            a.set_artist(artist['name'])
            a.set_listens(artist['playcount'])
            a.set_image(artist['image'][3]['#text'])
            res.append(a)

        return res

    def debug(self):
        print("Using LastFM to view\n\tuser: {user}\n\twith API Key: {key}".format(user=self._user, key=self._api_key))