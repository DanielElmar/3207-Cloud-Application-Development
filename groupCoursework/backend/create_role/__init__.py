# import logging
# import json
# import schema_validation
from helper_functions import Responses

import azure.functions as func

# # Denys
def main(req: func.HttpRequest) -> func.HttpResponse:
    return Responses.not_implemented()
#     logging.info('Python HTTP trigger function to create a role')

#     requestee_uuid = req.headers.get('X-Request-UUID')
#     req_body = req.get_json()

#     #validate req_body
#     if(not schema_validation.validate_role(req_body)):
#         return func.HttpResponse(
#             mimetype='application/json',
#             status_code= 400,
#             body= json.dumps( {"msg": "invalid request format"} )
#         )   

#     if(not helper_functions.check_permission(requestee_uuid, 'create_role')): # 'create_role' is a placeholder, redundant until roles come into effect
#         return func.HttpResponse(
#             mimetype='application/json',
#             status_code= 403,
#             body= json.dumps( {"msg": "no permissions"} )
#         )
    
#     companyId = helper_functions.query_container(f"SELECT * FROM r WHERE r.id='{requestee_uuid}'", 'employee_container')[0]['company_id']
#     company = helper_functions.query_container(f"SELECT * FROM r WHERE r.id='{companyId}'", 'company_container')[0]
#     for x in company['roles']:
#         if x['name'] == req_body.get('name'):
#             return func.HttpResponse(
#                 mimetype='application/json',
#                 status_code= 401,
#                 body= json.dumps( {"msg": "role name already exists"} )
#             ) 
    
#     company['roles'].append(req_body)
#     helper_functions.replace_container_item(company, 'company_container')
#     return func.HttpResponse(
#         mimetype='application/json',
#         status_code= 200,
#         body= json.dumps( {"msg": "created successfully"} )
#     ) 