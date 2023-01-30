<script>
	import Week from '$lib/Week.svelte';
	import Day from '$lib/Day.svelte';

	let firstDayOfWeek; // Might not be needed?
	let selectedDate = new Date();
	selectedDate.setMilliseconds(0);
	let timeOffField;
	let loading = true;
	let minWeekHours;

    // CHECKING IF VARIABLES HAVE CHANGED
	let notes = '';
	let initialNotes = '';
	let initialAvailability = [];
	let currentAvailability = [];
	let initialTimeOff = [];
	let timeOff = [];
    let initialMaxWeekHours = 0;
	let maxWeekHours = 0;
    let approved = null;

	let timeOffAmount = 1,
		timeOffPayType,
		timeOffNotes = '';

	function isSameDay(day1, day2) {
		return (
			day1.getUTCFullYear() === day2.getUTCFullYear() &&
			day1.getUTCMonth() === day2.getUTCMonth() &&
			day1.getUTCDate() === day2.getUTCDate()
		);
	}

	function formatDay(day) {
		return day.getUTCFullYear() + '-' + day.getUTCMonth() + '-' + day.getUTCDate();
	}

	function toTime(date) {
		return date.toLocaleTimeString('en', { hour: 'numeric', minute: 'numeric', hour12: false, timeZone: 'UTC' });
	}

	function getTimeDifference(start, end) {
		return (end - start) / (1000 * 60 * 60);
	}

	function getSlotsForDay(availabilityDays, thisDay) {
		if (!availabilityDays) {
			return [];
		}
		return availabilityDays.filter((slot) => isSameDay(new Date(slot.start), thisDay));
	}

	// GETTING AVAILABILITY
	let weekPromise = getWeek(new Date());

	async function getWeek(date) {
		loading = true;
		const response = await fetch(
			'/employee/availability?' +
				new URLSearchParams({
					weekCommencing: date.toISOString()
				})
		);
		const info = await response.json();

		if (!response.ok) throw new Error('Server Error'); // If error

		if (!info.availability) {
			// If null
			currentAvailability = [];
			initialAvailability = [];
			timeOff = [];
			initialTimeOff = [];
			notes = '';
			initialNotes = '';
            initialMaxWeekHours = 0;
            maxWeekHours = 0;
            approved = null;
		} else {
			currentAvailability = [...info.availability.availabilities]; // Make new arrays
			initialAvailability = [...info.availability.availabilities];
			initialTimeOff = [...info.availability.time_off];
			timeOff = [...info.availability.time_off];
			notes = info.availability.notes;
			initialNotes = info.availability.notes;
            initialMaxWeekHours = info.availability.max_hours;
            maxWeekHours = info.availability.max_hours;
            approved = info.availability.approved;
		}
		minWeekHours = info.minWeekHours;
		loading = false;

		return info;
	}
	// GETTING AVAILABILITY

	async function weekChange(week) {
		weekPromise = getWeek(week);
	}

	function hasChanged(first, second) {
		return JSON.stringify(first) !== JSON.stringify(second);
	}

	$: changed =
		hasChanged(currentAvailability, initialAvailability) ||
		hasChanged(timeOff, initialTimeOff) ||
		notes !== initialNotes ||
        maxWeekHours !== initialMaxWeekHours;

	async function submitAvailability(def) {
		loading = true;
		const response = await fetch('/employee/availability', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				week_start: firstDayOfWeek,
				availabilities: currentAvailability,
				max_hours: maxWeekHours,
				time_off: timeOff,
				notes: notes,
				def: def
			})
		});

		if (response.ok) {
			initialAvailability = [...currentAvailability];
			initialTimeOff = [...timeOff];
			initialNotes = notes;
			alert('Saved!');
			weekPromise = getWeek(new Date());
		} else {
			alert('Error saving');
		}
		loading = false;
	}

	function addTimeOff() {
		if (minWeekHours - timeOffAmount < 0) {
			timeOffField.setCustomValidity('Cannot take off more hours than contracted for');
			timeOffField.reportValidity();
			return;
		}

		timeOff.push({
			amount: timeOffAmount,
			pay_type: timeOffPayType,
			notes: timeOffNotes
		});
		timeOff = timeOff;
	}

	function removeTimeOff(i) {
		timeOff.splice(i, 1);
		timeOff = timeOff;
	}

	$: {
		if (timeOff.length > 0) {
			maxWeekHours = minWeekHours - timeOff.reduce((a, b) => a + b.amount, 0);
		} else if (maxWeekHours < minWeekHours) {
			maxWeekHours = minWeekHours;
		}
	}

	// ADDING AVAILABILITY
	let addStart = '09:00',
		addEnd = '17:00';

	function addAvailability() {
		if (!addStart && !addEnd) {
			alert('Please select a start and end time');
			return;
		}

		const addStartDate = new Date(selectedDate);
		const addStartSplit = addStart.split(':');
		addStartDate.setHours(addStartSplit[0]);
		addStartDate.setMinutes(addStartSplit[1]);

		const addEndDate = new Date(selectedDate);
		const addEndSplit = addEnd.split(':');
		addEndDate.setHours(addEndSplit[0]);
		addEndDate.setMinutes(addEndSplit[1]);

		if (addStartDate > addEndDate) {
			// Check if start is before end
			alert('Start time cannot be after end time');
			return;
		}

		// Check if availability overlaps with existing availability
		if (
			currentAvailability.some((slot) => {
				const slotStart = new Date(slot.start);
				const slotEnd = new Date(slot.end);
				return (
					(addStartDate >= slotStart && addStartDate < slotEnd) ||
					(addEndDate > slotStart && addEndDate <= slotEnd)
				);
			})
		) {
			alert('Availability overlaps with existing availability');
			return;
		}

		// Check if availability is less than an hour
		if (getTimeDifference(addStartDate, addEndDate) < 1) {
			alert('Availability must be at least an hour long');
			return;
		}

		currentAvailability.push({
			start: addStartDate.toISOString(),
			end: addEndDate.toISOString()
		});
		currentAvailability = currentAvailability;
	}

	function removeAvailability(day, start) {
		start = new Date(start);
		currentAvailability = currentAvailability.filter((slot) => {
			const slotStart = new Date(slot.start);
			return !(isSameDay(slotStart, day) && slotStart.getTime() === start.getTime());
		});
	}

