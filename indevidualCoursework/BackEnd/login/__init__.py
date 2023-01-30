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
    logging.info('Starting Login HTTP Trigger')

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)

    json_in = req.get_json()

    username = json_in.get('username')
    password = json_in.get('password')

    resp = {}
    resp['result'] = False

    query_result = list(players_container.query_items(query="SELECT p.password FROM p WHERE p.id = @username",
                                                 parameters=[{"name": "@username", "value": username}]))

    if len(query_result) == 0:
        logging.info("Username Incorrect")
        resp['msg'] = "Username or password incorrect"
        return func.HttpResponse(body=json.dumps(resp))

    if query_result[0]["password"] != password:
        logging.info("Password Incorrect")
        resp['msg'] = "Username or password incorrect"
        return func.HttpResponse(body=json.dumps(resp))

    else:
        logging.info("Login Success")
        resp['msg'] = "OK"
        resp['result'] = True
        return func.HttpResponse(body=json.dumps(resp))
