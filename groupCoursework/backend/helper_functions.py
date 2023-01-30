import json
import config
from azure.cosmos import CosmosClient, exceptions
import azure.functions as func
from datetime import datetime, timedelta


def query_container(query, params, container, filter=True):
    client = CosmosClient(url=config.settings['db_URI'], credential=config.settings['db_key'])
    database = client.get_database_client(config.settings['db_id'])
    container = database.get_container_client(config.settings[container])
    
    query_items = list(container.query_items(
        query=query, parameters=params, enable_cross_partition_query=True
    ))
    
    if not filter:
        return query_items
    
    # Loop through list, for each filter the dictionary to remove any keys beginning with "_"
    return [dict(filter(lambda x: not x[0].startswith("_"), dictionary.items())) for dictionary in query_items]
    

def get_object_attr(object_id, attr_name, container_name):
    """ use attr_name = None for whole object """
    attribute = ("." + attr_name) if attr_name is not None else ""
    query = f"SELECT VALUE o{attribute} FROM o WHERE o.id = @id"
    params = [
        { "name":"@id", "value": object_id }
    ]
    
    response = query_container(query, params, container_name, filter=False)
    if len(response) == 0:
        raise ItemNotFoundException()
    
    return response[0]
    

def update_user_attr(user_id, attribute, new_object):
    query = "SELECT VALUE e FROM e WHERE e.id='@id'"
    params = [
        { "name":"@id", "value": user_id }
    ]
    
    response = query_container(query, params, 'employee_container', filter=False)
    if len(response) == 0:
        raise UserDoesNotExistException()
    
    user = response[0]
    user[attribute] = new_object
    replace_container_item(user, 'employee_container')
        

def check_permission(user_id):
    try: return get_object_attr(user_id, 'admin', 'employee_container')
    except: raise UserDoesNotExistException()
    

def get_users_company_object(user_id):
    try: company_id = get_object_attr(user_id, 'company_id', 'employee_container')
    except: raise UserDoesNotExistException()
    
    try: return get_object_attr(company_id, None, 'company_container')   
    except: raise CompanyNotFoundException()


def check_company_ids_match(company_id, user_list):
    try:
        for user in user_list:
            if get_object_attr(user, 'company_id', 'employee_container') != company_id:
                return False
        return True
    except:
        raise UserDoesNotExistException()
    

def replace_container_item(item, container_name):
    client = CosmosClient(url=config.settings['db_URI'], credential=config.settings['db_key'])
    database = client.get_database_client(config.settings['db_id'])
    container = database.get_container_client(config.settings[container_name])

    container.replace_item(item['id'], item)


def create_container_item(item, container_name):
    client = CosmosClient(url=config.settings['db_URI'], credential=config.settings['db_key'])
    database = client.get_database_client(config.settings['db_id'])
    container = database.get_container_client(config.settings[container_name])

    container.create_item(item)  # Could return this if needed
    
    
def delete_container_item_by_id(item_id, container_name):
    client = CosmosClient(url=config.settings['db_URI'], credential=config.settings['db_key'])
    database = client.get_database_client(config.settings['db_id'])
    container = database.get_container_client(config.settings[container_name])
    
    try:
        container.delete_item(item=item_id, partition_key=item_id)
    except exceptions.CosmosResourceNotFoundError:
        raise ItemNotFoundException
    

# Non-database related:

def get_tuple_string(object_list):
    original_string = str(tuple(o for o in object_list))
    if original_string.endswith(",)"):
        original_string = original_string[:-2] + ")"
    return original_string
    

def get_string_from_datetime(datetime):
    return datetime.replace(tzinfo=None).isoformat("T", "seconds") + "Z"


def get_datetime_from_string(string):
    try:
        return datetime.fromisoformat(string.replace('Z', '+00:00'))
    except:
        return False


