import logging
from helper_functions import get_week_start_and_end, check_permission, check_company_ids_match, Responses, get_object_attr, change_time_slot_weeks, get_string_from_datetime
from helper_functions import UserDoesNotExistException, CompanyNotFoundException, ItemNotFoundException
from schema_validation import validate_get_availability

import azure.functions as func

# Charlie
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for get availability.')

    try:
        requester_uuid = req.headers.get('X-Request-UUID')

        req_body = req.get_json()
        if not validate_get_availability(req_body):
            return Responses.invalid_format()
        
        uuid = req_body.get('uuid')
        week_to_get_str = req_body.get('week_commencing')
        
        if uuid != requester_uuid:
            if not check_permission:
                return Responses.no_permissions()
            try:
                if not check_company_ids_match(get_object_attr(requester_uuid, 'company_id', 'employee_container'), [uuid]):
                    return Responses.company_id_mismatch()
            except UserDoesNotExistException:
                return Responses.user_not_found(uuid)
            except ItemNotFoundException:
                return Responses.internal_server_error(f"user has no company id association: {requester_uuid}")
            
        (week_start, _) = get_week_start_and_end(week_to_get_str)
        
        response = get_users_week_availability(uuid, get_string_from_datetime(week_start))
        if type(response) is func.HttpResponse:
            return response
        return Responses.success_dict(response)
                    
    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
    
    except CompanyNotFoundException:
        return Responses.item_not_found("user's company")


def get_users_week_availability(uuid, week_start, return_default=False):
    try:
        user_object = get_object_attr(uuid, None, 'employee_container')
    except ItemNotFoundException:
        return Responses.user_not_found(uuid)
            
    availability = None
    for week in user_object['manual_availability']:
        if week['week_start'] == week_start:
            availability = week
            break
    
    default_availability = user_object['default_availability']
    if (availability is not None) or (default_availability is None):
        if return_default:
            return { 'availability': availability, 'minimum_weekly_hours': user_object['minimum_weekly_hours'], 'default': False }
        return { 'availability': availability, 'minimum_weekly_hours': user_object['minimum_weekly_hours'] }

    # Adapt default_availability to this week
    new_time_slots = change_time_slot_weeks(default_availability['week_start'], default_availability['availabilities'], week_start)
    default_availability['week_start'] = week_start
    default_availability['availabilities'] = new_time_slots
    if return_default:
        return { 'availability': default_availability, 'minimum_weekly_hours': user_object['minimum_weekly_hours'], 'default': True }
    return { 'availability': default_availability, 'minimum_weekly_hours': user_object['minimum_weekly_hours'] }
