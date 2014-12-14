import uuid
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

    def handle_message(self, message):
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
        for u in self.users:
            if u == username:
                raise ServerError('Username {} is already taken'.format(username), 400)
            if u.handle == handle:
                raise ServerError('Handle {} is already taken'.format(handle), 400)
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
            raise ServerError('Invalid username or password', 400)

        user_id = uuid.uuid4().hex
        self.logged_in_users[user_id] = target_user
        return user_id




