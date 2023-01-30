import logging
from helper_functions import get_users_company_object, check_permission, Responses, replace_container_item
from helper_functions import UserDoesNotExistException, CompanyNotFoundException
from schema_validation import validate_string


import azure.functions as func

# Charlie
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed an add position request.')

    try:
        requester_uuid = str(req.headers.get('X-Request-UUID'))
        if not check_permission(requester_uuid):
            return Responses.no_permissions()
        
        req_body = req.get_json()        
        if not validate_string(req_body, 'position'):
            return Responses.invalid_format()
            
        position = req_body.get('position')
              
        company_object = get_users_company_object(requester_uuid)
        if position in company_object['positions']:
            return Responses.item_already_exists('position')
        
        company_object['positions'].append(position)
        replace_container_item(company_object, 'company_container')
        return Responses.success_message('position added successfully')

    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
    
    except CompanyNotFoundException:
        return Responses.item_not_found("user's company")
    