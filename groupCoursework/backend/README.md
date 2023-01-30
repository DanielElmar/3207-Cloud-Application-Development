Create a new azure account

Follow the azure guide https://learn.microsoft.com/en-us/azure/azure-functions/functions-create-function-app-portal to create a function app for Python 3.9.0.

In the function app, set PYTHON_ISOLATE_WORKER_DEPENDENCIES to 1 in the configurations. This is to prevent an issue with one of the libraries used.

Then follow https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/quickstart-portal to create a Cosmos DB account, creating a NoSQL database and creating a container for employees, companies, shifts and credentials

Make a config.py file in the backend folder which looks like the following:
settings = {
    'db_URI': 'you database URI',
    'db_key': 'you database key',
    'db_id': 'your database id',
    'credential_container': 'what you named the credential container',
    'shift_container': 'what you named the credential container',
    'employee_container': 'what you named the credential container',
    'company_container': 'what you named the credential container'
}

Make a local.settings.json and set which looks like the following:
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}

Create a venv for the backend folder and install Azure Command Line Interface (CLI) and Azure Functions Core Tools

(in the venv) run ```az login``` to log into your microsoft azure account

run ```func azure functionapp publish <name of your functionapp>``` to publish to azure





# Design


## DataBase Schema

time_slot{

start			date `"2022-12-26T22:00:00Z" `

end			date `"2022-12-26T22:00:00Z"`

}

credentials {

email:			string (max length of 64 chars, regex: ~~^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$ ~~)

hashed_pass:		string (min length of 8 chars, max length of 64 chars)

salt:			string

employee_id:		id

}

employee{

id:				id

position:			[string]			(Company titles)

first_name:			string

last_name:			string

email:				string			(mapped to lowercase)

telephone:			string

address:			string

manual_availability:		availability_week[ ]

default_availability:		availability_week | None

minimum_week_hours:	int

company_id:			string

company_name: 		string

admin: 			bool

~~roles:				string[]			(Permission roles)~~

}

availability_week{

week_start:		date (Monday 00:00)

max_hours                  int | None

time_off: 		time_off[]  ~~{ amount: int (hours), type: string (holiday, unpaid, sick), note: str }~~

current_hours:		int

availabilities:		time_slot[]

approved:		bool | None

notes:			str

}

time_off{

'amount': 		int,

'pay_type':		str,	(holiday, unpaid, sick)

'notes': 		str

}

~~role{~~

~~name: string,				(Unique)~~

~~access_to: {attr -> bool} ~~

~~}~~

~~attrs: [‘own_timetable’, ‘own_availability’, etc…]~~

~~contract{~~

~~availability:	  	[time_slot]~~

~~minHoursPerWeek:	int~~

~~maxHoursPerWeek:	int | null~~

~~}~~

company{

id:			string

company_name: 	string

locations: 		[string]

employees:		[empoyee_id]

positions:		[string]

~~roles:			[role]		(Permission roles)~~

}

shift{

id:			id

company id:		company-id

employee id:		emp-id

time_slot: 		time_slot

location: 		string		

cover: 			bool		(Whether the shift is available to be covered)

position: 		string 		(???)

~~Coveree: 		emp-id[]	(List of people wanting to cover the shift)~~

prev_owners: 		emp-id[]	(Starts as the original employee’s id, append on cover)

}

schedule_preset{

preset_id:		id

days:			[day]

}

day{

opening_hours:	time_slot

shift_length:		hh:mm || false

shift_allocations:	[time_slot] || false

position_map:		{ postion -> int }

}


# 


# API Documentation (frontend needs an API key):


## Login page

Talking point: Validation of lengths? Status codes? Messages? Rate limiting?



* Validation at both ends
* Use status codes and messages

Notes from meeting: unique usernames?

TODO: non case sensitive emails (tolower them)

**All endpoints, where applicable, will have:**

**fail 400: **

**{ msg: “invalid request format” } (Specific endpoints will have additional 400 messages)**

**{ msg: “invalid time slot format” }**

