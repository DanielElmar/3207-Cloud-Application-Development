import { getEmployees, /**getAutoScheduleShifts*/ getLocations } from '$lib/api';


/** @type {import('./$types').PageServerLoad} */
export async function load({ locals }) {
	console.log('Loading data...');

    const [ employees, locations ] = await Promise.all([
        getEmployees(locals.user.uuid),
        getLocations(locals.user.uuid)
    ]);

    if (employees.error || locations.error) {
        return { error: employees.error || locations.error };
    }

	return {
		...employees,
		...locations
	};
}
