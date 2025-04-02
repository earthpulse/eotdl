<script>
	import auth from "$stores/auth.svelte";
	import acceptTermsAndConditions from "$lib/auth/acceptTermsAndConditions";

	let geodb = $state(false);
	let sentinelhub = $state(false);
	let eoxhub = $state(false);

	$effect(() => {
		if (auth.user?.terms?.geodb) geodb = true;
		if (auth.user?.terms?.sentinelhub) sentinelhub = true;
		if (auth.user?.terms?.eoxhub) eoxhub = true;
	});

	let disabled = $derived(!geodb || !sentinelhub || !eoxhub);

	const submit = async (e) => {
		e.preventDefault();
		disabled = true;
		try {
			auth.user = await acceptTermsAndConditions(auth.id_token);
		} catch (e) {
			alert(e.message);
		}
		disabled = false;
	};
</script>

<h2 class="font-bold">Terms and Conditions:</h2>
<form class="flex flex-col items-left gap-1 text-sm" onsubmit={submit}>
	<span>
		{#if auth.user?.terms?.geodb}
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
		{#if auth.user?.terms?.sentinelhub}
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
		{#if auth.user?.terms?.eoxhub}
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
	{#if !auth.user?.terms?.geodb || !auth.user?.terms?.sentinelhub || !auth.user?.terms?.eoxhub}
		<button
			class="btn btn-outline btn-sm w-[100px]"
			type="submit"
			{disabled}>Submit</button
		>
	{/if}
</form>
