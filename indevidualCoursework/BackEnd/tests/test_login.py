import unittest
import requests
import azure.cosmos as cosmos
# Use this code block to access settings from a config.py
import config

db_URI = config.settings['db_URI']
db_id = config.settings['db_id']
db_key = config.settings['db_key']
players_cont = config.settings['players_container']
APP_KEY = config.settings["app_key"]
local_URI = config.settings["local_URI"]
cloud_URI = config.settings["cloud_URI"]


# Tests outside of the development server
# Therefore, environment variables are not available
# import os
# print(os.environ)
# db_URI = os.environ['db_URI']
# db_id = os.environ['db_id']
# db_key = os.environ['db_key']
# trees_cont = os.environ['trees_container']

class TestFunction(unittest.TestCase):
    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)

    # function_url = 'http://localhost:7071/api/player/login'
    function_url = cloud_URI + "/api/player/login"


    def setUp(self) -> None:
        pass

    def test_login_success(self):

        payload = {"username": "Delmar", "password": "Strong Password"}

        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp['msg'], 'OK')
        self.assertTrue(json_resp['result'])

    def test_login_incorrect_username(self):
        payload = {"username": "NotAUser", "password": "Strong Password"}

        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp['msg'], 'Username or password incorrect')
        self.assertTrue(not json_resp['result'])

    def test_login_incorrect_password(self):
        payload = {"username": "Delmar", "password": "WrongPassword"}

        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp['msg'], 'Username or password incorrect')
        self.assertTrue(not json_resp['result'])
