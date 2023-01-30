import logging
from helper_functions import get_users_company_object, check_permission, Responses, delete_container_item_by_id, check_company_ids_match, replace_container_item, get_object_attr
from helper_functions import UserDoesNotExistException, CompanyNotFoundException, ItemNotFoundException
from schema_validation import validate_string

import azure.functions as func

# Charlie
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed an delete position request.')

    try:
        requester_uuid = str(req.headers.get('X-Request-UUID'))
        if not check_permission(requester_uuid):
            return Responses.no_permissions()
        
        req_body = req.get_json()
        if not validate_string(req_body, 'uuid'):
            return Responses.invalid_format()
        
        uuid = req_body.get('uuid')
        company_object = get_users_company_object(requester_uuid)
        
        try:
            if not check_company_ids_match(company_object['id'], [uuid]):
                return Responses.company_id_mismatch()
        except UserDoesNotExistException:
            return Responses.user_not_found(uuid)
        
        user_email = get_object_attr(uuid, 'email', 'employee_container')
        delete_container_item_by_id(uuid, 'employee_container')
        
        delete_container_item_by_id(user_email, 'credential_container')
        
        company_object['employees'].remove(uuid)
        replace_container_item(company_object, 'company_container')
        return Responses.success_message('user deleted successfully')

    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
    
    except CompanyNotFoundException:
        return Responses.item_not_found("user's company")
    
    except ItemNotFoundException:
        return Responses.user_not_found(uuid)
    