<script>
	import { user, id_token } from "$stores/auth";
	import acceptTermsAndConditions from "$lib/auth/acceptTermsAndConditions";

	let geodb = false,
		sentinelhub = false,
		eoxhub = false;

	$: {
		if ($user.terms?.geodb) geodb = true;
		if ($user.terms?.sentinelhub) sentinelhub = true;
		if ($user.terms?.eoxhub) eoxhub = true;
	}

	$: console.log($user);

	$: disabled = !geodb || !sentinelhub || !eoxhub;

	const submit = async () => {
		disabled = true;
		try {
			$user = await acceptTermsAndConditions($id_token);
		} catch (e) {
			alert(e.message);
		}
		disabled = false;
	};
</script>

<h2 class="font-bold">Terms and Conditions:</h2>
<form
	class="flex flex-col items-left gap-1 text-sm"
	on:submit|preventDefault={submit}
>
	<span>
		{#if $user.terms?.geodb}
			<p>You have agreed to the GeoDB Terms and Condition.</p>
		{:else}
			<input type="checkbox" bind:checked={geodb} id="geodb" />
			<label for="geodb">I agree to the GeoDB Terms and Conditions.</label
			>
		{/if}
	</span>
	<span>
		{#if $user.terms?.sentinelhub}
			<p>You have agreed to the GeoDB Terms and Condition.</p>
		{:else}
			<input
				type="checkbox"
				bind:checked={sentinelhub}
				id="sentinelhub"
			/>
			<label for="sentinelhub"
				>I agree to the Sentinel HUB Terms and Conditions.</label
			>
		{/if}
	</span>
	<span>
		{#if $user.terms?.eoxhub}
			<p>You have agreed to the EOX HUB Terms and Condition.</p>
		{:else}
			<input type="checkbox" bind:checked={eoxhub} id="eoxhub" />
			<label for="eoxhub"
				>I agree to the EOX HUBTerms and Conditions.</label
			>
		{/if}
	</span>
	{#if !$user.terms?.geodb || !$user.terms?.sentinelhub || !$user.terms?.eoxhub}
		<button
			class="btn btn-outline btn-sm w-[100px]"
			type="submit"
			{disabled}>Submit</button
		>
	{/if}
</form>
