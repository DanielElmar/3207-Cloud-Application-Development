import { takeShift } from '$lib/api';
import { json } from '@sveltejs/kit';

/** @type {import('./$types').RequestHandler} */
export async function POST({ request,locals }) {
	const body = await request.json();

	const { error, response } = await takeShift(body.shiftId, locals.user.uuid);

	return json({response});
}
