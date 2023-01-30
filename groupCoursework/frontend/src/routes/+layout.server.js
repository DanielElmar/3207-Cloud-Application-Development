/** @type {import('./$types').LayoutSeverLoad} */
export async function load({ locals }) {
	let admin = [
		{ href: '/admin/employees', text: 'Employees' },
		{ href: '/admin/shifts', text: 'Shifts' },
		{ href: '/admin/auto-scheduler', text: 'Auto Schedule' },
		{ href: '/admin/approvals', text: 'Approvals' },
		{ href: '/admin/simple-shifts', text: 'Delete shifts' }
	];

	let items = [
		{ href: '/employee/schedule', text: 'Schedule' },
		{ href: '/employee/trading-board', text: 'Trading Board' },
		{ href: '/employee/availability', text: 'Availability' }
	];

	return {
		user: locals.user,
		items: locals.user ? items : [],
		admin: locals.user?.admin ? admin : []
	};
}
