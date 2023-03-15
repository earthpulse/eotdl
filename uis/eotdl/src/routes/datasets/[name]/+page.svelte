<script>
	import { user, id_token } from "$stores/auth";
	import { EOTDL_API } from "$lib/env";
	import { onMount } from "svelte";
	import { browser } from "$app/environment";
	import { datasets } from "$stores/datasets";
	import { goto } from "$app/navigation";

	export let data;

	$: ({ name, id, createdAt, uid, description, tags } = data.dataset);

	let createWriteStream;
	onMount(async () => {
		if (browser) {
			// only works in browser
			const streamsaver = await import("streamsaver");
			createWriteStream = streamsaver.createWriteStream;
		}
	});

	const download = async () => {
		// seems to work, but not sure if it will with large datasets (need to test)
		const fileName = `${name}.zip`;
		fetch(`${EOTDL_API}/datasets/${id}/download`, {
			method: "GET",
			headers: {
				Authorization: `Bearer ${$id_token}`,
			},
		}).then((res) => {
			const fileStream = createWriteStream(fileName);
			const writer = fileStream.getWriter();
			if (res.body.pipeTo) {
				writer.releaseLock();
				return res.body.pipeTo(fileStream);
			}
			const reader = res.body.getReader();
			const pump = () =>
				reader
					.read()
					.then(({ value, done }) =>
						done ? writer.close() : writer.write(value).then(pump)
					);
			return pump();
		});

		// this works but is slow with large files (no streaming)

		// const response = await fetch(`${EOTDL_API}/datasets/${id}/download`, {
		// 	method: "GET",
		// 	headers: {
		// 		Authorization: `Bearer ${$id_token}`,
		// 	},
		// });
		// const blob = await response.blob();
		// const url = URL.createObjectURL(blob);
		// const link = document.createElement("a");
		// link.href = url;
		// link.download = `${name}.zip`;
		// document.body.appendChild(link);
		// link.click();
		// document.body.removeChild(link);
	};

	let newName,
		newDescription,
		newTags,
		loading = false;
	$: {
		newTags = tags;
	}
	const edit = async () => {
		loading = true;
		try {
			await datasets.edit(
				id,
				newName,
				newDescription,
				newTags,
				$id_token
			);
			document.getElementById("edit-dataset").checked = false;
			data.dataset.tags = newTags;
			data.dataset.name = newName || name;
			data.dataset.description = newDescription || description;
			if (newName) goto(`/datasets/${newName}`, { replaceState: true });
		} catch (e) {
			alert(e.message);
		}
		loading = false;
	};

	const toggleTag = (tag) => {
		if (newTags.includes(tag)) {
			newTags = newTags.filter((t) => t !== tag);
		} else {
			newTags = [...newTags, tag];
		}
	};
</script>

<div class="w-full flex flex-col items-center">
	<div class="px-3 py-10 mt-10 w-full max-w-6xl">
		<div class="flex flex-row justify-between w-full">
			<span>
				<h1 class="text-3xl">{name}</h1>
				<div class="flex flex-wrap gap-1">
					{#each tags as tag}
						<p class="badge badge-outline">{tag}</p>
					{/each}
				</div>
			</span>
			<button
				class="btn btn-ghost btn-outline"
				disabled={!$user}
				on:click={download}>Download</button
			>
		</div>
		{#if uid == $user.sub}
			<label
				for="edit-dataset"
				class="text-gray-400 cursor-pointer hover:underline">Edit</label
			>
		{/if}
		<p class="text-gray-400">{createdAt}</p>
		<p class="py-10">{description}</p>
	</div>
</div>

<input type="checkbox" id="edit-dataset" class="modal-toggle" />
<label for="edit-dataset" class="modal cursor-pointer">
	<label class="modal-box relative" for="">
		<form on:submit|preventDefault={edit} class="flex flex-col gap-2">
			<h3 class="text-lg font-bold">Edit dataset</h3>
			<span>
				<input
					class="input input-bordered w-full"
					type="text"
					placeholder={name}
					bind:value={newName}
				/>
				<p class="text-sm text-gray-400">*Name should be unique</p>
			</span>
			<input
				class="input input-bordered w-full"
				type="text"
				placeholder={description}
				bind:value={newDescription}
			/>
			<span>
				<h3>Select relevant tags:</h3>
				<div class="flex flex-wrap gap-1">
					{#each data.tags as tag}
						<p
							class="badge badge-outline cursor-pointer {newTags.includes(
								tag
							) && 'badge-accent'}"
							on:click={() => toggleTag(tag)}
						>
							{tag}
						</p>
					{/each}
				</div>
			</span>
			<span class="self-end">
				<label
					for="edit-dataset"
					class="btn btn-ghost btn-outline btn-error">Close</label
				>
				<button
					class="btn btn-ghost btn-outline {loading && 'loading'}"
					type="submit">Update</button
				>
			</span>
		</form>
	</label>
</label>
