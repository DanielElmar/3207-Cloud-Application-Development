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

    # function_url = 'http://localhost:7071/api/prompts/getText'
    function_url = cloud_URI + '/api/prompts/getText'
    #create_function_url = 'http://localhost:7071/api/prompt/create'
    #register_function_url = 'http://localhost:7071/api/player/register'



    prompts_to_create_lower = ["a word",
                               "a word!?",
                               "a word!!!!",
                               "a word. Another one",
                               "a word.Another one",
                               "another,word",
                               "a word......another one",
                               "a word?!;;;;;!!!!another one",
                               ",word,",
                               ".word.",
                               ":word:",
                               ";word;",
                               "!word!",
                               "?word?"]
    prompts_to_create_upper = ["a Word",
                               "a Word!?",
                               "a Word!!!!",
                               "a Word. Another one",
                               "a Word.Another one",
                               "another,Word",
                               "a Word......another one",
                               "a Word?!;;;;;!!!!another one",
                               ",Word,",
                               ".Word.",
                               ":Word:",
                               ";Word;",
                               "!Word!",
                               "?Word?"]

    wrong_prompts_to_create = ["words",
                               "Norword",
                               "Words",
                               "Wor d"]

    char_20_buffer = "..................."
    char_20_wrong_buffer = "!!!!!!!!!!!!!!!!!!!"

    prompts_lower = [("..................." + x) for x in prompts_to_create_lower]
    prompts_upper = [("..................." + x) for x in prompts_to_create_upper]

    """
    def setUp(self) -> None:
        # Run Once Then Comment Out For Proceeding Tests!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Register Prompt Test User
        # payload1 = {"username": "PromptTestUser", "password": "PromptTestPassword"}
        # json_resp = requests.post(self.register_function_url, json=payload1).json()

        payload_list = []

        for prompt in self.wrong_prompts_to_create:
            payload_list.append(
                {"text": self.char_20_wrong_buffer + prompt, "username": "PromptTestUser", "password": "PromptTestPassword"})

        for payload in payload_list:
            json_resp = requests.post(self.create_function_url, json=payload).json()


    """

    def test_getText_not_exact(self):
        payload1 = {"word": "Word", "exact": False}
        json_resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY}).json()
        query_result1 = list(
            self.prompts_container.query_items(
                query="SELECT p.iid as id, p.text, p.username FROM p WHERE RegexMatch(p.text, @regex, @modifiers)",
                parameters=[{"name": "@regex", "value": "^Word\W|\WWord\W|\WWord$|^Word$"},
                            {"name": "@modifiers", "value": "i"}],
                enable_cross_partition_query=True))
        self.assertEqual(json_resp1, query_result1)

        payload2 = {"word": "word", "exact": False}
        json_resp2 = requests.post(self.function_url, json=payload2, headers={'x-functions-key': APP_KEY}).json()
        query_result2 = list(
            self.prompts_container.query_items(
                query="SELECT p.iid as id, p.text, p.username FROM p WHERE RegexMatch(p.text, @regex, @modifiers)",
                parameters=[{"name": "@regex", "value": "^word\W|\Wword\W|\Wword$|^word$"},
                            {"name": "@modifiers", "value": "i"}],
                enable_cross_partition_query=True))
        self.assertEqual(json_resp2, query_result2)

        prompts_from_resp1 = [x["text"] for x in json_resp1]
        prompts_from_resp2 = [x["text"] for x in json_resp2]
        self.assertEqual(prompts_from_resp1, (self.prompts_lower + self.prompts_upper))
        self.assertEqual(prompts_from_resp2, (self.prompts_lower + self.prompts_upper))

    def test_getText_exact(self):
        payload1 = {"word": "word", "exact": True}
        json_resp1 = requests.post(self.function_url, json=payload1, headers={'x-functions-key': APP_KEY}).json()
        query_result1 = list(
            self.prompts_container.query_items(
                query="SELECT p.iid as id, p.text, p.username FROM p WHERE RegexMatch(p.text, @regex, @modifiers)",
                parameters=[{"name": "@regex", "value": "^word\W|\Wword\W|\Wword$|^word$"},
                            {"name": "@modifiers", "value": ""}],
                enable_cross_partition_query=True))
        self.assertEqual(json_resp1, query_result1)

        payload2 = {"word": "Word", "exact": True}
        json_resp2 = requests.post(self.function_url, json=payload2, headers={'x-functions-key': APP_KEY}).json()
        query_result2 = list(
            self.prompts_container.query_items(
                query="SELECT p.iid as id, p.text, p.username FROM p WHERE RegexMatch(p.text, @regex, @modifiers)",
                parameters=[{"name": "@regex", "value": "^Word\W|\WWord\W|\WWord$|^Word$"},
                            {"name": "@modifiers", "value": ""}],
                enable_cross_partition_query=True))
        self.assertEqual(json_resp2, query_result2)

        prompts_from_resp1 = [x["text"] for x in json_resp1]
        self.assertEqual(prompts_from_resp1, self.prompts_lower)

        prompts_from_resp2 = [x["text"] for x in json_resp2]
        self.assertEqual(prompts_from_resp2, self.prompts_upper)



    # def test_RegexMatch_against_spec(self):

    #     query_result1 = list(
    #         self.prompts_container.query_items(
    #             query="SELECT p.iid as id, p.text, p.username FROM p WHERE RegexMatch(p.text, @modifiers, @modifiers)",
    #             parameters=[{"name": "@regex", "value": "\WWord\W"},
    #                         {"name": "@modifiers", "value": "i"}]))
    #     expected_result =

    #     self.assertEqual(query_result1, expected_result)
