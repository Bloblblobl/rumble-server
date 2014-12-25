
import uuid
import datetime
import dateutil.parser
from flask_restful import abort
from room import Room
from user import User

instance = None


def get_instance():
    global instance
    if instance is None:
        instance = Server()
    return instance


class Server(object):
    def __init__(self):
        self.rooms = {}
        self.users = {}
        self.logged_in_users = {}

    def _load_all_rooms(self):
        """
        :return:
        """
        pass

    def _load_all_users(self):
        """
        :return:
        """
        pass

    def _save_all_rooms(self):
        """
        :return:
        """
        pass

    def _save_all_users(self):
        """
        :return:
        """
        pass

    def register(self, username, password, handle):
        """
        :return:
        """
        for name, user in self.users.iteritems():
            if name == username:
                message = 'Username {} is already taken'.format(username)
                abort(400, message=message)
            if user.handle == handle:
                message = 'Handle {} is already taken'.format(handle)
                abort(400, message=message)
        new_user = User(username, password, handle, True)
        self.users[username] = new_user

    def login(self, username, password):
        """

        :param username:
        :param password:
        :return:
        """
        target_user = self.users.get(username, None)
        if target_user is None or password != target_user.password:
            abort(400, message='Invalid username or password')

        if target_user in self.logged_in_users.values():
            abort(400, message='Already logged in')

        user_id = uuid.uuid4().hex
        self.logged_in_users[user_id] = target_user
        return user_id

    def handle_message(self, user_id, name, message):
        """
        :return:
        """
        if user_id not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        if name not in self.rooms:
            abort(404, message='Room not found')
        room = self.rooms[name]
        if user_id not in room.members:
            abort(401, message='Only members can send messages')

        handle = self.logged_in_users[user_id].handle
        timestamp = datetime.datetime.utcnow().replace(microsecond=0)

        room.messages[timestamp] = (handle, message)

    def get_messages(self, user_id, name, start=None, end=None):
        if user_id not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        if name not in self.rooms:
            abort(404, message='Room not found')
        room = self.rooms[name]
        if user_id not in room.members:
            abort(401, message='Only members can receive messages')

        start = dateutil.parser.parse(start)
        end = dateutil.parser.parse(end)

        return {k: v for k, v in room.messages.iteritems() if start <= k < end}

    def create_room(self, user_id, name):
        if user_id not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        if name in self.rooms:
            abort(400, message='A room with this name already exists')
        room = Room(name, {}, {})
        self.rooms[name] = room

    def destroy_room(self, user_id, name):
        if user_id not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        if name not in self.rooms:
            abort(404, message='Room not found')
        del self.rooms[name]

    def join_room(self, user_id, name):
        if user_id not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        if name not in self.rooms:
            abort(404, message='Room not found')
        self.rooms[name].add_member(user_id, self.logged_in_users[user_id])

    def leave_room(self, user_id, name):
        if user_id not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        if name not in self.rooms:
            abort(404, message='Room not found')
        self.rooms[name].remove_member(user_id)

    def get_rooms(self, user_id):
        if user_id not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        return self.rooms.keys()

    def get_room_members(self, user_id, name):
        if user_id not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        if name not in self.rooms:
            abort(404, message='Room not found')
        members = self.rooms[name].members.values()
        return [m.handle for m in members]

