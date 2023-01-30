import logging
from all_timetables import get_all_users_shifts
from helper_functions import get_week_start_and_end, get_users_company_object, Responses, get_string_from_datetime
from helper_functions import UserDoesNotExistException, CompanyNotFoundException
from schema_validation import validate_get_unapproved_availabilities

import azure.functions as func

# Charlie
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for get trading board.')

    try:
        requester_uuid = req.headers.get('X-Request-UUID')

        req_body = req.get_json()
        if not validate_get_unapproved_availabilities(req_body):
            return Responses.invalid_format()
        
        week_to_get_str = req_body.get('week_commencing')
        company_object = get_users_company_object(requester_uuid)
        
        (week_start, week_end) = get_week_start_and_end(week_to_get_str)
        
        timetable = get_all_users_shifts(company_object['id'], get_string_from_datetime(week_start), get_string_from_datetime(week_end), [], [], uuids_to_filter=[requester_uuid], return_dict=True)
        
        coverable_shifts = get_all_users_shifts(company_object['id'], get_string_from_datetime(week_start), get_string_from_datetime(week_end), [], [], cover_only=True, return_dict=True)
        coverable_shifts = list(filter(lambda x: x['employee_id'] != requester_uuid, coverable_shifts))
        
        return Responses.success_dict({
            'week_commencing': get_string_from_datetime(week_start),
            'my_shifts': timetable,
            'cover_shifts': coverable_shifts
        })
                    
    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
    
    except CompanyNotFoundException:
        return Responses.item_not_found("user's company")
