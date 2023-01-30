import logging
from get_availability import get_users_week_availability
from helper_functions import Responses, check_permission, get_week_start_and_end, get_users_company_object, get_object_attr, get_string_from_datetime
from helper_functions import UserDoesNotExistException, CompanyNotFoundException, ItemNotFoundException
from schema_validation import validate_get_unapproved_availabilities

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a get unapproved availabilities request.')

    try:
        requester_uuid = req.headers.get('X-Request-UUID')
        company_object = get_users_company_object(requester_uuid)
        
        if not check_permission(requester_uuid):
            return Responses.no_permissions()
        
    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
    except CompanyNotFoundException:
        return Responses.item_not_found("user's company")
    
    req_body = req.get_json()
    if not validate_get_unapproved_availabilities(req_body):
        return Responses.invalid_format()
    
    (week_start, _) = get_week_start_and_end(req_body.get('week_commencing'))
    
    return_list = []
    try:
        for user in company_object['employees']:
            response = get_users_week_availability(user, get_string_from_datetime(week_start))
            
            if type(response) is func.HttpResponse:  # The user was not found
                return Responses.internal_server_error("database inconsistency")
            
            if response['availability'] is None:
                continue
            
            if response['availability']['approved'] is None:
                response['id'] = user
                response['first_name'] = get_object_attr(user, 'first_name', 'employee_container')
                response['last_name'] = get_object_attr(user, 'last_name', 'employee_container')
                return_list.append(response)
                
    except ItemNotFoundException:
        return Responses.internal_server_error("database inconsistency")
    
    return Responses.success_dict(return_list)
