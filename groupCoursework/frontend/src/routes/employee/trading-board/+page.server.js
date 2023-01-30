import { getTradingBoardShifts } from '$lib/api.js';

/** @type {import('./$types').PageServerLoad} */
export async function load({ locals, url }) {
	let weekCommencing = url.searchParams.get('weekCommencing');

	console.log(weekCommencing)

	if (!weekCommencing) {
		weekCommencing = new Date().toISOString();
	} else {
		weekCommencing = new Date(weekCommencing).toISOString();
	}

	let data = await getTradingBoardShifts(weekCommencing, locals.user.uuid);

	if (data.error) {
		return { shifts: [], error: data.error };
	}

	return data;
}