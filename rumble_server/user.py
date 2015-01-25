class User(object):
    def __init__(self, username, password, handle, registered):
        # List of invited members
        self.username = username
        self.password = password
        self.handle = handle
        self.registered = registered

    def __eq__(self, other):
        return((self.username, self.password, self.handle, self.registered) ==
               (other.username, other.password, other.handle, other.registered))
