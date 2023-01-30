<script>
    import Week from '$lib/Week.svelte';
	import Day from '$lib/Day.svelte';
    
    import MultiSelect from 'svelte-multiselect';
    
    /** @type {import('./$types').PageData} */
    export let data;
    
	let firstDayOfWeek; // Might not be needed?
	let selectedDate = new Date();
    selectedDate.setMilliseconds(0);
    let addStart = '09:00';
    let addEnd = '17:00'; 
    let timeSlots = [];
    let selectedLocation;
    let selectedEmployees = [];
    let generatedShifts = [];

    let min_employees = 1;
    let max_employees = 3;
    let min_shift_length = 4;
    let max_shift_length = 8;

    let page = 0;

    const weekDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    
    let options = data.employees?.map(e => e.id) || [];
    let locations = data.locations ?? [];

    $: console.log(data.employees);

    function getEmployeeFromID(id) {
        const employee = data.employees.filter(e => e.id === id)[0];
        //console.log("ID" + id)
        return employee.first_name + " " + employee.last_name + " (" + employee.email + ")";
    }

    function formatDay(day) {
		return day.getUTCFullYear() + '-' + day.getUTCMonth() + '-' + day.getUTCDate();
	}

    function toTime(date) {
		return date.toLocaleTimeString('en', { hour: 'numeric', minute: 'numeric', hour12: false });
	}

    function isSameDay(day1, day2) {
		return (
			day1.getUTCFullYear() === day2.getUTCFullYear() &&
			day1.getUTCMonth() === day2.getUTCMonth() &&
			day1.getUTCDate() === day2.getUTCDate()
		);
	}

    function getSlotsForDay(slotDays, thisDay) {
		if (!slotDays) {
			return [];
		}
		return slotDays.filter((slot) => isSameDay(new Date(slot.start), thisDay));
	}

    function getTimeDifference(start, end) {
		return (end - start) / (1000 * 60 * 60);
	}

    function addSlot() {
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
			timeSlots.some((slot) => {
				const slotStart = new Date(slot.start);
				const slotEnd = new Date(slot.end);
				return (
					(addStartDate >= slotStart && addStartDate < slotEnd) ||
					(addEndDate > slotStart && addEndDate <= slotEnd)
				);
			})
		) {
			alert('Slot overlaps with existing slot');
			return;
		}

		// Check if availability is less than an hour
		if (getTimeDifference(addStartDate, addEndDate) < 1) {
			alert('Slot must be at least an hour long');
			return;
		}

		timeSlots.push({
			start: addStartDate.toISOString(),
			end: addEndDate.toISOString()
		});
		timeSlots = timeSlots;
    }

    function removeSlot(day, start) {
		start = new Date(start);
		timeSlots = timeSlots.filter((slot) => {
			const slotStart = new Date(slot.start);
			return !(isSameDay(slotStart, day) && slotStart.getTime() === start.getTime());
		});
	}

	function newWeek(e) {
		// Do something with new week#
		// e.detail
        timeSlots = []
	}


    async function generateShifts() {
        if (!selectedLocation) {
            alert("Must select a location");
            return;
        }
        if (selectedEmployees.length < 1) {
            alert("Must select at least one employee");
            return;
        }
        if (timeSlots.length < 1) {
            alert("Must have at least one time slot");
            return;
        }
        const response = await fetch('/admin/auto-scheduler', {
            method: 'POST',
            headers: {
				'Content-Type': 'application/json'
			},
            body: JSON.stringify({
                week_start: firstDayOfWeek,
                uuids: selectedEmployees,
                location: selectedLocation,
                operating_hours: timeSlots,
                min_employees,
                max_employees,
                min_shift_length,
                max_shift_length
            })
        });

        if (!response.ok) {
            alert("Error creating shifts")
            return;
        }

        const info = await response.json();
        generatedShifts = info.solutions;
        console.log(generatedShifts);
        page = 1;
    }
    
    async function addAllShifts(weekShifts) {
        const response = await fetch('/admin/auto-scheduler/add-shifts', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                shifts: weekShifts,
            })});

        const info = await response.json();

        if (info.error) alert("Error adding shifts");
        else alert("All shifts added succesfully")
    }
</script>

