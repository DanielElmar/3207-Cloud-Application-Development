import logging
from helper_functions import get_users_company_object, check_permission, Responses, replace_container_item
from helper_functions import UserDoesNotExistException, CompanyNotFoundException
from schema_validation import validate_string

import azure.functions as func

# Charlie
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed an add location request.')

    try:
        requester_uuid = str(req.headers.get('X-Request-UUID'))
        if not check_permission(requester_uuid):
            return Responses.no_permissions()
        
        req_body = req.get_json()
        if not validate_string(req_body, 'location'):
            return Responses.invalid_format()
        
        location = req_body.get('location')
              
        company_object = get_users_company_object(requester_uuid)
        if location in company_object['locations']:
            return Responses.item_already_exists('location')
        
        company_object['locations'].append(location)
        replace_container_item(company_object, 'company_container')
        return Responses.success_message('location added successfully')

    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
    
    except CompanyNotFoundException:
        return Responses.item_not_found("user's company")
    