import json
import os
from unittest import TestCase
from datetime import datetime, timedelta
from rumble_server.api import create_app
import urllib


class ServerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        app = create_app()
        cls.test_app = app.test_client()

    def tearDown(self):
        pass

    def test_register(self):
        post_data = dict(username='Saar_Sayfan',
                         password='passwurd',
                         handle='Saar')

        response = self.test_app.post('/register', data=post_data)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.data)['result']
        self.assertTrue('OK', result)

