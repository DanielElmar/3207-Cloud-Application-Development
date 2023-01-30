import { fail, json } from '@sveltejs/kit';
import { deleteEmployee } from '$lib/api';

/** @type {import('./$types').RequestHandler} */
export async function POST({ request, locals }) {
	// Get the data
	const { id } = await request.json();

	if (!id) {
		return fail(400, { message: 'ID is required for delete operation' });
	}

	console.log('Deleting employee with ID ' + id);

	// Delete the employee
	await deleteEmployee(locals.user.uuid, id);

	return json({}, 200);
}
