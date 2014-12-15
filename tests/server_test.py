import json
import os
from unittest import TestCase

import uuid
import unittest

from mock import Mock
from rumble_server import server
from rumble_server.api import create_app
import urllib


class ServerTest(TestCase):
    def setUp(self):
        # Reset singleton every time
        server.instance = None
        app = create_app()
        self.test_app = app.test_client()

    def tearDown(self):
        pass


    def _register_test_user(self, username='Saar_Sayfan', handle='Saar'):
        post_data = dict(username=username,
                         password='passwurd',
                         handle=handle)

        return self.test_app.post('/register', data=post_data)

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

