import logging
from helper_functions import check_permission, Responses, delete_container_item_by_id, get_object_attr, check_company_ids_match
from helper_functions import UserDoesNotExistException, ItemNotFoundException
from schema_validation import validate_string

import azure.functions as func

# Charlie
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a delete shift request.')

    try:
        requester_uuid = str(req.headers.get('X-Request-UUID'))
        if not check_permission(requester_uuid):
            return Responses.no_permissions()
        
        req_body = req.get_json()
        if not validate_string(req_body, 'shift_id'):
            return Responses.invalid_format()
        
        shift_id = req_body.get('shift_id')
        if not check_company_ids_match(get_object_attr(shift_id, 'company_id', 'shift_container'), [requester_uuid]):
            return Responses.company_id_mismatch()
        
        delete_container_item_by_id(shift_id, 'shift_container')
        return Responses.success_message("shift deleted successfully")

    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
    
    except ItemNotFoundException:
        return Responses.item_not_found('shift')
    