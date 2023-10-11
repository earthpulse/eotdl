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
		quality,
		catalog,
		versions,
	} = data.dataset);

	// $: current_version = versions[versions.length - 1].version_id || 0;
	$: current_version = versions[versions.length - 1];

	let createWriteStream;
	let all_files = null;
	let files = null;
	let folders = null;
	let back = null;
	const load = async () => {
		await datasets.retrieve(fetch);
		all_files = await datasets.retrieveFiles(
			id,
			current_version.version_id
		);
		all_files = all_files.sort((f) => f.filename);
		folders = all_files
			.filter((f) => f.filename.includes("/"))
			.map((f) => f.filename.split("/")[0]);
		folders = [...new Set(folders)];
		files = all_files.filter((f) => !f.filename.includes("/"));
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

	const filter_by_folder = (folder) => {
		back = "root";
		if (folder == "root") {
			files = all_files.filter((f) => !f.filename.includes("/"));
			folders = all_files
				.filter((f) => f.filename.includes("/"))
				.map((f) => f.filename.split("/")[0]);
			back = null;
		} else {
			files = all_files.filter((f) => f.filename.includes(folder));
			folders = files
				.filter((f) => f.filename.includes("/"))
				.map((f) => f.filename.split("/")[0]);
		}

		folders = [...new Set(folders)];
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
			<!-- <span class="flex flex-row items-center gap-1">
				<Download color="gray" size={20} />
				<p>{data.dataset.downloads}</p>
			</span> -->
			<span class="flex flex-row items-center gap-1">
				<Sd color="gray" size={20} />
				<p>{formatFileSize(current_version.size)}</p>
			</span>
			<span class="flex flex-row items-center gap-1">
				<CheckDecagramOutline color="gray" size={20} />
				<p>Q{data.dataset.quality}</p>
			</span>
		</span>
		<span class="flex flex-row gap-3">
			<p>Version:</p>
			<select
				class="border w-10 select-accent"
				on:change={(e) => {
					const version_id = e.target.value;
					current_version = versions.find(
						(v) => v.version_id == version_id
					);
				}}
			>
				{#each versions as version}
					<option
						value={version.version_id}
						selected={current_version.version_id ==
							version.version_id}
					>
						{version.version_id}
					</option>
				{/each}
			</select>
			<p class="text-gray-400">
				Created {formatDistanceToNow(
					parseISO(current_version.createdAt)
				)} ago
			</p>
		</span>

		<!-- <p class="py-10">{description}</p> -->
		<div class="grid grid-cols-[auto,425px] gap-3">
			<div>
				<div class="content">
					{#if description}
						{@html description}
					{:else}
						<p class="italic">No description.</p>
					{/if}
				</div>
				{#if quality > 0}
					<pre class="text-xs bg-slate-100 p-3 mt-3">{JSON.stringify(
							catalog,
							null,
							4
						)}</pre>
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
					{#if files}
						<p>Files:</p>
						<div
							class="overflow-auto w-full max-h-[200px] border-2"
						>
							{#if back}
								<button
									class="hover:underline px-3"
									on:click={() => filter_by_folder(back)}
								>
									...
								</button>
							{/if}
							{#each files as file}
								<p class="flex flex-row gap-1 px-3">
									<!-- {#if $user}
												<button
													on:click={() =>
														download(file.name)}
													><Download
														color="gray"
														size={20}
													/></button
												>
											{/if} -->
									{file.filename}
								</p>
								<!-- <td>{formatFileSize(file.size)}</td>
										<td class="text-xs">{file.checksum}</td> -->
							{/each}
							{#each folders as folder}
								<button
									class="flex flex-row gap-1 cursor-pointer hover:underline px-3"
									on:click={() => filter_by_folder(folder)}
								>
									{folder}
								</button>
							{/each}
						</div>
					{:else}
						<p>Loading files ...</p>
					{/if}
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
