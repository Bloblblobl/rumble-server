import json
from unittest import TestCase
import uuid

from mock import Mock

from rumble_server import server
from rumble_server.api import create_app


class ServerTest(TestCase):
    def setUp(self):
        # Reset singleton every time
        server.instance = None
        app = create_app()
        self.test_app = app.test_client()

    def tearDown(self):
        pass


    def _register_test_user(self, username='Saar_Sayfan', password='passwurd', handle='Saar'):
        post_data = dict(username=username,
                         password=password,
                         handle=handle)

        return self.test_app.post('/register', data=post_data)

    def _login_test_user(self, username='Saar_Sayfan', password='passwurd', handle='Saar'):
        self._register_test_user(username, password, handle)

        post_data = dict(username=username,
                         password=password)

        response = self.test_app.post('/login', data=post_data)
        user_id = json.loads(response.data)['user_id']
        return user_id

    def test_register_success(self):
        response = self._register_test_user()
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        self.assertEqual('OK', result)

    def test_register_username_exists(self):
        # Register once
        self._register_test_user()

        # try to register again with the same user name
        response = self._register_test_user()
        self.assertEqual(400, response.status_code)
        message = json.loads(response.data)['message']
        self.assertEqual('Username Saar_Sayfan is already taken', message)

    def test_register_handle_exists(self):
        # Register once
        self._register_test_user()

        # try to register again with the another user name, but same handle
        response = self._register_test_user(username='Gigi')
        self.assertEqual(400, response.status_code)
        message = json.loads(response.data)['message']
        self.assertEqual('Handle Saar is already taken', message)

    def test_user_login_unregistered(self):
        post_data = dict(username='Saar_Sayfan',
                         password='passwurd', )

        response = self.test_app.post('/login', data=post_data)
        self.assertEqual(400, response.status_code)
        message = json.loads(response.data)['message']
        self.assertEqual('Invalid username or password', message)

    def test_user_login_success(self):
        self._register_test_user()

        post_data = dict(username='Saar_Sayfan',
                         password='passwurd', )

        # Mock uuid
        uuid4_orig = uuid.uuid4
        try:
            m = Mock()
            m.hex = '12345'
            uuid.uuid4 = lambda: m
            response = self.test_app.post('/login', data=post_data)
            self.assertEqual(200, response.status_code)
            user_id = json.loads(response.data)['user_id']
            self.assertTrue('12345', user_id)
        finally:
            uuid.uuid4 = uuid4_orig

    def test_create_room_success(self):
        user_id = self._login_test_user()

        post_data = dict(user_id=user_id,
                         name='room0')

        response = self.test_app.post('/room', data=post_data)
        self.assertEqual(200, response.status_code)


    def test_create_room_already_exists(self):
        user_id = self._login_test_user()

        post_data = dict(user_id=user_id,
                         name='room0')

        response = self.test_app.post('/room', data=post_data)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room', data=post_data)
        self.assertEqual(400, response.status_code)

    def test_create_room_unauthorized_user(self):
        post_data = dict(user_id='THIS IS A SHAM',
                         name='room0')

        response = self.test_app.post('/room', data=post_data)
        self.assertEqual(401, response.status_code)

    def test_join_room_success(self):
        user_id = self._login_test_user()

        post_data = dict(user_id=user_id,
                         name='room0')

        response = self.test_app.post('/room', data=post_data)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room_member', data=post_data)
        self.assertEqual(200, response.status_code)

    def test_join_room_already_joined(self):
        user_id = self._login_test_user()

        post_data = dict(user_id=user_id,
                         name='room0')

        response = self.test_app.post('/room', data=post_data)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room_member', data=post_data)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room_member', data=post_data)
        self.assertEqual(400, response.status_code)

    def test_join_room_no_such_room(self):
        user_id = self._login_test_user()

        post_data = dict(user_id=user_id,
                         name='room0')

        response = self.test_app.post('/room_member', data=post_data)
        self.assertEqual(404, response.status_code)

    def test_join_room_unauthorized_user(self):
        user_id = self._login_test_user()

        post_data = dict(user_id=user_id,
                         name='room0')

        response = self.test_app.post('/room', data=post_data)
        self.assertEqual(200, response.status_code)

        post_data = dict(user_id='NO SUCH USER',
                         name='room0')

        response = self.test_app.post('/room_member', data=post_data)
        self.assertEqual(401, response.status_code)

    def test_get_rooms_no_rooms(self):
        user_id = self._login_test_user()

        post_data = dict(user_id=user_id)

        response = self.test_app.post('/rooms', data=post_data)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        self.assertEqual([], result)

    def test_get_rooms_one_room(self):
        user_id = self._login_test_user()

        post_data = dict(user_id=user_id,
                         name='room0')

        response = self.test_app.post('/room', data=post_data)
        self.assertEqual(200, response.status_code)

        post_data = dict(user_id=user_id)

        response = self.test_app.post('/rooms', data=post_data)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        self.assertEqual(['room0'], result)

    def test_get_rooms_multiple_rooms(self):
        user_id = self._login_test_user()

        post_data = dict(user_id=user_id,
                         name='room0')

        response = self.test_app.post('/room', data=post_data)
        self.assertEqual(200, response.status_code)

        post_data = dict(user_id=user_id,
                         name='room1')

        response = self.test_app.post('/room', data=post_data)
        self.assertEqual(200, response.status_code)

        post_data = dict(user_id=user_id)

        response = self.test_app.post('/rooms', data=post_data)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        self.assertEqual(['room0', 'room1'], result)

    def test_get_room_members_no_member(self):
        user_id = self._login_test_user()

        post_data = dict(user_id=user_id,
                         name='room0')

        response = self.test_app.post('/room', data=post_data)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room_members', data=post_data)
        self.assertEqual(200, response.status_code)

        result = json.loads(response.data)['result']
        self.assertEqual([], result)

    def test_get_room_members_one_member(self):
        user_id = self._login_test_user()

        post_data = dict(user_id=user_id,
                         name='room0')

        response = self.test_app.post('/room', data=post_data)
        self.assertEqual(200, response.status_code)
        response = self.test_app.post('/room_member', data=post_data)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room_members', data=post_data)
        self.assertEqual(200, response.status_code)

        result = json.loads(response.data)['result']
        self.assertEqual(['Saar'], result)

    def test_get_room_members_multiple_members(self):
        user_id = self._login_test_user()
        user_id2 = self._login_test_user('Guy_Sayfan', 'passwird', 'Guy')

        post_data = dict(user_id=user_id,
                         name='room0')

        response = self.test_app.post('/room', data=post_data)
        self.assertEqual(200, response.status_code)
        response = self.test_app.post('/room_member', data=post_data)
        self.assertEqual(200, response.status_code)

        post_data = dict(user_id=user_id2,
                         name='room0')

        response = self.test_app.post('/room_member', data=post_data)
        self.assertEqual(200, response.status_code)

        post_data = dict(user_id=user_id,
                         name='room0')

        response = self.test_app.post('/room_members', data=post_data)
        self.assertEqual(200, response.status_code)

        result = set(json.loads(response.data)['result'])
        expected = {'Saar', 'Guy'}
        self.assertEqual(expected, result)


    # def test_destroy_room_success(self):
    #     user_id = self._login_test_user()
    #
    #     post_data = dict(user_id=user_id,
    #                      name='room0')
    #
    #     response = self.test_app.post('/room', data=post_data)
    #     self.assertEqual(200, response.status_code)
    #
    #     response = self.test_app.delete('/room', data=post_data)
    #     self.assertEqual(200, response.status_code)
    #
    #
    # def test_destroy_room_does_not_exist(self):
    #     user_id = self._login_test_user()
    #
    #     post_data = dict(user_id=user_id,
    #                      name='room0')
    #
    #     response = self.test_app.delete('/room', data=post_data)
    #     self.assertEqual(404, response.status_code)
    #
    # def test_destroy_room_unauthorized_user(self):
    #     post_data = dict(user_id='THIS IS A SHAM',
    #                      name='room0')
    #
    #     response = self.test_app.delete('/room', data=post_data)
    #     self.assertEqual(401, response.status_code)
