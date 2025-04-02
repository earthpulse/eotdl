<script>
	import retrieveFiles from "$lib/files/retrieveFiles";

	export let version;
	export let collection;

	let loading = true;
	let files = [];

	const load = async () => {
		loading = true;
		files = await retrieveFiles(collection, version.version_id);
		loading = false;
	};

	$: if (collection && version) {
		load();
	}

	let details = null;

	const showDetails = (file) => {
		details = file.assets.asset;
	};
</script>

{#if !loading}
	<h2>Files ({files.length}) :</h2>
	{#if details}
		<div class="flex flex-col gap-1 items-start">
			<button on:click={() => (details = null)}>Back</button>
			<p>{details.checksum}</p>
			<p>{details.href}</p>
		</div>
	{:else}
		<div
			class="max-h-[200px] overflow-y-auto flex flex-col gap-1 items-start"
		>
			{#each files as file}
				<button on:click={() => showDetails(file)}>{file.id}</button>
			{/each}
		</div>
	{/if}
{/if}
