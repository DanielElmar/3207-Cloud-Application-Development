import logging
import json
from helper_functions import check_permission, Responses, get_object_attr, check_company_ids_match, get_datetime_from_string, get_string_from_datetime
from all_timetables import get_all_users_shifts
from get_availability import get_users_week_availability
from helper_functions import ItemNotFoundException, UserDoesNotExistException
from schema_validation import validate_auto_schedule
from auto_schedule_model import ShiftDayScheduler
from datetime import timedelta

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function to auto schedule shifts')

    requester_uuid = str(req.headers.get('X-Request-UUID'))
    if not check_permission(requester_uuid):
        return Responses.no_permissions()

    req_body = req.get_json()
    if not validate_auto_schedule(req_body):
        return Responses.invalid_format()
    
    uuids = req_body.get('uuids')
    location = req_body.get('location')
    week_start = req_body.get('week_start')
    operating_hours = req_body.get('operating_hours')
    min_employees = req_body.get('min_employees')
    max_employees = req_body.get('max_employees')
    min_shift_length = req_body.get('min_shift_length')
    max_shift_length = req_body.get('max_shift_length')

    #check if all uuids exist
    try:
        company_id = get_object_attr(requester_uuid, 'company_id', 'employee_container')
    except ItemNotFoundException:
        return Responses.user_not_found(requester_uuid)
    
    for uuid in uuids:
        try:
            if not check_company_ids_match(company_id, [uuid]):
                return Responses.company_id_mismatch()
        except UserDoesNotExistException:
            return Responses.user_not_found(uuid)
    
    #check if any uuids already have shifts in the given times
    for time_slot in operating_hours:
        all_user_shifts = json.loads(get_all_users_shifts(company_id, time_slot['start'], time_slot['end'], get_object_attr(company_id, 'positions', 'company_container'), [location], tuple(uuid for uuid in uuids)).get_body().decode("utf-8"))
        if len(all_user_shifts['shifts']) != 0:
            return Responses.time_slot_overlap
    segment_multiplier = 1 #1 hour = 1 segment (if mult = 2, 1 hour = 2 segments)

    #create maps of days->segments->employee_availability and employee->min/max weekly hours
    all_days, employees_to_hours = map_user_availability_to_operating_hours(uuids, week_start, operating_hours, segment_multiplier)

    #convert min/max shift length to segments
    if min_shift_length:
        min_shift_length = min_shift_length * segment_multiplier
    else:
        min_shift_length = 0

    if max_shift_length:
        max_shift_length = max_shift_length * segment_multiplier
    else:
        max_shift_length = 0

    if not min_employees:
        min_employees = 0
    if not max_employees:
        max_employees = 9999

    #input all data into model
    data = ShiftDayScheduler(min_employees, max_employees, all_days, employees_to_hours, min_shift_length, max_shift_length)
    if len(data) == 0:
        return func.HttpResponse(
            mimetype='application/json', 
            body=json.dumps({"msg": "no solutions"}), 
            status_code=400
        )

    #tranlate model output to shift objects
    solutions = []
    for solution in data:
        shifts = []
        for day_num, day in enumerate(solution):
            start_time = get_datetime_from_string(operating_hours[day_num]['start'])
            for employee_num, employee in enumerate(day):
                employee_start_segment = 0
                employee_end_segment = 0
                shift_detected = False
                for segment_worked in employee:
                    if (not shift_detected) and (not segment_worked):
                        employee_start_segment += 1
                        employee_end_segment += 1
                    elif (not shift_detected) and segment_worked:
                        shift_detected = True
                        employee_end_segment += 1
                    elif shift_detected and segment_worked:
                        employee_end_segment += 1
                    elif shift_detected and (not segment_worked):
                        shift_time_slot = {
                        'start': get_string_from_datetime(start_time + timedelta(hours=employee_start_segment/segment_multiplier)),
                        'end': get_string_from_datetime(start_time + timedelta(hours=employee_end_segment/segment_multiplier))
                        }
                        shift = {
                            'uuid': uuids[employee_num],
                            'time_slot': shift_time_slot,
                            'location': location
                        }
                        shifts.append(shift)
                        employee_end_segment += 1
                        employee_start_segment = employee_end_segment
                        shift_detected = False
                
                if shift_detected:
                    shift_time_slot = {
                        'start': get_string_from_datetime(start_time + timedelta(hours=employee_start_segment/segment_multiplier)),
                        'end': get_string_from_datetime(start_time + timedelta(hours=employee_end_segment/segment_multiplier))
                        }
                    
                    shift = {
                        'uuid': uuids[employee_num],
                        'time_slot': shift_time_slot,
                        'location': location
                    }
                    shifts.append(shift)
        solutions.append(shifts)

        return func.HttpResponse(
            mimetype='application/json', 
            body=json.dumps({"solutions": solutions}), 
            status_code=200
        )