<div class="container-xl pb-5 mb-5">
    {#if page === 0}
    <section class="w-100 mt-5 p-5 bg-light shadow rounded-3 border border-dark">

        <div class="d-flex justify-content-between">
            <h1>Choose Options</h1>
            <button class="btn btn-info" class:d-none={!generatedShifts.length} on:click={() => page = 1} >Go to generated schedules</button>
        </div>

        <form>
            <div class="mb-3">
                <label for="employees" class="form-label">Employees</label>
                <MultiSelect 
                    id="employees" 
                    bind:selected={selectedEmployees} 
                    bind:options={options}
                >
                    <span let:option slot="selected"> {getEmployeeFromID(option)} </span>
                    <span let:option slot="option"> {getEmployeeFromID(option)} </span>
                </MultiSelect>
            </div>
            <div class="mb-3">
                <label for="location" class="form-label">Location</label>
                <select class="form-select" name="location" id="location" bind:value={selectedLocation} required>
                    <option value="" selected>Select one</option>
                    {#each locations as location}
                        <option value={location}>{location}</option>
                    {/each}
                </select>
            </div>
            <div class="row mb-3">
                <div class="col">
                    <label class="form-label" for="min_emp">Min employees</label>
                    <input type="number" class="form-control" name="min_emp" min="1" bind:value={min_employees}>
                </div>
                <div class="col">
                    <label class="form-label" for="max_emp">Max employees</label>
                    <input type="number" class="form-control" name="max_emp" min="1" bind:value={max_employees}>
                </div>
                <div class="col">
                    <label class="form-label" for="min_shift_length">Min shift length (hours)</label>
                    <input type="number" class="form-control" name="min_shift_length" min="1" bind:value={min_shift_length}> 
                </div>
                <div class="col">
                    <label class="form-label" for="max_shift_length">Max shift length (hours)</label>
                    <input type="number" class="form-control" name="max_shift_length" min="1" bind:value={max_shift_length}>
                </div>
            </div>
        </form>

        <h2>Add Opening Hours</h2>

        <Week
            let:selectable
            let:weekDates
            bind:firstDayOfWeek
            bind:selectedDate
            on:weekChange={newWeek}
        >
            {#each weekDates as date}
                <Day day={date} bind:selectedDate {selectable}>
                    {#each getSlotsForDay(timeSlots, date) as slot}
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
								class="btn btn-primary"
								on:click={addSlot}
                            >Add slot</button>
						</div>
					</div>
                </div>
                {#each getSlotsForDay(timeSlots, selectedDate) as { start, end }}
                    <div class="d-flex mb-1">
                        <div class="text-bg-success rounded-1 py-1 px-2 col">
                            <span class="align-middle fs-5"
                                >{toTime(new Date(start)) + ' - ' + toTime(new Date(end))}
                                <button
                                    class="badge bg-danger btn"
                                    on:click={removeSlot(selectedDate, start)}>Remove</button
                                >
                            </span>
                        </div>
                    </div>
                {:else}
                    <p class="text-muted">No availability set</p>
                {/each}
            </div>
        </Week>
        <hr>
        <div class="d-grid">
            <button class="btn btn-primary mt-3" on:click={() => generateShifts()}>Auto-generate Shifts</button>
        </div>
    </section>

    {:else}

    <section class="w-100 mt-5 p-5 bg-light shadow rounded-3 border border-info pb-5">
        <div class="d-flex justify-content-between mb-3">
            <h2>Generated Schedules</h2>
            <button class="btn btn-info" on:click={() => page = 0}>Go back</button>
        </div>
        {#each generatedShifts as weekShifts, i}
        <h4>Option {i+1}</h4>
        <ul class="list-group mb-2">
            {#each weekShifts as shift}
            <li class="list-group-item">
                    <b>{weekDays[(new Date(shift.time_slot['start']).getDay())]}</b>
                    <span class="badge text-bg-warning" style="font-size: 1em">
                        {toTime(new Date(shift.time_slot['start'])) + '-' + toTime(new Date(shift.time_slot['end']))}
                    </span>
                    {getEmployeeFromID(shift['uuid'])} 
            </li>
            {/each}
            </ul>
            <button class="btn btn-success" on:click={() => addAllShifts(weekShifts)}>Add all shifts</button>
            <hr>

        {:else}
            <p class="text-muted">No shifts generated yet</p>
        {/each}
    </section>

    {/if}
</div>