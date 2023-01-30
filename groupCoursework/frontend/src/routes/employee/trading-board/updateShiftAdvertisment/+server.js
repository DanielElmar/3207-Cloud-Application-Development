import { updateShiftAdvertisement } from '$lib/api';
import { json } from '@sveltejs/kit';

/** @type {import('./$types').RequestHandler} */
export async function POST({ request, locals }) {
	const body = await request.json();
	const userId = locals.user.uuid;

	const { error, response } = await updateShiftAdvertisement(body.shiftId, userId, body.available);

	return json({response});
}
