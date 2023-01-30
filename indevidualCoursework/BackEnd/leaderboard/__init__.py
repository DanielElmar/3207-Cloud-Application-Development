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
    logging.info('Starting Leaderboard HTTP Trigger')

    json_in = req.get_json()

    top_n = json_in.get('top')

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)

    query_result = players_container.query_items(
        query="SELECT TOP @n p.id as username, p.total_score as score, p.games_played FROM p ORDER BY p.total_score DESC, p.id ASC",
        parameters=[{"name": "@n", "value": top_n}],
        enable_cross_partition_query=True)

    # logging.info("Query Result: " + str(list(query_result)))

    """
    myList = []

    for row in query_result:
        logging.info("ROW BEFORE:")
        logging.info(row)

        row["username"] = row["id"]
        row.pop("id")

        row["score"] = row["total_score"]
        row.pop("total_score")

        myList.append(row)
        logging.info("ROW AFTER: ")
        logging.info(row)

    # parsed_data = list(map(json.loads, a))

    #logging.info("Adjusted Query Result: " + str(list(query_result)))
    logging.info("My List: " + str(myList))
    
    """

    query_result_list = list(query_result)

    logging.info("Returning Following: ")
    logging.info(query_result_list)
    logging.info(type(query_result_list))
    return func.HttpResponse(body=json.dumps(query_result_list))
