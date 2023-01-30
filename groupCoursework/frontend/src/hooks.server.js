import jwt from 'jsonwebtoken';
import { JWT_SECRET } from '$env/static/private';
import { redirect } from '@sveltejs/kit';

/** @type {import('@sveltejs/kit').Handle} */
export const handle = async ({ event, resolve }) => {
	const token = event.cookies.get('jwt');

	if (token) {
		try {
			const jwtUser = jwt.verify(token, JWT_SECRET);
			if (typeof jwtUser === 'string') {
				throw new Error('Something went wrong');
			}

			const sessionUser = {
				...jwtUser
			};

			//console.log('JWT: User verified', sessionUser)

			event.locals.user = sessionUser;
		} catch (error) {
			console.log('JWT: Error verifying token');
		}
	}

	if (event.url.pathname.startsWith('/employee')) {
		// PROTECTED PATHS
		if (!event.locals.user) {
			throw redirect(303, '/');
		}
	}
	if (event.url.pathname.startsWith('/admin')) {
		if (!event.locals.user || !event.locals.user.admin) {
			throw redirect(303, '/');
		}
	}

	return await resolve(event);
};
