from rumble_server.user import User


class Server(object):
    def __init__(self):
        self.rooms = {}
        self.users = []

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
        :return:
        """
        for u in self.users:
            if u.username == username:
                raise Exception('Username {} is already taken'.format(username))
            if u.handle == handle:
                raise Exception('Handle {} is already taken'.format(handle))
        new_user = User(username, password, handle, True)
        self.users.append(new_user)