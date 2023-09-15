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
			<p>
				You have agreed to the <a
					class="hover:underline text-green-200"
					href="https://nor-discover.cloudeo.group/Service/Brockmann-EDC-xcube/SLA"
					target="_blank">GeoDB Terms and Conditions</a
				>.
			</p>
		{:else}
			<input type="checkbox" bind:checked={geodb} id="geodb" />
			<label for="geodb"
				>I agree to the <a
					class="hover:underline text-green-200"
					href="https://nor-discover.cloudeo.group/Service/Brockmann-EDC-xcube/SLA"
					target="_blank">GeoDB Terms and Conditions</a
				>.</label
			>
		{/if}
	</span>
	<span>
		{#if $user.terms?.sentinelhub}
			<p>
				You have agreed to the <a
					class="hover:underline text-green-200"
					href="https://www.sentinel-hub.com/tos/#terms"
					target="_blank">Sentinel HUB Terms and Conditions</a
				>.
			</p>
		{:else}
			<input
				type="checkbox"
				bind:checked={sentinelhub}
				id="sentinelhub"
			/>
			<label for="sentinelhub"
				>I agree to the <a
					class="hover:underline text-green-200"
					href="https://www.sentinel-hub.com/tos/#terms"
					target="_blank">Sentinel HUB Terms and Conditions</a
				>.</label
			>
		{/if}
	</span>
	<span>
		{#if $user.terms?.eoxhub}
			<p>
				You have agreed to the <a
					class="hover:underline text-green-200"
					href="https://eox.at/service-terms-and-conditions/ "
					target="_blank">EOX HUB Terms and Conditions</a
				>.
			</p>
		{:else}
			<input type="checkbox" bind:checked={eoxhub} id="eoxhub" />
			<label for="eoxhub"
				>I agree to the <a
					class="hover:underline text-green-200"
					href="https://eox.at/service-terms-and-conditions/ "
					target="_blank">EOX HUB Terms and Conditions</a
				>.</label
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
