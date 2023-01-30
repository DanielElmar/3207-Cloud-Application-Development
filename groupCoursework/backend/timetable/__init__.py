import logging

import azure.functions as func
from all_timetables import get_all_users_shifts
from helper_functions import check_permission, Responses, get_object_attr, check_company_ids_match
from helper_functions import UserDoesNotExistException, ItemNotFoundException
from schema_validation import validate_get_timetable

# Charlie
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for all timetables.')

    requester_uuid = req.headers.get('X-Request-UUID')

    req_body = req.get_json()
    if not validate_get_timetable(req_body):
        return Responses.invalid_format()
    
    uuids = req_body.get('uuids')
    time_start = req_body.get('time_start')
    time_end = req_body.get('time_end')
    positions = req_body.get('positions')
    locations = req_body.get('locations')
    
    try:
        if any(x != requester_uuid for x in uuids) and not check_permission(requester_uuid):
            return Responses.no_permissions()
    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
        
    try:
        company_id = get_object_attr(requester_uuid, 'company_id', 'employee_container')
    except ItemNotFoundException:
        return Responses.user_not_found(requester_uuid)
    
    for uuid in uuids:
        try:
            if not check_company_ids_match(company_id, [uuid]):
                return Responses.company_id_mismatch()
        except UserDoesNotExistException:
            return Responses.user_not_found(uuid)
                        
    return get_all_users_shifts(company_id, time_start, time_end, positions, locations, tuple(uuid for uuid in uuids))
        