</script>

<svelte:head>
	<title>Shiftable - Availability</title>
</svelte:head>

<!--! TIME OFF MODAL -->
<div
	class="modal modal-lg fade"
	id="timeOff"
	tabindex="-1"
	aria-labelledby="timeOffLabel"
	aria-hidden="true"
>
	<div class="modal-dialog">
		<div class="modal-content">
			<div class="modal-header">
				<h1 class="modal-title fs-5" id="timeOffLabel">Edit time off</h1>
				<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" />
			</div>
			<div class="modal-body">
				<table class="table">
					<thead>
						<tr>
							<th scope="col" class="col-1">Hours</th>
							<th scope="col" class="col-2">Pay type</th>
							<th scope="col">Notes</th>
						</tr>
					</thead>
					<tbody>
						{#each timeOff as slot, i}
							<tr>
								<th scope="row">
									{slot.amount}
									{#if slot.amount > 1}hours{:else}hour{/if}
								</th>
								<td>
									{slot.pay_type}
								</td>
								<td class="text-break">
									{slot.notes}
								</td>
								<td>
									<button class="btn btn-danger" on:click={() => removeTimeOff(i)}>Delete</button>
								</td>
							</tr>
						{/each}
						<tr>
							<th scope="row">
								<div class="input-group" style="width: 130px;">
									<input
										type="number"
										min="1"
										name="amount"
										class="form-control"
										bind:this={timeOffField}
										bind:value={timeOffAmount}
									/>
									<span class="input-group-text" id="basic-addon1">hours</span>
								</div>
							</th>
							<td>
								<select class="form-select" name="payType" bind:value={timeOffPayType}>
									<option value="holiday" selected>Holiday</option>
									<option value="sick">Sick</option>
									<option value="unpaid">Unpaid</option>
								</select>
							</td>
							<td>
								<input
									type="text"
									class="form-control"
									name="notes"
									placeholder="Enter any notes here..."
									bind:value={timeOffNotes}
								/>
							</td>
							<td>
								<button type="submit" class="btn btn-primary" on:click={addTimeOff}>Add</button>
							</td>
						</tr>
					</tbody>
				</table>
			</div>
			<div class="modal-footer">
				<button type="button" class="btn btn-danger" data-bs-dismiss="modal">Close</button>
			</div>
		</div>
	</div>
</div>

<div class="container-xxl pb-5">
	<section class="w-100 mt-5 mb-5 p-5 bg-light shadow rounded-3 border border-dark">
		<div class="d-flex align-items-center border-bottom pb-2">
			<!--! TOP HEADER -->
			<h1 class="me-3 mb-0 d-block">Your Availability</h1>
			{#await weekPromise}
				<div class="spinner-border spinner-border-sm text-primary" role="status">
					<span class="visually-hidden">Loading...</span>
				</div>
			{:then { availability }}
				{#if !availability}
					<div class="alert alert-warning py-1 px-2 mb-0">No availability set</div>
				{:else} 
                    {#if approved}
                        <div class="alert alert-success py-1 px-2 mb-0">Approved</div>
                    {:else if approved === null}
                        <div class="alert alert-warning py-1 px-2 mb-0">Pending Approval</div>
                    {:else}
                        <div class="alert alert-warning py-1 px-2 mb-0">Denied</div>
                    {/if}
                {/if}
			{:catch}
				<button class="btn btn-outline-danger" on:click={weekChange(firstDayOfWeek)}>
					<i class="bi bi-exclamation-triangle-fill" /> Try again
				</button>
			{/await}
			<div class="ms-auto d-flex">
				<div class="input-group" style="width: 170px;">
					<span class="input-group-text" id="basic-addon1">Max hours</span>
					<input
						type="number"
						class="form-control"
						min={minWeekHours}
						bind:value={maxWeekHours}
						disabled={timeOff.length || loading}
					/>
				</div>
				<div class="ms-2">
					<span class="lead">
						Contract hours:
						{#await weekPromise}
							...
						{:then { minWeekHours }}
							{minWeekHours}
						{:catch}
							...
						{/await}
					</span>
				</div>
			</div>
		</div>
		<div class="d-flex align-items-center my-2">
			<!--! BUTTON ACTIONS -->
			<button
				class="btn btn-success"
				class:disabled={!changed}
				on:click={() => submitAvailability(false)}>Submit availability</button
			>
			<button
				class="btn btn-danger ms-2"
				class:disabled={!changed}
				on:click={() => weekChange(firstDayOfWeek)}>Revert changes</button
			>
			<button
				type="button"
				class="btn btn-warning ms-2"
				data-bs-toggle="modal"
				data-bs-target="#timeOff"
				class:disabled={loading}>Edit time off</button
			>
			<div class="ms-auto">
				<button
					class="ms-1 btn btn-outline-primary"
					class:disabled={loading}
					on:click={() => submitAvailability(true)}>Submit as default</button
				>
			</div>
		</div>
		<Week
			let:selectable
			let:weekDates
			bind:firstDayOfWeek
			bind:selectedDate
			on:weekChange={(e) => weekChange(e.detail)}
		>
			{#each weekDates as day}
				<Day {day} bind:selectedDate {selectable}>
					{#each getSlotsForDay(currentAvailability, day) as slot}
						<li class="badge text-bg-success mb-1" style="font-size: 1em">
							{toTime(new Date(slot.start)) + ' - ' + toTime(new Date(slot.end))}
						</li>
					{/each}
				</Day>
			{/each}

			<div slot="day">
				<div class="d-flex align-items-center mb-2">
					<h2 class="d-block mb-0">
						{selectedDate.toLocaleDateString('en-UK', {
							weekday: 'long',
							day: '2-digit',
							month: 'long',
							year: 'numeric'
						})}
					</h2>
					<div class="d-flex ms-auto">
						<div class="input-group" style="width: 155px;">
							<span class="input-group-text">Start</span>
							<input type="time" name="end" class="form-control" bind:value={addStart} />
						</div>
						<div class="input-group ms-2" style="width: 150px;">
							<span class="input-group-text">End</span>
							<input type="time" name="end" class="form-control" bind:value={addEnd} />
						</div>
						<div class="ms-2">
							<button
								class="btn btn-primary btn-block"
								on:click={addAvailability}
								class:disabled={loading}>Add availability</button
							>
						</div>
					</div>
				</div>
				{#await weekPromise}
					<p class="text-muted">Loading...</p>
				{:then}
					{#each getSlotsForDay(currentAvailability, selectedDate) as { start, end }}
						<div class="d-flex mb-1">
							<div class="text-bg-success rounded-1 py-1 px-2 col">
								<span class="align-middle fs-5"
									>{toTime(new Date(start)) + ' - ' + toTime(new Date(end))}
									<button
										class="badge bg-danger btn"
										on:click={removeAvailability(selectedDate, start)}>Remove</button
									>
								</span>
							</div>
						</div>
					{:else}
						<p class="text-muted">No availability set</p>
					{/each}
				{:catch}
					<p class="text-muted">Error loading...</p>
				{/await}
			</div>
		</Week>
		<hr />
		<div class="mb-3">
			<label for="notes" class="form-label">Addtional week notes</label>
			<input
				class="form-control"
				name="notes"
				placeholder="Enter any additional information here..."
				bind:value={notes}
			/>
		</div>
	</section>
</div>

<style>
</style>
