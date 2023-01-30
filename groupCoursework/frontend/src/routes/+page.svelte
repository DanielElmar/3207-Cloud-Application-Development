<script>
	import { onMount } from 'svelte';
	/** @type {import('./$types').PageData} */
	export let data;

	let start;
	let arrow;

	onMount(() => {
		start.addEventListener('mouseleave', () => {
			arrow.classList.add('bi-arrow-right-short');
			arrow.classList.remove('bi-arrow-right');
		});
		start.addEventListener('mouseenter', () => {
			arrow.classList.add('bi-arrow-right');
			arrow.classList.remove('bi-arrow-right-short');
		});
	});
</script>

<svelte:head>
	<title>Shiftable</title>
</svelte:head>

<div id="main" class="container-fluid p-5 h-100 d-flex flex-column">
	<div id="center-piece" class="w-75">
		<h1 class="display-1 mt-5 fw-bold text-white">Organise your shifts in one easy place</h1>
		<p class="lead mt-3 text-light">
			Shiftable places all the important information right where you need it, and provides you with
			the tools to organise your business. (New upload NEW)
		</p>
		{#if !data.user}
			<a
				type="button"
				bind:this={start}
				class="btn btn-lg text-white d-inline rounded-0"
				id="get-started"
				href="/register"
				>Start now
				<i id="arrow" bind:this={arrow} class="bi bi-arrow-right-short text-white d-inline" />
			</a>
		{:else}
			<a
				type="button"
				bind:this={start}
				class="btn btn-lg text-white d-inline rounded-0"
				id="get-started"
				href="/employee/schedule"
				>Check schedule
				<i id="arrow" bind:this={arrow} class="bi bi-arrow-right-short text-white d-inline" /></a
			>
		{/if}
	</div>
</div>

<style>
	#arrow {
		vertical-align: -1px;
	}
	.container-fluid {
		background: linear-gradient(120deg, rgb(208, 138, 255) 0%, rgb(87, 0, 168) 100%);
	}
	#get-started {
		background: linear-gradient(90deg, rgb(69, 0, 197), rgb(93, 6, 255));
		border: none;
	}
	#get-started:hover {
		opacity: 0.8;
	}
	@media (min-width: 1400px) {
		#center-piece {
			width: 50% !important;
		}
	}
</style>
