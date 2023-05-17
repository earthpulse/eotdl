<script>
	import { user, id_token } from "$stores/auth";
	import { PUBLIC_EOTDL_API } from "$env/static/public";
	import { onMount } from "svelte";
	import { browser } from "$app/environment";
	import { datasets } from "$stores/datasets";
	import { goto } from "$app/navigation";
	import { parseISO, formatDistanceToNow } from "date-fns";
	import HeartOutline from "svelte-material-icons/HeartOutline.svelte";
	import Download from "svelte-material-icons/CloudDownloadOutline.svelte";
	import "../../../styles/dataset.css";
	import TextEditor from "../TextEditor.svelte";
	import Sd from "svelte-material-icons/Sd.svelte";
	import CheckDecagramOutline from "svelte-material-icons/CheckDecagramOutline.svelte";
	import formatFileSize from "../../../lib/datasets/formatFileSize.js";
	import Update from "./Update.svelte";

	export let data;

	$: ({ name, id, createdAt, uid, description, tags } = data.dataset);

	$: content = description || "";

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
		fetch(`${PUBLIC_EOTDL_API}/datasets/${id}/download`, {
			method: "GET",
			headers: {
				Authorization: `Bearer ${$id_token}`,
			},
		})
			.then((res) => {
				if (!res.ok) return res.json();
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
							done
								? writer.close()
								: writer.write(value).then(pump)
						);
				data.dataset.downloads = data.dataset.downloads + 1;
				return pump();
			})
			.then((res) => {
				alert(res.detail);
			});

		// this works but is slow with large files (no streaming)

		// const response = await fetch(`${PUBLIC_EOTDL_API}/datasets/${id}/download`, {
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
		newTags,
		loading = false;
	$: {
		newTags = tags;
	}
	const edit = async () => {
		loading = true;
		try {
			await datasets.edit(id, newName, content, newTags, $id_token);
			document.getElementById("edit-dataset").checked = false;
			data.dataset.tags = newTags;
			data.dataset.name = newName || name;
			data.dataset.description = content || description;
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

	const like = () => {
		if (!$user) return;
		datasets.like(id, $id_token);
		if ($user.liked_datasets.includes(id)) {
			$user.liked_datasets = $user.liked_datasets.filter((d) => d !== id);
			data.dataset.likes = data.dataset.likes - 1;
		} else {
			$user.liked_datasets = [...$user.liked_datasets, id];
			data.dataset.likes = data.dataset.likes + 1;
		}
	};
</script>

<svelte:head>
	<title>EOTDL | {data.name}</title>
	<meta name="description" content={description} />
</svelte:head>

<div class="w-full flex flex-col items-center">
	<div class="px-3 py-10 mt-10 w-full max-w-6xl flex flex-col gap-2">
		<div class="flex flex-col sm:flex-row justify-between w-full gap-3">
			<span class="flex flex-col gap-2">
				<h1 class="text-3xl">{name}</h1>
				<div class="flex flex-wrap gap-1">
					{#each tags as tag}
						<p
							class="badge badge-outline border-slate-300 text-slate-400 text-xs"
						>
							{tag}
						</p>
					{/each}
				</div>
			</span>
			{#if $user}
				<span class="flex flex-row gap-3">
					<button
						class="btn btn-ghost btn-outline"
						on:click={download}>Download</button
					>
					<Update dataset_id={data.dataset.id} />
				</span>
			{:else}
				<p class="badge badge-warning p-3">Sign in to download</p>
			{/if}
		</div>

		<p class="text-gray-400">
			Created {formatDistanceToNow(parseISO(createdAt))} ago
		</p>
		<span class="text-gray-400 flex flex-row gap-3 items-center">
			<span class="flex flex-row gap-1">
				<button on:click={like}
					><HeartOutline
						color={$user.liked_datasets?.includes(id)
							? "red"
							: "gray"}
					/></button
				>
				<p>{data.dataset.likes}</p>
			</span>
			<span class="flex flex-row items-center gap-1">
				<Download color="gray" size={20} />
				<p>{data.dataset.downloads}</p>
			</span>
			<span class="flex flex-row items-center gap-1">
				<Sd color="gray" size={20} />
				<p>{formatFileSize(data.dataset.size)}</p>
			</span>
			<span class="flex flex-row items-center gap-1">
				<CheckDecagramOutline color="gray" size={20} />
				<p>Q{data.dataset.quality}</p>
			</span>
		</span>
		{#if uid == $user?.uid}
			<label
				for="edit-dataset"
				class="text-gray-400 cursor-pointer hover:underline">Edit</label
			>
		{/if}
		<!-- <p class="py-10">{description}</p> -->
		<div class="content">
			{@html description}
		</div>
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
			<TextEditor bind:content />
			<span>
				<h3>Select relevant tags:</h3>
				<div class="flex flex-wrap gap-1">
					{#each data.tags as tag}
						<p
							class="badge badge-outline cursor-pointer text-slate-400 text-xs {newTags.includes(
								tag
							) && 'badge-accent'}"
							on:click={() => toggleTag(tag)}
							on:keyup={() => {}}
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

<style>
</style>
