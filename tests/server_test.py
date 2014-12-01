import json
import os
from unittest import TestCase
from datetime import datetime, timedelta
from rumble_server.api import create_app
import urllib


class ServerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        
        cls.test_app = app.test_client()

    def tearDown(self):
        pass

    def test_register(self):
        post_data = dict(username='Saar_Sayfan',
                         password='passwurd',
                         handle='Saar')

        response = self.test_app.post('/register', data=post_data)
        self.assertEqual(200, response.status_code)
        self.assertTrue('OK', response.content)
    #
    # query_params = dict(modalities='temperature',
    # start_time=str(self.start),
    #                     end_time=str(self.start + PERIOD))
    # url = '/v1/query?' + urllib.urlencode(query_params)
    # response = self.test_app.get(url)
    # result = json.loads(response.data)
    # self.assertEqual(1, len(result))
    # temperature_data = self._get_data(result, 'temperature')
    # self.assertEqual(self.expected_temperature, temperature_data)