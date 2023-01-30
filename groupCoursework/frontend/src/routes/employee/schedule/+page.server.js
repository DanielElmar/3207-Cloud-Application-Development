import { getScheduleShifts } from '$lib/api.js';

/** @type {import('./$types').PageServerLoad} */
export async function load({ locals, url }) {
	let weekCommencing = url.searchParams.get('weekCommencing');

	if (weekCommencing === null) {
		let today = new Date();
		let day = today.getDay(),
			diff = today.getDate() - day + (day === 0 ? -6 : 1);
		weekCommencing = new Date(today.setDate(diff));
	} else {
		weekCommencing = new Date(weekCommencing);
	}

	let data = await getScheduleShifts(weekCommencing, locals.user.uuid);

	console.log("+page.server.js");
	console.log(data);

	if (data.error) {
		return { shifts: [], error: data.error };
	}

	return data;

	//let shift = {"shift_id": 1545452, "employee_id":85745855, "date": "17/07/2002", "time_slot": {"start": "0900", "end": "1700"}, "location": "A Shop", "cover": false, "coveree": [], "prev_owners": []}
	//return {"shifts": [shift,shift,shift,shift,shift,shift]}
}
