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

    # function_url = 'http://localhost:7071/api/player/update'
    function_url = cloud_URI + "/api/player/update"

    def setUp(self) -> None:
        pass

    """
    def test_simple(self):

        payload1 = {"username": "Delmar", "password": "Strong Password", "add_to_games_played": 1}
        #payload2 = {"username": "Delmar", "password": "Strong Password", "add_to_score": 1}
        #payload3 = {"username": "Delmar", "password": "Strong Password", "add_to_score": 10,"add_to_games_played": 10}

        resp1 = requests.get(self.function_url, json=payload1)
        json_resp1 = resp1.json()
        self.assertEqual(json_resp1['msg'], 'OK')
        self.assertTrue(json_resp1['result'])

        resp2 = requests.get(self.function_url, json=payload2)
        json_resp2 = resp2.json()
        self.assertEqual(json_resp2['msg'], 'OK')
        self.assertTrue(json_resp2['result'])

        resp3 = requests.get(self.function_url, json=payload3)
        json_resp3 = resp3.json()
        self.assertEqual(json_resp3['msg'], 'OK')
        self.assertTrue(json_resp3['result'])

    """

    def test_update_success(self):
        query_result1 = list(self.players_container.query_items(query="SELECT p.games_played, p.total_score FROM p "
                                                                      "WHERE p.id = 'Delmar'",
                                                                headers={'x-functions-key': APP_KEY}))

        original_games_played = query_result1[0]["games_played"]
        original_total_score = query_result1[0]["total_score"]

        score_add = 2
        games_add = 1

        payload1 = {"username": "Delmar", "password": "Strong Password", "add_to_games_played": games_add}
        payload2 = {"username": "Delmar", "password": "Strong Password", "add_to_score": score_add}
        payload3 = {"username": "Delmar", "password": "Strong Password", "add_to_score": score_add,
                    "add_to_games_played": games_add}

        json_resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp1['msg'], 'OK')
        self.assertTrue(json_resp1['result'])

        json_resp2 = requests.post(self.function_url, json=payload2, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp2['msg'], 'OK')
        self.assertTrue(json_resp2['result'])

        json_resp3 = requests.post(self.function_url, json=payload3, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp3['msg'], 'OK')
        self.assertTrue(json_resp3['result'])

        query_result2 = list(self.players_container.query_items(query="SELECT p.games_played, p.total_score FROM p "
                                                                      "WHERE p.id = 'Delmar'",
                                                                headers={'x-functions-key': APP_KEY}))

        final_games_played = query_result2[0]["games_played"]
        final_total_score = query_result2[0]["total_score"]

        self.assertEqual(final_games_played, (original_games_played + (2 * games_add)))
        self.assertEqual(final_total_score, (original_total_score + (2 * score_add)))

    def test_update_user_not_exist(self):
        payload1 = {"username": "NotAUser", "password": "Strong Password", "add_to_games_played": 1}
        payload2 = {"username": "NotAUser", "password": "Strong Password", "add_to_score": 1}
        payload3 = {"username": "NotAUser", "password": "Strong Password", "add_to_score": 1, "add_to_games_played": 1}

        json_resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp1['msg'], 'user does not exist')
        self.assertTrue(not json_resp1['result'])

        json_resp2 = requests.post(self.function_url, json=payload2, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp2['msg'], 'user does not exist')
        self.assertTrue(not json_resp2['result'])

        json_resp3 = requests.post(self.function_url, json=payload3, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp3['msg'], 'user does not exist')
        self.assertTrue(not json_resp3['result'])

    def test_update_non_positive_boundary(self):
        payload1 = {"username": "Delmar", "password": "Strong Password", "add_to_games_played": 1}
        payload2 = {"username": "Delmar", "password": "Strong Password", "add_to_score": 1}
        payload3 = {"username": "Delmar", "password": "Strong Password", "add_to_score": 1, "add_to_games_played": 1}

        json_resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp1['msg'], 'OK')
        self.assertTrue(json_resp1['result'])

        json_resp2 = requests.post(self.function_url, json=payload2, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp2['msg'], 'OK')
        self.assertTrue(json_resp2['result'])

        json_resp3 = requests.post(self.function_url, json=payload3, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp3['msg'], 'OK')
        self.assertTrue(json_resp3['result'])

        payload4 = {"username": "Delmar", "password": "Strong Password", "add_to_games_played": 0}
        payload5 = {"username": "Delmar", "password": "Strong Password", "add_to_score": 0}
        payload6 = {"username": "Delmar", "password": "Strong Password", "add_to_score": 0, "add_to_games_played": 1}
        payload7 = {"username": "Delmar", "password": "Strong Password", "add_to_score": 1, "add_to_games_played": 0}

        json_resp4 = requests.post(self.function_url, json=payload4, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp4['msg'], 'Value to add is <=0')
        self.assertTrue(not json_resp4['result'])

        json_resp5 = requests.post(self.function_url, json=payload5, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp5['msg'], 'Value to add is <=0')
        self.assertTrue(not json_resp5['result'])

        json_resp6 = requests.post(self.function_url, json=payload6, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp6['msg'], 'Value to add is <=0')
        self.assertTrue(not json_resp6['result'])

        json_resp7 = requests.post(self.function_url, json=payload7, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp7['msg'], 'Value to add is <=0')
        self.assertTrue(not json_resp7['result'])



    def test_update_non_positive_extreme(self):
        payload1 = {"username": "Delmar", "password": "Strong Password", "add_to_games_played": -4516516}
        payload2 = {"username": "Delmar", "password": "Strong Password", "add_to_score": -89456198456}
        payload3 = {"username": "Delmar", "password": "Strong Password", "add_to_score": -4516456566,
                    "add_to_games_played": 1}
        payload4 = {"username": "Delmar", "password": "Strong Password", "add_to_score": 1,
                    "add_to_games_played": -54646516512}

        json_resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp1['msg'], 'Value to add is <=0')
        self.assertTrue(not json_resp1['result'])

        json_resp2 = requests.post(self.function_url, json=payload2, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp2['msg'], 'Value to add is <=0')
        self.assertTrue(not json_resp2['result'])

        json_resp3 = requests.post(self.function_url, json=payload3, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp3['msg'], 'Value to add is <=0')
        self.assertTrue(not json_resp3['result'])

        json_resp4 = requests.post(self.function_url, json=payload4, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp4['msg'], 'Value to add is <=0')
        self.assertTrue(not json_resp4['result'])

    def test_update_incorrect_password(self):
        payload1 = {"username": "Delmar", "password": "WrongPassword", "add_to_games_played": 1}
        payload2 = {"username": "Delmar", "password": "WrongPassword", "add_to_score": 1}
        payload3 = {"username": "Delmar", "password": "WrongPassword", "add_to_score": 1, "add_to_games_played": 1}

        json_resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp1['msg'], 'wrong password')
        self.assertTrue(not json_resp1['result'])

        json_resp2 = requests.post(self.function_url, json=payload2, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp2['msg'], 'wrong password')
        self.assertTrue(not json_resp2['result'])

        json_resp3 = requests.post(self.function_url, json=payload3, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(json_resp3['msg'], 'wrong password')
        self.assertTrue(not json_resp3['result'])
