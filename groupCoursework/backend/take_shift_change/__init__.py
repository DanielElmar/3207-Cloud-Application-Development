import logging
from helper_functions import check_permission, Responses, check_company_ids_match, get_object_attr, replace_container_item
from helper_functions import UserDoesNotExistException, ItemNotFoundException
from schema_validation import validate_reassign_shift

import azure.functions as func

# Charlie
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a reassign shift request.')

    try:
        requester_uuid = str(req.headers.get('X-Request-UUID'))
        if not check_permission(requester_uuid):
            return Responses.no_permissions()
        
        req_body = req.get_json()
        if not validate_reassign_shift(req_body, 'shift_id'):
            return Responses.invalid_format()
        
        shift_id = req_body.get('shift_id')
        shift_object = get_object_attr(shift_id, None, 'shift_container')
        
        if not check_company_ids_match(shift_object['company_id'], [requester_uuid]):
            return Responses.company_id_mismatch()
        
        shift_object['prev_owners'].append(shift_object['employee_id'])
        shift_object['employee_id'] = requester_uuid
        shift_object['cover'] = False
        
        replace_container_item(shift_object, 'shift_container')
        return Responses.success_message("shift swapped successfully")
        
    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
    
    except ItemNotFoundException:
        return Responses.item_not_found('shift')
    