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

    text = json_in["text"]
    username = json_in["username"]
    password = json_in["password"]

    resp = {'result': False}

    if len(text) < 20 or len(text) > 100:
        logging.info("Bad Prompt")
        resp['msg'] = "prompt length is <20 or > 100 characters"
        return func.HttpResponse(body=json.dumps(resp))

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)

    query_result1 = list(players_container.query_items(query="SELECT p.password FROM p WHERE p.id = @username",
                                                       parameters=[{"name": "@username", "value": username}]))

    if len(query_result1) == 0:
        logging.info("Username Incorrect")
        resp['msg'] = "bad username or password"
        return func.HttpResponse(body=json.dumps(resp))

    if query_result1[0]["password"] != password:
        logging.info("Password Incorrect")
        resp['msg'] = "bad username or password"
        return func.HttpResponse(body=json.dumps(resp))

    prompts_container = db_client.get_container_client(prompts_cont)

    query_result2 = list(
        prompts_container.query_items(query="SELECT p.id FROM p WHERE p.username = @username AND p.text = @text",
                                      parameters=[{"name": "@username", "value": username},
                                                  {"name": "@text", "value": text}],
                                      enable_cross_partition_query=True))

    if len(query_result2) != 0:
        logging.info("User already created this prompt")
        resp['msg'] = "This user already has a prompt with the same text"
        return func.HttpResponse(body=json.dumps(resp))

    # new_highest_index = list(prompts_container.query_items(query="SELECT TOP 1 p.id FROM p ORDER BY p.if DESC"))[0]["id"] + 1

    all_ids_list = list(prompts_container.query_items(query="SELECT p.iid FROM p", enable_cross_partition_query=True))

    if len(all_ids_list) == 0:
        new_lowest_index = 1
    else:
        all_ids_string = "(" + str(all_ids_list[0]["iid"])
        del all_ids_list[0]

        for id_dict in all_ids_list:
            all_ids_string += (", " + str(id_dict["iid"]))

        all_ids_string += ")"

        logging.info("MEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE: " + str(all_ids_string))

        query = "SELECT TOP 1 p.iid FROM p WHERE (p.iid + 1) NOT IN " + str(all_ids_string) + " ORDER BY p.iid ASC"

        logging.info("MEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE: " + query)

        new_lowest_index2 = list(prompts_container.query_items(
            query="SELECT TOP 1 p.iid FROM p WHERE (p.iid + 1) NOT IN (1, 3) ORDER BY p.iid ASC",
            parameters=[{"name": "@all_ids_string", "value": all_ids_string}],
            enable_cross_partition_query=True))[0]["iid"]

        #new_lowest_index1 = list(prompts_container.query_items(
        #    query="SELECT TOP 1 p.iid FROM p WHERE (p.iid + 1) NOT IN @all_ids_string ORDER BY p.iid ASC",
        #    parameters=[{"name": "@all_ids_string", "value": str(all_ids_string)}],
        #    enable_cross_partition_query=True))[0]["iid"]

        new_lowest_index = list(prompts_container.query_items(
            query=query,
            parameters=[{"name": "@all_ids_string", "value": str(all_ids_string)}],
            enable_cross_partition_query=True))[0]["iid"] + 1

    logging.info(new_lowest_index)

    prompts_container.create_item(body={"iid": new_lowest_index, "username": username, "text": text},
                                  enable_automatic_id_generation=True)

    logging.info("Prompt create Successful")
    resp['msg'] = "OK"
    resp['result'] = True
    return func.HttpResponse(body=json.dumps(resp))
