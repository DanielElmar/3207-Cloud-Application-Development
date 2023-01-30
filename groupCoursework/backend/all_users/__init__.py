import logging
from helper_functions import check_permission, Responses, get_users_company_object, query_container, get_object_attr, get_tuple_string
from helper_functions import UserDoesNotExistException, CompanyNotFoundException, ItemNotFoundException

import azure.functions as func

# Denys
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function to get all users')
    
    try:
        requester_uuid = req.headers.get('X-Request-UUID')
        if not check_permission(requester_uuid):
            return Responses.no_permissions()

        company_obj = get_users_company_object(requester_uuid)
        employee_ids = company_obj['employees']
        
        for employee_id in employee_ids:
            try:
                if get_object_attr(employee_id, 'company_id', 'employee_container') != company_obj['id']:
                    return Responses.internal_server_error(f"database inconsistency with user: '{employee_id}'")
            
            except ItemNotFoundException:
                return Responses.user_not_found(employee_id)
        
        logging.error("1")
        query = f"SELECT * FROM employee e WHERE e.id IN {get_tuple_string(employee_ids)}"
        logging.error("query: " + query)
        # params = [{ "name":"@ids", "value": + ")" }
        employee_objects = query_container(query, None, 'employee_container', filter=False)

        return Responses.success_dict({ "employees": employee_objects })
    
    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)

    except CompanyNotFoundException:
        return Responses.item_not_found("user's company")
