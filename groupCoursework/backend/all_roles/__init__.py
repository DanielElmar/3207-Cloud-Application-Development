# import logging
# import json
from helper_functions import Responses

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    return Responses.not_implemented()
#     logging.info('Python HTTP trigger function to create a role')

#     requestee_uuid = req.headers.get('X-Request-UUID')

#     if(not helper_functions.check_permission(requestee_uuid, 'delete_role')): # 'delete_role' is a placeholder, redundant until roles come into effect
#         return func.HttpResponse(
#             mimetype='application/json',
#             status_code= 403,
#             body= json.dumps( {"msg": "no permissions"} )
#         )
    
#     companyId = helper_functions.query_container(f"SELECT * FROM r WHERE r.id='{requestee_uuid}'", 'employee_container')[0]['company_id']
#     company = helper_functions.query_container(f"SELECT * FROM r WHERE r.id='{companyId}'", 'company_container')[0]

#     return func.HttpResponse(
#         mimetype='application/json',
#         status_code= 200,
#         body= json.dumps( { "roles": company['roles']} )
#     ) 
