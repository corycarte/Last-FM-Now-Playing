import requests
import json
import datetime
import time

API_ROOT = "https://ws.audioscrobbler.com/2.0/"

class LastFmApi:

    _user = None
    _api_key = None

    def __init__(self, api_key: str):
        self._api_key = api_key

    def set_user(self, user: str):
        print(f'Setting current user to {user}')
        self._user = user

    def _make_api_request(self, endpoint: str):
        return requests.get(endpoint)

    def user_get_recent_tracks(self, limit:int=None, page:int=None, from_date:datetime=None, to_date:datetime=None, extended:bool = False) -> dict:
        base_endpoint = API_ROOT + '?method=user.getrecenttracks&user={user_name}&api_key={key}&format=json'.format(user_name=self._user, key=self._api_key)

        if limit:
            base_endpoint += f'&limit={limit}'

        if from_date:
            base_endpoint += f'&from={int(time.mktime(from_date.timetuple()))}'
        
        if to_date:
            base_endpoint += f'&to={int(time.mktime(to_date.timetuple()))}'

        if extended:
            base_endpoint += f'&extended=1'

        print(f"Starting data pull for {self._user}\nWith endpoint {base_endpoint}")

        req_endpoint = base_endpoint
        response = requests.get(req_endpoint)

        tracklist = []
        current_page = total_pages = 1

        if response.status_code == 200:
            tmp = json.loads(response.text)

            current_page = int(tmp['recenttracks']['@attr']['page'])
            total_pages = int(tmp['recenttracks']['@attr']['totalPages'])
            tracklist = tmp['recenttracks']['track']

            while current_page < total_pages and len(tracklist) < limit:
                current_page += 1
                # print("Requesting page {} of {}".format(current_page, total_pages))

                req_endpoint = base_endpoint + '&page={}'.format(current_page)
                response = requests.get(req_endpoint)

                if response.status_code == 200:
                    tmp = json.loads(response.text)
                    tracklist = tracklist + tmp['recenttracks']['track']

        print("Retrieved {} tracks".format(len(tracklist)))
        return tracklist

    def pull_since(self, start_date: datetime) -> dict:
        try:
            res = self.user_get_recent_tracks(from_date=start_date)
        except Exception as ex:
            print(ex)
            res = {}
        finally:
            return res

    def pull_last_days_songs(self, total_days: int=None) -> dict:
        res = {}

        if not total_days or total_days < 1:
            res = self.user_get_recent_tracks()
        else:
            today = datetime.date.today()
            pull_start = today - datetime.timedelta(days=total_days)

            res = self.user_get_recent_tracks(from_date=pull_start, to_date=today)

        return res

    def debug(self):
        print("Using LastFM to view\n\tuser: {user}\n\twith API Key: {key}".format(user=self._user, key=self._api_key))

def csv_headers():
    print("Write headers")
    return '"played_date","track_name","artist","album","album_art_link"'

def track_to_csv(track: dict):
    track_name=track['name'].replace('"', "'")
    artist=track['artist']['#text'].replace('"', "'")
    album=track['album']['#text'].replace('"', "'")
    played_date=datetime.datetime.strptime(track['date']['#text'], '%d %b %Y, %H:%M')
    album_art_link=track['image'][-1]['#text'].replace('"', "'")

    return f'"{played_date}","{track_name}","{artist}","{album}","{album_art_link}"'

def get_track_name(track: dict) -> str:
    return track['name']