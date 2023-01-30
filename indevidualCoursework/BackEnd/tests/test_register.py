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

    # function_url = 'http://localhost:7071/api/player/register'
    function_url = cloud_URI + "/api/player/register"

    def setUp(self) -> None:
        # Delete users Delmar, Delmar1, Delmar3, 1234, 1234567891234567
        pass

    def test_register_player_success_and_already_exists(self):
        payload = {"username": "Delmar", "password": "Strong Password"}

        json_resp1 = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp1['msg'], 'OK')
        self.assertTrue(json_resp1['result'])

        json_resp2 = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp2['msg'], 'Username already exists')
        self.assertTrue(not json_resp2['result'])

    def test_register_player_password_short_boundary(self):
        payload1 = {"username": "Delmar1", "password": "1234567"}

        resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY})

        json_resp1 = resp1.json()

        self.assertEqual(json_resp1['msg'], 'Password less than 8 characters or more than 24 characters')
        self.assertTrue(not json_resp1['result'])

        payload2 = {"username": "Delmar1", "password": "12345678"}

        resp2 = requests.post(self.function_url, json=payload2, headers={'x-functions-key': APP_KEY})

        json_resp2 = resp2.json()

        self.assertEqual(json_resp2['msg'], 'OK')
        self.assertTrue(json_resp2['result'])

    def test_register_player_password_short_extreme(self):
        payload = {"username": "Delmar2", "password": ""}

        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp['msg'], 'Password less than 8 characters or more than 24 characters')
        self.assertTrue(not json_resp['result'])

    def test_register_player_password_long_boundary(self):
        payload1 = {"username": "Delmar3", "password": "1234567891234567891234567"}

        resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY})

        json_resp1 = resp1.json()

        self.assertEqual(json_resp1['msg'], 'Password less than 8 characters or more than 24 characters')
        self.assertTrue(not json_resp1['result'])

        payload2 = {"username": "Delmar3", "password": "123456789123456789123456"}

        resp2 = requests.post(self.function_url, json=payload2, headers={'x-functions-key': APP_KEY})

        json_resp2 = resp2.json()

        self.assertEqual(json_resp2['msg'], 'OK')
        self.assertTrue(json_resp2['result'])

    def test_register_player_password_long_extreme(self):
        payload = {"username": "Delmar4",
                   "password": "fhbjwdfijbwciwefhb wejdubeh rbh jfupwbihd cwribhdsjrfuhbsjyguhbrfdncjsyg8ihbwrfsyguhbwrfsyguhbjtrgfsyguhbjtrgfsyughbj4trgfsy8guhbja4twrfs8yguhbjtrgfsvyghbtsregfy8ghibwtrsyhib"}

        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp['msg'], 'Password less than 8 characters or more than 24 characters')
        self.assertTrue(not json_resp['result'])

    def test_register_player_username_short_boundary(self):
        payload1 = {"username": "123", "password": "Strong Password"}

        resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY})

        json_resp1 = resp1.json()

        self.assertEqual(json_resp1['msg'], 'Username less than 4 characters or more than 16 characters')
        self.assertTrue(not json_resp1['result'])

        payload2 = {"username": "1234", "password": "Strong Password"}

        resp2 = requests.post(self.function_url, json=payload2, headers={'x-functions-key': APP_KEY})

        json_resp2 = resp2.json()

        self.assertEqual(json_resp2['msg'], 'OK')
        self.assertTrue(json_resp2['result'])

    def test_register_player_username_short_extreme(self):
        payload = {"username": "", "password": "Strong Password"}

        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp['msg'], 'Username less than 4 characters or more than 16 characters')
        self.assertTrue(not json_resp['result'])

    def test_register_player_username_long_boundary(self):
        payload1 = {"username": "12345678912345678", "password": "Strong Password"}

        resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY})

        json_resp1 = resp1.json()

        self.assertEqual(json_resp1['msg'], 'Username less than 4 characters or more than 16 characters')
        self.assertTrue(not json_resp1['result'])

        payload = {"username": "1234567891234567", "password": "Strong Password"}

        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp['msg'], 'OK')
        self.assertTrue(json_resp['result'])

    def test_register_player_username_long_extreme(self):
        payload = {
            "username": "ebchibipjcbguoahq C ET7OUHIy8pahibjye\gihbdsrygwuifhbdsjeuhdibjrw8yfuhisjncrw8uhidjnkzeq9guadhvbjozt9geuoadbvjz9euoadbjt9eguofadbjgudbjvk c9ugdbjkvz cmugdbjvkzcm ugdjbkv",
            "password": "Strong Password"}

        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp['msg'], 'Username less than 4 characters or more than 16 characters')
        self.assertTrue(not json_resp['result'])
