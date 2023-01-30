<script>
	import Week from '$lib/Week.svelte';
	import Day from '$lib/Day.svelte';

	/** @type {import('./$types').PageData} */
	export let data;

	import { goto, invalidateAll } from '$app/navigation';

	//TODO: add api calls to update shifts, link employee_ids

	let modalShift = null;

	let selectedDate = new Date();
	let firstDayOfWeek = new Date(data.week_commencing);

	function getTime(dateString) {
		let date = new Date(dateString);
		return date.toLocaleTimeString('en', { hour: 'numeric', minute: 'numeric', hour12: false });
	}

	function shiftsOnDate(dateString, iterateMe, extraCheck) {
		let date = new Date(dateString);
		let ret = [];

		for (const shift of iterateMe) {
			//console.log(shift)

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

	let selectedWeekEnd;
	$: selectedWeekEnd = getLastDayOfWeek(firstDayOfWeek);

	function getLastDayOfWeek(week) {
		let date = new Date(week);
		let day = date.getDay();
		let diff = date.getDate() - day + (day === 0 ? -6 : 1) + 6;
		return new Date(date.setDate(diff));
	}

	async function updateShiftAdvertisement(body) {
		const res = await fetch('/employee/trading-board/updateShiftAdvertisment', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(body)
		});

		return res.json();
	}

	async function takeShift(body) {
		const res = await fetch('/employee/trading-board/takeShift', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(body)
		});

		return res.json();
	}

	function updateShiftCover(shift, namedParams) {
		if (namedParams['cover'] !== undefined) {
			updateShiftAdvertisement({ shiftId: shift.id, available: namedParams['cover'] }).then(
				(data) => {
					console.log('RESP: ' + data['msg']);
					invalidateAll();
				}
			);
		} else if (namedParams.take !== undefined && namedParams.take === true) {
			takeShift({ shiftId: shift.id }).then((data) => {
				console.log('RESP: ');
				console.log(data);
				invalidateAll();
			});
		}
	}
</script>

<svelte:head>
	<title>Shiftable</title>
</svelte:head>

<div class="container-xxl">
	<section class="w-100 mt-5 p-5 bg-light shadow-sm rounded-3">
		{#if !data.error}
			<h2>Trading Board</h2>

			<Week
				title=""
				let:selectable
				let:weekDates
				bind:firstDayOfWeek
				bind:selectedDate
				on:weekChange={(e) => weekChange(e.detail)}
			>
				{#each weekDates as day}
					<Day {day} bind:selectedDate {selectable}>
						{#each shiftsOnDate(day, data.cover_shifts, 0) as shift}
							<button
								type="button"
								on:click={() => shiftClicked(shift)}
								class="btn btn-primary mb-1 shadow badge fs-6 fw-bold"
								data-bs-toggle="modal"
								data-bs-target="#takeShiftModal"
							>
								{getTime(shift.time_slot.start) + ' - ' + getTime(shift.time_slot.end)}
							</button>
						{/each}

						{#each shiftsOnDate(day, data.my_shifts, 1) as shift}
							<button
								type="button"
								on:click={() => shiftClicked(shift)}
								class="btn btn-success mb-1 shadow badge fs-6 fw-bold"
								data-bs-toggle="modal"
								data-bs-target="#advertiseShiftModal"
							>
								{getTime(shift.time_slot.start) + ' - ' + getTime(shift.time_slot.end)}
							</button>
						{/each}

						{#each shiftsOnDate(day, data.my_shifts, 2) as shift}
							<button
								type="button"
								on:click={() => shiftClicked(shift)}
								class="btn btn-info mb-1 shadow badge fs-6 fw-bold"
								data-bs-toggle="modal"
								data-bs-target="#takeDownShiftModal"
							>
								{getTime(shift.time_slot.start) + ' - ' + getTime(shift.time_slot.end)}
							</button>
						{/each}
					</Day>
				{/each}

				<div slot="key">
					<div class="d-flex align-items-center m-2">
						<span class=""><span class="btn btn-primary pe-none" /> Shift available to take</span>
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

						{#each shiftsOnDate(selectedDate, data.cover_shifts, 0) as shift}
							<button
								class="btn btn-primary mb-2 shadow badge fs-6 fw-bold text-wrap"
								style="height: 75px; width: auto; margin-left: {((new Date(
									shift.time_slot.start
								).getHours() +
									new Date(shift.time_slot.start).getMinutes() / 60) /
									24) *
									100}%; width: {((new Date(shift.time_slot.end).getHours() +
									new Date(shift.time_slot.end).getMinutes() / 60) /
									24) *
									100 -
									((new Date(shift.time_slot.start).getHours() +
										new Date(shift.time_slot.start).getMinutes() / 60) /
										24) *
										100}%"
								type="button"
								on:click={() => shiftClicked(shift)}
								data-bs-toggle="modal"
								data-bs-target="#takeShiftModal"
							>
								{getTime(shift.time_slot.start) + ' - ' + getTime(shift.time_slot.end)}
							</button>
						{/each}

						{#each shiftsOnDate(selectedDate, data.my_shifts, 1) as shift}
							<button
								class="btn btn-success mb-2 shadow badge fs-6 text-wrap"
								style="height: 75px; width: auto; margin-left: {((new Date(
									shift.time_slot.start
								).getHours() +
									new Date(shift.time_slot.start).getMinutes() / 60) /
									24) *
									100}%; width: {((new Date(shift.time_slot.end).getHours() +
									new Date(shift.time_slot.end).getMinutes() / 60) /
									24) *
									100 -
									((new Date(shift.time_slot.start).getHours() +
										new Date(shift.time_slot.start).getMinutes() / 60) /
										24) *
										100}%"
								type="button"
								on:click={() => shiftClicked(shift)}
								data-bs-toggle="modal"
								data-bs-target="#advertiseShiftModal"
							>
								{getTime(shift.time_slot.start) + ' - ' + getTime(shift.time_slot.end)}
							</button>
						{/each}

						{#each shiftsOnDate(selectedDate, data.my_shifts, 2) as shift}
							<button
								class="btn btn-info mb-2 shadow badge fs-6 text-wrap"
								style="height: 75px; width: auto; margin-left: {((new Date(
									shift.time_slot.start
								).getHours() +
									new Date(shift.time_slot.start).getMinutes() / 60) /
									24) *
									100}%; width: {((new Date(shift.time_slot.end).getHours() +
									new Date(shift.time_slot.end).getMinutes() / 60) /
									24) *
									100 -
									((new Date(shift.time_slot.start).getHours() +
										new Date(shift.time_slot.start).getMinutes() / 60) /
										24) *
										100}%"
								type="button"
								on:click={() => shiftClicked(shift)}
								data-bs-toggle="modal"
								data-bs-target="#takeDownShiftModal"
							>
								{getTime(shift.time_slot.start) + ' - ' + getTime(shift.time_slot.end)}
							</button>
						{/each}
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

