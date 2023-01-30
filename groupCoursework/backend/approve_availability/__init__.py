import logging
from helper_functions import get_users_company_object, check_permission, Responses, check_company_ids_match, get_string_from_datetime, get_week_start_and_end, get_object_attr, replace_container_item
from helper_functions import UserDoesNotExistException, CompanyNotFoundException, ItemNotFoundException
from schema_validation import validate_approve_availability
from get_availability import get_users_week_availability

import azure.functions as func

# Charlie
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed an add shift request.')

    try:
        requester_uuid = str(req.headers.get('X-Request-UUID'))
        if not check_permission(requester_uuid):
            return Responses.no_permissions()
        
        req_body = req.get_json()
        if not validate_approve_availability(req_body):
            return Responses.invalid_format()
        
        uuid = req_body.get('uuid')
        week_commencing = req_body.get('week_commencing')
        approved = req_body.get('approved')
                
        company_object = get_users_company_object(requester_uuid)
        
        try:
            if not check_company_ids_match(company_object['id'], [uuid]):
                return Responses.company_id_mismatch()
        except UserDoesNotExistException:
            return Responses.user_not_found(uuid)
        
        (week_start, _) = get_week_start_and_end(week_commencing)
        week_start = get_string_from_datetime(week_start)
        response = get_users_week_availability(uuid, week_start, return_default=True)
        users_week = response['availability']
        default = response['default']
        
        if users_week is None:
            return Responses.item_not_found("availability")
        users_week['approved'] = approved

        user_object = get_object_attr(uuid, None, 'employee_container')
        if default:
            user_object['default_availability'] = users_week
        else:
            found = None
            for (index, current_week) in enumerate(user_object['manual_availability']):
                if current_week['week_start'] == week_start:
                    found = index
                    break
            if found is None: user_object['manual_availability'].append(users_week)
            else: user_object['manual_availability'][found] = users_week
        
        try:
            replace_container_item(user_object, 'employee_container')
        except:
            return Responses.internal_server_error("something went wrong updating the database")
            
        return Responses.success_message("shift approved successfully")

    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
    
    except CompanyNotFoundException:
        return Responses.item_not_found("user's company")
    
    except ItemNotFoundException:
        return Responses.user_not_found(uuid)
        