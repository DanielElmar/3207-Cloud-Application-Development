import logging
import random
from helper_functions import get_object_attr, get_users_company_object, check_permission, Responses, check_timeslot_overlaps, create_container_item, check_company_ids_match, query_container
from helper_functions import UserDoesNotExistException, CompanyNotFoundException, TimeSlotFormatException
from schema_validation import validate_add_shift

import azure.functions as func

# Charlie
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed an add shift request.')

    try:
        requester_uuid = str(req.headers.get('X-Request-UUID'))
        if not check_permission(requester_uuid):
            return Responses.no_permissions()
        
        req_body = req.get_json()
        if not validate_add_shift(req_body):
            return Responses.invalid_format()
        
        uuid = req_body.get('uuid')
        time_slot = req_body.get('time_slot')
        location = req_body.get('location')
                
        company_object = get_users_company_object(requester_uuid)
        
        try:
            if not check_company_ids_match(company_object['id'], [uuid]):
                return Responses.company_id_mismatch()
        except UserDoesNotExistException:
            return Responses.user_not_found(uuid)

        if location not in company_object['locations']:
            return Responses.item_not_found('location')
        
        query = 'SELECT VALUE s.time_slot FROM shift s WHERE s.employee_id = @id'
        params = [{ "name":"@id", "value": uuid }]
        users_shifts = query_container(query, params, 'shift_container', filter=False)
                
        if not check_timeslot_overlaps(time_slot, users_shifts):
            return Responses.time_slot_overlap()
                
        while(True):
            shift_id = str(random.randint(1, 1000000000000))
            try:
                # Raises exeption if no user exists with that id
                get_object_attr(shift_id, None, 'employee_container')
            except:
                break

        create_container_item({
            'id': shift_id,
            'employee_id': uuid,
            'company_id': company_object['id'],
            'time_slot': time_slot,
            'location': location,
            'cover': False,
            'prev_owners': []
        }, 'shift_container')
                
        return Responses.success_message("shift added successfully")

    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
    
    except CompanyNotFoundException:
        return Responses.item_not_found("user's company")
    
    except TimeSlotFormatException:
        return Responses.invalid_time_slot_format()
        