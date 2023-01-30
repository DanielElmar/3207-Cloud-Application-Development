<script>
	import { enhance } from '$app/forms';
	import { onMount } from 'svelte';
	import 'intl-tel-input/build/css/intlTelInput.css';
	import intlTelInput from 'intl-tel-input';

	/** @type {import('./$types').ActionData} */
	export let form;

	let password = '';
	let confirmPassword = '';

	const validatePassword = (event) => {
		if (password !== confirmPassword) {
			event.target.setCustomValidity('Passwords must match');
		} else {
			event.target.setCustomValidity('');
		}
	};

	const validateNumber = (event) => {
		if (phoneInput.isValidNumber()) {
			event.target.setCustomValidity('');
			event.target.classList.remove('is-invalid');
			event.target.classList.add('is-valid');
		} else {
			event.target.setCustomValidity('Invalid phone number');
			event.target.classList.remove('is-valid');
			event.target.classList.add('is-invalid');
		}
	};

	let phoneInput;
	onMount(() => {
		const phoneInputField = document.querySelector('#phone');
		phoneInput = intlTelInput(phoneInputField, {
			utilsScript: 'https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js',
			formatOnDisplay: true,
			separateDialCode: true,
			initialCountry: 'gb'
		});
	});

	let phoneNum;

	$: if (form?.error) submitted = false; // Show submitting state
	let submitted;
</script>

<svelte:head>
	<title>Shiftable • Register</title>
	<meta name="description" content="Register page" />
</svelte:head>

<section class="container-fluid py-5 align-self-center">
	<div class="bg-light border p-3 rounded-3" style="min-width: 600px">
		<h1 class="text-center mb-2 display-4">Start now</h1>
		<p class="text-muted text-center mb-3">Register your company to start using Shiftable!</p>

		<form method="POST" on:submit={() => (submitted = true)} use:enhance>
			<div class="mb-4">
				<h2 class="display-6">Company</h2>
				<div class="form-outline mb-3">
					<label for="username" class="form-label">Name</label>
					<input
						class="form-control"
						name="company_name"
						type="text"
						placeholder="Company name..."
						required
					/>
				</div>
			</div>
			<h2 class="display-6">Main User</h2>
			<div class="row mb-3">
				<div class="form-outline col">
					<label for="first_name" class="form-label">First Name</label>
					<input
						class="form-control"
						name="first_name"
						type="text"
						placeholder="First Name"
						required
					/>
				</div>
				<div class="form-outline col">
					<label for="last_name" class="form-label">Last Name</label>
					<input
						class="form-control"
						name="last_name"
						type="text"
						placeholder="Last Name"
						required
					/>
				</div>
			</div>
			<div class="row mb-3">
				<div class="form-outline col">
					<label for="address" class="form-label">Address</label>
					<input
						class="form-control"
						name="address"
						type="text"
						placeholder="Address..."
						required
					/>
				</div>
			</div>
			<div class="row mb-3">
				<div class="form-outline col-5">
					<label for="phone_number" class="form-label">Phone Number</label>
					<input
						on:input={validateNumber}
						on:input={() => (phoneNum = phoneInput.getNumber())}
						class="form-control"
						id="phone"
						type="tel"
						required
					/>
				</div>
				<input type="hidden" name="telephone" bind:value={phoneNum} />
				<div class="form-outline col-7">
					<label for="email" class="form-label">Email</label>
					<input class="form-control" name="email" type="email" placeholder="Email" required />
				</div>
			</div>
			<div class="row mb-4">
				<div class="form-outline col">
					<label for="password" class="form-label">Password</label>
					<input
						bind:value={password}
						minlength="8"
						maxlength="64"
						class="form-control"
						name="password"
						type="password"
						placeholder="Password"
						required
					/>
				</div>
				<div class="form-outline col">
					<label for="confirm_password" class="form-label">Confirm Password</label>
					<input
						bind:value={confirmPassword}
						on:input={validatePassword}
						class="form-control"
						name="confirm_password"
						type="password"
						placeholder="Confirm password"
						required
					/>
				</div>
			</div>
			<button type="submit" class="btn btn-primary w-100" class:disabled={submitted}>
				{#if submitted}
					Signing up...
				{:else}
					Sign up
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
	.iti__flag {
		background-image: url('path/to/flags.png');
	}
	@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
		.iti__flag {
			background-image: url('path/to/flags@2x.png');
		}
	}
</style>
