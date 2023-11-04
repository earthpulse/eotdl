<script>
	import { user, id_token } from "$stores/auth";
	import { browser } from "$app/environment";
	import "$styles/dataset.css";
	import retrieveModel from "$lib/models/retrieveModel";
	import { models } from "$stores/models";
	import Info from "$components/Info.svelte";
	import Metadata from "$components/Metadata.svelte";
	import FileExplorer from "$components/FileExplorer.svelte";
	import { fade } from "svelte/transition";
	import retrieveModelFiles from "$lib/models/retrieveModelFiles";

	export let data;

	let model = null;
	let version = null;
	let message = null;

	const load = async () => {
		model = await retrieveModel(data.name);
	};

	$: if (browser) load();

	const copyToClipboard = (text) => {
		navigator.clipboard.writeText(text);
		console.log("copied to clipboard");
		message = "Copied!";
		setTimeout(() => {
			message = null;
		}, 1000);
	};
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

			<Info
				data={model}
				store={models}
				field="liked_models"
				bind:version
			/>

			<div class="grid grid-cols-[auto,425px] gap-3">
				<div>
					<div class="content">
						{#if model.description}
							{@html model.description}
						{:else}
							<p class="italic">No description.</p>
						{/if}
					</div>
					<!-- {#if dataset.quality > 0}
						<pre
							class="text-xs bg-slate-100 p-3 mt-3">{JSON.stringify(
								dataset.catalog,
								null,
								4
							)}</pre>
					{/if} -->
				</div>
				<div class="flex flex-col gap-3">
					<p>Download the model with the CLI:</p>
					<div class="relative">
						<pre class="bg-gray-200 p-3"><button
								on:click={() =>
									copyToClipboard(
										`eotdl datasets get ${model.name}`
									)}>eotdl models get {model.name}</button
							></pre>
						{#if message}
							<span
								class="text-sm text-gray-400 absolute bottom-[-20px] right-0"
								in:fade
								out:fade>{message}</span
							>
						{/if}
					</div>
					{#if model.quality == 0}
						<div class="flex flex-col gap-3">
							<Metadata data={model} />
							<FileExplorer
								data={model}
								{version}
								retrieveFiles={retrieveModelFiles}
							/>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}
