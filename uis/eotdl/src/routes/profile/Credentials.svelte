<script>
	import { user, id_token } from "$stores/auth";
	import Credential from "./Credential.svelte";

	export let data;
	$: ({ credentials } = data.user);

	$: console.log(data.user);

	const _credentials = [
		"GEODB_API_SERVER_PORT",
		"GEODB_API_SERVER_URL",
		"GEODB_AUTH_AUD",
		"GEODB_AUTH_CLIENT_ID",
		"GEODB_AUTH_CLIENT_SECRET",
		"GEODB_AUTH_DOMAIN",
		"SH_CLIENT_ID",
		"SH_CLIENT_SECRET",
		"SH_INSTANCE_ID",
		"SH_OWNER_ID",
	];

	const download = () => {
		const element = document.createElement("a");
		const file = new Blob([JSON.stringify(credentials)], {
			type: "text/plain;charset=utf-8",
		});
		element.href = URL.createObjectURL(file);
		element.download = "credentials.json";
		document.body.appendChild(element); // Required for this to work in FireFox
		element.click();
	};
</script>

<h2 class="font-bold">Your credentials:</h2>
{#if credentials}
	<button
		class="btn btn-outline w-[100px]"
		on:click={download}
		disabled={!credentials}>Download</button
	>

	{#each _credentials as credential}
		{#if credentials[credential]}
			<span class="flex flex-row gap-2">
				<p class="font-bold">{credential}:</p>
				<Credential value={credentials[credential]} />
			</span>
		{:else}
			<span class="flex flex-row gap-2">
				<p class="font-bold">{credential}:</p>
				<p>Not found</p>
			</span>
		{/if}
	{/each}
	<p>
		Note: If you already had a Sentinel HUB account before accepting the
		Terms and Conditions, your SH credentials will NOT appear here (you can
		retrieve them from you Sentinel HUB dashboard).
	</p>
{:else}
	<p>Accept the Terms and Conditions to generate the credentials.</p>
	<p>
		If you already accepted, your credential will appear here as soon as
		they are ready.
	</p>
{/if}
