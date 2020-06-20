import json
import os


class jsonparser():
    def __init__(self, path=None):
        self.path = path
        with open(self.path, "r") as fp:
            self.content = json.load(fp)

    def getjsonkey(self, key):
        return self.content[key]
