from schema import Schema, And, Optional
from helper_functions import get_datetime_from_string
import re

_employee_id_obj = str
_valid_ISOformat_string = lambda x: get_datetime_from_string(x) != False
_email_regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
_email_obj = And(str, lambda x: re.fullmatch(_email_regex, x), lambda x: len(x) <= 64)


def validate_time_slot(data) -> bool:
    """ Returns false if start and end are equal """
    start_ISO = get_datetime_from_string(data['start'])
    end_ISO = get_datetime_from_string(data['end'])
    
    if not (start_ISO == False or end_ISO == False or start_ISO >= end_ISO):
        return True

    return False


def validate_string(data, key) -> bool:
    return Schema({
        key: str
    }).is_valid(data)
    

def validate_add_shift(data) -> bool:
    return Schema({
        'uuid': _employee_id_obj,
        'time_slot': lambda x: validate_time_slot(x),
        'location': str
    }).is_valid(data)
    
    
def validate_approve_availability(data) -> bool:
    return Schema({
        'uuid': _employee_id_obj,
        'week_commencing': _valid_ISOformat_string,
        'approved': bool
    }).is_valid(data)


def validate_get_timetable(data) -> bool:
    return Schema({
        Optional('uuids'): [str],
        'time_start': _valid_ISOformat_string,
        'time_end': _valid_ISOformat_string,
        'positions': [str],
        'locations': [str]
    }).is_valid(data)


def validate_login_credentials(data) -> bool:
    return Schema({
        'email': _email_obj,
        'password': And(str, lambda x: 8 <= len(x) <= 64),
    }).is_valid(data)
    

def validate_get_unapproved_availabilities(data) -> bool:
    return Schema({
        'week_commencing': _valid_ISOformat_string
    }).is_valid(data)
    

def validate_get_availability(data) -> bool:
    return Schema({
        'uuid': _employee_id_obj,
        'week_commencing': _valid_ISOformat_string
    }).is_valid(data)


def validate_reassign_shift(data) -> bool:
    return Schema({
        'shift_id': str,
        'coverer_uuid': _employee_id_obj
    }).is_valid(data)
    

def validate_register(data) -> bool:
    return Schema({
        'email': _email_obj,
        'password': And(str, lambda x: 8 <= len(x) <= 64),
        'company_name': str,
        'first_name': str,
        'last_name': str,
        'telephone': str,
        'address': str
    }).is_valid(data)


def validate_shift_advertisement(data) -> bool:
    return Schema({
        'shift_id': str,
        'available': bool    
    }).is_valid(data)
    

def validate_time_off(data) -> bool:
    return Schema({
        'amount': int,
        'pay_type': str,
        'notes': str
    }).is_valid(data)


def validate_availability_week(data) -> bool:
    return Schema({
        'week_start': _valid_ISOformat_string,
        'availabilities': lambda x: all(validate_time_slot(y) for y in x),
        'max_hours': int,
        'time_off': lambda x: all(validate_time_off(y) for y in x),
        'notes': str,
        'default': bool
    }).is_valid(data)


def validate_update_shift(data) -> bool:
    return Schema({
        'shift_id': str,
        'time_slot': lambda x: validate_time_slot(x),
        'location': str
    }).is_valid(data)


def validate_create_user(data) -> bool:
    return Schema({
        'email': _email_obj,
        'starting_pass': And(str, lambda x: 8 <= len(x) <= 64),
        'positions': [str],
        'first_name': str,
        'last_name': str,
        'telephone': str,
        'address': str,
        'minimum_weekly_hours': int
    }).is_valid(data)


def validate_employee(data) -> bool:
    return Schema({
        'id': _employee_id_obj,
        'positions': [str],
        'first_name': str,
        'last_name': str,
        'email': _email_obj,
        'telephone': str,
        'manual_availability': lambda x: all(validate_availability_week(y) for y in x),
        'default_availability': lambda x: validate_availability_week(x) or x is None,
        'address': str,
        'company_id' : str,
        'company_name' : str,
        'admin' : bool,
        'minimum_weekly_hours': int
    }).validate(data)


def validate_auto_schedule(data) -> bool:
    return Schema({
        'uuids' : [str],
        'location' : str,
        'week_start' : _valid_ISOformat_string,
        'operating_hours' : lambda x: all(validate_time_slot(y) for y in x),
        Optional('min_employees') : int,
        Optional('max_employees') : int,
        Optional('min_shift_length') : int,
        Optional('max_shift_length') : int
    }).is_valid(data)   


# def validate_role(data) -> bool:
#     return Schema({
#         'name' : str,
#         'access_to' : object # TODO {attr -> bool} map
#     }).is_valid(data)    
