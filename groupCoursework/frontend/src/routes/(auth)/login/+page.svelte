<script>
	import { enhance } from '$app/forms';

	/** @type {import('./$types').ActionData} */
	export let form;

	$: if (form?.error) submitted = false;
	let submitted;
</script>

<svelte:head>
	<title>Login</title>
	<meta name="description" content="Login page" />
</svelte:head>

<section class="container-fluid py-5 align-self-center">
	<div class="bg-light border p-3 rounded-3" style="min-width: 400px">
		<h1 class="text-center mb-2 display-4">Log in</h1>
		<p class="text-muted text-center mb-3">Please log in to your account</p>

		<form method="POST" on:submit={() => (submitted = true)} use:enhance>
			<div class="form-outline mb-3">
				<label for="username" class="form-label">Email</label>
				<input class="form-control" name="email" type="email" placeholder="Email" required />
			</div>
			<div class="mb-4">
				<label for="password" class="form-label">Password</label>
				<input
					minlength="8"
					class="form-control"
					name="password"
					type="password"
					placeholder="Password"
					required
				/>
			</div>
			<button type="submit" class="btn btn-primary w-100" class:disabled={submitted}>
				{#if submitted}
					Signing in...
				{:else}
					Sign in
				{/if}
			</button>
			{#if form?.error}
				<div class="alert alert-danger m-0 mt-3" role="alert">{form.error}</div>
			{/if}
		</form>
	</div>
</section>

<style>
	:global(body) {
		background: linear-gradient(120deg, rgb(208, 138, 255) 0%, rgb(87, 0, 168) 100%);
		min-height: calc(100vh - 56px);
		background-repeat: no-repeat;
		background-attachment: fixed;
	}

	.container-fluid {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
	}
</style>
