import os
import sqlite3
import uuid
import datetime
import dateutil.parser
from flask_restful import abort
from room import Room
from user import User

instance = None
script_dir = os.path.dirname(__file__)
db_file = os.path.join(os.path.join(script_dir, 'rumble.db'))
schema_file = os.path.join(os.path.join(script_dir, 'rumble_schema.sql'))


def get_instance():
    global instance
    if instance is None:
        instance = Server()
    return instance


class Server(object):
    def __init__(self):
        self.conn = sqlite3.connect(db_file)
        self.rooms = {}
        self.users = {}
        self.logged_in_users = {}
        self._load_all_users()

    def _load_all_rooms(self):
        """
        :return:
        """
        pass

    def _load_all_users(self):
        """
        :return:
        """
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM user")
            users = cur.fetchall()
            for u in users:
                user = User(u[1], u[2], u[3], True)
                self.users[u[1]] = user

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

        with self.conn:
            db = self.conn.cursor()
            db.execute("INSERT INTO user (name, password, handle) VALUES('{}', '{}', '{}')".format(username, password, handle))

    def login(self, username, password):
        """

        :param username:
        :param password:
        :return:
        """
        target_user = self.users.get(username, None)
        if target_user is None or password != target_user.password:
            abort(401, message='Invalid username or password')

        if target_user in self.logged_in_users.values():
            abort(400, message='Already logged in')

        user_auth = uuid.uuid4().hex
        self.logged_in_users[user_auth] = target_user
        return user_auth

    def handle_message(self, user_auth, name, message):
        """
        :return:
        """
        if user_auth not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        if name not in self.rooms:
            abort(404, message='Room not found')
        room = self.rooms[name]
        if user_auth not in room.members:
            abort(401, message='Only members can send messages')

        handle = self.logged_in_users[user_auth].handle
        timestamp = datetime.datetime.utcnow().replace(microsecond=0)

        room.messages[timestamp] = (handle, message)

        with self.conn:
            db = self.conn.cursor()
            # Find sender's user_id in Db by user name
            db.execute("SELECT id FROM user WHERE handle = '{}'".format(handle))
            sender_id = db.fetchone()[0]
            # Find room_id in Db by room name
            db.execute("SELECT id FROM room WHERE name = '{}'".format(name))
            room_id = db.fetchone()[0]
            # Save message to DB
            cmd = "INSERT INTO message (room_id, user_id, timestamp, message) VALUES({}, {}, '{}', '{}')"
            cmd = cmd.format(room_id, sender_id, timestamp, message)
            db.execute(cmd)

    def get_messages(self, user_auth, name, start=None, end=None):
        if user_auth not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        if name not in self.rooms:
            abort(404, message='Room not found')
        room = self.rooms[name]
        if user_auth not in room.members:
            abort(401, message='Only members can receive messages')

        start = dateutil.parser.parse(start)
        end = dateutil.parser.parse(end)

        return {k: v for k, v in room.messages.iteritems() if start <= k < end}

    def create_room(self, user_auth, name):
        if user_auth not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        if name in self.rooms:
            abort(400, message='A room with this name already exists')
        room = Room(name, {}, {})
        self.rooms[name] = room

        with self.conn:
            db = self.conn.cursor()
            db.execute("INSERT INTO room (name) VALUES('{}')".format(name))

    def destroy_room(self, user_auth, name):
        if user_auth not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        if name not in self.rooms:
            abort(404, message='Room not found')
        del self.rooms[name]

        with self.conn:
            db = self.conn.cursor()
            db.execute("DELETE FROM room WHERE name = '{}'".format(name))

    def join_room(self, user_auth, name):
        if user_auth not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        if name not in self.rooms:
            abort(404, message='Room not found')
        self.rooms[name].add_member(user_auth, self.logged_in_users[user_auth])

    def leave_room(self, user_auth, name):
        if user_auth not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        if name not in self.rooms:
            abort(404, message='Room not found')
        self.rooms[name].remove_member(user_auth)

    def get_rooms(self, user_auth):
        if user_auth not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        return self.rooms.keys()

    def get_room_members(self, user_auth, name):
        if user_auth not in self.logged_in_users:
            abort(401, message='Unauthorized user')
        if name not in self.rooms:
            abort(404, message='Room not found')
        members = self.rooms[name].members.values()
        return [m.handle for m in members]

