import logging
from helper_functions import replace_container_item, check_timeslot_overlaps, Responses, get_object_attr, get_week_start_and_end, get_string_from_datetime, get_datetime_from_string
from helper_functions import ItemNotFoundException
from schema_validation import validate_availability_week

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a set availability request.')
    
    requester_uuid = req.headers.get('X-Request-UUID')
    try:
        user_object = get_object_attr(requester_uuid, None, 'employee_container')
    except ItemNotFoundException:
        return Responses.user_not_found(requester_uuid)

    req_body = req.get_json()
    if not validate_availability_week(req_body):
        return Responses.invalid_format()
    
    week_start = req_body.get('week_start')
    availabilities = req_body.get('availabilities')
    max_hours = req_body.get('max_hours')
    time_off = req_body.get('time_off')
    notes = req_body.get('notes')
    if notes is None:
        notes = ""
    default = req_body.get('default')
    
    (week_start, week_end) = get_week_start_and_end(week_start)
    
    week_start_str = get_string_from_datetime(week_start)
    week_start = get_datetime_from_string(week_start_str)
    week_end_str = get_string_from_datetime(week_end)
    week_end = get_datetime_from_string(week_end_str)
    
    # Check for overlaps
    checked_time_slots = []
    for time_slot in availabilities:
        if not check_timeslot_overlaps(time_slot, checked_time_slots):
            return Responses.time_slot_overlap()
        if not (week_start <= get_datetime_from_string(time_slot['start']) < get_datetime_from_string(time_slot['end']) <= week_end):
            return Responses.fail_message("time slot out of bounds")
        checked_time_slots.append(time_slot)
            
    new_availability_week = {
        'week_start': week_start_str,
        'availabilities': availabilities,
        'max_hours': max_hours,
        'time_off': time_off,
        'notes': notes,
        'approved': None,
        'current_hours': calculate_time_slot_total_hours(availabilities)
    }
    
    if default:
        user_object['default_availability'] = new_availability_week
        replace_container_item(user_object, 'employee_container')
    
    found = None
    for (index, current_week) in enumerate(user_object['manual_availability']):
        if current_week['week_start'] == week_start_str:
            found = index
            break
        
    if found is None:
        user_object['manual_availability'].append(new_availability_week)
    else:
        user_object['manual_availability'][found] = new_availability_week
       
    replace_container_item(user_object, 'employee_container')
    return Responses.success_message("availability set successfully")


def calculate_time_slot_total_hours(time_slots):
    total_seconds = 0
    for time_slot in time_slots:
        t_start = get_datetime_from_string(time_slot['start'])
        t_end = get_datetime_from_string(time_slot['end'])

        if t_start == False or t_end == False:
             raise Exception
        total_seconds += abs((t_end - t_start).total_seconds())
        
    return int(total_seconds/3600)
    