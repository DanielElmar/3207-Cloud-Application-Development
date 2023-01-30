# import logging
# import json
# from helper_functions import check_users_exist, query_container, replace_container_item
# from schema_validation import validate_time_slot
from helper_functions import Responses
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    return Responses.not_implemented()
#     logging.info('Python HTTP trigger function processed a delete availability request.')

#     try:
#         requester_uuid = req.headers.get('X-Request-UUID')

#         req_body = req.get_json()
#         uuid = req_body.get('uuid')
#         time_slot_strs = req_body.get('time_slot')
        
#         uuid_check = check_users_exist([uuid])
#         if uuid_check is not None:
#             return uuid_check
        
#         if not validate_time_slot(time_slot_strs):
#             raise Exception("time slot is in an invalid format")

#         user_object = query_container(f"SELECT VALUE e FROM employee e WHERE e.id = '{uuid}'", 'employee_container')[0]
        
#         if time_slot_strs not in user_object['contract']['availability']:
#             return func.HttpResponse(
#                 mimetype='application/json', 
#                 body=json.dumps({"msg": "time slot not found"}), 
#                 status_code=400
#             )
        
#         user_object['contract']['availability'].remove(time_slot_strs)
#         replace_container_item(user_object, 'employee_container')
        
#         return func.HttpResponse(
#             mimetype='application/json', 
#             body=json.dumps({"msg": "availability deleted successfully"}), 
#             status_code=200
#         )
                   
#     except Exception as e:
#         logging.info("Something went wrong in processing delete availability")
#         logging.error(e)
#         return func.HttpResponse(
#             mimetype='application/json', 
#             body=json.dumps({"msg": "invalid request format"}), 
#             status_code=400
#         )