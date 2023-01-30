import logging
import schema_validation
from helper_functions import Responses, check_permission, replace_container_item, check_company_ids_match, get_users_company_object, get_object_attr
from helper_functions import UserDoesNotExistException, CompanyNotFoundException, ItemNotFoundException

import azure.functions as func

# Denys
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function to update a user')

    requestee_uuid = req.headers.get('X-Request-UUID')
    req_body = req.get_json()

    #validate req_body
    information = req_body.get("information")
    if not schema_validation.validate_employee(information):
        return Responses.invalid_format()

    try:
        if (information['id'] != requestee_uuid and not check_permission(requestee_uuid)):
            return Responses.no_permissions()
    except UserDoesNotExistException:
        return Responses.user_not_found(requestee_uuid)
    
    try:
        if not check_company_ids_match(get_users_company_object(requestee_uuid)['id'], [information['id']]):
            return Responses.company_id_mismatch()
    except UserDoesNotExistException:
        return Responses.user_not_found(information['id'])
    except CompanyNotFoundException:
        return Responses.item_not_found("user's company")
    
    try:
        if get_object_attr(information['id'], 'email', 'employee_container') != information['email']:        
            return Responses.fail_message("user's email can't be changed")
    except ItemNotFoundException:
        return Responses.user_not_found(information['id'])
    
    try:
        replace_container_item(information, 'employee_container')
        return Responses.success_message("user updated successfully")
    except:
        return Responses.user_not_found(information['id'])
    