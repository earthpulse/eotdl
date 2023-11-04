<script>
	import { user, id_token } from "$stores/auth";
	import { browser } from "$app/environment";
	import { datasets } from "$stores/datasets";
	import "$styles/dataset.css";
	import Update from "./Update.svelte";
	import retrieveDataset from "$lib/datasets/retrieveDataset";
	import Info from "$components/Info.svelte";
	import Metadata from "$components/Metadata.svelte";
	import FileExplorer from "$components/FileExplorer.svelte";
	import { fade } from "svelte/transition";
	import retrieveDatasetFiles from "$lib/datasets/retrieveDatasetFiles";

	export let data;

	let dataset = null;
	let version = null;
	let message = null;

	const load = async () => {
		dataset = await retrieveDataset(data.name);
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
	<meta name="description" content={dataset?.description} />
</svelte:head>

{#if dataset}
	<div class="w-full flex flex-col items-center">
		<div class="px-3 py-10 mt-10 w-full max-w-6xl flex flex-col gap-2">
			<div class="flex flex-col sm:flex-row justify-between w-full gap-3">
				<span class="flex flex-col gap-2">
					<h1 class="text-3xl">{dataset.name}</h1>
					<div class="flex flex-wrap gap-1">
						{#each dataset.tags as tag}
							<p
								class="badge badge-outline border-slate-300 text-slate-400 text-xs"
							>
								{tag}
							</p>
						{/each}
					</div>
				</span>
				<!-- {#if $user}
				<span class="flex flex-row gap-2">
					<a
						class="btn btn-outline"
						href={`https://notebooks.api.eotdl.com/?search=${data.dataset.name}`}
						target="_blank">Open</a
					>
					{#if $user.uid == data.dataset.uid}
						<Update
							dataset_id={data.dataset.id}
							tags={data.tags}
							current_tags={tags}
							{name}
							{quality}
							bind:authors={data.dataset.authors}
							bind:source={data.dataset.source}
							bind:license={data.dataset.license}
							bind:description={data.dataset.description}
							bind:selected_tags={data.dataset.tags}
							bind:size={data.dataset.size}
							bind:files={data.dataset.files}
						/>
					{/if}
				</span>
			{/if} -->
			</div>

			<Info
				data={dataset}
				store={datasets}
				field="liked_datasets"
				bind:version
			/>

			<div class="grid grid-cols-[auto,425px] gap-3">
				<div>
					<div class="content">
						{#if dataset.description}
							{@html dataset.description}
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
					<p>Download the dataset with the CLI:</p>
					<div class="relative">
						<pre class="bg-gray-200 p-3"><button
								on:click={() =>
									copyToClipboard(
										`eotdl datasets get ${dataset.name}`
									)}>eotdl datasets get {dataset.name}</button
							></pre>
						{#if message}
							<span
								class="text-sm text-gray-400 absolute bottom-[-20px] right-0"
								in:fade
								out:fade>{message}</span
							>
						{/if}
					</div>
					{#if dataset.quality == 0}
						<div class="flex flex-col gap-3">
							<Metadata data={dataset} />
							<FileExplorer
								data={dataset}
								{version}
								retrieveFiles={retrieveDatasetFiles}
							/>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}
