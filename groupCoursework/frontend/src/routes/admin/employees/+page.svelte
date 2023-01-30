<script>
	import { onMount } from 'svelte';
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';

	import MultiSelect from 'svelte-multiselect';
	import parsePhoneNumber from 'libphonenumber-js';

	import { checkShiftsOverlap } from '$lib/utils';

	import EmployeeEditor from '$lib/EmployeeEditor.svelte';

	/** @type {import('./$types').PageData} */
	export let data;

	/** @type {import('./$types').ActionData} */
	export let form;

	// Page Data
	$: employees = data.employees;
	// $: availableRoles = data.roles;
	$: availableShifts = data.shifts.map((s) => {
		s.value = s.shift_id;
		s.label = `${s.time_slot.start} - ${s.time_slot.end}`;
		return s;
	});
	$: availablePositions = data.positions;
	const adminID = data.adminID;

	let currentlyEditing = null;
	let selectedShifts = [];

	// UI State
	let selectedIndex = null;
	let editModalTitle = 'Edit Employee';

	let formAction = 'create';
	let employeeEditorVisible = false;
	let shiftAssignVisible = false;

	$: isAddMode = formAction === 'create';
	$: isEditMode = !isAddMode;

	// UI Components
	let editModal;
	let assignModal;

	onMount(async () => {
		// Set up the tooltips
		const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
		const tooltipList = [...tooltipTriggerList].map(
			(tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
		);

		// Add event handlers to the modal
		var employeeModal = document.getElementById('editEmployeeModal');

		// Handle loading and unloading the editor component
		employeeModal.addEventListener('show.bs.modal', () => (employeeEditorVisible = true));
		employeeModal.addEventListener('hidden.bs.modal', () => (employeeEditorVisible = false));

		employeeModal.addEventListener('shown.bs.modal', function () {
			console.log('Opening employee dialog...');

			// Get the field
			const firstNameField = document.getElementById('firstName');

			// Focus the first name field
			firstNameField.focus();
		});

		var shiftsModal = document.getElementById('shiftAssignModal');

		// Handle loading and unloading the shifts component
		shiftsModal.addEventListener('show.bs.modal', () => (shiftAssignVisible = true));
		shiftsModal.addEventListener('hidden.bs.modal', () => (shiftAssignVisible = false));

		// Add event handlers to the form
		const employeeEditForm = document.getElementById('employeeEditor');
		employeeEditForm.addEventListener('submit', function () {
			// Log
			console.log('Employee edit form submitted');

			// Hide the modal
			editModal.hide();

			// Reload the data after a dialog has been closed
			invalidateAll();
		});

		const shiftAssignForm = document.getElementById('assignShifts');
		shiftAssignForm.addEventListener('submit', function () {
			// Log
			console.log('Shift assign form submitted');

			// Hide the modal
			assignModal.hide();

			// Reload the data after a dialog has been closed
			invalidateAll();
		});
	});

	function handleAddEmployee() {
		// Set a placeholder employee
		currentlyEditing = {
			minimum_weekly_hours: 0,
			positions: []
		};

		// Set the mode for the edit form
		formAction = 'create';

		showEditEmployeeModal('Add Employee');
	}

	function handleEditEmployee(index) {
		// Get the current employee
		const current = employees[index];

		// Set the employee to edit
		currentlyEditing = {
			id: current.id,
			first_name: current.first_name,
			last_name: current.last_name,
			email: current.email,
			telephone: current.telephone,
			address: current.address,
			minimum_weekly_hours: current.minimum_weekly_hours ?? 0,
			positions: current.positions
		};

		// console.log("Currently editing:");
		// console.log(currentlyEditing);

		// Set the mode for the edit form
		formAction = 'update';

		showEditEmployeeModal('Edit Employee');
	}

	function handleEditShifts(index) {
		console.log(employees.map((e) => e.shifts));

		// Get the item at index
		const current = employees[index];

		// Set the employee to edit
		currentlyEditing = {
			id: current.id
		};

		// Set the shifts
		selectedShifts = availableShifts.filter((s) => current.shifts.some((id) => s.shift_id === id));

		console.log('Selected shifts:');
		console.log(selectedShifts);

		// Show the modal
		showAssignShiftsModal();
	}

	async function handleDeleteEmployee(index) {
		// Confirm
		const result = confirm('Are you sure you want to delete this employee?');

		if (!result) {
			return;
		}

		// Get the item at index
		const item = employees[index];

		const res = await fetch('/admin/employees/delete', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				uuid: item.id
			})
		});

		if (res.ok) {
			invalidateAll();
		} else {
			alert('Cannot delete employee');
		}
	}

	function showEditEmployeeModal(title) {
		// Set the title for the form
		editModalTitle = title;

		// Load the modal from the HTML body
		editModal = new bootstrap.Modal('#editEmployeeModal', {

			keyboard: false
		});

		// Show the modal
		editModal.show();
	}

	function showAssignShiftsModal() {
		// Load the modal from the HTML body
		assignModal = new bootstrap.Modal('#shiftAssignModal', {

			keyboard: false
		});

		// Show the modal
		assignModal.show();
	}

	function shiftsCheckForDuplicates(shift1, shift2) {
		console.log('Checking duplicates');

		const label1 = getLabel(shift1);
		const label2 = getLabel(shift2);

		const time1 = extractStartAndEnd(label1);
		const time2 = extractStartAndEnd(label2);

		return checkShiftsOverlap(time1, time2);
	}

	function getLabel(option) {
		return option instanceof Object ? option.label : option;
	}

	function extractStartAndEnd(label) {
		const parts = label.split(' - ');
		return {
			start: parseTime(parts[0]).getTime(),
			end: parseTime(parts[1]).getTime()
		};
	}

	function parseTime(time) {
		return new Date(Date.parse(`1970-01-01T${time}:00.000Z`));
	}

	function isAdminUser(id) {
		return id.toString() === adminID.toString();
	}
