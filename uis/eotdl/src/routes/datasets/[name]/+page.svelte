<script>
	import { user, id_token } from "$stores/auth";
	import { PUBLIC_EOTDL_API } from "$env/static/public";
	import { onMount } from "svelte";
	import { browser } from "$app/environment";
	import { datasets } from "$stores/datasets";
	import { parseISO, formatDistanceToNow } from "date-fns";
	import HeartOutline from "svelte-material-icons/HeartOutline.svelte";
	import Download from "svelte-material-icons/CloudDownloadOutline.svelte";
	import "../../../styles/dataset.css";
	import Sd from "svelte-material-icons/Sd.svelte";
	import CheckDecagramOutline from "svelte-material-icons/CheckDecagramOutline.svelte";
	import formatFileSize from "../../../lib/datasets/formatFileSize.js";
	import Update from "./Update.svelte";

	export let data;

	$: ({
		name,
		id,
		createdAt,
		description,
		tags,
		author,
		link,
		license,
		size,
		checksum,
	} = data.dataset);

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
	};

	const like = () => {
		if (!$user) return;
		datasets.like(id, $id_token);
		if ($user?.liked_datasets.includes(id)) {
			$user.liked_datasets = $user?.liked_datasets.filter(
				(d) => d !== id
			);
			data.dataset.likes = data.dataset.likes - 1;
		} else {
			$user.liked_datasets = [...$user?.liked_datasets, id];
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
					<Update
						dataset_id={data.dataset.id}
						tags={data.tags}
						current_tags={tags}
						bind:author={data.dataset.author}
						bind:link={data.dataset.link}
						bind:license={data.dataset.license}
						bind:description={data.dataset.description}
						bind:selected_tags={data.dataset.tags}
						bind:size={data.dataset.size}
						bind:checksum={data.dataset.checksum}
					/>
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
						color={$user?.liked_datasets?.includes(id)
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
				<p>{formatFileSize(size)}</p>
			</span>
			<span class="flex flex-row items-center gap-1">
				<CheckDecagramOutline color="gray" size={20} />
				<p>Q{data.dataset.quality}</p>
			</span>
		</span>
		<!-- <p class="py-10">{description}</p> -->
		<div class="flex flex-row gap-3">
			<div class="content">
				{#if description}
					{@html description}
				{:else}
					<p class="italic">No description.</p>
				{/if}
			</div>
			<table class="table border-2 rounded-lg table-compact h-[100px]">
				<tbody>
					<tr>
						<th class="w-[20px]">Author</th>
						<td>{author || "-"}</td>
					</tr>
					<tr>
						<th>License</th>
						<td>{license || "-"}</td>
					</tr>
					<tr>
						<th>Source</th>
						<td>
							{#if link}
								<a
									href={link}
									target="_blank"
									rel="noopener noreferrer"
									class="text-green-200 hover:underline"
									>{link}</a
								>
							{:else}
								-
							{/if}
						</td>
					</tr>
					<tr>
						<th>Checksum (md5)</th>
						<td>{checksum || "-"}</td>
					</tr>
				</tbody>
			</table>
		</div>
	</div>
</div>
