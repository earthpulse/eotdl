<script>
	import retrieveFiles from "$lib/files/retrieveFiles";

	let { version, collection } = $props();

	let loading = $state(true);
	let files = $state([]);

	const load = async () => {
		loading = true;
		files = await retrieveFiles(collection, version.version_id);
		loading = false;
	};

	$effect(() => {
		if (collection && version) {
			load();
		}
	});

	let details = $state(null);

	const showDetails = (file) => {
		// details = file.assets.asset;
	};
</script>

{#if !loading}
	<h2>Files ({files.length}) :</h2>
	<div class="flex flex-col gap-1 items-start border-1 border-gray-200 p-3">
		{#if details}
			<div class="flex flex-col gap-1 items-start">
				<button onclick={() => (details = null)}>Back</button>
				<p>{details.checksum}</p>
				<p>{details.href}</p>
			</div>
		{:else}
			<div
				class="max-h-[200px] overflow-y-auto flex flex-col gap-1 items-start"
			>
				{#each files as file}
					<button
						onclick={() => showDetails(file)}
						class="hover:underline cursor-pointer">{file.id}</button
					>
				{/each}
			</div>
		{/if}
	</div>
{/if}
