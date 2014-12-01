class Room(object):
    def __init__(self, name, members, messages):
        # List of invited members
        self.name = name
        self.members = members
        self.messages = messages
