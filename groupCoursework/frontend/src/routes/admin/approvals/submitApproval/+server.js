import { approveRequest } from '$lib/api';
import { json } from '@sveltejs/kit';

/** @type {import('./$types').RequestHandler} */
export async function POST({ request, locals }) {
	const data = await request.json();

    let uuid = locals.user.uuid;
    let employee_uuid = data.id;
    let week_commencing = data.availability.week_start;
    let approved = data.approved;

	const { error, response } = await approveRequest(uuid, employee_uuid, week_commencing, approved);

    return json({response});

}
