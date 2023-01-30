import { fail, redirect } from '@sveltejs/kit';
import { getAllShiftsForAdmin, getEmployees, deleteShift } from '$lib/api';
import { getMonday, shiftsTransform } from '$lib/utils';
import { createShift } from '$lib/api';
import { getLocations } from '$lib/api';
import {  checkContainsPropertyList } from '$lib/utils';

let shiftKeys;
let shifts;
let allShiftData;

/** @type {import('./$types').PageServerLoad} */
export async function load({locals}){
    console.log("Load");
    let thisWeek = getMonday(new Date()); 
    let alllocations = await getLocations(locals.user.uuid);
    allShiftData = (await getAllShiftsForAdmin(locals.user.uuid, {
        time_start: "2023-01-09T00:00:00Z",
        time_end: "2024-01-16T00:00:00Z",
        positions: [],
        locations: []
    }));
    let fullShiftData = shiftsTransform(allShiftData.shifts);
    shifts = fullShiftData.shifts;
    shiftKeys = fullShiftData.keyToShifts;
    let employees = await getEmployees(locals.user.uuid);

    return {
        shifts : shifts,
        employees : employees,
        keys: shiftKeys,
        everylocation : alllocations
    }
}
/** @type {import('./$types').Actions} */
export const actions = {
    create: async  ({ request,locals}) => {
        console.log("Creating shifts");
        const {shift_id,employees_ids, time_slot, location, error} = await loadShiftsFormData(request,[ "employees", "start", "end", "location"])
        
        if (error) {
            console.error("shift create error load" + error);
            return fail(401,{error : error})
        }
        let emp = [...employees_ids];
        
        console.log("employee" + emp);

        let listUpdate = emp.map(function(A) {return A.id;});
        console.log(listUpdate);
        for(let i of listUpdate){
            console.log("list" + i + time_slot + location);
            await createShift(locals.user.uuid, {uuid: i,  time_slot: time_slot , location: location});
            console.log("did it ");
        }

        throw redirect(302, '/admin/shifts');
    },

    update: async  ({request, locals}) => {
        console.log("Updating shifts");
        const {shift_id, employees_ids, time_slot, location,  error} = await loadShiftsFormData(request,["id", "employees", "start", "end", "location"])
        
        if (error) {
            console.error("shift update error load" + error);
            return fail(401,{error : error})
        }
        let listUpdate = shiftKeys[shift_id];

        let emp = [...employees_ids]
        let otheLi = emp.map(function(A) {return A.id;});
        
        for(let i of listUpdate){
            
            console.log(" FUCKING " + (shifts.map(function(shit) {return shit.shift_id;})));
            let foundShift = ((allShiftData.shifts).find(shift => shift.id === i)).employee_id;

            console.log(foundShift);
            
            if (foundShift in otheLi){
                otheLi.pop(foundShift);
                await updateShift(locals.user.uuid, {i,  time_slot , location });
            } else{
                await deleteShift(locals.user.uuid,{uuid:i});
            }

        }
        if (otheLi.length != 0 ){
            console.log("MOFO" + otheLi.length);
            for(let x of otheLi){
                await createShift(locals.user.uuid, {uuid:x,time_slot , location });
            }
        }
        throw redirect(302, '/admin/shifts');
    }
    
}
async function loadShiftsFormData(request, required ){
    const data = Object.fromEntries(await request.formData());
    console.log(data);
    const checkRes = checkContainsPropertyList(data, required);

    

    if(!checkRes.isOK){
        const many = checkRes.missing.length > 0;
        const propList = checkRes.missing
            .map(p => "'" + p + "'").join(', ');
        
        return { 
            error: `Missing ${ many ? "properties" : "property" } ${ propList }`
        };
    }
    const id = parseInt(data.id);
    const employees = JSON.parse(data.employees);
    const time_slotStart = new Date(data.start).toISOString();
    const time_slotEnd = new Date(data.end).toISOString(); 
    const alocation = data.location;

    return{
        shift_id:id,
        employees_ids: employees,
        time_slot: {start : time_slotStart, end : time_slotEnd}, 
        location: alocation,
        ...data
    }
}