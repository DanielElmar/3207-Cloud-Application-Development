<script>
    import {goto, invalidateAll} from '$app/navigation';
	import Day from '$lib/Day.svelte';
	import Week from '$lib/Week.svelte';

	/** @type {import('./$types').PageData} */
	export let data;

	let modalApproval = null;

	let selectedDate = new Date();
	let firstDayOfWeek = new Date(data.week_commencing);

	let datesOfWeek, selectedWeekEnd;
	$: datesOfWeek = getDatesOfWeek(firstDayOfWeek);
	$: selectedWeekEnd = getLastDayOfWeek(firstDayOfWeek);

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
		let time = date.toLocaleTimeString('en', { hour: 'numeric', minute: 'numeric', hour12: false });

		return time === '24:00' ? '00:00' : time;
	}

    function approvalClicked(dataArg){
        modalApproval = dataArg
    }

	function weekChange() {
		firstDayOfWeek = firstDayOfWeek;

        data = {approvals: [], loading: true}

        console.log(data)

		goto('?weekCommencing=' + firstDayOfWeek.toDateString());
	}

	async function approveRequestServerLink(obj) {
        return await fetch('/admin/approvals/submitApproval', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(obj)
		})
        .then(response => {
            console.log(response);
            return response.json();
        })


    }

	function approveRequest(obj) {
		let resp = approveRequestServerLink(obj)
        console.log("rfffdwfh5")
        console.log(resp)
	}

    /*.then((data) => {
            console.log('RESP: ');

            console.log("111111")
            console.log(data)


            if (data === "availability set successfully"){
                console.log("REMOVE")
                console.log(obj)
                console.log("FROM")
                console.log(data.approvals)
                data.approvals.pop(obj)
                console.log(data.approvals)
            }
            invalidateAll();
        });;*/

    function modalSubmit(approvalObject, approvedBool){
        approvalObject['approved'] = approvedBool;
        approveRequest(approvalObject);

        invalidateAll();

        //data = {approvals: [], loading: true}
        //goto('?weekCommencing=' + firstDayOfWeek.toDateString());
    }

	function availabilityOnDate(dateString, iterateMe, extraCheck) {
		let date = new Date(dateString);
		let ret = [];

		for (const available of iterateMe) {
			let date2 = new Date(available.start);
			if (
				date2.getDate() === date.getDate() &&
				date2.getMonth() === date.getMonth() &&
				date2.getFullYear() === date.getFullYear()
			) {
				ret.push(available);
			}
		}
		return ret;
	}
</script>

<svelte:head>
	<title>Shiftable</title>
</svelte:head>

<div class="container-xxl">

    <section class="w-100 mt-5 p-5 bg-light shadow-sm rounded-3">

        {#if !data.error}
            <h2>Approvals</h2>

        <div>
            {#if (selectedDate !== null)}
                {#if data.approvals !== undefined}
                    {#if data.approvals.size === 0}
                        <p class="text-muted">You have no approvals for this day</p>
                    {/if}
                    <Week let:selectable let:weekDates bind:firstDayOfWeek bind:selectedDate on:weekChange={(e) => weekChange(e.detail)}>
                        <div class="mt-3">
                            {#each data.approvals as approval}
                                <div>
                                    <button type="button" on:click={ () => approvalClicked(approval)}
                                            class="btn btn-success mb-2 p-3 badge shadow badge fw-bold fs-5 text-wrap w-25"
                                            data-bs-toggle="modal" data-bs-target="#approveRequestModal">
                                            Weekly Availablity: {approval.first_name} {approval.last_name}
                                    </button>

                                    </div>
                                {/each}
                            {#if data.loading}
                                <div class="d-flex">
                                    <p class="me-3 fs-5">Loading...</p>
                                    <div class="spinner-border" role="status">
                                        <span class="sr-only"></span>
                                    </div>
                                </div>
                            {:else}
                                {#if data.approvals.length == 0}<h4>Nothing to approve</h4>{/if}
                            {/if}
                        </div>
                    </Week>

                    {/if}
                {:else}
                    <div class="text-muted">No Shifts This Day</div>
                {/if}
            </div>

        {:else}
            <h2>Server Error</h2>
            <div class="alert alert-danger m-0 mt-3" role="alert">Server Error: {data.error}</div>
        {/if}

    </section>
</div>

<div class="modal modal-xl fade" id="approveRequestModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title">Availablity</h2>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">



                {#if (modalApproval != null)}
                    <p>Details</p>
                    <ul>
                        <li> Employee ID: {modalApproval.id} </li>
                        <li> Minimum week hours: {modalApproval.minimum_weekly_hours} </li>
                        <li> Current hours: {modalApproval.availability.current_hours} </li>
                        <li> Approved? {modalApproval.availability.approved} </li>
                        <li> General Notes: {modalApproval.availability.notes} </li>
                    </ul>

					<p>Time Off Requests</p>
					{#each modalApproval.availability.time_off as timeOff}
						<ul>
							<li>Amount Off: {timeOff.amount}</li>
							<li>Pay Type: {timeOff.pay_type}</li>
							<li>Specific notes: {timeOff.notes}</li>
						</ul>
					{/each}



                    <Week  controls={false} let:selectable let:weekDates bind:firstDayOfWeek bind:selectedDate on:weekChange={(e) => weekChange(e.detail)}>
                        {#each weekDates as day}
                            <Day {day} bind:selectedDate {selectable}>

                                {#each availabilityOnDate(day, modalApproval.availability.availabilities) as availableTime}
                                    <span
                                            class="badge text-bg-success ms-2 mb-2 p-3  badge shadow fw-bold text-wrap"
                                            data-bs-toggle="modal" data-bs-target="#shiftDetailsModal">
                                        { getTime(availableTime.start) + " - " + getTime(availableTime.end) }
                                    </span>
                                {/each}

                            </Day>
                        {/each}

                    </Week>



                {/if}

                
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-info" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-danger" data-bs-dismiss="modal" on:click={modalSubmit(modalApproval, false)}>Deny</button>
                <button type="button" class="btn btn-success" data-bs-dismiss="modal" on:click={modalSubmit(modalApproval, true)}>Approve</button>
            </div>
        </div>
    </div>
</div>
