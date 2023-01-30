import logging
from helper_functions import Responses, replace_container_item, get_object_attr
from helper_functions import UserDoesNotExistException, CompanyNotFoundException, TimeSlotFormatException
from schema_validation import validate_shift_advertisement

import azure.functions as func

# Charlie
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed an add shift request.')

    try:
        requester_uuid = str(req.headers.get('X-Request-UUID'))
        
        req_body = req.get_json()
        if not validate_shift_advertisement(req_body):
            return Responses.invalid_format()
        
        available = req_body.get('available')
        shift_id = req_body.get('shift_id')
        
        shift = get_object_attr(shift_id, None, 'shift_container')
        if shift['employee_id'] != requester_uuid:
            return Responses.no_permissions()

        shift['cover'] = available
        replace_container_item(shift, 'shift_container')  
        return Responses.success_message("shift added successfully")

    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
    
    except CompanyNotFoundException:
        return Responses.item_not_found("user's company")
    
    except TimeSlotFormatException:
        return Responses.invalid_time_slot_format()
        