<div class="modal fade" id="takeShiftModal" tabindex="-1" aria-hidden="true">
	<div class="modal-dialog">
		<div class="modal-content">
			<div class="modal-header">
				<h2 class="modal-title">Cover Shift?</h2>
				<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" />
			</div>
			<div class="modal-body">
				<p>Are you willing to take the following shift?</p>

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
			<div class="modal-footer">
				<button type="button" class="btn btn-danger" data-bs-dismiss="modal">Cancel</button>
				<button
					type="button"
					class="btn btn-primary"
					data-bs-dismiss="modal"
					on:click={updateShiftCover(modalShift, { take: true })}>Confirm</button
				>
			</div>
		</div>
	</div>
</div>

<div class="modal fade" id="advertiseShiftModal" tabindex="-1" aria-hidden="true">
	<div class="modal-dialog">
		<div class="modal-content">
			<div class="modal-header">
				<h2 class="modal-title">Advertise Shift?</h2>
				<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" />
			</div>
			<div class="modal-body">
				<p>Do you want to advertise the following shift?</p>

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
			<div class="modal-footer">
				<button type="button" class="btn btn-danger btn-lg" data-bs-dismiss="modal">Cancel</button>
				<button
					type="button"
					class="btn btn-primary btn-lg"
					data-bs-dismiss="modal"
					on:click={updateShiftCover(modalShift, { cover: true })}>Confirm</button
				>
			</div>
		</div>
	</div>
</div>

<div class="modal fade" id="takeDownShiftModal" tabindex="-1" aria-hidden="true">
	<div class="modal-dialog">
		<div class="modal-content">
			<div class="modal-header">
				<h2 class="modal-title">Take Down Shift?</h2>
				<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" />
			</div>
			<div class="modal-body">
				<p>Do you want to stop advertising the following shift?</p>

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
			<div class="modal-footer">
				<button type="button" class="btn btn-danger btn-lg" data-bs-dismiss="modal">Cancel</button>
				<button
					type="button"
					class="btn btn-primary btn-lg"
					data-bs-dismiss="modal"
					on:click={updateShiftCover(modalShift, { cover: false })}>Confirm</button
				>
			</div>
		</div>
	</div>
</div>
