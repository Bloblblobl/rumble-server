from flask_restful import abort


class Room(object):
    def __init__(self, name, members, messages):
        # List of invited members
        self.name = name
        self.members = members
        self.messages = messages

    def add_member(self, user_auth, user):
        if user_auth in self.members:
            abort(400, message='User already in the room')
        self.members[user_auth] = user

    def remove_member(self, user_auth):
        if user_auth not in self.members:
            abort(404, message='User not found')
        del self.members[user_auth]
