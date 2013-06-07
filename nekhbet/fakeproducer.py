

class FakeProducer:

    def __init__(self, config):
        self.config = config

    def sendMessage(self):
        # add to db
