<script>
	import { datasets } from "$stores/datasets";
	import { user, id_token } from "$stores/auth";
	import Leaderboard from "./Leaderboard.svelte";
	import Card from "./Card.svelte";
	import HeartOutline from "svelte-material-icons/HeartOutline.svelte";
	import Code from "../docs/components/Code.svelte";
	import CLI from "../docs/components/CLI.svelte";

	export let data;

	let loading = false;
	let name = "",
		description = "",
		files = null;
	const ingest = async () => {
		if (name.length === 0 || description.length === 0 || files === null)
			return;
		if (!validate_file(files[0])) return;
		loading = true;
		try {
			await datasets.ingest(files[0], name, description, $id_token);
			document.getElementById("ingest-dataset").checked = false;
			name = "";
		} catch (e) {
			alert(e.message);
		}
		loading = false;
	};

	let selected_tags = [];
	const toggleTag = (tag) => {
		if (selected_tags.includes(tag)) {
			selected_tags = selected_tags.filter((t) => t !== tag);
		} else {
			selected_tags = [...selected_tags, tag];
		}
	};

	let filterName = "";
	let show_liked = false;
	let filtered_datasets;
	$: {
		filtered_datasets = $datasets.data
			?.filter((dataset) => {
				if (selected_tags.length === 0) return true;
				return selected_tags.every((tag) => dataset.tags.includes(tag));
			})
			.filter((dataset) => {
				if (filterName.length === 0) return true;
				return dataset.name
					.toLowerCase()
					.includes(filterName.toLowerCase());
			});
		if (show_liked) {
			filtered_datasets = filtered_datasets.filter((dataset) =>
				data.liked_datasets.includes(dataset.id)
			);
		}
	}

	const maxVisibleDatasets = 9;
	let currentPage = 0;
	$: numPages = Math.ceil(filtered_datasets?.length / maxVisibleDatasets);
	$: if (numPages > 0) currentPage = 0;
	$: visible_datasets = filtered_datasets?.slice(
		currentPage * maxVisibleDatasets,
		(currentPage + 1) * maxVisibleDatasets
	);

	const toggleLike = () => {
		if ($user) show_liked = !show_liked;
	};

	let valid_file = true;
	const validate_file = (file) => {
		// 100 MB limit
		if (file.size > 100000000) valid_file = false;
		else valid_file = true;
		return valid_file;
	};
</script>

<div class="w-full flex flex-col items-center">
	<div
		class="px-3 py-10 mt-10 w-full max-w-6xl flex flex-col items-center h-full"
	>
		<div class="grid grid-cols-1 sm:grid-cols-[250px,auto] gap-8 w-full">
			<div class="flex flex-col w-full">
				<div class="flex flew-row justify-between text-3xl">
					<h1 class="font-bold">Datasets</h1>
					<p class="text-gray-400">{filtered_datasets?.length}</p>
				</div>
				<input
					class="input input-bordered max-w-full input-xs"
					type="text"
					placeholder="Filter by name"
					bind:value={filterName}
				/>
				<span class="flex flew-row justify-between mt-1">
					<p
						class="text-gray-400 hover:underline cursor-pointer text-sm"
					>
						advanced filtering
					</p>
					<button on:click={toggleLike}
						><HeartOutline
							color={show_liked ? "red" : "gray"}
						/></button
					>
				</span>
				{#if $user}
					<label
						for="ingest-dataset"
						class="btn btn-ghost btn-outline mt-4"
						>+ Ingest Dataset</label
					>
				{/if}
			</div>
			<div class="flex flex-wrap gap-1 content-start">
				{#each data?.tags as tag}
					<button
						class="badge badge-outline bg-white text-slate-400 text-xs {selected_tags.includes(
							tag
						) && 'badge-accent'}"
						on:click={() => toggleTag(tag)}
					>
						{tag}
					</button>
				{/each}
			</div>
		</div>
		{#if visible_datasets?.length > 0}
			<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full mt-3">
				{#each visible_datasets as dataset}
					<Card
						{dataset}
						liked={data.liked_datasets.includes(dataset.id)}
					/>
				{/each}
			</div>
		{:else}
			<p class="text-gray-400 text-center">No datasets found</p>
		{/if}
		<div>
			{#if numPages > 1}
				<div
					class="grid grid-cols-3 w-[250px] btn-xs mt-3 items-center"
				>
					<button
						class="btn btn-ghost btn-xs disabled:bg-white"
						disabled={currentPage === 0}
						on:click={() =>
							(currentPage = Math.max(0, currentPage - 1))}
						>Previous</button
					>
					<p class="w-full text-center">
						{currentPage + 1} / {numPages}
					</p>
					<button
						class="btn btn-ghost btn-xs disabled:bg-white"
						disabled={currentPage === numPages - 1}
						on:click={() =>
							(currentPage = Math.min(currentPage + 1, numPages))}
						>Next</button
					>
				</div>
			{/if}
		</div>
	</div>
	<Leaderboard leaderboard={data.leaderboard} />
</div>

<input type="checkbox" id="ingest-dataset" class="modal-toggle" />
<label for="ingest-dataset" class="modal cursor-pointer">
	<label class="modal-box relative" for="">
		<form on:submit|preventDefault={ingest} class="flex flex-col gap-2">
			<h3 class="text-lg font-bold">Ingest dataset</h3>
			<input
				type="file"
				accept=".zip"
				required
				bind:files
				on:change={(e) => validate_file(e.target.files[0])}
			/>
			<span>
				<input
					class="input input-bordered w-full"
					type="text"
					placeholder="Dataset name"
					required
					bind:value={name}
				/>
				<p class="text-sm text-gray-400">*Name should be unique</p>
			</span>
			<input
				class="input input-bordered w-full"
				type="text"
				placeholder="Dataset description"
				required
				bind:value={description}
			/>
			{#if !valid_file}
				<CLI>
					You are trying to upload a big dataset. Please, use the CLI
					instead:
					<Code>eotdl-cli datasets ingest {`<dataset-path>`}</Code>
					Instruction to install the CLI
					<a
						class="text-green-200 hover:underline"
						href="/docs/getting-started/install">here</a
					>
				</CLI>
			{/if}
			<span class="self-end">
				<label
					for="ingest-dataset"
					class="btn btn-ghost btn-outline btn-error">Close</label
				>
				<button
					class="btn btn-ghost btn-outline {loading && 'loading'}"
					disabled={!valid_file}
					type="submit">Ingest</button
				>
			</span>
		</form>
	</label>
</label>
