import datetime as DT

"""
Logger to write standard log lines starting with current time and error leve
"""
class Logger:
    _log = None
    _levels = ["Critical", "Error", "Warn", "Info"]

    def __init__(self, log_path: str = None) -> None:
        if log_path:
            self._log = open(log_path, "a")

    """
    Write a log message to log and console
    """
    def write_log(self, message: str, level: int = 3):
        try:
            time = DT.datetime.now()
            log_message = f'[{time.strftime("%Y%m%d - %H:%M:%S.%f")}]: {self._levels[level]} - {message}'
            print(log_message)
            if self._log:
                self._log.write(f'{log_message}\n')
        except Exception as ex:
            print(f"Logger failure: {ex}")
