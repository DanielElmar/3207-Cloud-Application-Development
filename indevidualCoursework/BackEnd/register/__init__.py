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
    logging.info('Starting Register HTTP Trigger')

    # name = req.params.get('name')
    # if not name:
    #    try:
    #        req_body = req.get_json()
    #    except ValueError:
    #        pass
    #    else:
    #        name = req_body.get('name')

    # name = req.params.get('name')

    json_in = req.get_json()

    username = json_in.get('username')
    password = json_in.get('password')

    resp = {}
    resp['result'] = False

    if len(username) < 4 or len(username) > 16:
        logging.info("Username Invalid")
        resp['msg'] = "Username less than 4 characters or more than 16 characters"
        return func.HttpResponse(body=json.dumps(resp))

    if len(password) < 8 or len(password) > 24:
        logging.info("Password Invalid")
        resp['msg'] = "Password less than 8 characters or more than 24 characters"
        return func.HttpResponse(body=json.dumps(resp))



    #query_result = list(players_container.query_items(query="SELECT * FROM p WHERE p.id = @username",
    #                                                  parameters=[{"name": "@username", "value": username}]))

    # logging.info("STARTING OF ROW FOR EACH")
    #
    # query_result_empty
    # for row in query_result:
    #    logging.info("IN FOR EACH")
    #    logging.info(json.dumps(query_result, indent=True))
    #    logging.info(json.dumps(query_result))
    #    logging.info(query_result[0])
    #
    # logging.info("OUT OF ROW FOR EACH")

    #if len(query_result) > 0:
    #    msg = "Username already exists"
    #    return func.HttpResponse(body=json.dumps({result, msg}))
    #else:
    #    players_container.create_item(body=json_in)
    #    msg = "OK"
    #    result = True
    #    return func.HttpResponse(body=json.dumps({result, msg}))

    json_in["id"] = str(json_in['username'])
    json_in.pop('username')
    json_in["games_played"] = 0
    json_in["total_score"] = 0

    try:

        client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
        db_client = client.get_database_client(db_id)
        players_container = db_client.get_container_client(players_cont)


        players_container.create_item(body=json_in)

        logging.info("Player Register Succsess")

        resp['msg'] = "OK"
        resp['result'] = True
        return func.HttpResponse(body=json.dumps(resp))

    except exceptions.CosmosHttpResponseError:
        logging.info("Username Allready Exists")

        resp['msg'] = "Username already exists"
        return func.HttpResponse(body=json.dumps(resp))

    # if username:
    #    return func.HttpResponse(f"Hello, {username}. This HTTP triggered function executed successfully.")
    # else:
    #    return func.HttpResponse(
    #        "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
    #        status_code=200
    #    )
