import { redirect } from '@sveltejs/kit';

/** @type {import('./$types').RequestHandler} */
export async function POST({ cookies, locals }) {
	await cookies.delete('jwt');
	locals.user = null;

	throw redirect(303, '/');
}
