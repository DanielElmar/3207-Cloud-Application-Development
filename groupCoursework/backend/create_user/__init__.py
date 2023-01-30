import logging
import hashlib
import random
import os
from schema_validation import validate_create_user
from helper_functions import check_permission, Responses, query_container, get_users_company_object, create_container_item, replace_container_item, get_object_attr
from helper_functions import UserDoesNotExistException, CompanyNotFoundException

import azure.functions as func

# Denys
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request to create a new user')

    try:
        requester_uuid = req.headers.get('X-Request-UUID')
        if not check_permission(requester_uuid):
            return Responses.no_permissions()
        
        req_body = req.get_json()
        if not validate_create_user(req_body):
            return Responses.invalid_format()

        email = req_body.get('email').lower()
        positions = req_body.get('positions')
        first_name = req_body.get('first_name')
        last_name = req_body.get('last_name')
        telephone = req_body.get('telephone')
        address = req_body.get('address')
        starting_pass = req_body.get('starting_pass')
        minimum_weekly_hours = req_body.get('minimum_weekly_hours')
        
        company_object = get_users_company_object(requester_uuid)
        
        email_query = "SELECT * FROM r WHERE r.id=@id"
        email_params = [{ "name":"@id", "value": email }]
        if len(query_container(email_query, email_params, 'credential_container')) != 0:
            return Responses.item_already_exists("email")

        for position in positions:
            if position not in company_object['positions']:
                return Responses.item_not_found(f"position '{position}'")

        # hash password
        salt = os.urandom(32)
        hashedPass = hashlib.pbkdf2_hmac('sha256', starting_pass.encode(), salt, 10000)

        # generate random id
        while(True):
            employee_id = str(random.randint(1, 1000000000000))
            try:
                # Raises exeption if no user exists with that id
                get_object_attr(employee_id, None, 'employee_container')
            except:
                break
    
        create_container_item({
            'id': email,
            'password': hashedPass.hex(),
            'salt': salt.hex(),
            'employee_id': employee_id
        }, 'credential_container')
        
        create_container_item({
            'id': employee_id,
            'positions': positions,
            'company_id' : company_object['id'],
            'company_name': company_object['company_name'],
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'telephone': telephone,
            'address': address,
            'manual_availability': [],
            'default_availability': None,
            'minimum_weekly_hours': minimum_weekly_hours, 
            'admin': False
        }, 'employee_container')
        
        company_object['employees'].append(employee_id)
        replace_container_item(company_object, 'company_container')
        return Responses.success_message("user created successfully")
    
    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
    
    except CompanyNotFoundException:
        return Responses.item_not_found("user's company")
