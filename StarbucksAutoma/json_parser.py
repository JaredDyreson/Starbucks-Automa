import json
import os


class jsonparser():
    def __init__(self, content: dict):
        self.content = content

    def getjsonkey(self, key):
        return self.content[key]
