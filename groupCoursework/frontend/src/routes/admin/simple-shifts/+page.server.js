import { getAllTimetables, getPositions, getLocations, getEmployees } from '$lib/api.js'

export async function load({locals, url}){
    const uuid = locals.user.uuid;
    let weekCommencing = url.searchParams.get('weekCommencing');

    if (!weekCommencing) {
        weekCommencing = getFirstDayOfWeek(new Date());
    } else {
        weekCommencing = getFirstDayOfWeek(new Date(weekCommencing));
    }

    // get the monday and sunday of week commencing
    let monday = new Date(weekCommencing);
    monday.setDate(monday.getDate() - monday.getDay() + 1);
    monday.setHours(0, 0, 0, 0);
    let time_start = monday.toISOString()

    let sunday = new Date(weekCommencing);
    sunday.setDate(sunday.getDate() - sunday.getDay() + 7);
    sunday.setHours(23, 59, 59);
    let time_end = sunday.toISOString()


    //let { locations}  = await getLocations(uuid);
    //let { positions } = await getPositions(uuid);

    const { employees } = await getEmployees(uuid);

    const { shifts } = await getAllTimetables({ locations: [], positions: [], time_start, time_end }, uuid);

    console.log(employees)

    return { shifts, employees };
}

function getFirstDayOfWeek(currentDate) {
    // Get first day of week (monday)
    let date = new Date(currentDate);
    let day = date.getDay();
    let diff = date.getDate() - day + (day == 0 ? -6 : 1);
    return new Date(date.setDate(diff));
}