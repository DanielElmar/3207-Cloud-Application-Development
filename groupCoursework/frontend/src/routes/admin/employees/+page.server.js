import { fail, redirect } from '@sveltejs/kit';

import {
	getEmployees,
	getEmployee,
	createEmployee,
	updateEmployee,
	getAllShiftsForAdmin,
	assignShiftsToEmployee,
	getPositions,
	createPosition, createLocation
} from '$lib/api';
import { checkContainsPropertyList } from '$lib/utils';

/** Load Events */

/** @type {import('./$types').PageServerLoad} */
export async function load({ locals }) {
	console.log('Loading data...');

	// let roles = await getRoles();
	// let employeeResponse = getEmployees(locals.user.uuid);
	// let shifts = (getAllShiftsForAdmin(locals.user.uuid, {
	//     time_start: "2023-01-09T00:00:00Z",
	//     time_end: "2023-01-16T00:00:00Z",
	//     positions: [],
	//     locations: []
	// })).shifts;

	// let shifts = [];
	//let positions = getPositions(locals.user.uuid);

	// console.log("Shifts:");
	// console.log((await getAdminShifts(thisWeek)));

	const [employeeResponse, shifts, positions] = await Promise.all([
		getEmployees(locals.user.uuid),
		getAllShiftsForAdmin(locals.user.uuid, {
			time_start: '2023-01-09T00:00:00Z',
			time_end: '2023-01-16T00:00:00Z',
			positions: [],
			locations: []
		}),
		getPositions(locals.user.uuid)
	]);

	console.log(employeeResponse)

	return {
		// roles: roles,
		employees: employeeResponse.employees,
		shifts: shifts.shifts,
		positions: positions.positions,
		adminID: locals.user.uuid
	};
}

/** Form Actions */

/** @type {import (./$types).Actions} */
export const actions = {
	location: async ({ request, locals }) => {
		const data = Object.fromEntries(await request.formData());

		let location = data.location

		const response = await createLocation(locals.user.uuid, { location } );

		if (response.error) {
			return fail(401, { error: response.error });
		}

		return { location: true };
	},
	create: async ({ request, locals }) => {
		console.log('Create called');

		// Get the form data
		const {
			firstName,
			lastName,
			email,
			phone,
			address,
			newPassword,
			newPasswordConfirm,
			minimum_weekly_hours,
			positions,
			error
		} = await loadEmployeeFormData(
			request,
			'firstName lastName email phone address newPassword newPasswordConfirm minimum_weekly_hours positions'.split(
				' '
			)
		);

		if (error) {
			console.error('Load Error: ' + error);
			return fail(401, { error: error });
		}

		if (!newPassword) {
			return fail(401, { error: 'New password cannot be null' });
		}

		if (!newPasswordConfirm) {
			return fail(401, { error: 'Confirm password cannot be null' });
		}

		if (newPassword !== newPasswordConfirm) {
			return fail(401, { error: "Password and confirm don't match" });
		}

		// Get the existing positions from the API
		let existingPositions = (await getPositions(locals.user.uuid)).positions;

		// Add all the new positions
		await createNeededPositions(locals.user.uuid, existingPositions, positions);

		const createData = createEmployee(locals.user.uuid, {
			first_name: firstName,
			last_name: lastName,
			email: email,
			telephone: phone,
			address: address,
			positions: positions,
			starting_pass: newPassword,
			minimum_weekly_hours: minimum_weekly_hours
		});

		if (createData.error) {
			console.error('Create Error: ' + createData.error);
			return fail(401, { error: createData.error });
		}

		throw redirect(302, '/admin/employees');
	},
	update: async ({ request, locals }) => {
		console.log('Update called');

		// Get the form data
		const {
			id,
			firstName,
			lastName,
			phone,
			address,
			newPassword,
			newPasswordConfirm,
			minimum_weekly_hours,
			positions,
			error
		} = await loadEmployeeFormData(
			request,
			'firstName lastName phone address minimum_weekly_hours'.split(' ')
		);

		if (error) {
			console.error('Update Error: ' + error);
			return fail(401, { error: error });
		}

		if (newPassword && newPassword !== '') {
			if (!newPasswordConfirm || newPasswordConfirm === '') {
				return fail(401, { error: 'Confirm password cannot be null' });
			}

			if (newPassword !== newPasswordConfirm) {
				return fail(401, { error: "Password and confirm don't match" });
			}
		}

		// Get the employee
		const employeeData = await getEmployee(locals.user.uuid, id);

		if (employeeData.error) {
			return { error: 'Cannot read employee to update' };
		}

		// Get the existing positions from the API
		let existingPositions = (await getPositions(locals.user.uuid)).positions;

		// Add all the new positions
		await createNeededPositions(locals.user.uuid, existingPositions, positions);

		// Read the data from the object
		const employee = employeeData.employee;

		// Update the values
		employee.first_name = firstName;
		employee.last_name = lastName;
		employee.telephone = phone;
		employee.address = address;
		employee.minimum_weekly_hours = minimum_weekly_hours;
		employee.positions = positions;

		// Remove the ID
		delete employee.id;

		// Temporary
		delete employee._rid;
		delete employee._self;
		delete employee._etag;
		delete employee._attachments;
		delete employee._ts;

		// Call the update function
		await updateEmployee(locals.user.uuid, id, employee);

		throw redirect(302, '/admin/employees');
	},
	shiftAssign: async ({ request }) => {
		console.log('Assign shifts called');

		// Get the form data
		const { id, shifts, error } = await loadAssignShiftsFormData(request);

		if (error) {
			console.error('Shift assign error: ' + error);
			return fail(401, { error: error });
		}

		// Assign the shifts to the employee
		await assignShiftsToEmployee(id, shifts);

		throw redirect(302, '/admin/employees');
	}
};

