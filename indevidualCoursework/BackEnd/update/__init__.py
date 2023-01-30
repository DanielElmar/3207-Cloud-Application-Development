import json
import logging

import azure.functions as func
from azure import cosmos
import azure.cosmos.exceptions as exceptions

import os

db_URI = os.environ['db_URI']
db_id = os.environ['db_id']
db_key = os.environ['db_key']
players_cont = os.environ['players_container']


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Starting Update HTTP Trigger')

    json_in = req.get_json()

    username = json_in.get('username')
    password = json_in.get('password')
    add_to_games_played = json_in.get('add_to_games_played')
    add_to_score = json_in.get('add_to_score')

    logging.info(type(add_to_score))
    logging.info(add_to_score is not None)
    logging.info(add_to_score)

    resp = {}
    resp['result'] = False

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)

    query_result = list(players_container.query_items(query="SELECT * FROM p WHERE p.id = @username",
                                                      parameters=[{"name": "@username", "value": username}]))
    if len(query_result) == 0:
        logging.info("user does not exist")
        resp['msg'] = "user does not exist"
        return func.HttpResponse(body=json.dumps(resp))

    if add_to_games_played is not None and add_to_games_played <= 0:
        logging.info("add_to_games_played is <=0")

        resp['msg'] = "Value to add is <=0"
        return func.HttpResponse(body=json.dumps(resp))

    if add_to_score is not None and add_to_score <= 0:
        logging.info("add_to_score is <=0")

        resp['msg'] = "Value to add is <=0"
        return func.HttpResponse(body=json.dumps(resp))

    if query_result[0]['password'] != password:
        logging.info("wrong password")

        resp['msg'] = "wrong password"
        return func.HttpResponse(body=json.dumps(resp))

    # Update values

    # current_total_games = query_result["games_played"]
    # current_total_score = query_result["total_score"]

    if add_to_games_played is not None and add_to_score is not None:

        logging.info("GAMES AND SCORE DETECCTEDDDDDDDDDDDDDDD")
        # new_games_played = current_total_games + json_in["add_to_games_played"]
        # new_total_score = current_total_score + json_in["add_to_score"]

        query_result[0]["games_played"] += add_to_games_played
        query_result[0]["total_score"] += add_to_score

        players_container.upsert_item(body=query_result[0])

    elif add_to_games_played:
        # new_games_played = current_total_games + json_in["add_to_games_played"]

        query_result[0]["games_played"] += add_to_games_played

        players_container.upsert_item(body=query_result[0])

    elif add_to_score:
        # new_total_score = current_total_score + json_in["add_to_score"]

        query_result[0]["total_score"] += add_to_score
        players_container.upsert_item(body=query_result[0])

    ### EDIT what if update not sussfull???

    logging.info("Value Updates successful")

    resp['msg'] = "OK"
    resp['result'] = True
    return func.HttpResponse(body=json.dumps(resp))
