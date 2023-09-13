<script>
	import { user, id_token } from "$stores/auth";
	import { PUBLIC_EOTDL_API } from "$env/static/public";
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
		authors,
		source,
		license,
		size,
		files,
		quality,
	} = data.dataset);

	let createWriteStream;
	const load = async () => {
		await datasets.retrieve(fetch);
		// only works in browser
		const streamsaver = await import("streamsaver");
		createWriteStream = streamsaver.createWriteStream;
	};

	$: if (browser) load();

	const download = async (fileName) => {
		// seems to work, but not sure if it will with large datasets (need to test)
		fetch(`${PUBLIC_EOTDL_API}/datasets/${id}/download/${fileName}`, {
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
				<span class="flex flex-row gap-1">
					{#if $user.uid == data.dataset.uid}
						<Update
							dataset_id={data.dataset.id}
							tags={data.tags}
							current_tags={tags}
							{name}
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
		<div class="grid grid-cols-[auto,425px] gap-3">
			<div class="content">
				{#if description}
					{@html description}
				{:else}
					<p class="italic">No description.</p>
				{/if}
			</div>
			{#if quality == 0}
				<div class="flex flex-col gap-3">
					<div class="overflow-auto w-full">
						<table
							class="table border-2 rounded-lg table-compact h-[100px] w-full"
						>
							<tbody>
								<tr>
									<th class="w-[20px]">Author(s)</th>
									<td>{authors.join(", ") || "-"}</td>
								</tr>
								<tr>
									<th>License</th>
									<td>{license || "-"}</td>
								</tr>
								<tr>
									<th>Source</th>
									<td>
										{#if source}
											<a
												href={source}
												target="_blank"
												rel="noopener noreferrer"
												class="text-green-200 hover:underline"
												>{source.length > 30
													? source.slice(0, 30) +
													  "..."
													: source}</a
											>
										{:else}
											-
										{/if}
									</td>
								</tr>
							</tbody>
						</table>
					</div>
					<p>Files ({files.length}):</p>
					<div class="overflow-auto w-full">
						<table
							class="table border-2 rounded-lg table-compact h-[100px] w-full"
						>
							<tbody>
								<tr>
									<th> Name </th>
									<th>Size</th>
									<th>Checksum (SHA1)</th>
								</tr>
								{#each files as file}
									<tr>
										<td class="flex flex-row gap-1">
											{#if $user}
												<button
													on:click={() =>
														download(file.name)}
													><Download
														color="gray"
														size={20}
													/></button
												>
											{/if}
											{file.name}
										</td>
										<td>{formatFileSize(file.size)}</td>
										<td class="text-xs">{file.checksum}</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</div>
			{:else}
				<div>
					<p>Download the dataset with the CLI</p>
					<p>eotdl datasets get {name}</p>
				</div>
			{/if}
		</div>
	</div>
</div>
