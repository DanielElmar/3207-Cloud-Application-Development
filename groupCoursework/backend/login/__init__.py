import logging
import hashlib
import schema_validation
from helper_functions import Responses, query_container, get_object_attr
from helper_functions import ItemNotFoundException

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request to login a user.')

    req_body = req.get_json()
    if not schema_validation.validate_login_credentials(req_body):
        return Responses.invalid_format()
    
    email = req_body.get('email').lower()
    password = req_body.get('password')

    query="SELECT VALUE cr FROM credentials cr WHERE cr.id = @id"
    params=[{ "name":"@id", "value": email }]
    credentials_object_list = query_container(query, params, 'credential_container', filter=False)

    if len(credentials_object_list) == 0:
        return Responses.item_not_found("email or password incorrect")
    
    user_credentials = credentials_object_list[0]
    salt = bytearray.fromhex(user_credentials["salt"])
    hashedPass = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 10000)

    if hashedPass.hex() != user_credentials["password"]:
        return Responses.item_not_found("email or password incorrect")

    try:
        employee_object = get_object_attr(user_credentials['employee_id'], None, 'employee_container')
    except ItemNotFoundException:
        return Responses.user_not_found(user_credentials['employee_id'])

    return Responses.success_dict({
        "id": employee_object['id'],
        "first_name": employee_object['first_name'],
        "last_name": employee_object['last_name'],
        "email": email,
        "company_name": employee_object['company_name'],
        "admin": employee_object['admin']
    })
