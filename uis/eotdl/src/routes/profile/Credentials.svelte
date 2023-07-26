<script>
	import { user, id_token } from "$stores/auth";
	import Credential from "./Credential.svelte";

	const credentials = [
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
</script>

<h2 class="font-bold">Your credentials:</h2>
<p class="text-red-400">*placeholder data</p>
<button class="btn btn-outline w-[100px]">Download</button>
{#each credentials as credential}
	<span class="flex flex-row gap-2">
		<p>{credential}:</p>
		<Credential />
	</span>
{/each}
