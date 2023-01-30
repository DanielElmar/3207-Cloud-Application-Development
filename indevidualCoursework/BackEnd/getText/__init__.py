import json
import logging
import random

import azure.functions as func
from azure import cosmos
import azure.cosmos.exceptions as exceptions

import os

db_URI = os.environ['db_URI']
db_id = os.environ['db_id']
db_key = os.environ['db_key']
players_cont = os.environ['players_container']
prompts_cont = os.environ['prompts_container']


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Starting GetText HTTP Trigger')

    json_in = req.get_json()

    word = json_in.get("word")
    exact = json_in.get("exact")

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    prompts_container = db_client.get_container_client(prompts_cont)

    # query_result = list(prompts_container.query_items(query="SELECT * FROM p WHERE @word IN p.text",
    #                                                  parameters=[{"name": "@word", "value": word}]))

    # query_result = list(prompts_container.query_items(query="SELECT * FROM p WHERE CONTAINS(p.text, @word, @exact)",
    #                                                  parameters=[{"name": "@word", "value": word},
    #                                                              {"name": "@exact", "value": exact}]))

    regex = "^" + word + "\W|" + "\W" + word + "\W|" + "\W" + word + "$|^" + word + "$"
    modifiers = ""
    if not exact:
        modifiers += "i"

    query_result = list(
        prompts_container.query_items(
            query="SELECT p.iid as id, p.text, p.username FROM p WHERE RegexMatch(p.text, @regex, @modifiers)",
            parameters=[{"name": "@regex", "value": regex},
                        {"name": "@modifiers", "value": modifiers}],
            enable_cross_partition_query=True))

    logging.info(word)
    logging.info(exact)
    logging.info([x["text"] for x in query_result])
    return func.HttpResponse(body=json.dumps(query_result))
