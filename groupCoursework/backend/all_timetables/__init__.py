import logging
from helper_functions import Responses, check_permission, query_container, get_users_company_object, get_tuple_string
from helper_functions import UserDoesNotExistException, CompanyNotFoundException
from schema_validation import validate_get_timetable, validate_time_slot

import azure.functions as func


# Charlie
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for all timetables.')

    try:
        requester_uuid = req.headers.get('X-Request-UUID')
        if not check_permission(requester_uuid):
            return Responses.no_permissions()

        req_body = req.get_json()
        if not validate_get_timetable(req_body):
            return Responses.invalid_format()
        
        time_start = req_body.get('time_start')
        time_end = req_body.get('time_end')
        positions = req_body.get('positions')
        locations = req_body.get('locations')
                
        return get_all_users_shifts(get_users_company_object(requester_uuid)['id'], time_start, time_end, positions, locations)
    
    except UserDoesNotExistException:
        return Responses.user_not_found(requester_uuid)
    
    except CompanyNotFoundException:
        return Responses.item_not_found("user's company")

        
def get_all_users_shifts(company_id, time_start, time_end, positions, locations, uuids_to_filter=None, cover_only=False, return_dict=False):
    if not validate_time_slot({'start': time_start, 'end': time_end}):
        return Responses.invalid_time_slot_format()

    query = "SELECT * FROM shifts s WHERE (s.company_id = @company_id) AND "
    start_time_q = "(s.time_slot['start'] BETWEEN @time_start AND @time_end)"
    end_time_q = " AND (s.time_slot['end'] BETWEEN @time_start AND @time_end)"
    
    ids_tuple = get_tuple_string(uuids_to_filter) if uuids_to_filter is not None else ""
    ids_q = f"s.employee_id IN {ids_tuple} AND "
    
    positions_tuple = get_tuple_string(positions)
    positons_q = f" AND s.positon IN {positions_tuple}"
    
    locations_tuple = get_tuple_string(locations)
    locations_q = f" AND s.location IN {locations_tuple}"
    
    params = [
        { "name":"@company_id", "value": company_id },
        { "name":"@time_start", "value": time_start },
        { "name":"@time_end", "value": time_end }
    ]
    
    if uuids_to_filter is not None:
        query = query + ids_q
    
    query = query + start_time_q + end_time_q
    
    if len(positions) != 0:
        query = query + positons_q
    if len(locations) != 0:
        query = query + locations_q
    if cover_only:
        query = query + " AND (s.cover = true)"
    
    logging.error(query)
    
    response_dict = query_container(query, params, 'shift_container', filter=False)
    if return_dict:
        return(response_dict)
    return Responses.success_dict({"shifts": response_dict})
