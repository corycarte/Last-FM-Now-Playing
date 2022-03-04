import datetime as DT


class Logger:
    _log = None
    _levels = ["Critical", "Error", "Warn", "Info"]

    def __init__(self, log_path: str) -> None:
        self._log = open(log_path, "a")

    def write_log(self, message: str, level: int = 3):
        try:
            time = DT.datetime.now()
            self._log.write(f'[{time.strftime("%Y%m%d - %H:%M:%S.%f")}]: {self._levels[level]} - {message}\n')
        except Exception as ex:
            print(f"Logger failure: {ex}")
