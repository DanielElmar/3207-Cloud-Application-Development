<script>
	import { onMount } from 'svelte';
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';

	import ShiftEditor from '$lib/ShiftEditor.svelte';

	/** @type {import('./$types').PageData} */
	export let data;

    /** @type {import('./$types').ActionData} */
    export let form;
    
    //page data 
    $: overviewshifts = data.shifts;
    $: employee_ids = data.employees; 
    $: shiftsIndiv = data.keys;
    $: locations = data.everylocation;

    //ui states
    let selectedShift = null;
    let editModal;
    let editorVisible = false; 
    
    
    // form pieces
    let editModalTitle = "Edit Shift";
    let formAction = "create";
    let currentEdit = null;
    

    async function handleDeleteShift(index){
       //Confirm 
       const result = confirm("Are you sure you wish to delete this shift ?");
       
       if(!result){
        return;
       }

       // get item 
       const item = overviewshifts[index];
       const idsToDel = shiftsIndiv[item.id];
    
        for (i in idsToDel){
            const res = await fetch('/admin/shifts/delete',{
                                method: 'POST',
                                headers:{
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    id: i 
                                })
                            });
            if (res.ok){
                console.log(res);
            } else{
                console.log(res);
                alert("Cannot Delete Employee");
            }
        }
        invalidateAll();
        console.log("done");
    }
    function getTime(dateString){
        let date = new Date(dateString)
        return date.toLocaleTimeString('en', { hour: 'numeric', minute: 'numeric', hour12: false } );
    }

    function handleEditShift(index){
        // setting form action 
        formAction = "update";

        //setting object/shift to edit 
        currentEdit = overviewshifts[index];
        console.log(currentEdit);
        // displaying model 
        showModal("Edit Shift"); 
        //setting edit to null as no longer editing 
        
    }
    function handleAddShift(){
        //alert("handle Add shift");
        if ((locations.locations).length === 0){
            alert("you need locations to add shifts");
            return;
        }
        console.log((locations.locations).length === 0 );
        currentEdit = {
            employee_ids: [],
            time_slot: {start: null, end: null},
            location: ''
        };
        
        formAction = "create";
        

        showModal("Add shift"); 
        
    }
    onMount(async () => {
		const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
		const tooltipList = [...tooltipTriggerList].map(
			(tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
		);

		var modal = document.getElementById('editShiftModal'); // shift edit modal
		modal.addEventListener('show.bs.modal', () => (editorVisible = true));
		modal.addEventListener('hidden.bs.modal', () => (editorVisible = false));

		modal.addEventListener('show.bs.modal', function () {
			console.log('Opening dialog...');

			// Get the field
			const employeesField = document.getElementById('Employees'); // change this

			// Focus the first name field
			employeesField.focus(); //change this
		});

		// Add event handlers to the form
		const formControl = document.getElementById('shiftEditor');
		formControl.addEventListener('submit', function () {
			// Log
			console.log('Form submitted');

			// Hide the modal
			editModal.hide();

			// Reload the data after a dialog has been closed
			invalidateAll();
		});
	});
	function showModal() {
		// Load the modal from the HTML body
		editModal = new bootstrap.Modal('#editShiftModal', {
			keyboard: false
		});

		// Show the modal
		editModal.show();
	}
</script>
<section class="container-xl" >
    <div class="card m-4">
        <div class="card-body m-4 p-4">
            <h2 class="card-title">Shifts</h2>
            <h6 class="card-subtitle mb-2 text-muted"> Edit shifts</h6>

			<table class="table mt-4">
				<thead>
					<tr>
						<th scope="col">Id</th>
						<th scope="col">Employees</th>
						<th scope="col">Time</th>
						<th scope="col">Location</th>
						<th scope="col"><!--  Actions --></th>
					</tr>
				</thead>
				<tbody>
					{#each overviewshifts as { shift_id, employee_ids, time_slot, department, location }, index}
						<tr
							on:mouseenter={() => (selectedShift = index)}
							on:mouseleave={() => (selectedShift = null)}
						>
							<th scope="row">{shift_id}</th>
							<td>
								{#each employee_ids as name}
									{name} |
								{/each}
							</td>
							<td>{getTime(time_slot.start)} - {getTime(time_slot.end)}</td>
							<td>{location}</td>
							<td>
								<!--<div class:hidden-action-group={selectedShift !== index}>-->
								<div>
									<button
										type="button"
										class="btn btn-outline-primary"
										on:click={() => handleEditShift(index)}
										data-bs-toggle="tooltip"
										data-bs-title="Edit"
									>
										<i class="bi bi-pencil-square" />
									</button>
									<button
										type="button"
										class="btn btn-outline-danger"
										on:click={() => handleDeleteShift(index)}
										data-bs-toggle="tooltip"
										data-bs-title="Delete"
									>
										<i class="bi bi-trash3" />
									</button>
								</div>
							</td>
						</tr>{/each}
				</tbody>
			</table>
			<div id="footer">
				<button class="btn btn-outline-primary" on:click={handleAddShift}>
					<i class="bi bi-plus-lg" />&nbsp;Add Shift
				</button>
			</div>
		</div>
	</div>
</section>

<!-- Modal -->
<div class="modal fade " id="editShiftModal" tabindex="-1" aria-labelledby="editShiftModalLabel" aria-hidden="true">
    <div class="modal-dialog ">
        <div class="modal-content">
            <div class="modal-header">
                <h1 class="modal-title" id="editShiftModalLabel">{editModalTitle}</h1>
            </div>
            <div class="modal-body">
                <form id="shiftEditor" method="POST" action={"?/" + formAction} use:enhance>
                    {#if editorVisible}
                    <ShiftEditor 
                    shift = {currentEdit ?? {}}
                    employees = {employee_ids}
                    locations = {locations}
                    />
                    {/if}
                </form>
                {#if form?.error}
                    <div class="alert alert-danger" role="alert">{form.error}</div>
                {/if}
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-danger" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary" form="shiftEditor">Save Changes</button>
            </div>
        </div>
    </div>
</div>

<style>
    .container-fluid {
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: stretch;
        align-items: center;
    }
</style>
