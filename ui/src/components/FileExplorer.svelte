<script>
		import { browser } from "$app/environment";
		import Folder from "svelte-material-icons/Folder.svelte";
		import ArrowLeft from "svelte-material-icons/ArrowLeft.svelte";
		import Eye from "svelte-material-icons/Eye.svelte";
		import File from "svelte-material-icons/File.svelte";
		import { id_token } from "$stores/auth";
		import { PUBLIC_EOTDL_API } from "$env/static/public";
		import { onMount } from "svelte";
    	import { object_without_properties } from "svelte/internal";

		let allowedExtensions = { 
			image:["jpg","png","jpeg","tif","tiff",],
			map:"geojson",
			text:"txt",
			pdf:"pdf",
			md:"md"}
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
	let onPreview = false;
	
	let blob;
	let details = {};
	let currentFileName = null;

	let currentImg;
	let currentPdf;
	let currentMd;
	let currentMap;
	let currentText;
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
				console.log(res);
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

	const getFileFormat = (fileName) => {
		const ext = fileName.split(".").pop();
		for (const type of Object.keys(allowedExtensions)) {
			if (allowedExtensions[type].includes(ext)){
				return type;
			} 
		};
		return false;
	}

	const preview = async () => {
		await fetch(
			`${PUBLIC_EOTDL_API}/datasets/${datasetId}/download/${currentFileName}`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${$id_token}`,
				},
			},
		)
		.then(async (res) => {
					blob = await res.blob();
					switch(getFileFormat(currentFileName).toString()){
						case "image":
							currentImg = await URL.createObjectURL(blob);
							currentMap = null;
							currentMd = null;
							currentPdf = null;
							currentText = null;
							onPreview = true;
							break;

						case "text":
							currentImg = null;
							currentMap = null;
							currentMd = null;
							currentPdf = null;
							currentText = await blob.text();
							onPreview = true;
							break;

						case "pdf":
							blob = blob.slice(0, blob.size, "application/pdf")
							currentImg = null;
							currentMap = null;
							currentMd = null;
							currentPdf = await URL.createObjectURL(blob);
							currentText = null;
							onPreview = true;
                        	break;
					}
				});
		}
</script>

{#if onPreview}		
	<div class="fixed items-center justify-center flex z-40 h-screen w-screen top-0 left-0">
		<div class="z-40 rounded-xl shadow-lg items-center justify-between flex flex-col bg-slate-100 h-[34rem] w-[30rem] border-slate-200 border-[1px]">
			<button class="fixed self-end mx-4 my-4 z-[41]" on:click={() => onPreview = false}>X</button>			
			{#if currentPdf}
				<div class="h-full w-full">
					<iframe src="{currentPdf}" class="h-full p-8 w-full" title="PDFViewer" alt="PDFViewer"></iframe>
				</div>		
			{:else if currentImg}				
				<img class="z-40 mt-16 w-96 h-96 shadow-sm" src="{currentImg}" alt="ImgPReview">
			{:else if currentText}				
				<div class="p-1 m-8 w-[90%] h-[95%] rounded-md bg-slate-50">
					<p class="text-left">{currentText}</p>
				</div>	
			{/if}
		</div>
	</div>
{/if}
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
					<button class="btn" on:click={() =>preview()}
						>Preview</button
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
