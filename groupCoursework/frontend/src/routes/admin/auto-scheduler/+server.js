import { error as err, json } from '@sveltejs/kit';
import { generateAutoSchedule } from '$lib/api';

/** @type {import('./$types').RequestHandler} */
export async function GET() {
	//const week = url.searchParams.get('weekCommencing');
}

export async function POST({ request, locals }) {
	const data = await request.json();

	console.log(data);

	const { error, solutions } = await generateAutoSchedule(data, locals.user.uuid);

	if (error) throw err(500, 'Server error');

	console.log(solutions)

	return json({ solutions });
}
