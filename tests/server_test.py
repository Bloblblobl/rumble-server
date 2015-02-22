from datetime import datetime, timedelta
import os
import time
import json
from unittest import TestCase
import uuid

from mock import Mock
from werkzeug.datastructures import Headers

from rumble_server import server
from rumble_server.api import create_app
from rumble_server.room import Room
from rumble_server.user import User


class ServerTest(TestCase):
    def setUp(self):
        db_file = os.path.abspath('rumble.db')
        if os.path.isfile(db_file):
            os.remove(db_file)
        cmd = 'sqlite3 {} < ../rumble_server/rumble_schema.sql'
        cmd = cmd.format(db_file)
        os.system(cmd)

        # Reset singleton every time
        server.db_file = db_file
        server.instance = None
        app = create_app()
        self.conn = server.get_instance().conn
        self.test_app = app.test_client()

        self.bad_auth = Headers()
        self.bad_auth['Authorization'] = 'No such user'


    def tearDown(self):
        server.instance.conn.close()

    def _register_test_user(self, username='Saar_Sayfan', password='passwurd', handle='Saar'):
        post_data = dict(username=username,
                         password=password,
                         handle=handle)
        return self.test_app.post('/user', data=post_data)

    def _login_test_user(self, username='Saar_Sayfan', password='passwurd', handle='Saar'):
        self._register_test_user(username, password, handle)

        post_data = dict(username=username,
                         password=password)

        response = self.test_app.post('/active_user', data=post_data)
        user_auth = json.loads(response.data)['user_auth']
        headers = Headers()
        headers['Authorization'] = user_auth
        return headers

    def test_register_success(self):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM user")
            users = cur.fetchall()
            expected = []
            self.assertEqual(expected, users)

        response = self._register_test_user()
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        self.assertEqual('OK', result)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM user")
            users = cur.fetchall()
            expected = [(1, 'Saar_Sayfan', 'passwurd', 'Saar')]
            self.assertEqual(expected, users)

    def test_register_username_exists(self):
        # Register once
        self._register_test_user()

        # try to register again with the same user name
        response = self._register_test_user()
        self.assertEqual(400, response.status_code)
        message = json.loads(response.data)['message']
        self.assertEqual('Username Saar_Sayfan is already taken', message)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM user")
            users = cur.fetchall()
            expected = [(1, 'Saar_Sayfan', 'passwurd', 'Saar')]
            self.assertEqual(expected, users)

    def test_register_handle_exists(self):
        # Register once
        self._register_test_user()

        # try to register again with the another user name, but same handle
        response = self._register_test_user(username='Gigi')
        self.assertEqual(400, response.status_code)
        message = json.loads(response.data)['message']
        self.assertEqual('Handle Saar is already taken', message)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM user")
            users = cur.fetchall()
            expected = [(1, 'Saar_Sayfan', 'passwurd', 'Saar')]
            self.assertEqual(expected, users)

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
            response = self.test_app.post('/active_user', data=post_data)
            self.assertEqual(200, response.status_code)
            user_auth = json.loads(response.data)['user_auth']
            self.assertTrue('12345', user_auth)
        finally:
            uuid.uuid4 = uuid4_orig

    def test_user_login_wrong_password(self):
        self._register_test_user()

        post_data = dict(username='Saar_Sayfan',
                         password='passwird', )
        response = self.test_app.post('/active_user', data=post_data)
        self.assertEqual(401, response.status_code)

    def test_user_login_unregistered(self):
        post_data = dict(username='Saar_Sayfan',
                         password='passwurd', )

        response = self.test_app.post('/active_user', data=post_data)
        self.assertEqual(401, response.status_code)
        message = json.loads(response.data)['message']
        self.assertEqual('Invalid username or password', message)

    def test_user_login_already_logged_in(self):
        self._register_test_user()

        post_data = dict(username='Saar_Sayfan',
                         password='passwurd', )

        response = self.test_app.post('/active_user', data=post_data)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/active_user', data=post_data)
        self.assertEqual(400, response.status_code)

    def test_user_logout_success(self):
        self._register_test_user()
        auth = self._login_test_user()

        s = server.get_instance()
        self.assertTrue(len(s.logged_in_users) == 1)
        response = self.test_app.delete('/active_user', headers=auth)
        self.assertEqual(200, response.status_code)
        self.assertTrue(len(s.logged_in_users) == 0)

    def test_user_logout_not_logged_in(self):
        self._register_test_user()
        auth = [('Authorization', '12343tyui876543345678976543')]

        s = server.get_instance()
        self.assertTrue(len(s.logged_in_users) == 0)
        response = self.test_app.delete('/active_user', headers=auth)
        self.assertEqual(401, response.status_code)
        self.assertTrue(len(s.logged_in_users) == 0)

    def test_create_room_success(self):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM room")
            rooms = cur.fetchall()
            expected = []
            self.assertEqual(expected, rooms)

        auth = self._login_test_user()
        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM room")
            rooms = cur.fetchall()
            expected = [(1, 'room0')]
            self.assertEqual(expected, rooms)

    def test_create_room_already_exists(self):
        auth = self._login_test_user()

        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM room")
            rooms = cur.fetchall()
            expected = [(1, 'room0')]
            self.assertEqual(expected, rooms)

        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(400, response.status_code)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM room")
            rooms = cur.fetchall()
            expected = [(1, 'room0')]
            self.assertEqual(expected, rooms)

    def test_create_room_unauthorized_user(self):
        response = self.test_app.post('/room/room0', headers=self.bad_auth)
        self.assertEqual(401, response.status_code)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM room")
            rooms = cur.fetchall()
            expected = []
            self.assertEqual(expected, rooms)

    def test_join_room_success(self):
        auth = self._login_test_user()
        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room_member/room0', headers=auth)
        self.assertEqual(200, response.status_code)

    def test_join_room_already_joined(self):
        auth = self._login_test_user()

        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room_member/room0',
                                      headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room_member/room0',
                                      headers=auth)
        self.assertEqual(400, response.status_code)

    def test_join_room_no_such_room(self):
        auth = self._login_test_user()

        response = self.test_app.post('/room_member/room0', headers=auth)
        self.assertEqual(404, response.status_code)

    def test_join_room_unauthorized_user(self):
        auth = self._login_test_user()

        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room_member/room0',
                                      headers=self.bad_auth)
        self.assertEqual(401, response.status_code)

    def test_get_rooms_no_rooms(self):
        auth = self._login_test_user()
        response = self.test_app.get('/rooms', headers=auth)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        self.assertEqual([], result)

    def test_get_rooms_one_room(self):
        auth = self._login_test_user()
        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.get('/rooms', headers=auth)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        self.assertEqual(['room0'], result)

    def test_get_rooms_multiple_rooms(self):
        auth = self._login_test_user()
        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room/room1', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.get('/rooms', headers=auth)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        self.assertEqual(['room0', 'room1'], result)

    def test_get_room_members_no_member(self):
        auth = self._login_test_user()
        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.get('/room_members/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        result = json.loads(response.data)['result']
        self.assertEqual([], result)

    def test_get_room_members_one_member(self):
        auth = self._login_test_user()
        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)
        response = self.test_app.post('/room_member/room0',
                                      headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.get('/room_members/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        result = json.loads(response.data)['result']
        self.assertEqual(['Saar'], result)

    def test_get_room_members_multiple_members(self):
        auth = self._login_test_user()
        auth2 = self._login_test_user('Guy_Sayfan', 'passwird', 'Guy')

        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room_member/room0',
                                      headers=auth)
        self.assertEqual(200, response.status_code)
        response = self.test_app.post('/room_member/room0',
                                      headers=auth2)
        self.assertEqual(200, response.status_code)

        response = self.test_app.get('/room_members/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        result = set(json.loads(response.data)['result'])
        expected = {'Saar', 'Guy'}
        self.assertEqual(expected, result)

    def test_destroy_room_success(self):
        auth = self._login_test_user()
        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.delete('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM room")
            rooms = cur.fetchall()
            expected = []
            self.assertEqual(expected, rooms)

    def test_destroy_room_with_messages_success(self):
        auth = self._login_test_user()
        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room_member/room0',
                                      headers=auth)
        self.assertEqual(200, response.status_code)

        post_data = dict(name='room0', message='message')

        response = self.test_app.post('/message/room0',
                                      data=post_data,
                                      headers=auth)
        self.assertEqual(200, response.status_code)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT room_id, user_id, message FROM message")
            messages = cur.fetchall()
            expected = [(1, 1, 'message')]
            self.assertEqual(expected, messages)

        response = self.test_app.delete('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM room")
            rooms = cur.fetchall()
            expected = []
            self.assertEqual(expected, rooms)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT room_id, user_id, message FROM message")
            messages = cur.fetchall()
            expected = []
            self.assertEqual(expected, messages)

    def test_destroy_room_does_not_exist(self):
        auth = self._login_test_user()
        response = self.test_app.delete('/room/room0', headers=auth)
        self.assertEqual(404, response.status_code)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM room")
            rooms = cur.fetchall()
            expected = []
            self.assertEqual(expected, rooms)

    def test_destroy_room_unauthorized_user(self):
        auth = self._login_test_user()
        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.delete('/room/room0', headers=self.bad_auth)
        self.assertEqual(401, response.status_code)

    def test_handle_message_success(self):
        auth = self._login_test_user()

        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room_member/room0',
                                      headers=auth)
        self.assertEqual(200, response.status_code)

        post_data = dict(name='room0', message='message')

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT room_id, user_id, message FROM message")
            messages = cur.fetchall()
            expected = []
            self.assertEqual(expected, messages)

        response = self.test_app.post('/message/room0',
                                      data=post_data,
                                      headers=auth)
        self.assertEqual(200, response.status_code)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT room_id, user_id, message FROM message")
            messages = cur.fetchall()
            expected = [(1, 1, 'message')]
            self.assertEqual(expected, messages)

    def test_handle_message_unauthorized_user(self):
        auth = self._login_test_user()
        post_data = dict(name='room0', message='message')

        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/message/room0',
                                      data=post_data,
                                      headers=self.bad_auth)
        self.assertEqual(401, response.status_code)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT room_id, user_id, message FROM message")
            messages = cur.fetchall()
            expected = []
            self.assertEqual(expected, messages)

    def test_handle_message_room_does_not_exist(self):
        auth = self._login_test_user()
        post_data = dict(name='room0', message='message')

        response = self.test_app.post('/message/room0',
                                      data=post_data,
                                      headers=auth)
        self.assertEqual(404, response.status_code)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT room_id, user_id, message FROM message")
            messages = cur.fetchall()
            expected = []
            self.assertEqual(expected, messages)

    def test_handle_message_not_member(self):
        auth = self._login_test_user()
        post_data = dict(name='room0', message='message')

        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/message/room0',
                                      data=post_data,
                                      headers=auth)
        self.assertEqual(401, response.status_code)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT room_id, user_id, message FROM message")
            messages = cur.fetchall()
            expected = []
            self.assertEqual(expected, messages)

    def test_get_messages_unauthorized_user(self):
        auth = self._login_test_user()

        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.get('/messages/room0/start/end', headers=self.bad_auth)
        self.assertEqual(401, response.status_code)


    def test_get_messages_room_does_not_exist(self):
        auth = self._login_test_user()

        response = self.test_app.get('/messages/room0/start/end', headers=auth)
        self.assertEqual(404, response.status_code)

    def test_get_messages_not_member(self):
        auth = self._login_test_user()

        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.get('/messages/room0/start/end', headers=auth)
        self.assertEqual(401, response.status_code)

    def test_get_messages_no_messages(self):
        auth = self._login_test_user()

        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room_member/room0',
                                      headers=auth)
        self.assertEqual(200, response.status_code)
        start = '2014-12-24T00:00:00'
        end = '2014-12-25T00:00:00'

        response = self.test_app.get('/messages/room0/{}/{}'.format(start, end), headers=auth)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        self.assertEqual([], result)

    def test_get_messages_one_message(self):
        auth = self._login_test_user()

        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room_member/room0',
                                      headers=auth)
        self.assertEqual(200, response.status_code)
        start = datetime.now().replace(microsecond=0)
        end = start + timedelta(days=1)

        start = start.isoformat()
        end = end.isoformat()

        post_data = dict(message='TEST MESSAGE')
        response = self.test_app.post('/message/room0',
                                      data=post_data,
                                      headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.get('/messages/room0/{}/{}'.format(start, end), headers=auth)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        self.assertEqual('TEST MESSAGE', result[0][2])

    def test_get_room_members_multiple_messages(self):
        auth = self._login_test_user()

        response = self.test_app.post('/room/room0', headers=auth)
        self.assertEqual(200, response.status_code)

        response = self.test_app.post('/room_member/room0',
                                      headers=auth)
        self.assertEqual(200, response.status_code)
        start = datetime.utcnow().replace(microsecond=0)

        # send 3 messages 1 second apart
        for i in range(3):
            post_data = dict(message='TEST MESSAGE {}'.format(i))
            response = self.test_app.post('/message/room0',
                                          data=post_data,
                                          headers=auth)
            self.assertEqual(200, response.status_code)
            time.sleep(1)

        # no messages in range
        end = start
        response = self.test_app.get('/messages/room0/{}/{}'.format(start.isoformat(), end.isoformat()), headers=auth)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        self.assertEqual([], result)

        # 1 message in range
        end = start + timedelta(seconds=1)
        response = self.test_app.get('/messages/room0/{}/{}'.format(start.isoformat(), end.isoformat()), headers=auth)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        self.assertEqual('TEST MESSAGE 0', result[0][2])

        # all messages in range
        end = start + timedelta(seconds=4)
        response = self.test_app.get('/messages/room0/{}/{}'.format(start.isoformat(), end.isoformat()), headers=auth)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        values = sorted(result)
        self.assertEqual('TEST MESSAGE 0', values[0][2])
        self.assertEqual('TEST MESSAGE 1', values[1][2])
        self.assertEqual('TEST MESSAGE 2', values[2][2])

    def test_get_users_unauthorized_user(self):
        auth = None

        response = self.test_app.get('/users', headers=auth)
        self.assertEqual(401, response.status_code)

    def test_get_users_one_member(self):
        auth = self._login_test_user()

        response = self.test_app.get('/users', headers=auth)
        self.assertEqual(401, response.status_code)

    def test_get_users_multiple_members(self):
        auth = self._login_test_user()
        auth2 = self._login_test_user("a", "b", "c")

        response = self.test_app.get('/users', headers=auth)
        self.assertEqual(401, response.status_code)


    def test_server_init(self):
        s = server.get_instance()
        auth = self._login_test_user()

        for name in ('room0', 'room1'):
            response = self.test_app.post('/room/' + name, headers=auth)
            self.assertEqual(200, response.status_code)

            response = self.test_app.post('/room_member/{}'.format(name),
                                          headers=auth)
            self.assertEqual(200, response.status_code)

            post_data = dict(name=name, message='message')
            response = self.test_app.post('/message/' + name,
                                          data=post_data,
                                          headers=auth)
            self.assertEqual(200, response.status_code)

            time.sleep(1)

            post_data = dict(name=name, message='message2')
            response = self.test_app.post('/message/' + name,
                                          data=post_data,
                                          headers=auth)
            self.assertEqual(200, response.status_code)

        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT room_id, user_id, message FROM message")
            messages = cur.fetchall()
        expected = [(1, 1, 'message'), 
                    (1, 1, 'message2'), 
                    (2, 1, 'message'), 
                    (2, 1, 'message2')]
        self.assertEqual(expected, messages)

        server.instance.disconnect()
        server.instance = None

        s = server.get_instance()
        u = User('Saar_Sayfan', 'passwurd', 'Saar', True)
        expected_users = [u]
        m = (('Saar','message'),('Saar','message2'))
        expected_rooms = {('room0', m[0]), ('room0', m[1]), ('room1', m[0]), ('room1', m[1])}

        self.assertEqual(expected_users, s.users.values())
        rooms = set()
        for r in s.rooms.values():
            for m in r.messages.values():
                rooms.add((r.name, m))

        for r in expected_rooms:
            self.assertIn(r, rooms)