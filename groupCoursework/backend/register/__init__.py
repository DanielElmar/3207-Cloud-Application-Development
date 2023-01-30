import logging
import json
import hashlib
import os
import random

from schema_validation import validate_register
from helper_functions import Responses, get_object_attr, create_container_item

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request to create a new admin user and comapny.')

    req_body = req.get_json()
    if not validate_register(req_body):
        return Responses.invalid_format()
    
    email = req_body.get('email').lower()
    password = req_body.get('password')
    company_name = req_body.get('company_name')
    first_name = req_body.get('first_name')
    last_name = req_body.get('last_name')
    telephone = req_body.get('telephone')
    address = req_body.get('address')
    
    try:
        # Raises exeption if no email exists with that id
        get_object_attr(email, None, 'credential_container')
        return Responses.item_already_exists("email")
    except:
        pass
    
    #hash password
    salt = os.urandom(32)
    hashedPass = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 10000)
    
    #generate random id
    while(True):
        employee_id = str(random.randint(1, 1000000000000))
        try:
            # Raises exeption if no user exists with that id
            get_object_attr(employee_id, None, 'employee_container')
        except:
            break
    
    #generate random company id
    while(True):
        company_id = str(random.randint(1, 1000000000000))
        try:
            # Raises exeption if no companies exist with that id
            get_object_attr(company_id, None, 'company_container')
        except:
            break

    try:
        create_container_item({
            'id': email,
            'password': hashedPass.hex(),
            'salt': salt.hex(),
            'employee_id': employee_id
        }, 'credential_container')
        
        create_container_item({
            'id': employee_id,
            'positions': [],
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'telephone': telephone,
            'address': address,
            'manual_availability' : [],
            'default_availability' : None,
            'minimum_weekly_hours' : 0,
            'company_id' : company_id,
            'company_name': company_name,
            'admin' : True
        }, 'employee_container')
        
        create_container_item({
            'id' : company_id,
            'company_name' : company_name,
            'locations' : [],
            'employees' : [employee_id],
            'positions' : []
        }, 'company_container')

        return Responses.success_dict({
            "id": employee_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "company_name": company_name
        })
    
    except:
        return Responses.internal_server_error("items could not be added to database")
    