#a function that maps user's availabilities onto bool arrays corresponding to operating_hours segments
def map_user_availability_to_operating_hours(uuids, week_start, operating_hours, segment_multiplier):
    all_days = []
    days_to_segments = []
    #converts datetime to segments and scaffolds availabilty arrays
    for time_slot in operating_hours:
        hours = divmod((get_datetime_from_string(time_slot['end']) - get_datetime_from_string(time_slot['start'])).total_seconds(), 3600)[0]
        days_to_segments.append(int(hours*segment_multiplier))
    for day in days_to_segments:
        all_days.append((day) * [None]) 
    #maps the user's availability onto the scaffolded segment arrays
    employees_to_hours = []
    for employee_num, uuid in enumerate(uuids):
        week_availability = get_users_week_availability(uuid, week_start)
        #if a user's availability is not set, it defaults to always available
        if week_availability['availability'] == None:
            employees_to_hours.append([week_availability['minimum_weekly_hours'], 9999])
            for day_num, day in enumerate(all_days):
                for segment_num, segment in enumerate(day):
                    if segment == None:
                        all_days[day_num][segment_num] = [True]
                    else:
                        all_days[day_num][segment_num].append(True)
        
        else:
            employees_to_hours.append([week_availability['minimum_weekly_hours'], week_availability['availability']['max_hours']])
            for day_num, day in enumerate(operating_hours):
                availability_map = []
                for availability in week_availability['availability']['availabilities']:
                    availability_map.append(map_segment_overlap(day, availability, segment_multiplier))
                segment_map = []
                for i in range(len(availability_map[0])):
                    segment_bool = False
                    for x in range(len(availability_map)):
                        segment_bool = segment_bool or availability_map[x][i]
                    segment_map.append(segment_bool)
                model_day = all_days[day_num]
                for segment_num, segment in enumerate(model_day):
                    if segment == None:
                        all_days[day_num][segment_num] = [segment_map[segment_num]]
                    else:
                        all_days[day_num][segment_num].append(segment_map[segment_num])
    
    return all_days, employees_to_hours

#function that maps if each segment of the base_time_slot is overlapped by the overlap_time_slot, returning an array of bools
def map_segment_overlap(base_time_slot, overlap_time_slot, segment_multiplier):
    segment_map = []
    segments = int(divmod((get_datetime_from_string(base_time_slot['end']) - get_datetime_from_string(base_time_slot['start'])).total_seconds(), 3600)[0] * segment_multiplier)
    segment_delta = timedelta(hours=(1/segment_multiplier))
    base_time_start = get_datetime_from_string(base_time_slot['start'])
    overlap_time_start = get_datetime_from_string(overlap_time_slot['start'])
    overlap_time_end = get_datetime_from_string(overlap_time_slot['end'])
    for i in range(segments):
        if(check_time_slot_overlap(base_time_start + (segment_delta*i), base_time_start + (segment_delta*(i+1)), overlap_time_start, overlap_time_end)):
            segment_map.append(True)
        else:
            segment_map.append(False)
    
    return segment_map

#function to check if two time slots overlap, returns a bool
def check_time_slot_overlap(time_slot_1_start, time_slot_1_end, time_slot_2_start, time_slot_2_end):
    latest_start = max(time_slot_1_start, time_slot_2_start)
    earliest_end = min(time_slot_1_end, time_slot_2_end)
    delta = (earliest_end - latest_start).total_seconds() + 1
    if delta > 0:
        return True
    return False