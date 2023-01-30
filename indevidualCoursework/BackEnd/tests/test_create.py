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

    # function_url = 'http://localhost:7071/api/prompt/create'
    function_url = cloud_URI + "/api/prompt/create"
    delete_function_url = cloud_URI + "/api/prompt/delete"

    setUp = False

    def setUp(self) -> None:
        # Manually delete below
        """
        if not self.setUp:
            payload1 = {"text": "My First Prompt My First Prompt My First Prompt", "username": "Delmar",
                        "password": "Strong Password"}
            payload2 = {"text": "My First Prompt My First Prompt My First Prompt", "username": "Delmar1",
                        "password": "12345678"}
            payload3 = {"text": "I am 20 characters!!", "username": "Delmar",
                        "password": "Strong Password"}
            payload4 = {
                "text": "I am 100 characters I am 100 characters I am 100 characters I am 100 characters I am 100 characters!",
                "username": "Delmar",
                "password": "Strong Password"}
            json_resp1 = requests.post(self.delete_function_url, json=payload1,
                                       headers={'x-functions-key': APP_KEY}).json()
            json_resp2 = requests.post(self.delete_function_url, json=payload2,
                                       headers={'x-functions-key': APP_KEY}).json()
            json_resp3 = requests.post(self.delete_function_url, json=payload3,
                                       headers={'x-functions-key': APP_KEY}).json()
            json_resp4 = requests.post(self.delete_function_url, json=payload4,
                                       headers={'x-functions-key': APP_KEY}).json()
            self.setUp = True
        else:
            pass
        """
    def test(self):
        pass


    def test_create_success_and_already_exists(self):
        payload = {"text": "My First Prompt My First Prompt My First Prompt", "username": "Delmar",
                   "password": "Strong Password"}

        json_resp1 = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp1['msg'], "OK")
        self.assertTrue(json_resp1['result'])

        json_resp2 = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp2['msg'], "This user already has a prompt with the same text")
        self.assertTrue(not json_resp2['result'])

    def test_create_different_user_same_prompt(self):
        payload = {"text": "My First Prompt My First Prompt My First Prompt", "username": "Delmar1",
                   "password": "12345678"}

        json_resp1 = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp1['msg'], "OK")
        self.assertTrue(json_resp1['result'])

    def test_create_user_not_exist(self):
        payload = {"text": "Test Prompt Test Prompt Test Prompt ", "username": "NotAUser",
                   "password": "Strong Password"}

        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp['msg'], 'bad username or password')
        self.assertTrue(not json_resp['result'])

    def test_create_prompt_short_boundary(self):
        payload1 = {"text": "I am 19 characters!", "username": "Delmar",
                    "password": "Strong Password"}

        json_resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp1['msg'], "prompt length is <20 or > 100 characters")
        self.assertTrue(not json_resp1['result'])

        payload2 = {"text": "I am 20 characters!!", "username": "Delmar",
                    "password": "Strong Password"}

        json_resp2 = requests.post(self.function_url, json=payload2, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp2['msg'], "OK")
        self.assertTrue(json_resp2['result'])

    def test_create_prompt_short_extreme(self):
        payload1 = {"text": "", "username": "Delmar",
                    "password": "Strong Password"}

        json_resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp1['msg'], "prompt length is <20 or > 100 characters")
        self.assertTrue(not json_resp1['result'])

    def test_create_prompt_long_boundary(self):
        payload1 = {
            "text": "I am 101 characters I am 101 characters I am 101 characters I am 101 characters I am 101 characters!!",
            "username": "Delmar",
            "password": "Strong Password"}

        json_resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp1['msg'], "prompt length is <20 or > 100 characters")
        self.assertTrue(not json_resp1['result'])

        payload2 = {
            "text": "I am 100 characters I am 100 characters I am 100 characters I am 100 characters I am 100 characters!",
            "username": "Delmar",
            "password": "Strong Password"}

        json_resp2 = requests.post(self.function_url, json=payload2, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp2['msg'], "OK")
        self.assertTrue(json_resp2['result'])

    def test_create_prompt_long_extreme(self):
        payload = {
            "text": "I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! "
                    "I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! "
                    "I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! "
                    "I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! "
                    "I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! "
                    "I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! "
                    "I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! "
                    "I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! "
                    "I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! I am MANY characters!!! ",
            "username": "Delmar",
            "password": "Strong Password"}

        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp['msg'], "prompt length is <20 or > 100 characters")
        self.assertTrue(not json_resp['result'])

    def test_create_incorrect_password(self):
        payload = {"text": "I am 25 characters!!!!!!!", "username": "Delmar", "password": "WrongPassword"}

        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertEqual(json_resp['msg'], 'bad username or password')
        self.assertTrue(not json_resp['result'])

