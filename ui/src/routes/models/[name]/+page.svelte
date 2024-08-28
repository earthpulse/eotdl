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
	import Update from "$components/Update.svelte";

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
								class="badge border-0 text-slate-200 text-xs"
								style="background-color: {data.tags?.find(
									(t) => t.name == tag,
								).color || 'none'};"
							>
								{tag}
							</p>
						{/each}
					</div>
				</span>

				{#if $user}
					<span class="flex flex-row gap-2">
						<!-- <a
					class="btn btn-outline"
					href={`https://notebooks.api.eotdl.com/?search=${dataset.name}`}
					target="_blank">Open</a
				> -->
						{#if $user.uid == model.uid}
							<Update
								store={models}
								route="models"
								id={model.id}
								tags={data.tags}
								current_tags={model.tags}
								bind:name={model.name}
								quality={model.quality}
								bind:authors={model.authors}
								bind:source={model.source}
								bind:license={model.license}
								bind:description={model.description}
								bind:selected_tags={model.tags}
							/>
						{/if}
					</span>
				{/if}
			</div>

			<Info
				data={model}
				store={models}
				field="liked_models"
				bind:version
			/>

			<div class="grid grid-cols-[auto,350px] gap-3 mt-5">
				<div class="w-full overflow-auto">
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
				<div class="flex flex-col gap-3 text-xs">
					<p>Download the model with the CLI:</p>
					<div class="relative">
						<pre class="bg-gray-200 p-3 overflow-x-auto"><button
								on:click={() =>
									copyToClipboard(
										`eotdl models get ${model.name} -v ${version?.version_id}`,
									)}
								>eotdl models get {model.name} -v {version?.version_id}</button
							></pre>
						{#if message}
							<span
								class=" text-gray-400 absolute bottom-[-20px] right-0"
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
