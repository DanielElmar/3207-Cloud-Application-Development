import { error, json } from '@sveltejs/kit';
import { deleteShiftt } from '$lib/api';

export async function POST({ request, locals }) {
	const data = await request.json();

	const { success, err } = await deleteShiftt(data, locals.user.uuid);

	if (err) throw error(500, 'Server error');

	if (success) return json({ success: true });
}
