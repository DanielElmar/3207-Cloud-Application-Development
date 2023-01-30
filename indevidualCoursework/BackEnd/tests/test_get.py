import unittest
import requests
import azure.cosmos as cosmos
# Use this code block to access settings from a config.py
import config

db_URI = config.settings['db_URI']
db_id = config.settings['db_id']
db_key = config.settings['db_key']
prompts_cont = config.settings['prompts_container']
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
    prompts_container = db_client.get_container_client(prompts_cont)
    players_container = db_client.get_container_client(players_cont)

    # function_url = 'http://localhost:7071/api/prompts/get'
    function_url = cloud_URI + "/api/prompts/get"

    # DOESNT TEST RANDOMNESS OF UR SOL, FIGURE IT OUT UR SELF LMAO
    def setUp(self) -> None:
        # Edit Payload ID's manually below
        pass

    def test_get_norm(self):
        num_prompts = 3
        payload1 = {"prompts": num_prompts}
        """
        json_resp1 = requests.post(self.function_url, json=payload1).json()
        json_resp2 = requests.post(self.function_url, json=payload1).json()
        json_resp3 = requests.post(self.function_url, json=payload1).json()
        json_resp4 = requests.post(self.function_url, json=payload1).json()
        json_resp5 = requests.post(self.function_url, json=payload1).json()
        json_resp6 = requests.post(self.function_url, json=payload1).json()
        json_resp7 = requests.post(self.function_url, json=payload1).json()

        my_list = []

        for i in range(num_prompts):
            my_list.append(json_resp1[i]["id"])
            my_list.append(json_resp2[i]["id"])
            # my_list.append(json_resp3[i])
            # my_list.append(json_resp4[i])
            # my_list.append(json_resp5[i])

        self.assertEqual(len(set(my_list)), (2 * num_prompts))
        """

        json_resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(len(json_resp1), num_prompts)

        payload2 = {"players": ["Delmar", "Delmar1", "Delmar2"]}
        json_resp2 = requests.post(self.function_url, json=payload2, headers={'x-functions-key': APP_KEY}).json()
        query = "SELECT p.iid as id, p.text, p.username FROM p WHERE p.username IN (\"Delmar\", \"Delmar1\", \"Delmar2\")"
        query_result = list(self.prompts_container.query_items(query=query, enable_cross_partition_query=True))
        expected_resp2 = [
            {"id": 41, "text": "My First Prompt Edited My First Prompt Edited", "username": "Delmar1"},
            {"id": 42,
             "text": "I am 100 characters I am 100 characters I am 100 characters I am 100 characters I am 100 characters?",
             "username": "Delmar"},
            {"id": 43, "text": "I am 20 characters??", "username": "Delmar"}
        ]
        self.assertListEqual(query_result, json_resp2)
        self.assertListEqual(expected_resp2, json_resp2)

    def test_get_lower_boundary(self):
        payload1 = {"prompts": 1}
        json_resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(len(json_resp1), 1)

        payload2 = {"prompts": 0}
        json_resp2 = requests.post(self.function_url, json=payload2, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(len(json_resp2), 0)

        payload3 = {"players": ["Adin"]}
        json_resp3 = requests.post(self.function_url, json=payload3, headers={'x-functions-key': APP_KEY}).json()
        query = "SELECT p.iid as id, p.text, p.username FROM p WHERE p.username IN (\"Adin\")"
        query_result = list(self.prompts_container.query_items(query=query, enable_cross_partition_query=True))
        expected_resp3 = [{'id': 7, 'text': 'MY NAMES ADIN IM A TWITCH STREAMER', 'username': 'Adin'}]
        self.assertListEqual(query_result, json_resp3)
        self.assertListEqual(expected_resp3, json_resp3)

        payload4 = {"players": []}
        json_resp4 = requests.post(self.function_url, json=payload4, headers={'x-functions-key': APP_KEY}).json()
        # query = "SELECT p.iid as id, p.text, p.username FROM p WHERE p.username IN ()"
        # query_result = list(self.prompts_container.query_items(query=query, enable_cross_partition_query=True))
        # self.assertListEqual(query_result, json_resp4)
        self.assertListEqual([], json_resp4)

    def test_get_lower_extreme(self):
        payload = {"prompts": -199551}
        json_resp = requests.post(self.function_url, json=payload, headers={'x-functions-key': APP_KEY}).json()
        self.assertEqual(len(json_resp), 0)

    def test_get_upper_boundary(self):
        query_result1 = list(self.prompts_container.query_items(query="SELECT p.iid as id, p.text, p.username FROM p",
                                                                enable_cross_partition_query=True))

        query_result2 = list(self.players_container.query_items(query="SELECT p.id FROM p",
                                                                enable_cross_partition_query=True))

        total_num_of_prompts = len(query_result1)
        payload1 = {"prompts": total_num_of_prompts}
        json_resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY}).json()
        self.assertListEqual(query_result1, json_resp1)

        payload2 = {"prompts": (total_num_of_prompts + 1)}
        json_resp2 = requests.post(self.function_url, json=payload2, headers={'x-functions-key': APP_KEY}).json()
        self.assertListEqual(query_result1, json_resp2)

        usernames_list = []
        for username in query_result2:
            usernames_list.append(username["id"])
        payload3 = {"players": usernames_list}
        json_resp3 = requests.post(self.function_url, json=payload3, headers={'x-functions-key': APP_KEY}).json()
        self.assertListEqual(query_result1, json_resp3)

        usernames_list.append("NotAUser")

        payload4 = {"players": usernames_list}
        json_resp4 = requests.post(self.function_url, json=payload4, headers={'x-functions-key': APP_KEY}).json()
        self.assertListEqual(query_result1, json_resp4)

    def test_get_upper_extreme(self):
        query_result1 = list(self.prompts_container.query_items(query="SELECT p.iid as id, p.text, p.username FROM p",
                                                                enable_cross_partition_query=True))

        extreme_num_of_prompts = len(query_result1) + 1000
        payload1 = {"prompts": extreme_num_of_prompts}
        json_resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY}).json()
        self.assertListEqual(query_result1, json_resp1)