def check_timeslot_overlaps(new_time_slot_str_dict, current_time_slots_str_dicts):
    try:
        new_time_start = datetime.fromisoformat(new_time_slot_str_dict['start'].replace('Z', '+00:00'))
        new_time_end = datetime.fromisoformat(new_time_slot_str_dict['start'].replace('Z', '+00:00'))
        
        for current_time_slot in current_time_slots_str_dicts:
            curr_time_start = datetime.fromisoformat(current_time_slot['start'].replace('Z', '+00:00'))
            curr_time_end = datetime.fromisoformat(current_time_slot['end'].replace('Z', '+00:00'))
            
            # If the current start is within the new shift
            if new_time_start < curr_time_start < new_time_end:
                return False

            # If the current end is within the new shift
            if new_time_start < curr_time_end < new_time_end:
                return False
            
            # If the new shift is within a current shift
            if curr_time_start <= new_time_start <= new_time_end <= curr_time_end:
                return False
        return True
    except:
        raise TimeSlotFormatException()
        
    
def get_week_start_and_end(date_str):
    week_to_get = get_datetime_from_string(date_str)
    just_days = datetime(year=week_to_get.year, month=week_to_get.month, day=week_to_get.day)
    week_start = just_days - timedelta(days=just_days.weekday())
    week_end = week_start + timedelta(days=7)
    return (week_start, week_end)
    
    
def change_time_slot_weeks(current_week_start: str, current_time_slots, new_week_start):
    (current_week_start, _) = get_week_start_and_end(current_week_start)
    (new_week_start, _) = get_week_start_and_end(new_week_start)
    time_difference = new_week_start - current_week_start
    
    new_time_slots = []
    for time_slot in current_time_slots:
        new_start = get_string_from_datetime(time_difference + get_datetime_from_string(time_slot['start']))
        new_end = get_string_from_datetime(time_difference + get_datetime_from_string(time_slot['end']))
        new_time_slots.append({ 'start': new_start, 'end': new_end })
    
    return new_time_slots
        
        
class CompanyNotFoundException(Exception):
    pass


class UserDoesNotExistException(Exception):
    pass


class TimeSlotFormatException(Exception):
    pass


class ItemNotFoundException(Exception):
    pass


# Error responses
class Responses:
    def success_message(message):
        return func.HttpResponse(
            mimetype='application/json', 
            body=json.dumps({"msg": message}), 
            status_code=200
        )
    
    def fail_message(message):
        return func.HttpResponse(
            mimetype='application/json', 
            body=json.dumps({"msg": message}), 
            status_code=401
        )
        
    def success_dict(dictionary):
        return func.HttpResponse(
            mimetype='application/json', 
            body=json.dumps(dictionary), 
            status_code=200
        )
    
    def company_id_mismatch():
        return func.HttpResponse(
            mimetype='application/json', 
            body=json.dumps({"msg": "company id did not match for a user"}), 
            status_code=400
        )
        
    def invalid_format():
        return func.HttpResponse(
            mimetype='application/json', 
            body=json.dumps({"msg": "invalid request format"}), 
            status_code=400
        )
        
    def invalid_time_slot_format():
        return func.HttpResponse(
            mimetype='application/json', 
            body=json.dumps({"msg": "invalid time slot format"}), 
            status_code=400
        )
        
    def no_permissions():
        return func.HttpResponse(
            mimetype='application/json', 
            body=json.dumps({"msg": "no permissions"}), 
            status_code=403
        )

    def user_not_found(uuid):
        return func.HttpResponse(
            mimetype='application/json', 
            body=json.dumps({"msg": f"user id not found: {uuid}"}), 
            status_code=400
        )

    def time_slot_overlap():
        return func.HttpResponse(
            mimetype='application/json', 
            body=json.dumps({"msg": "time slot overlap"}), 
            status_code=400
        )
        
    def item_not_found(item_name):
        return func.HttpResponse(
            mimetype='application/json', 
            body=json.dumps({"msg": f"{item_name} not found"}), 
            status_code=400
        )
        
    def item_already_exists(item_name):
        return func.HttpResponse(
            mimetype='application/json', 
            body=json.dumps({"msg": f"{item_name} already exists"}), 
            status_code=400
        )

    def internal_server_error(message):
        return func.HttpResponse(
            mimetype='application/json', 
            body=json.dumps({"msg": message}), 
            status_code=500
        )
    
    def not_implemented():
        return func.HttpResponse(
            mimetype='application/json', 
            body=json.dumps({"msg": "not implemented"}), 
            status_code=200
        )
    