<script>
	import Nav from './Nav.svelte';
	//! Bootstrap Icons !//
	import 'bootstrap-icons/font/bootstrap-icons.css';

	/** @type {import('./$types').LayoutData} */
	export let data;
</script>

<Nav items={data.items} admin={data.admin} />

<main>
	<slot />
</main>

<style>
	:global(main) {
		flex-grow: 1;
		display: flex;
	}
</style>
