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
prompts_cont = os.environ['prompts_container']


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Starting Create HTTP Trigger')

    json_in = req.get_json()

    prompt_id = json_in["id"]
    username = json_in["username"]
    password = json_in["password"]

    resp = {'result': False}

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    prompts_container = db_client.get_container_client(prompts_cont)

    # Check Prompt exists
    query_result1 = list(prompts_container.query_items(query="SELECT p.id, p.iid, p.username FROM p WHERE p.iid = @id",
                                                       parameters=[{"name": "@id", "value": prompt_id}],
                                                       enable_cross_partition_query=True))

    if len(query_result1) == 0:
        logging.info("Prompt ID Doesnt Exist")
        resp['msg'] = "prompt id does not exist"
        return func.HttpResponse(body=json.dumps(resp))

    players_container = db_client.get_container_client(players_cont)

    # Check Username and Password
    query_result2 = list(players_container.query_items(query="SELECT p.password FROM p WHERE p.id = @username",
                                                       parameters=[{"name": "@username", "value": username}]))

    if len(query_result2) == 0:
        logging.info("Username Incorrect")
        resp['msg'] = "bad username or password"
        return func.HttpResponse(body=json.dumps(resp))

    if query_result2[0]["password"] != password:
        logging.info("Password Incorrect")
        resp['msg'] = "bad username or password"
        return func.HttpResponse(body=json.dumps(resp))

    # Check User owns This Prompt
    if len(query_result1) > 0 and query_result1[0]["username"] != username:
        logging.info("Access to Prompt Denied")
        resp['msg'] = "access denied"
        return func.HttpResponse(body=json.dumps(resp))

    # Delete prompt
    prompts_container.delete_item(item=query_result1[0]["id"], partition_key=query_result1[0]["id"])

    logging.info("Prompt Deleted")
    resp['msg'] = "OK"
    resp['result'] = True
    return func.HttpResponse(body=json.dumps(resp))

# except exceptions.CosmosResourceNotFoundError:
#     logging.info("Prompt ID Doesnt Exist")
#     resp['msg'] = "prompt id does not exist"
#     return func.HttpResponse(body=json.dumps(resp))