**fail 403:**

**{ msg: “no permissions” }**


<table>
  <tr>
   <td>API endpoint
   </td>
   <td>Request
   </td>
   <td>Response
   </td>
  </tr>
  <tr>
   <td>/login
   </td>
   <td>{
<p>
email: string,
<p>
password: string
<p>
}
   </td>
   <td>success 200 
<p>
{
<p>
<del>msg: “credentials correct”, </del>
<p>
id: str
<p>
first_name: string,
<p>
last_name: string,
<p>
email: string,
<p>
company_name: string,
<p>
admin: bool
<p>
<del>access: [string], //TODO</del>
<p>
<del>admin_access: [string] //TODO</del>
<p>
}
<p>
fail 400: 
<p>
{ msg: “username or password incorrect” }
   </td>
  </tr>
  <tr>
   <td>/register
   </td>
   <td>{
<p>
company_name: string
<p>
email: string,
<p>
password: string,
<p>
first_name: string,
<p>
last_name: string,
<p>
telephone: string
<p>
address: string
<p>
}
   </td>
   <td>success 200 
<p>
{ <del>msg: “company created”,</del>
<p>
id: str
<p>
first_name: string,
<p>
last_name: string,
<p>
email: string,
<p>
company_name: string,
<p>
<del>admin: bool</del>
<p>
<del>access: [string],</del>
<p>
<del>admin_access: [string]</del>
<p>
 }
<p>
fail 400: 
<p>
{
<p>
msg: “username already exists” OR “username / password wrong length”
<p>
}
   </td>
  </tr>
  <tr>
   <td>/create_user
<p>
<strong>needs admin</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
email: string,
<p>
positions: string[],
<p>
first_name: string,
<p>
last_name: string,
<p>
telephone: string,
<p>
address: string,
<p>
starting_pass: string,
<p>
minimum_weekly_hours: int
<p>
}
   </td>
   <td>success 200 
<p>
{ msg: “user created successfully” }
<p>
fail 400: 
<p>
{ msg: “email already exists” }
<p>
{ msg: “user’s company not found” }
<p>
{ msg: “email already exists” }
   </td>
  </tr>
</table>



## Dashboard page

**Note: employee_ids will be replaced with employee objects**

Frontend server translates the token to the username? Handling authentication? Lots of endpoints for the dashboard? Front end getting permissions object?


<table>
  <tr>
   <td>API endpoint (/dashboard/)
   </td>
   <td>Request
   </td>
   <td>Response
   </td>
  </tr>
  <tr>
   <td>/timetable
<p>
<strong>needs admin if uuids contains not self</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
uuids: [string],
<p>
time_start: date,
<p>
time_end: date,
<p>
positions: [string],
<p>
locations: [string]
<p>
}
   </td>
   <td>success 200:
<p>
{ shifts: [shift] }
<p>
fail 400:
<p>
{ msg: “user id not found: &lt;uuid>” }
<p>
{ "msg": "company id did not match for a user" }
   </td>
  </tr>
  <tr>
   <td>/all_timetables
<p>
<strong>needs admin</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
time_start: date,
<p>
time_end: date,
<p>
postions: [string],
<p>
locations: [string]
<p>
}
   </td>
   <td>success 200:
<p>
{
<p>
shifts: [shift]
<p>
 }
   </td>
  </tr>
  <tr>
   <td>/get_availability
<p>
<strong>needs admin if uuid is not self</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
uuid: str,
<p>
week_commencing: ISO date
<p>
}
   </td>
   <td>success 200:
<p>
{
<p>
availability: availability_week | None
<p>
minimum_week_hours: int
<p>
}
<p>
fail 400:
<p>
{ msg: “user id not found: &lt;uuid>” }
<p>
{ msg: “user’s company not found” } (where uuid != None)
<p>
{ "msg": "company id did not match for a user" }
   </td>
  </tr>
  <tr>
   <td>/set_availability
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
week_start:		date (Monday 00:00)
<p>
availabilities:		time_slot[]
<p>
max_hours                  int
<p>
time_off: 		time_off[]
<p>
notes:                          str
<p>
default:                        bool
<p>
}
   </td>
   <td>success 200:
