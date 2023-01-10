import json
from time import sleep
from datetime import datetime
import os
from threading import Timer

os.chdir(os.path.dirname(__file__))

class jsonOP:
    """
    Class for JSON operations
    """
    def __init__(self, JSONFILENAME: str):
        self.json = JSONFILENAME
        if not os.path.exists(self.json):
            self.data = {}
            self.saveJSON(self.data)
        else:
            self.data = self.loadJSON()


    def saveJSON(self, data):
        """
        Saves the data to the JSON file
        """
        with open(self.json, "w") as f:
            json.dump(data, f)

    def loadJSON(self):
        """
        Loads the JSON file
        """
        with open(self.json, "r") as f:
            data = json.load(f)
        return data


def print_bot(message):
        print(f"[{current_time()}] **Bot**: {message}")


def current_time():
    """
    Acquires the current time and returns it
    """
    now = datetime.now()
    this = now.strftime("%d/%m/%Y %H:%M:%S")
    return this


def isInteger(n):
    x = int(n)
    temp2 = float(n) - x
    if (temp2) > 0:
        return False
    return True


def delayedCall(time, func, *args):
    """
    Delays the call to the function
    """
    Timer(interval=5, function=func, args=args).start()