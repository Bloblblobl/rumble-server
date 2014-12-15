import uuid
from flask.ext.restful import abort
from rumble_server.user import User

instance = None


def get_instance():
    global instance
    if instance is None:
        instance = Server()
    return instance


class ServerError(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code


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

        :param username:
        :param password:
        :param handle:
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

        user_id = uuid.uuid4().hex
        self.logged_in_users[user_id] = target_user
        return user_id

    def handle_message(self, user_id, message):
        """
        :return:
        """
        pass