<p>
{ msg: “successfully added” }
<p>
fail 400:
<p>
{ msg: “time slot overlap” }
<p>
{ msg: “not enough availability for maximum hours” }
<p>
{ msg: “user id not found: &lt;uuid>” }
<p>
{ msg: “time slot out of bounds” }
   </td>
  </tr>
  <tr>
   <td>/approve_availability
<p>
<strong>needs admin</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
uuid: str,
<p>
week_commencing: date,
<p>
approved: bool
<p>
}
   </td>
   <td>success 200:
<p>
{ msg: “successfully deleted” }
<p>
fail 400: (invalid request format where start after end)
<p>
{ msg: “user id not found: &lt;uuid>” }
<p>
{ "msg": "company id did not match for a user" }
<p>
{ "msg": "availability not found" } &lt;- where get_availability is None for those inputs
   </td>
  </tr>
  <tr>
   <td>/get_unapproved_availabilities
<p>
<strong>needs admin</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
week_commencing: date
<p>
}
   </td>
   <td>success 200:
<p>
[{ id: uuid, availability: availability_week, minimum_week_hours: int }]
<p>
fail 400:
<p>
{ msg: “user’s company not found” }
<p>
fail 500:
<p>
{ msg: “database inconsistency” }
   </td>
  </tr>
  <tr>
   <td>/set_default_availability
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
week_start:		date (Monday 00:00)
<p>
max_hours                  int
<p>
availabilities:		time_slot[]
<p>
time_off: 		[{ amount: int (hours), type: string (holiday, unpaid, sick) }] 
<p>
notes:                          str
<p>
}
   </td>
   <td>success 200:
<p>
{ msg: “successfully added” }
<p>
fail 400:
<p>
{ msg: “time slot overlap” }
<p>
{ msg: “not enough availability for maximum hours” }
<p>
{ msg: “user id not found: &lt;uuid>” }
<p>
{ msg: “time slot out of bounds” }
<p>
{ msg: “default availability cannot have time off requests” }
   </td>
  </tr>
  <tr>
   <td>/shift_trading
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
//leave comments on what you might want here please
<p>
}
<p>
SEE BELOW (Shift Trading section)
   </td>
   <td>success 200:
<p>
{
<p>
//leave comments on what you might want here please 
<p>
}
   </td>
  </tr>
  <tr>
   <td>/employee_management
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
//leave comments on what you might want here please
<p>
}
   </td>
   <td>success 200:
<p>
{
<p>
//leave comments on what you might want here please
<p>
 }
   </td>
  </tr>
  <tr>
   <td>/add_position
<p>
<strong>needs admin</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
position: string
<p>
}
   </td>
   <td>success 200:
<p>
{ msg: “position added successfully” }
<p>
fail 400: (invalid request format where start after end)
<p>
{ msg: “position already exists” }
<p>
{ msg: “user id not found: &lt;uuid>” }
<p>
{ msg: “user’s company not found” }
   </td>
  </tr>
  <tr>
   <td>/delete_position
<p>
<strong>needs admin</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
position: string
<p>
}
   </td>
   <td>success 200:
<p>
{ msg: “position deleted successfully” }
<p>
fail 400: (invalid request format where start after end)
<p>
{ msg: “position not found” }
<p>
{ msg: “user id not found: &lt;uuid>” }
<p>
{ msg: “user’s company not found” }
   </td>
  </tr>
  <tr>
   <td>/all_postions
   </td>
   <td>X-Request-UUID: string
   </td>
   <td>success 200:
<p>
{ positions: [position] }
   </td>
  </tr>
  <tr>
   <td>/add_location
<p>
<strong>needs admin</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
location: string
<p>
}
   </td>
   <td>success 200:
