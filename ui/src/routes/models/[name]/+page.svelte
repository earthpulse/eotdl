<script>
	import { user, id_token } from "$stores/auth";
	import { browser } from "$app/environment";
	import "$styles/dataset.css";
	import retrieveModel from "$lib/models/retrieveModel";
	import { models } from "$stores/models";
	// import Info from "./Info.svelte";
	import Metadata from "$components/Metadata.svelte";
	// import FileExplorer from "./FileExplorer.svelte";

	export let data;

	let model = null;
	let version = null;

	const load = async () => {
		model = await retrieveModel(data.name);
		console.log(model);
	};

	$: if (browser) load();
</script>

<svelte:head>
	<title>EOTDL | {data.name}</title>
	<meta name="description" content={model?.description} />
</svelte:head>

{#if model}
	<div class="w-full flex flex-col items-center">
		<div class="px-3 py-10 mt-10 w-full max-w-6xl flex flex-col gap-2">
			<div class="flex flex-col sm:flex-row justify-between w-full gap-3">
				<span class="flex flex-col gap-2">
					<h1 class="text-3xl">{model.name}</h1>
					<div class="flex flex-wrap gap-1">
						{#each model.tags as tag}
							<p
								class="badge badge-outline border-slate-300 text-slate-400 text-xs"
							>
								{tag}
							</p>
						{/each}
					</div>
				</span>
			</div>

			<!-- <Info {dataset} bind:version /> -->

			<div class="grid grid-cols-[auto,425px] gap-3">
				<div>
					<div class="content">
						{#if model.description}
							{@html model.description}
						{:else}
							<p class="italic">No description.</p>
						{/if}
					</div>
				</div>
				{#if model.quality == 0}
					<div class="flex flex-col gap-3">
						<Metadata data={model} />
						<!-- <FileExplorer {model} {version} /> -->
					</div>
				{:else}
					<div>
						<p>Download the model with the CLI</p>
						<p>eotdl models get {name}</p>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}
