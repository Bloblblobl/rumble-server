import json
from unittest import TestCase
import uuid
import unittest

from mock import Mock

from rumble_server.api import create_app


class ServerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        app = create_app()
        cls.test_app = app.test_client()

    def tearDown(self):
        pass

    def test_register(self):
        response = self._register_test_user()
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        self.assertTrue('OK', result)

    @unittest.skip('Need to fix error handling')
    def test_user_login(self):
        post_data = dict(username='Saar_Sayfan',
                         password='passwurd', )

        response = self.test_app.post('/login', data=post_data)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        self.assertTrue('OK', result)

    def _register_test_user(self):
        post_data = dict(username='Saar_Sayfan',
                         password='passwurd',
                         handle='Saar')

        return self.test_app.post('/register', data=post_data)

    def test_successful_user_login(self):
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