<p>
{ msg: “added location successfully” }
<p>
fail 400:
<p>
{ msg: “location already exists” }
<p>
{ msg: “user id not found: &lt;uuid>” }
<p>
{ msg: “user’s company not found” }
   </td>
  </tr>
  <tr>
   <td>/delete_location
<p>
<strong>needs admin</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
position: string
<p>
}
   </td>
   <td>success 200:
<p>
{ msg: “position deleted successfully” }
<p>
fail 400:
<p>
{ msg: “location not found” }
<p>
{ msg: “user id not found: &lt;uuid>” }
<p>
{ msg: “user’s company not found” }
   </td>
  </tr>
  <tr>
   <td>/all_locations
   </td>
   <td>X-Request-UUID: string
   </td>
   <td>success 200:
<p>
{ locations: [location] }
   </td>
  </tr>
  <tr>
   <td>/add_shift
<p>
<strong>needs admin</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
uuid: string,
<p>
time_slot: time_slot,
<p>
location: string	
<p>
}
   </td>
   <td>success 200:
<p>
{ msg: “added shift successfully” }
<p>
400:
<p>
{ msg: “time slot collision” }
<p>
{ msg: “location / user not found” }
<p>
{ "msg": "company id did not match for a user" }
   </td>
  </tr>
  <tr>
   <td>/delete_shift
<p>
<strong>needs admin</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
shift_id: string
<p>
}
   </td>
   <td>success 200:
<p>
{ msg: “shift deleted successfully” }
<p>
fail 400:
<p>
{ msg: “user id not found: &lt;uuid>” }
<p>
{ msg: “shift not found” }
<p>
{ "msg": "company id did not match for a user" }
   </td>
  </tr>
  <tr>
   <td>/update_shift
<p>
<strong>needs admin</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
shift_id: string
<p>
time_slot: time_slot,
<p>
location: string
<p>
}
   </td>
   <td>success 200:
<p>
{ msg: “shift updated successfully” }
<p>
fail 400:
<p>
{ msg: “time slot collision” }
<p>
{ msg: “location /user id not found: &lt;uuid>” }
<p>
{ msg: “shift not found” }
<p>
{ "msg": "company id did not match for a user" }
   </td>
  </tr>
</table>



## Shift Trading Board


<table>
  <tr>
   <td>API endpoint
   </td>
   <td>Request
   </td>
   <td>Response
   </td>
  </tr>
  <tr>
   <td>/get_trading_board
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
week_comencing: “2022-12-26T20:00:00.000Z” iso format string,
<p>
<del>uuid: str</del>
<p>
<del>user: {first_name: “Dan”, email: “<a href="mailto:123fake@gmail.com">123fake@gmail.com</a>, UIDD}</del>
<p>
}
   </td>
   <td>success 200:
<p>
{ 
<p>
week_comencing: iso format,
<p>
cover_shifts: [..Shifts] (shifts which are available for covering excluding emplouee)
<p>
my_shifts: [..Shifts] (shifts for this employee)
<p>
}
   </td>
  </tr>
  <tr>
   <td>/update_shift_advertisement
<p>
(Advertise / take down shift)
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
shift_id: string
<p>
available: bool (True = advertised)
<p>
}
   </td>
   <td>success 200:
<p>
{ msg: “shift updated successfully” }
<p>
fail 400:
<p>
{ "msg": "shift id did not match for a user" }
<p>
{ msg: “user id not found: &lt;uuid>” }
   </td>
  </tr>
  <tr>
   <td>/take_shift_change
<p>
<strong>needs admin</strong>
<p>
(take shift)
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
shift_id: string
<p>
<del>coverer_uuid: string</del>
<p>
}
   </td>
   <td>success 200:
<p>
{ msg: “shift swapped successfully” }
<p>
fail 400:
<p>
{ "msg": "company id did not match for a user" }
<p>
{ msg: “user id not found: &lt;uuid>” }
   </td>
  </tr>
</table>



## (Admin) Employee Management


<table>
  <tr>
   <td>API endpoint
   </td>
   <td>Request
   </td>
   <td>Response
   </td>
  </tr>
  <tr>
   <td>/all_users
