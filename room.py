from flask_restful import abort


class Room(object):
    def __init__(self, name, members, messages):
        # List of invited members
        self.name = name
        self.members = members
        self.messages = messages

    def add_member(self, user_id, user):
        if user_id in self.members:
            abort(400, message='User already in the room')
        self.members[user_id] = user

    def remove_member(self, user_id):
        if user_id not in self.members:
            abort(404, message='User not found')
        del self.members[user_id]
