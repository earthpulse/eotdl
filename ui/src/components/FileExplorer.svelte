<script>
	import { browser } from "$app/environment";
	import Folder from "svelte-material-icons/Folder.svelte";
	import ArrowLeft from "svelte-material-icons/ArrowLeft.svelte";
	import File from "svelte-material-icons/File.svelte";
	import { id_token } from "$stores/auth";
	import { PUBLIC_EOTDL_API } from "$env/static/public";
	import { onMount } from "svelte";

	export let data;
	export let retrieveFiles;
	export let version;
	export let datasetId;

	let createWriteStream;
	let files = null;
	let tree = null;
	let currentLevel = {};
	let navigationStack = [];
	let loading = false;
	let currentPath = [];
	let onDetails = false;
	let details = {};
	let currentFileName = null;
	onMount(async () => {
		if (browser) {
			// only works in browser
			const streamsaver = await import("streamsaver");
			createWriteStream = streamsaver.createWriteStream;
		}
	});

	const sizeFormat = (bytes) => {
		const size = bytes;
		if (size < 1024) return `${size} bytes`;
		else if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`;
		else if (size < 1024 * 1024 * 1024)
			`${(size / (1024 * 1024)).toFixed(2)} MB`;
		else return `${(size / (1024 * 1024 * 1024)).toFixed(2)} GB`;
	};

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
	};

	const goBack = () => {
		if (onDetails) {
			currentPath = currentPath.slice(0, currentPath.length - 1);
			onDetails = false;
		} else {
			currentLevel = navigationStack.pop();
			currentPath = currentPath.slice(0, currentPath.length - 1);
		}
	};

	const goToLevel = (folder) => {
		const folderIndex = currentPath.indexOf(folder) + 1;

		if (
			currentPath.length > navigationStack.length &&
			folder.split(".").length < 2
		) {
			onDetails = false;
			currentPath = currentPath.slice(0, currentPath.length - 1);
		}
		for (let i = 0; navigationStack.length - folderIndex > 0; i++) {
			goBack();
		}
	};

	const goToDetails = (file, filename) => {
		onDetails = true;
		details = {
			checksum: file.checksum,
			version: file.version,
			size: sizeFormat(file.size),
		};
		currentPath = [...currentPath, filename];
		currentFileName = file.filename;
	};

	const getCurrentPath = (intoFolder) => {
		if (navigationStack.length > 0) {
			currentPath = [...currentPath, intoFolder];
		} else {
			currentPath = [];
		}
	};

	const download = async () => {
		// seems to work, but not sure if it will with large datasets (need to test)
		fetch(
			`${PUBLIC_EOTDL_API}/datasets/${datasetId}/download/${currentFileName}`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${$id_token}`,
				},
			},
		)
			.then((res) => {
				if (!res.ok) return res.json();
				const fileStream = createWriteStream(currentFileName);
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
								: writer.write(value).then(pump),
						);
				return pump();
			})
			.then((res) => {
				alert(res.detail);
			});
	};
</script>

{#if !loading}
	{#if files}
		<p>Files ({files.length}) :</p>
		<div class="overflow-auto w-full max-h-[200px] border-2">
			<div class="text-[13px] flex">
				{#if navigationStack.length > 0 || onDetails}
					<button class="hover:underline flex p-2" on:click={goBack}
						><ArrowLeft class="self-center mr-1" />
					</button>
				{/if}
				{#each currentPath as folder}
					<button
						on:click={goToLevel(folder)}
						class="hover:underline"
					>
						/{folder}</button
					>
				{/each}
			</div>
			<table class="ml-2">
				{#if onDetails == false}
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
										on:click={() => openFolder(item)}
									>
										<Folder
											class=" self-center mr-[2px]"
										/>{item}</button
									>
								</td>
							</tr>
						{:else}
							<tr>
								<td class="pr-1">
									<button
										on:click={goToDetails(
											currentLevel[item],
											item,
										)}
										><p class="hover:underline flex">
											<File class=" self-center" />
											{item}
										</p></button
									>
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
				{:else}
					{#each Object.keys(details) as detail}
						<tr>
							<th class="text-left">{detail}:</th>
							<td class="pl-1">{details[detail]}</td>
						</tr>
					{/each}
					<button class="btn" on:click={() => download(details)}
						>download</button
					>
				{/if}
			</table>
		</div>
	{:else}
		<p>No files found.</p>
	{/if}
{:else}
	<p>Loading files ...</p>
{/if}
