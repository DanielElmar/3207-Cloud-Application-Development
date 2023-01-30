<script>
	import { goto, invalidateAll } from '$app/navigation';
	import Week from '$lib/Week.svelte';
	import Day from '$lib/Day.svelte';

	/** @type {import('./$types').PageData} */
	export let data;

    const weekDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

    let selectedDate = new Date();
    selectedDate.setMilliseconds(0);
    let firstDayOfWeek;

	function getTime(dateString) {
		let date = new Date(dateString);
		return date.toLocaleTimeString('en', { hour: 'numeric', minute: 'numeric', hour12: false });
	}

    function getEmployeeByID(id) {
        return data.employees.filter(employee => employee.id === id)[0]
    }

    $: console.log(data.shifts)

	function weekChange() {
		firstDayOfWeek = firstDayOfWeek;

		goto('?weekCommencing=' + firstDayOfWeek.toDateString());
	}

    async function deleteShift(shift) { 
        const response = await fetch('/admin/simple-shifts/deleteShift', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                shift_id: shift.id
            })
        })

        const info = await response.json();

        invalidateAll();
    }
</script>

<svelte:head>
	<title>Shiftable</title>
</svelte:head>

<div class="container-xxl">
	<section class="w-100 mt-5 p-5 bg-light shadow rounded-3">
		{#if !data.error}
			<h2>Shifts</h2>

			<Week
				let:selectable
				let:weekDates
				bind:firstDayOfWeek
				bind:selectedDate
				on:weekChange={(e) => weekChange(e.detail)}
			>
                {#if data?.shifts?.length}
                <ul>
                    {#each data.shifts as shift}
                        <li class="mb-1">Employee: {getEmployeeByID(shift.employee_id).first_name} {getEmployeeByID(shift.employee_id).last_name} ({getEmployeeByID(shift.employee_id).email})-
                            <b>{weekDays[(new Date(shift.time_slot.start).getDay())]}</b>
                            <span class="badge text-bg-success mb-1" style="font-size: 1em">
                                {getTime(shift.time_slot.start) + ' - ' + getTime(shift.time_slot.end)}
                            </span>
                            <button class="ms-3 badge btn btn-danger p-1" style="font-size: 1em" on:click={() => deleteShift(shift)}>Delete shift</button>
                        </li>
                    {/each}
                </ul>
                {:else}
                    <p class="text-muted">No shifts to display</p>
                {/if}
				
			
			</Week>
		{:else}
			<h2>Server Error</h2>
			<div class="alert alert-danger m-0 mt-3" role="alert">Server Error: {data.error}</div>
		{/if}
	</section>
</div>
