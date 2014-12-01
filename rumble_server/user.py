class User(object):
    def __init__(self, username, password, handle, registered):
        # List of invited members
        self.username = username
        self.password = password
        self.handle = handle
        self.registered = registered
