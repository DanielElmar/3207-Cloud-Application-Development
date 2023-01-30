import { error, json } from '@sveltejs/kit';
import { getAvailability, setAvailability } from '$lib/api';

/** @type {import('./$types').RequestHandler} */
export async function GET({ url, locals }) {
	const week = url.searchParams.get('weekCommencing');

	const { availability, minWeekHours, err } = await getAvailability(
		week,
		locals.user.uuid,
		locals.user.uuid
	);

	if (err) throw error(500, 'Server error');

	return json({ availability, minWeekHours });
}

export async function POST({ request, locals }) {
	const data = await request.json();

	console.log('[availability/server.js] Data being submitted: ' + data);

	const { success, err } = await setAvailability(data, locals.user.uuid);

	if (err) throw error(500, 'Server error');

	if (success) return json({ success: true });
}
