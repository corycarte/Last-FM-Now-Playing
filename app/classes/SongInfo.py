import datetime as DT

class Artist:
    _artist = None
    _image = None
    _listens = None

    def __init__(self):
        self._artist = None
        self._image = None
        self._listens = None

    def set_artist(self, artist: str) -> None:
        self._artist = artist

    def get_artist(self) -> str:
        return self._artist

    def set_image(self, im_link: str) -> None:
        self._image = im_link

    def get_image(self) -> str:
        return self._image

    def set_listens(self, listens: int) -> None:
        self._listens = listens

    def get_listens(self) -> int:
        return self._listens

class Album:
    _artist = None
    _album = None
    _image = None
    _listens = None
    _release = None

    def __init__(self):
        self._artist = None
        self._album = None
        self._image = None
        self._listens = 0
        self._release = DT.datetime.now()

    def __repr__(self):
        return f"{self._album} by {self._artist}"

    def set_artist(self, artist) -> None:
        self._artist = artist

    def set_album(self, album) -> None:
        self._album = album

    def set_image(self, image) -> None:
        self._image = image

    def set_listens(self, listens) -> None:
        self._listens = listens

    def get_artist(self) -> str:
        return self._artist

    def get_album(self) -> str:
        return self._album

    def get_image(self) -> str:
        return self._image

    def get_listens(self) -> int:
        return self._listens


class Song(Album):
    _track = None
    _love = None
    _playing = False

    def __init__(self):
        super().__init__()
        self._track = ''
        self._love = False
        self._playing = False

    def __repr__(self):
        return f"{self._track} by {self._artist}"

    # Setters
    def set_song_info(self, artist: str = None, track: str = None, album: str = None) -> None:
        self._track = track
        self._artist = artist
        self._album = album

    def set_love(self, love: bool) -> None:
        print(f"Setting love to {love}")
        self._love=love

    def set_playing(self, p: bool) -> None:
        self._playing = p

    # Getters
    def get_track(self) -> str:
        return self._track

    def loved(self) -> bool:
        return self._love

    def playing(self) -> bool:
        return self._playing

    def toJSON(self):
        res = {}

        res['track'] = self._track
        res['artist'] = self._artist
        res['album'] = self._album
        res['love'] = self._love
        res['listens'] = self._listens
        res['image'] = self._image
        res['playing'] = self._playing

        return res