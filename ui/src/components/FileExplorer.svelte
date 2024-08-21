<script>
	import { browser } from "$app/environment";
	import Folder from "svelte-material-icons/Folder.svelte";
	import ArrowLeft from "svelte-material-icons/ArrowLeft.svelte";
	import Download from "svelte-material-icons/Download.svelte";
	import Eye from "svelte-material-icons/Eye.svelte";
	import File from "svelte-material-icons/File.svelte";
	import { id_token } from "$stores/auth";
	import { PUBLIC_EOTDL_API } from "$env/static/public";
	import { onMount } from "svelte";
	import Map from "$components/Map.svelte";
	import { Carta } from "carta-md";
	import DOMPurify from "isomorphic-dompurify";
	import "$styles/file-explorer-md.css";

	const carta = new Carta({
		extensions: [],
		sanitizer: DOMPurify.sanitize,
	});

	let allowedExtensions = {
		image: ["jpg", "png", "jpeg"],
		map: ["geojson"],
		tif: ["tiff", "tif"],
		text: ["txt"],
		pdf: ["pdf"],
		md: ["md"],
	};
	let blobFunctions = {
		image: async () => {
			return URL.createObjectURL(blob);
		},
		text: async () => {
			return blob.text();
		},
		pdf: async () => {
			blob = blob.slice(0, blob.size, "application/pdf");
			return await URL.createObjectURL(blob);
		},
		map: async () => {
			return JSON.parse(await blob.text());
		},
		tif: async () => {
			return blob.arrayBuffer();
		},
		md: async () => {
			return carta.render(await blob.text());
		},
	};

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
	let blob;
	let details = {};
	let currentFileName = null;

	let currentBlob;
	let currentFormat;
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

	const getFileFormat = (fileName) => {
		const ext = fileName.split(".").pop();
		for (const type of Object.keys(allowedExtensions)) {
			if (allowedExtensions[type].includes(ext)) return type;
		}
		return false;
	};

	const preview = async () => {
		await fetch(
			`${PUBLIC_EOTDL_API}/datasets/${datasetId}/download/${currentFileName}`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${$id_token}`,
				},
			},
		).then(async (res) => {
			blob = await res.blob();
			currentBlob = null;
			currentFormat = getFileFormat(currentFileName).toString();
			currentBlob = await blobFunctions[currentFormat]();
		});
	};
</script>

<input type="checkbox" id="preview_modal" class="modal-toggle" />
<div role="dialog" class="modal">
	<div class="modal-box flex justify-center">
		<form method="dialog">
			<label
				for="preview_modal"
				class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2"
				>✕</label
			>
		</form>
		{#if $id_token}
			{#if currentBlob && currentFormat == "pdf"}
				<div class="h-full w-full">
					<iframe
						src={currentBlob}
						class="h-[450px] ml-2 my-4 w-[450px]"
						title="PDFViewer"
						alt="PDFViewer"
					></iframe>
				</div>
			{:else if currentBlob && currentFormat == "image"}
				<img
					class="z-40 my-10 w-96 h-96 shadow-sm"
					src={currentBlob}
					alt="ImgPReview"
				/>
			{:else if currentBlob && currentFormat == "text"}
				<div
					class="w-[full] m-3 overflow-auto h-[300px] rounded-md bg-slate-50"
				>
					<p class="text-left m-1">{currentBlob}</p>
				</div>
			{:else if (currentBlob && currentFormat == "map") || (currentBlob && currentFormat == "tif")}
				<div class="flex flex-col my-4 gap-3 w-full h-[300px]">
					<Map
						geojson={currentFormat == "map" ? currentBlob : null}
						geotif={currentFormat == "tif" ? currentBlob : null}
					/>
				</div>
			{:else if currentBlob && currentFormat == "md"}
				<div id="md" class="flex flex-col my-4 gap-3 w-full h-[300px]">
					{@html currentBlob}
				</div>
			{/if}
		{:else}
			<p>Please log in to download or preview files.</p>
		{/if}
	</div>
</div>

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
					<div class="flex py-2 gap-2">
						<label
							class="hover:cursor-pointer"
							for={$id_token ? "" : "preview_modal"}
							title="Download"
							on:click={() => download(details)}
							><Download size="20" /></label
						>
						{#if getFileFormat(currentFileName)}
							<label
								class="hover:cursor-pointer"
								title="Preview"
								for="preview_modal"
								on:click={() => {
									preview();
								}}
							>
								<Eye size="20" />
							</label>
						{/if}
					</div>
				{/if}
			</table>
		</div>
	{:else}
		<p>No files found.</p>
	{/if}
{:else}
	<p>Loading files ...</p>
{/if}
