<script>
	import { browser } from "$app/environment";

	export let dataset;

	let createWriteStream;
	let all_files = null;
	let files = null;
	let folders = null;
	let back = null;

	const load = async () => {
		// only works in browser
		// const streamsaver = await import("streamsaver");
		// createWriteStream = streamsaver.createWriteStream;
	};

	$: if (browser) load();

	// const retrieve_files = async () => {
	// 	files = null;
	// 	folders = null;
	// 	all_files = await datasets.retrieveFiles(
	// 		id,
	// 		current_version.version_id
	// 	);
	// 	all_files = all_files.sort((f) => f.filename);
	// 	folders = all_files
	// 		.filter((f) => f.filename.includes("/"))
	// 		.map((f) => f.filename.split("/")[0]);
	// 	folders = [...new Set(folders)];
	// 	files = all_files.filter((f) => !f.filename.includes("/"));
	// };

	// const download = async (fileName) => {
	// 	// seems to work, but not sure if it will with large datasets (need to test)
	// 	fetch(`${PUBLIC_EOTDL_API}/datasets/${id}/download/${fileName}`, {
	// 		method: "GET",
	// 		headers: {
	// 			Authorization: `Bearer ${$id_token}`,
	// 		},
	// 	})
	// 		.then((res) => {
	// 			if (!res.ok) return res.json();
	// 			const fileStream = createWriteStream(fileName);
	// 			const writer = fileStream.getWriter();
	// 			if (res.body.pipeTo) {
	// 				writer.releaseLock();
	// 				return res.body.pipeTo(fileStream);
	// 			}
	// 			const reader = res.body.getReader();
	// 			const pump = () =>
	// 				reader
	// 					.read()
	// 					.then(({ value, done }) =>
	// 						done
	// 							? writer.close()
	// 							: writer.write(value).then(pump)
	// 					);
	// 			data.dataset.downloads = data.dataset.downloads + 1;
	// 			return pump();
	// 		})
	// 		.then((res) => {
	// 			alert(res.detail);
	// 		});
	// };

	// const filter_by_folder = (folder) => {
	// 	back = "root";
	// 	if (folder == "root") {
	// 		files = all_files.filter((f) => !f.filename.includes("/"));
	// 		folders = all_files
	// 			.filter((f) => f.filename.includes("/"))
	// 			.map((f) => f.filename.split("/")[0]);
	// 		back = null;
	// 	} else {
	// 		files = all_files.filter((f) => f.filename.includes(folder));
	// 		folders = files
	// 			.filter((f) => f.filename.includes("/"))
	// 			.map((f) => f.filename.split("/")[0]);
	// 	}

	// 	folders = [...new Set(folders)];
	// };
</script>

<!-- {#if files}
	<p>Files:</p>
	<div class="overflow-auto w-full max-h-[200px] border-2">
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
				{#if $user}
					<button on:click={() => download(file.name)}
						><Download color="gray" size={20} /></button
					>
				{/if}
				{file.filename}
			</p>
			<td>{formatFileSize(file.size)}</td>
			<td class="text-xs">{file.checksum}</td>
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
{/if} -->
