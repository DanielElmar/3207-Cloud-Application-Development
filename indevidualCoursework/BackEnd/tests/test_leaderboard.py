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

    # function_url = 'http://localhost:7071/api/player/leaderboard'
    function_url = cloud_URI + "/api/player/leaderboard"
    update_function_url = cloud_URI + "/api/player/update"




    def setUp(self) -> None:
        # Only Run Once
        # payload1 = {"username": "Delmar1", "password": "12345678", "add_to_score": 8}
        # json_resp1 = requests.post(self.update_function_url, json=payload1, headers={'x-functions-key': APP_KEY}).json()
        pass

    def test_leaderboard_norm(self):

        query_result1 = list(self.players_container.query_items(
            query="SELECT TOP 4 p.id as username, p.total_score as score, p.games_played FROM p ORDER BY "
                  "p.total_score DESC, p.id ASC",
            enable_cross_partition_query=True))

        payload = {"top": 4}
        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()
        self.assertGreater(len(json_resp), 0)
        self.assertEqual(len(json_resp), len(query_result1))

        for i in range(len(query_result1)):
            self.assertDictEqual(list(query_result1)[i], json_resp[i])

    def test_leaderboard_boundary(self):
        query_result = list(self.players_container.query_items(
            query="SELECT TOP 1 p.id as username, p.total_score as score, p.games_played FROM p ORDER BY "
                  "p.total_score DESC, p.id ASC",
            enable_cross_partition_query=True))

        payload = {"top": 1}
        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertGreater(len(json_resp), 0)
        self.assertEqual(len(json_resp), len(query_result))

        for i in range(len(query_result)):
            self.assertDictEqual(list(query_result)[i], json_resp[i])

        self.assertDictEqual({"username": "Delmar1", "score": 8, "games_played": 0}, json_resp[0])

    def test_leaderboard_extreme(self):
        query_result = list(self.players_container.query_items(
            query="SELECT TOP 60 p.id as username, p.total_score as score, p.games_played FROM p ORDER BY "
                  "p.total_score DESC, p.id ASC",
            enable_cross_partition_query=True))

        payload = {"top": 60}
        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()

        self.assertGreater(len(json_resp), 0)
        self.assertEqual(len(json_resp), len(query_result))

        for i in range(len(query_result)):
            self.assertDictEqual(query_result[i], json_resp[i])
