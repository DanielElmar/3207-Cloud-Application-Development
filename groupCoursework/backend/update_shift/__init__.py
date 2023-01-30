import logging
from schema_validation import validate_update_shift
from helper_functions import Responses, check_permission, replace_container_item, check_company_ids_match, get_users_company_object, get_object_attr, query_container, check_timeslot_overlaps
from helper_functions import UserDoesNotExistException, CompanyNotFoundException, ItemNotFoundException, TimeSlotFormatException

import azure.functions as func

# Denys
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function to update a user')

    requestee_uuid = req.headers.get('X-Request-UUID')
    try:
        if not check_permission(requestee_uuid):
            return Responses.no_permissions()
    except UserDoesNotExistException:
        return Responses.user_not_found(requestee_uuid)
    
    req_body = req.get_json()
    if not validate_update_shift(req_body):
        return Responses.invalid_format()
    
    shift_id = req_body.get('shift_id')
    time_slot = req_body.get('time_slot')
    location = req_body.get('location')
    
    try:
        shift_object = get_object_attr(shift_id, None, 'shift_container')
        company_object = get_users_company_object(requestee_uuid)
    except ItemNotFoundException:
        return Responses.item_not_found("shift")
    except CompanyNotFoundException:
        return Responses.item_not_found("user's company")
    except UserDoesNotExistException:
        return Responses.user_not_found(requestee_uuid)
    
    if location not in company_object['locations']:
        return Responses.item_not_found('location')
    
    if company_object['id'] != shift_object['company_id']:
        return Responses.company_id_mismatch()
    
    try:
        query = 'SELECT VALUE s.time_slot FROM shift s WHERE s.employee_id = @id'
        params = [{ "name":"@id", "value": shift_object['employee_id'] }]
        users_shifts = query_container(query, params, 'shift_container', filter=False)
    except:
        return Responses.item_not_found("shift's employee")
    
    try:
        if not check_timeslot_overlaps(time_slot, users_shifts):
            return Responses.time_slot_overlap()
    except TimeSlotFormatException:
        return Responses.invalid_time_slot_format()
    
    shift_object['location'] = location
    shift_object['time_slot'] = time_slot
    try:
        replace_container_item(shift_object, 'shift_container')
        return Responses.success_message("user updated successfully")
    except:
        return Responses.item_not_found("shift")
    