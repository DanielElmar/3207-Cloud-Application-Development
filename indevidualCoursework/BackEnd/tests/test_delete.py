import unittest
import requests
import azure.cosmos as cosmos
# Use this code block to access settings from a config.py
import config

db_URI = config.settings['db_URI']
db_id = config.settings['db_id']
db_key = config.settings['db_key']
prompts_cont = config.settings['prompts_container']
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
    prompts_container = db_client.get_container_client(prompts_cont)

    # function_url = 'http://localhost:7071/api/prompt/delete'
    function_url = cloud_URI + "/api/prompt/delete"


    def setUp(self) -> None:
        # Edit Payload ID's manually below
        pass

    def test_delete_success_and_not_exists(self):
        payload = {"id": 44, "text": "My First Prompt Edited My First Prompt Edited", "username": "Delmar",
                   "password": "Strong Password"}

        json_resp1 = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp1['msg'], "OK")
        self.assertTrue(json_resp1['result'])

        json_resp2 = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp2['msg'], "prompt id does not exist")
        self.assertTrue(not json_resp2['result'])

    def test_delete_user_not_exist(self):
        payload = {"id": 41, "text": "My First Prompt Edited My First Prompt Edited", "username": "NotAUser", "password": "12345678"}

        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp['msg'], 'bad username or password')
        self.assertTrue(not json_resp['result'])

    def test_delete_incorrect_password(self):
        payload = {"id": 41, "text": "My First Prompt Edited My First Prompt Edited", "username": "Delmar1", "password": "WrongPassword"}

        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp['msg'], 'bad username or password')
        self.assertTrue(not json_resp['result'])

    def test_delete_access_denied(self):
        payload = {"id": 41, "text": "My First Prompt Edited My First Prompt Edited", "username": "Delmar",
                   "password": "Strong Password"}

        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp['msg'], 'access denied')
        self.assertTrue(not json_resp['result'])




