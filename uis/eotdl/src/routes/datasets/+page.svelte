<script>
	import { datasets } from "$stores/datasets";
	import { user, id_token } from "$stores/auth";

	export let data;

	let loading = false;
	let name = "",
		description = "",
		files = null;
	const ingest = async () => {
		if (name.length === 0 || description.length === 0 || files === null)
			return;
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

	$: filtered_datasets = $datasets?.data
		.filter((dataset) => {
			if (selected_tags.length === 0) return true;
			return selected_tags.every((tag) => dataset.tags.includes(tag));
		})
		.filter((dataset) => {
			if (filterName.length === 0) return true;
			return dataset.name
				.toLowerCase()
				.includes(filterName.toLowerCase());
		});
</script>

<div class="w-full flex flex-col items-center">
	<div class="px-3 py-5 mt-10 w-full max-w-6xl">
		<div class="grid grid-cols-[200px,auto] gap-3">
			<div class="flex flex-col">
				<div class="flex flew-row justify-between">
					<h1>Datasets</h1>
					<p>{filtered_datasets.length}</p>
				</div>
				<input
					class="input input-bordered w-full max-w-xs"
					type="text"
					placeholder="Filter by name"
					bind:value={filterName}
				/>
				<p class="text-gray-400 hover:underline cursor-pointer">
					advanced filtering
				</p>
				{#if $user}
					<label
						for="ingest-dataset"
						class="btn btn-ghost btn-outline mt-4"
						>+ Ingest Dataset</label
					>
				{/if}
			</div>
			<div class="flex flex-wrap gap-1 content-start">
				{#each data.tags as tag}
					<p
						class="badge badge-outline cursor-pointer {selected_tags.includes(
							tag
						) && 'badge-accent'}"
						on:click={() => toggleTag(tag)}
					>
						{tag}
					</p>
				{/each}
			</div>
		</div>
		<div class="grid grid-cols-3 gap-3 w-full mt-3">
			{#each filtered_datasets as dataset}
				<a
					href="/datasets/{dataset.name}"
					class="w-full bg-gray-100 border-2 rounded-xl p-3 flex flex-col justify-between"
				>
					<span
						><p>{dataset.name}</p>
						<p class="text-gray-400">{dataset.description}</p></span
					>
					<span>
						<div class="flex flex-wrap gap-1 content-start">
							{#each dataset.tags as tag}
								<p class="badge badge-outline">{tag}</p>
							{/each}
						</div>
						<p class="text-gray-400">{dataset.createdAt}</p>
					</span>
				</a>
			{/each}
		</div>
	</div>
</div>

<input type="checkbox" id="ingest-dataset" class="modal-toggle" />
<label for="ingest-dataset" class="modal cursor-pointer">
	<label class="modal-box relative" for="">
		<form on:submit|preventDefault={ingest} class="flex flex-col gap-2">
			<h3 class="text-lg font-bold">Ingest dataset</h3>
			<input type="file" accept=".zip" required bind:files />
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
			<span class="self-end">
				<label
					for="ingest-dataset"
					class="btn btn-ghost btn-outline btn-error">Close</label
				>
				<button
					class="btn btn-ghost btn-outline {loading && 'loading'}"
					type="submit">Ingest</button
				>
			</span>
		</form>
	</label>
</label>
