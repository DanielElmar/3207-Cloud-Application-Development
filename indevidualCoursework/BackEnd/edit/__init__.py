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
    text = json_in["text"]
    username = json_in["username"]
    password = json_in["password"]

    resp = {'result': False}

    # Check Prompt
    if len(text) < 20 or len(text) > 100:
        logging.info("Bad Prompt")
        resp['msg'] = "prompt length is <20 or >100 characters"
        return func.HttpResponse(body=json.dumps(resp))

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    prompts_container = db_client.get_container_client(prompts_cont)

    # Check Prompt exists
    query_result1 = list(prompts_container.query_items(query="SELECT p.id FROM p WHERE p.iid = @id",
                                                       parameters=[{"name": "@id", "value": prompt_id}],
                                                       enable_cross_partition_query=True))

    if len(query_result1) == 0:
        logging.info("Prompt ID Doesnt Exist")
        resp['msg'] = "prompt id does not exist"
        return func.HttpResponse(body=json.dumps(resp))

    players_container = db_client.get_container_client(players_cont)

    # Check Username and Password
    query_result2 = list(players_container.query_items(query="SELECT p.password FROM p WHERE p.id = @username",
                                                       parameters=[{"name": "@username", "value": username}],
                                                       enable_cross_partition_query=True))

    if len(query_result2) == 0:
        logging.info("Username Incorrect")
        resp['msg'] = "bad username or password"
        return func.HttpResponse(body=json.dumps(resp))

    if query_result2[0]["password"] != password:
        logging.info("Password Incorrect")
        resp['msg'] = "bad username or password"
        return func.HttpResponse(body=json.dumps(resp))

    # Check if Prompt already exists
    query_result3 = list(
        prompts_container.query_items(query="SELECT p.iid FROM p WHERE p.username = @username AND p.text = @text",
                                      parameters=[{"name": "@username", "value": username},
                                                  {"name": "@text", "value": text}],
                                      enable_cross_partition_query=True))

    if len(query_result3) != 0:
        logging.info("User already created this prompt")
        resp['msg'] = "This user already has a prompt with the same text"
        return func.HttpResponse(body=json.dumps(resp))

    # edit prompt

    logging.info("STARTING TO EDIT PROMPT")
    logging.info(username)
    logging.info(text)
    logging.info( int(prompt_id) )
    logging.info(query_result1[0]["id"])

    prompts_container.upsert_item(body={"id": query_result1[0]["id"], "iid": int(prompt_id), "username": username, "text": text})

    resp['msg'] = "OK"
    resp['result'] = True
    return func.HttpResponse(body=json.dumps(resp))
