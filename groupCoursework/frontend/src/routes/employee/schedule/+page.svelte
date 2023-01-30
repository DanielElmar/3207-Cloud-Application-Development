<script>
	import { goto } from '$app/navigation';
	import Week from '$lib/Week.svelte';
	import Day from '$lib/Day.svelte';

	/** @type {import('./$types').PageData} */
	export let data;

	let modalShift = null;

	let selectedDate = new Date();
	let firstDayOfWeek = new Date(data.week_commencing);

	let datesOfWeek, selectedWeekEnd;
	$: datesOfWeek = getDatesOfWeek(firstDayOfWeek);
	$: selectedWeekEnd = getLastDayOfWeek(firstDayOfWeek);

	// return first day of week mon - sun
	function getFirstDayOfWeek(dayDate) {
		let date = new Date(dayDate);
		let day = date.getDay(),
			diff = date.getDate() - day + (day === 0 ? -6 : 1);
		return new Date(date.setDate(diff));
	}

	//get last day of week
	function getLastDayOfWeek(dayDate) {
		let date = new Date(dayDate);
		let day = date.getDay(),
			diff = date.getDate() - day + (day === 0 ? -6 : 1);
		return new Date(date.setDate(diff + 6));
	}

	// return all dates within week containing day mon - sun
	function getDatesOfWeek(day) {
		let date = new Date(firstDayOfWeek);
		let dates = [];
		for (let i = 0; i < 7; i++) {
			dates.push(new Date(date));
			date.setDate(date.getDate() + 1);
		}
		return dates;
	}

	function getTime(dateString) {
		let date = new Date(dateString);
		return date.toLocaleTimeString('en', { hour: 'numeric', minute: 'numeric', hour12: false });
	}

	function shiftsOnDate(dateString, iterateMe, extraCheck) {
		let date = new Date(dateString);
		let ret = [];

		//console.log(iterateMe)
		//console.log(datesOfWeek)
		//console.log(date)

		for (const shift of iterateMe) {
			let date2 = new Date(shift.time_slot.start);
			if (
				date2.getDate() === date.getDate() &&
				date2.getMonth() === date.getMonth() &&
				date2.getFullYear() === date.getFullYear()
			) {
				switch (extraCheck) {
					case 0:
						ret.push(shift);
						break;
					case 1:
						if (!shift.cover) {
							ret.push(shift);
						}
						break;
					case 2:
						if (shift.cover) {
							ret.push(shift);
						}
						break;
					default:
						break;
				}
			}
		}
		return ret;
	}

	function shiftClicked(dataArg) {
		modalShift = dataArg;
	}

	function weekChange() {
		firstDayOfWeek = firstDayOfWeek;

		goto('?weekCommencing=' + firstDayOfWeek.toDateString());
	}
</script>

<svelte:head>
	<title>Shiftable</title>
</svelte:head>