</script>

<svelte:head>
	<title>Employees</title>
	<meta name="description" content="Employee Management" />
</svelte:head>

<div class="container-xl">
	<section class="w-100 mt-5 p-5 bg-light shadow-sm rounded-3 overflow-auto">

		<div class="d-flex justify-content-between">
			<h2>Employees</h2>

			<div class="d-flex align-items-center">
				<form class="row g-3 align-items-center" method="POST" action="?/location">
					<div class="col">
						<input type="text" class="form-control" name="location" placeholder="Add location..." required>
					</div>
					<div class="col">
						<button type="submit" class="btn btn-primary">Add Location</button>
					</div>
				</form>
				{#if form?.location}
					<div class="alert alert-success alert-dismissible fade show mb-auto" role="alert">
						Added location
						<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
					</div>
				{/if}
			</div>
		</div>

		<span class="lead">Manage and edit employees</span>

		<table class="table mt-4">
			<thead>
				<tr>
					<th scope="col">ID</th>
					<th scope="col">First Name</th>
					<th scope="col">Last Name</th>
					<th scope="col">Email</th>
					<th scope="col">Phone</th>
					<th scope="col"><!-- Actions --></th>
				</tr>
			</thead>
			<tbody>
				{#each employees as { id, first_name, last_name, email, telephone }, index}
					<tr
						on:mouseenter={() => (selectedIndex = index)}
						on:mouseleave={() => (selectedIndex = null)}
					>
						<th scope="row">{id}</th>
						<td>{first_name}</td>
						<td>{last_name}</td>
						<td>{email}</td>
						<td>{parsePhoneNumber(telephone).formatInternational()}</td>
						<td>
							<div class="btn-group">
								<button
									type="button"
									class="btn btn-outline-primary"
									data-bs-toggle="tooltip"
									data-bs-title="Edit"
									on:click={() => handleEditEmployee(index)}
								>
									<i class="bi bi-pencil-square" />
								</button>

								<button
									type="button"
									class="btn btn-outline-success"
									data-bs-toggle="tooltip"
									data-bs-title="Edit Shifts"
									on:click={() => handleEditShifts(index)}
								>
									<i class="bi bi-clock" />
								</button>

								<button
									type="button"
									class="btn btn-outline-danger"
									data-bs-toggle="tooltip"
									data-bs-title="Delete"
									on:click={() => handleDeleteEmployee(index)}
									disabled={isAdminUser(id) ? 'yes' : null}
								>
									<i class="bi bi-trash3" />
								</button>
							</div>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>

		<div id="footer">
			<button class="btn btn-outline-primary" on:click={handleAddEmployee}>
				<i class="bi bi-plus-lg" />&nbsp;Add Employee
			</button>
		</div>
	</section>
</div>

<!-- Employee Edit Modal -->
<div
	class="modal fade"
	id="editEmployeeModal"
	tabindex="-1"
	aria-labelledby="editEmployeeModalLabel"
	aria-hidden="true">

	<div class="modal-dialog modal-xl">
		<div class="modal-content">
			<div class="modal-header">
				<h1 class="modal-title fs-5" id="editEmployeeModalLabel">{editModalTitle}</h1>
			</div>
			<div class="modal-body">
				<form id="employeeEditor" method="POST" action={'?/' + formAction} use:enhance>
					{#if employeeEditorVisible}
						<EmployeeEditor
							title={editModalTitle}
							user={currentlyEditing ?? {}}
							{availablePositions}
							forceNewPassword={isAddMode}
							disableEmailChange={isEditMode}
						/>
					{/if}
				</form>
				{#if form?.error}
					<div class="alert alert-danger" role="alert">{form.error}</div>
				{/if}
			</div>
			<div class="modal-footer">
				<button type="button" class="btn btn-danger" data-bs-dismiss="modal">Cancel</button>
				<button type="submit" class="btn btn-primary" form="employeeEditor">{formAction === 'create' ? 'Add' : 'Update'}</button>
			</div>
		</div>
	</div>
</div>

<!-- Shift Assign Modal -->
<div
	class="modal fade"
	id="shiftAssignModal"
	tabindex="-1"
	aria-labelledby="shiftAssignModalLabel"
	aria-hidden="true"
>
	<div class="modal-dialog">
		<div class="modal-content">
			<div class="modal-header">
				<h2 class="modal-title fs-5" id="shiftAssignModalLabel">Assign Shifts</h2>
				<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" />
			</div>
			<div class="modal-body">
				<form id="assignShifts" method="POST" action="?/shiftAssign" use:enhance>
					<div class="col-12">
						<div class="form-group">
							<label for="shifts">Select from available shifts:</label>
							{#if shiftAssignVisible}
								<MultiSelect
									name="shifts"
									allowUserOptions={false}
									bind:selected={selectedShifts}
									options={availableShifts}
									duplicateFunc={shiftsCheckForDuplicates}
								>
									<span let:idx let:option slot="option">
										<div class="container">
											<div class="row">
												<div class="col-12">
													<i class="bi bi-clock" />
													{option.time_slot.start} - {option.time_slot.end}
												</div>
												<div class="col-6">
													<i class="bi bi-geo-alt-fill" />
													{option.location}
												</div>
												<div class="col-6">
													<i class="bi bi-building" />
													{option.department}
												</div>
											</div>
										</div>
									</span>

									<span let:idx let:option slot="selected">
										{option.time_slot.start} - {option.time_slot.end}
									</span>
								</MultiSelect>

								{#if currentlyEditing}
									<!-- Hidden Inputs -->
									<input type="hidden" name="id" bind:value={currentlyEditing.id} />
								{/if}
							{/if}
						</div>
					</div>
				</form>
				{#if form?.error}
					<div class="alert alert-danger" role="alert">{form.error}</div>
				{/if}
			</div>
			<div class="modal-footer">
				<button type="button" class="btn btn-danger" data-bs-dismiss="modal">Cancel</button>
				<button type="submit" class="btn btn-primary" form="assignShifts">Save Changes</button>
			</div>
		</div>
	</div>
</div>

<style>
	.hidden-action-group .btn {
		border-color: white;
		background: white;
		text-shadow: 0 1px 1px white;
		-webkit-box-shadow: inset 0 1px 0 white;
		-moz-box-shadow: inset 0 1px 0 white;
		box-shadow: inset 0 1px 0 white;
	}

	.hidden-action-group {
		opacity: 0;
	}
</style>
