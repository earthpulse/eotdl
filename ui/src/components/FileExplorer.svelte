<script>
	import { browser } from "$app/environment";

	import Folder from "svelte-material-icons/Folder.svelte"
	import ArrowLeft from "svelte-material-icons/ArrowLeft.svelte"
	import File from "svelte-material-icons/File.svelte"

	export let data;
	export let retrieveFiles;
	export let version;

	// $: console.log(dataset, version);

	let createWriteStream;
	let files = null;
	let tree = null;
	let currentLevel = {};
	let navigationStack = [];
	let loading = false;
	let currentPath = [];

	const load = async () => {
		loading = true;
		tree = null;
		files = null;
		currentLevel = {};
		navigationStack = [];
		// only works in browser
		// const streamsaver = await import("streamsaver");
		// createWriteStream = streamsaver.createWriteStream;
		files = await retrieveFiles(data.id, version.version_id);
		//console.log(files);
		tree = buildFileTree(files);
		currentLevel = tree;
		loading = false;
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
		getCurrentPath(folderName);
		console.log(currentPath);
	};
	
	const goBack = () => {
		currentLevel = navigationStack.pop();

		currentPath = currentPath.slice(0,currentPath.length-1);
	};


	const getCurrentPath = (intoFolder) => {
		if (navigationStack.length > 0){
			currentPath = [...currentPath, intoFolder];
		}
		else {
            currentPath = [];
        }
	} 
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

{#if !loading}
	{#if files}
		<p>Files ({files.length}) :</p>
		<div class="overflow-auto w-full max-h-[200px] border-2">			
				<div class="pl-2 pb-2 text-[13px] font-semibold flex">Path:	/			
						{#each currentPath as folder}
							<button class="hover:underline"> {folder}/</button>
						{/each}
				</div>
			<table class="ml-2">			
			{#if navigationStack.length > 0}
				<button class="hover:underline flex" on:click={goBack}
				><ArrowLeft class="self-center mr-1"/> Return </button
				>
			{/if}
				{#each Object.keys(currentLevel) as item}
					<!-- {#if $user}
					<button on:click={() => download(file.name)}
						><Download color="gray" size={20} /></button
						>
						{/if} -->
						{#if typeof currentLevel[item] === "object" && !currentLevel[item].checksum}
						<tr>
							<td>
								<button
								class="hover:underline flex"
								on:click={() => openFolder(item)}>
								<Folder class=" self-center mr-[2px]" />{item}</button
								>
							</td>
						</tr>
						
					{:else}
						<tr>					
							<td class="pr-1">
								<p class="flex"><File class=" self-center"/> {item}</p>
							</td>
					   <!-- <td class="px-1">
								<p>
										{currentLevel[item].checksum.substr(0, 8)}...
								</p>
							</td>
							<td class="px-1">
								<p>
										{currentLevel[item].version}
								</p>
							</td> -->
						</tr>
					{/if}
						<!-- <td>{formatFileSize(file.size)}</td> -->
						<!-- <td class="text-xs">{current_files[file].checksum}</td> -->
				{/each}
				
			</table>		
		</div>
	{:else}
		<p>No files found.</p>
	{/if}
{:else}
	<p>Loading files ...</p>
{/if}