/** Private Functions */

async function createNeededPositions(adminUUID, existingPositions, newPositions) {
	// Don't do anything if we don't have new positions
	if (newPositions.length === 0) {
		return;
	}

	// Get the positions we need to create
	const neededPositions = newPositions.filter((p) => !existingPositions.includes(p));

	// Create each position
	for (const pos of neededPositions) {
		await createPosition(adminUUID, {
			position: pos
		});
	}
}

async function loadEmployeeFormData(request, requiredFields = []) {
	const data = Object.fromEntries(await request.formData());
	const checkRes = checkContainsPropertyList(data, requiredFields);

	// console.log(data);

	if (!checkRes.isOK) {
		const many = checkRes.missing.length > 0;
		const propList = checkRes.missing.map((p) => "'" + p + "'").join(', ');

		return {
			error: `Missing ${many ? 'properties' : 'property'} ${propList}`
		};
	}

	// Get the properties
	const id = parseInt(data.id);
	const positions = JSON.parse(data.positions);
	const minimum_weekly_hours = parseInt(data.minimum_weekly_hours);

	// Make sure we don't have a redundant ID
	delete data.id;

	// Delete the other properties
	delete data.minHoursPerWeek;
	delete data.positions;
	delete data.minimum_weekly_hours;

	return {
		id: id,
		positions: positions,
		minimum_weekly_hours: minimum_weekly_hours,
		manual_availability: data.manual_availability ? data.manual_availability : [],
		...data
	};
}

async function loadAssignShiftsFormData(request) {
	const data = Object.fromEntries(await request.formData());
	const checkRes = checkContainsPropertyList(data, ['id', 'shifts']);

	console.log(data);

	if (!checkRes.isOK) {
		const many = checkRes.missing.length > 0;
		const propList = checkRes.missing.map((p) => "'" + p + "'").join(', ');

		return {
			error: `Missing ${many ? 'properties' : 'property'} ${propList}`
		};
	}

	return {
		id: parseInt(data.id),
		shifts: JSON.parse(data.shifts).map((s) => s.shift_id)
	};
}
