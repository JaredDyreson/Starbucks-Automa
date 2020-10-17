from StarbucksAutoma.initialize import initializer, DEFAULT_BUILD_CONFIG


class jsonparser():
    def __init__(self):
        self.contents = initializer(DEFAULT_BUILD_CONFIG).read_contents()

    def getjsonkey(self, key):
        return self.contents[key]