<div class="container-xxl">
	<section class="w-100 mt-5 p-5 bg-light shadow rounded-3">
		{#if !data.error}
			<h2>My Schedule</h2>

			<Week
				let:selectable
				let:weekDates
				bind:firstDayOfWeek
				bind:selectedDate
				on:weekChange={(e) => weekChange(e.detail)}
			>
				{#each weekDates as day}
					<Day {day} bind:selectedDate {selectable}>
						{#each shiftsOnDate(day, data.shifts, 1) as shift}
							<button
								type="button"
								on:click={() => shiftClicked(shift)}
								class="btn btn-success mb-1 badge shadow badge fw-bold text-wrap"
								data-bs-toggle="modal"
								data-bs-target="#shiftDetailsModal"
							>
								{getTime(shift.time_slot.start) + ' - ' + getTime(shift.time_slot.end)}
							</button>
						{/each}
						{#each shiftsOnDate(day, data.shifts, 2) as shift}
							<button
								type="button"
								on:click={() => shiftClicked(shift)}
								class="btn btn-info mb-1 shadow badge fw-bold text-wrap"
								data-bs-toggle="modal"
								data-bs-target="#shiftDetailsModal"
							>
								{getTime(shift.time_slot.start) + ' - ' + getTime(shift.time_slot.end)}
							</button>
						{/each}
					</Day>
				{/each}

				<div slot="key">
					<div class="d-flex align-items-center m-2">
						<span class="ms-3"
							><span class="btn btn-success pe-none" /> My Shifts (Not advertised)</span
						>
						<span class="ms-3"><span class="btn btn-info pe-none" /> My Shifts (Advertised)</span>
					</div>
				</div>

				<div slot="day">
					<h2>
						{selectedDate.toLocaleDateString('en-UK', {
							weekday: 'long',
							day: '2-digit',
							month: 'long',
							year: 'numeric'
						})}
					</h2>
					{#if selectedDate !== null}
						{#if shiftsOnDate(selectedDate, data.shifts, 0).length === 0}
							<p class="text-muted">You have no shifts schedules for this day</p>
						{:else}
							<div class="d-grid mb-3" style="grid-template-columns: repeat(auto-fill, 4.1666%);">
								{#each Array(24) as _, i}
									<div class="border">
										{#if i < 10}
											<span>0{i}</span>
										{:else}
											<span>{i}</span>
										{/if}
									</div>
								{/each}
							</div>
							{#each shiftsOnDate(selectedDate, data.shifts, 1) as { shift_id, employee_id, time_slot, location, cover, coveree, prev_owners }}
								<button
									class="btn btn-success mb-2 shadow badge fs-6 fw-bold text-wrap"
									style="height: 75px; width: auto; margin-left: {((new Date(
										time_slot.start
									).getHours() +
										new Date(time_slot.start).getMinutes() / 60) /
										24) *
										100}%; width: {((new Date(time_slot.end).getHours() +
										new Date(time_slot.end).getMinutes() / 60) /
										24) *
										100 -
										((new Date(time_slot.start).getHours() +
											new Date(time_slot.start).getMinutes() / 60) /
											24) *
											100}%"
									type="button"
									on:click={() =>
										shiftClicked({
											shift_id,
											employee_id,
											time_slot,
											location,
											cover,
											coveree,
											prev_owners
										})}
									data-bs-toggle="modal"
									data-bs-target="#shiftDetailsModal"
								>
									{getTime(time_slot.start) + ' - ' + getTime(time_slot.end)}
								</button>
							{/each}
							{#each shiftsOnDate(selectedDate, data.shifts, 2) as { shift_id, employee_id, time_slot, location, cover, coveree, prev_owners }}
								<button
									class="btn btn-info mb-2 shadow badge fs-6 text-wrap"
									style="height: 75px; width: auto; margin-left: {((new Date(
										time_slot.start
									).getHours() +
										new Date(time_slot.start).getMinutes() / 60) /
										24) *
										100}%; width: {((new Date(time_slot.end).getHours() +
										new Date(time_slot.end).getMinutes() / 60) /
										24) *
										100 -
										((new Date(time_slot.start).getHours() +
											new Date(time_slot.start).getMinutes() / 60) /
											24) *
											100}%"
									type="button"
									on:click={() =>
										shiftClicked({
											shift_id,
											employee_id,
											time_slot,
											location,
											cover,
											coveree,
											prev_owners
										})}
									data-bs-toggle="modal"
									data-bs-target="#shiftDetailsModal"
								>
									{getTime(time_slot.start) + ' - ' + getTime(time_slot.end)}
								</button>
							{/each}
						{/if}
					{:else}
						<div class="text-muted">No Shifts This Day</div>
					{/if}
				</div>
			</Week>
		{:else}
			<h2>Server Error</h2>
			<div class="alert alert-danger m-0 mt-3" role="alert">Server Error: {data.error}</div>
		{/if}
	</section>
</div>

<!-- POP UP MODAL -->
<div class="modal fade" id="shiftDetailsModal" tabindex="-1" aria-hidden="true">
	<div class="modal-dialog">
		<div class="modal-content">
			<div class="modal-header">
				<h2 class="modal-title">Shift Details</h2>
				<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" />
			</div>
			<div class="modal-body">
				<p>Details</p>
				{#if modalShift != null}
					<ul>
						<li>Shift ID: {modalShift.shift_id}</li>
						<li>Shift Location: {modalShift.location}</li>
						<li>
							Shift Start Date: {new Date(modalShift.time_slot.start).toLocaleDateString('en-UK')}
						</li>
						<li>Shift Start Time: {getTime(modalShift.time_slot.start)}</li>
						<li>Shift End Time: {getTime(modalShift.time_slot.end)}</li>
					</ul>
				{/if}
			</div>
		</div>
	</div>
</div>
