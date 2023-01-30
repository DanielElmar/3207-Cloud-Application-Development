<script>
	import { page } from '$app/stores';

	export let items = [];
	export let admin = [];

	$: path = $page.url.pathname;

	// logout
	const logout = async () => {
		const res = await fetch('/logout', {
			method: 'POST'
		});

		window.location.href = res.url;
	};
</script>

<nav
	class="navbar navbar-expand-md bg-light shadow sticky-top"
	data-sveltekit-reload
	data-sveltekit-preload-data="hover"
>
	<div class="container-fluid">
		<a class="navbar-brand mb-0" href="/">Shiftable</a>
		<button
			class="navbar-toggler"
			type="button"
			data-bs-toggle="collapse"
			data-bs-target="#navbarNav"
			aria-controls="navbarNav"
			aria-expanded="false"
			aria-label="Toggle navigation"
		>
			<span class="navbar-toggler-icon" />
		</button>
		<div class="collapse navbar-collapse" id="navbarNav">
			{#if $page.data.user}
				<ul class="navbar-nav me-auto">
					{#each items as { href, text }}
						<li class="nav-item">
							<a class="nav-link" {href} class:active={path === href}>{text}</a>
						</li>
					{/each}

					{#if admin}
						<div class="d-flex">
							{#each admin as { href, text }}
								<li class="nat-item border-bottom border-danger">
									<a class="nav-link" class:active={path === href} {href}>{text}</a>
								</li>
							{/each}
						</div>
					{/if}
				</ul>

				<ul class="navbar-nav">
					<li class="nav-item dropdown ms-auto">
						<span
							class="nav-link dropdown-toggle"
							role="button"
							data-bs-toggle="dropdown"
							aria-expanded="false"
						>
							User
						</span>
						<ul class="dropdown-menu dropdown-menu-end" style="font-size: 14px">
							<li><p class="dropdown-header">{$page.data.user.company_name}</p></li>
							<li><hr class="dropdown-divider" /></li>
							<li>
								<a role="menuitem" class="dropdown-item" href="#"
									>Signed in as
									<br /><strong>{$page.data.user.first_name} {$page.data.user.last_name}</strong></a
								>
							</li>
							<li><hr class="dropdown-divider" /></li>
							<li>
								<button
									class="dropdown-item text-danger fw-bold"
									style="cursor: pointer;"
									on:click={logout}>Sign out</button
								>
							</li>
						</ul>
					</li>
				</ul>
			{:else if path !== '/login'}
				<a class="btn shadow text-white ms-auto px-4 py-1 fw-bold rounded-pill" href="/login"
					>Login</a
				>
			{/if}
		</div>
	</div>
</nav>

<style>
	a.active {
		font-weight: bold;
	}
	[href='/login'] {
		background-color: rgb(212, 0, 255);
		letter-spacing: 0.5px;
		text-shadow: #fff 1px 0 12px;
	}
	[href='/login']:hover {
		opacity: 0.8;
	}
</style>
