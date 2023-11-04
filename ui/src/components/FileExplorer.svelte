<script>
	import { browser } from "$app/environment";

	export let data;
	export let retrieveFiles;
	export let version;

	// $: console.log(dataset, version);

	let createWriteStream;
	let files = null;
	let tree = null;
	let currentLevel = {};
	let navigationStack = [];

	const load = async () => {
		tree = null;
		files = null;
		currentLevel = {};
		navigationStack = [];
		// only works in browser
		// const streamsaver = await import("streamsaver");
		// createWriteStream = streamsaver.createWriteStream;
		files = await retrieveFiles(data.id, version.version_id);
		// console.log(files);
		tree = buildFileTree(files);
		currentLevel = tree;
	};

	$: if (browser && version) load();

	const buildFileTree = (files) => {
		const tree = {};
		files.forEach((file) => {
			const path = file.filename.split("/");
			let current = tree;
			path.forEach((folder, i) => {
				if (i == path.length - 1) {
					current[folder] = file;
				} else {
					if (!current[folder]) current[folder] = {};
					current = current[folder];
				}
			});
		});
		return tree;
	};

	const openFolder = (folderName) => {
		navigationStack = [...navigationStack, currentLevel];
		currentLevel = currentLevel[folderName];
	};

	const goBack = () => {
		currentLevel = navigationStack.pop();
	};

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
</script>

{#if files}
	<p>Files ({files.length}) :</p>
	<div class="overflow-auto w-full max-h-[200px] border-2">
		{#if navigationStack.length > 0}
			<button class="px-3 hover:underline" on:click={goBack}>...</button>
		{/if}
		{#each Object.keys(currentLevel) as item}
			<p class="flex flex-row gap-1 px-3">
				<!-- {#if $user}
					<button on:click={() => download(file.name)}
						><Download color="gray" size={20} /></button
					>
				{/if} -->
				{#if typeof currentLevel[item] === "object" && !currentLevel[item].checksum}
					<button
						class="hover:underline"
						on:click={() => openFolder(item)}>{item}</button
					>
				{:else}
					{item}
				{/if}
			</p>
			<!-- <td>{formatFileSize(file.size)}</td> -->
			<!-- <td class="text-xs">{current_files[file].checksum}</td> -->
		{/each}
	</div>
{:else}
	<p>Loading files ...</p>
{/if}
