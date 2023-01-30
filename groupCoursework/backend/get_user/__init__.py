import logging
import schema_validation
from helper_functions import check_permission, Responses, get_object_attr
from helper_functions import UserDoesNotExistException, ItemNotFoundException

import azure.functions as func

# Denys
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function to get a user')

    try:
        requester_uuid = req.headers.get('X-Request-UUID')
        
        req_body = req.get_json()
        if not schema_validation.validate_string(req_body, 'uuid'):
            return Responses.invalid_format()

        uuid = req_body.get('uuid')
        
        if (uuid != requester_uuid) and (not check_permission(requester_uuid)):
            return Responses.no_permissions()
        
        try:
            user_object = get_object_attr(uuid, None, 'employee_container')
        except ItemNotFoundException:
            return Responses.user_not_found(uuid)
        
        return Responses.success_dict({ 'information': user_object })
    
    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
    