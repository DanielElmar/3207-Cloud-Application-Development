import { fail, redirect } from '@sveltejs/kit';
import { registerCompany } from '$lib/api';

/** @type {import (./$types).Actions} */
export const actions = {
	default: async ({ request, cookies }) => {
		const data = Object.fromEntries(await request.formData());

		//Loop through fields and make list of missing fields
		let expectedFields = [
			'company_name',
			'email',
			'password',
			'confirm_password',
			'telephone',
			'first_name',
			'last_name',
			'address'
		];

		for (const field of expectedFields) {
			if (!data[field]) {
				return fail(401, { error: `Missing ${field}` });
			}
		}

		if (data.password !== data.confirm_password) {
			return fail(401, { error: 'Passwords do not match' });
		} // EMAIL VALIDATION ETC...

		delete data.confirm_password;

		const { token, error } = await registerCompany(data);

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

		throw redirect(302, '/admin/approvals');
	}
};
