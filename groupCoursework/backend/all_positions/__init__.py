import logging
from helper_functions import get_users_company_object, Responses
from helper_functions import UserDoesNotExistException, CompanyNotFoundException

import azure.functions as func

# Charlie
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a get positions request.')

    try:
        requester_uuid = req.headers.get('X-Request-UUID')
        # Check user permissions not required
        
        company_object = get_users_company_object(requester_uuid)
        return Responses.success_dict({'positions': company_object['positions']})
                                   
    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
    
    except CompanyNotFoundException:
        return Responses.item_not_found("user's company")
