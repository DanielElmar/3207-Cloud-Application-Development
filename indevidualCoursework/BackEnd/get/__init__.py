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
    logging.info('Starting Get HTTP Trigger')

    json_in = req.get_json()

    prompts_num = json_in.get("prompts")
    players_usernames_ls = json_in.get("players")

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    prompts_container = db_client.get_container_client(prompts_cont)

    if prompts_num is not None:

        if prompts_num <= 0:
            return func.HttpResponse(body=json.dumps([]))
        else:

            total_prompts_num = list(prompts_container.query_items(query="SELECT VALUE COUNT(1) FROM p",
                                                                   enable_cross_partition_query=True))[0]

            logging.info("Getting Prompts From Num: " + str(prompts_num) + " : " + str(total_prompts_num))

            if total_prompts_num <= prompts_num:
                query_result = list(prompts_container.read_all_items())

                for row in query_result:
                    del row['_rid']
                    del row['_self']
                    del row['_etag']
                    del row['_attachments']
                    del row['_ts']
                    row["id"] = int(row['iid'])
                    del row['iid']

                logging.info(query_result)
                return func.HttpResponse(body=json.dumps(query_result))

            else:

                prompts_iid_max = \
                list(prompts_container.query_items(query="SELECT TOP 1 p.iid FROM p ORDER BY p.iid DESC",
                                                   enable_cross_partition_query=True))[0]["iid"]

                logging.info(prompts_iid_max)

                tried_prompt_iids = []
                return_prompts_ls = []

                while len(return_prompts_ls) < prompts_num:
                    generated_prompt_iids = random.sample(range(1, prompts_iid_max + 1), prompts_num)
                    new_prompt_iids = [x for x in generated_prompt_iids if x not in tried_prompt_iids]

                    if len(new_prompt_iids) != 0:
                        new_prompt_iids = new_prompt_iids[0: (prompts_num - len(return_prompts_ls))]

                        # Build ids string
                        iids_string = "(" + str(new_prompt_iids[0])
                        del new_prompt_iids[0]

                        for prompt_iid in new_prompt_iids:
                            iids_string += (", " + str(prompt_iid))
                        iids_string += ")"

                        query = "SELECT p.iid as id, p.text, p.username FROM p WHERE p.iid IN " + iids_string
                        logging.info(query)
                        query_result = list(
                            prompts_container.query_items(query=query, enable_cross_partition_query=True))

                        tried_prompt_iids += new_prompt_iids
                        return_prompts_ls += query_result

                """
                all_prompts = list(prompts_container.read_all_items())
                random_indexes = random.sample(range(0, len(all_prompts)), prompts_num)
        
                return_prompts = [all_prompts[i] for i in random_indexes]
                """

                logging.info(return_prompts_ls)
                return func.HttpResponse(body=json.dumps(return_prompts_ls))

    if players_usernames_ls is not None:

        logging.info("Getting Prompts From UserName: " + str(players_usernames_ls))

        if len(players_usernames_ls) == 0:
            return func.HttpResponse(body=json.dumps([]))
        else:
            # Build usernames string
            usernames_string = "( \"" + players_usernames_ls[0] + "\""
            del players_usernames_ls[0]

            for username in players_usernames_ls:
                usernames_string += (", \"" + username + "\"")

            usernames_string += ")"

            query = "SELECT p.iid as id, p.text, p.username FROM p WHERE p.username IN " + usernames_string
            logging.info(query)
            query_result = list(prompts_container.query_items(query=query, enable_cross_partition_query=True))

            logging.info(query_result)
            return func.HttpResponse(body=json.dumps(query_result))

    else:
        return func.HttpResponse(body=json.dumps({"ERROR": "WELP"}))