<p>
<strong>needs admin</strong>
   </td>
   <td>X-Request-UUID: string
<p>
no body
   </td>
   <td>success 200:
<p>
{ employees:  [ employee ] }
<p>
<del>^ only the users that the admin has permissions for</del>
<p>
fail 500:
<p>
{ msg: “database inconsistency with user: &lt;uuid>” }
   </td>
  </tr>
  <tr>
   <td>/get_user
<p>
<strong>needs admin if not self</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body:
<p>
{
<p>
<del>user_</del>uuid: string
<p>
}
   </td>
   <td>success 200:
<p>
{
<p>
information: employee,
<p>
<del>edit_access: bool</del> (this will only return if they have edit access)
<p>
}
   </td>
  </tr>
  <tr>
   <td>/delete_user
<p>
<strong>needs admin</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body:
<p>
{
<p>
uuid: string
<p>
}
   </td>
   <td>success 200:
<p>
{ msg: “user deleted successfully” }
<p>
fail 400:
<p>
{ msg: “user id not found: &lt;uuid>” }
   </td>
  </tr>
  <tr>
   <td>/update_user
<p>
<strong>needs admin if not self</strong>
   </td>
   <td>X-Request-UUID: string
<p>
body: {
<p>
information: employee
<p>
}
   </td>
   <td>success 200:
<p>
{ msg: “updated successfully” }
   </td>
  </tr>
  <tr>
   <td>/create_role
<p>
/update_role
   </td>
   <td>X-Request-UUID: string
<p>
body: { role }
   </td>
   <td>success 200:
<p>
{ msg: “created/updated successfully” }
<p>
for creating
<p>
401:
<p>
{ msg: “role name already exists” }
   </td>
  </tr>
  <tr>
   <td>/delete_role
   </td>
   <td>X-Request-UUID: string
<p>
body: { role }
   </td>
   <td>success 200:
<p>
{ msg: “deleted successfully” }
   </td>
  </tr>
  <tr>
   <td>/all_roles
   </td>
   <td>X-Request-UUID: string
<p>
no body
   </td>
   <td>success 200:
<p>
{ roles: [role] }
   </td>
  </tr>
</table>



## (Admin) Approvals


<table>
  <tr>
   <td>API endpoint
   </td>
   <td>Request
   </td>
   <td>Response
   </td>
  </tr>
  <tr>
   <td>/getRequests
   </td>
   <td>X-Request-UUID: string
<p>
body:
<p>
{
<p>
user-UUID: string
<p>
}
   </td>
   <td>success 200:
<p>
{
<p>
}
<p>
fail 403:
<p>
{ msg: “no permissions” }
   </td>
  </tr>
  <tr>
   <td>/approveRequest
   </td>
   <td>X-Request-UUID: string
<p>
body:
<p>
{
<p>
user-UUID: string
<p>
}
   </td>
   <td>success 200:
<p>
{
<p>
}
<p>
fail 403:
<p>
{ msg: “no permissions” }
   </td>
  </tr>
</table>



## (Admin) Auto Scheduler


<table>
  <tr>
   <td>API endpoint
   </td>
   <td>Request
   </td>
   <td>Response
   </td>
  </tr>
  <tr>
   <td>/auto_schedule
   </td>
   <td>X-Request-UUID: string
<p>
{
<p>
    "uuids" : [string]
<p>
    "location" : string
<p>
    "week_start" : datetime
<p>
    "operating_hours" : [time_slot]
<p>
    "min_employees" : int (optional)
<p>
    "max_employees" : int (optional)
<p>
    "min_shift_length" : int (optional)
<p>
    "max_shift_length" : int (optional)
<p>
}
   </td>
   <td>success 200:
<p>
{
<p>
“solutions” : 
<p>
[[{
<p>
“employee_id”:string
<p>
“time_slot”: time_slot
<p>
“location”: string
<p>
}]]
<p>
}
   </td>
  </tr>
</table>
