import { fail, redirect } from '@sveltejs/kit';
import { loginUser } from '$lib/api';

/** @type {import (./$types).PageServerLoad} */
export async function load() {}

/** @type {import (./$types).Actions} */
export const actions = {
	default: async ({ cookies, request }) => {
		const data = Object.fromEntries(await request.formData());

		if (!data.email || !data.password) {
			return fail(401, { error: 'Missing username or password' });
		}

		const { error, token, admin } = await loginUser(data);

		if (error) {
			return fail(401, { error });
		}

		cookies.set('jwt', token, {
			path: '/',
			maxAge: 60 * 60 * 24, // 24 hours
			sameSite: 'strict',
			httpOnly: true,
			secure: true
		});

		if (admin) {
			throw redirect(302, '/admin/approvals');
		} else {
			throw redirect(302, '/employee/schedule');
		}
	}
};
