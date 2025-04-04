<script>
	import retrieveFiles from "$lib/files/retrieveFiles";
	import { createFileTree } from "$lib/files/fileTree";
	import fetchEOTDL from "$lib/shared/fetchEOTDL";
	import auth from "$stores/auth.svelte";

	let { version, collection } = $props();

	let loading = $state(true);
	let files = $state([]);
	let fileTree = $state({});
	let currentPath = $state("");
	let currentView = $state([]); // Current files/folders being displayed
	let searchTerm = $state(""); // Search term for filtering
	let filteredView = $state([]); // Filtered view based on search
	let downloadLoading = $state(false);

	const load = async () => {
		loading = true;
		files = await retrieveFiles(collection, version.version_id);
		fileTree = createFileTree(files);
		navigateToPath("");
		loading = false;
	};

	$effect(() => {
		if (collection && version) {
			load();
		}
	});

	// Filter the current view based on search term
	$effect(() => {
		if (searchTerm.trim() === "") {
			filteredView = currentView;
		} else {
			const term = searchTerm.toLowerCase();
			filteredView = currentView.filter((item) =>
				item.name.toLowerCase().includes(term),
			);
		}
	});

	function navigateToPath(path) {
		currentPath = path;
		if (path === "") {
			// Root level
			currentView = Object.keys(fileTree).map((key) => ({
				name: key,
				isFolder: !key.includes(".") || fileTree[key].children,
				fullPath: key,
			}));
		} else {
			// Get the node at current path
			const parts = path.split("/");
			let current = fileTree;
			for (const part of parts) {
				if (current[part]) {
					current = current[part].children || {};
				}
			}

			// Map the current folder's contents
			currentView = Object.keys(current).map((key) => ({
				name: key,
				isFolder: !key.includes(".") || current[key].children,
				fullPath: path ? `${path}/${key}` : key,
			}));
		}
		// Reset search when navigating
		searchTerm = "";
	}

	function navigateUp() {
		if (!currentPath) return;
		const parts = currentPath.split("/");
		parts.pop();
		navigateToPath(parts.join("/"));
	}

	function handleItemClick(item) {
		if (item.isFolder) {
			navigateToPath(item.fullPath);
		} else {
			// Find the file object
			const file = files.find((f) => f.id === item.fullPath);
			if (file) showDetails(file);
		}
	}

	let details = $state(null);
	let selectedFile = $state(null);

	const showDetails = (file) => {
		selectedFile = file;
		details = file.assets?.asset || {};
	};

	// Format file size in human-readable format
	function formatFileSize(bytes) {
		if (!bytes || isNaN(bytes)) return "Unknown size";

		const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
		if (bytes === 0) return "0 Bytes";

		const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)), 10);
		if (i === 0) return `${bytes} ${sizes[i]}`;

		return `${(bytes / 1024 ** i).toFixed(2)} ${sizes[i]}`;
	}

	// Download the file using the API
	async function downloadFile() {
		if (!auth.id_token) {
			alert("Please login to download files");
			return;
		}
		if (!selectedFile) return;

		try {
			downloadLoading = true;

			// Call the API to get the presigned URL
			const { data, error } = await fetchEOTDL(
				selectedFile.assets.asset.href,
				auth.id_token,
			);

			if (error) {
				throw new Error(`Failed to get download URL: ${error}`);
			}

			// Create an anchor element
			const downloadLink = document.createElement("a");
			downloadLink.href = data.presigned_url;

			// Set the download attribute with the filename
			const filename = selectedFile.id.split("/").pop(); // Extract filename from path
			downloadLink.download = filename;

			// Append to the body, click it, and remove it
			document.body.appendChild(downloadLink);
			downloadLink.click();
			document.body.removeChild(downloadLink);
		} catch (error) {
			console.error("Download error:", error);
			alert("Failed to download file. Please try again.");
		} finally {
			downloadLoading = false;
		}
	}
</script>

{#if !loading}
	<h2>Files ({files.length}):</h2>
	<div class="flex flex-col gap-1 items-start border-1 border-gray-200 p-3">
		{#if details}
			<div class="w-full bg-gray-50 p-4 rounded-lg">
				<div class="flex justify-between items-center mb-4">
					<h3 class="text-lg font-bold truncate">
						{selectedFile?.id || "File Details"}
					</h3>
					<button
						onclick={() => {
							details = null;
							selectedFile = null;
						}}
						class="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
					>
						⬆️
					</button>
				</div>

				<div class="flex flex-col gap-2 mb-4">
					<div class="flex flex-col">
						<span class="text-sm text-gray-500">Checksum</span>
						<span
							class="font-mono text-sm overflow-hidden text-ellipsis"
							>{details.checksum || "N/A"}</span
						>
					</div>
					<div class="flex flex-col">
						<span class="text-sm text-gray-500">Size</span>
						<span
							>{formatFileSize(
								details.file_size || details.size,
							)}</span
						>
					</div>
					<div class="flex flex-col">
						<span class="text-sm text-gray-500">Path</span>
						<span class="overflow-hidden text-ellipsis"
							>{selectedFile?.id || "N/A"}</span
						>
					</div>
				</div>

				<button
					onclick={downloadFile}
					disabled={downloadLoading}
					class="w-full py-2 px-4 bg-blue-500 text-white rounded disabled:cursor-not-allowed cursor-pointer"
				>
					{downloadLoading ? "Preparing..." : "Download"}
				</button>
			</div>
		{:else}
			<div class="mb-2">
				<span class="font-semibold">Current path:</span>
				{currentPath || "/"}
				{#if currentPath}
					<button
						onclick={navigateUp}
						class="ml-2 px-2 py-1 bg-gray-200 rounded hover:bg-gray-300"
					>
						⬆️ Up
					</button>
				{/if}
			</div>
			<div class="mb-2 w-full">
				<input
					type="text"
					placeholder="Search in current folder..."
					bind:value={searchTerm}
					class="px-2 py-1 border border-gray-300 rounded w-full"
				/>
			</div>
			<div
				class="max-h-[200px] overflow-y-auto w-full flex flex-col gap-1 items-start"
			>
				{#each filteredView as item}
					<button
						onclick={() => handleItemClick(item)}
						class="hover:underline cursor-pointer flex items-center w-full text-left"
					>
						<span class="mr-2">
							{#if item.isFolder}
								📁
							{:else}
								📄
							{/if}
						</span>
						<span class="overflow-hidden text-ellipsis"
							>{item.name}</span
						>
					</button>
				{/each}
			</div>
			{#if filteredView.length === 0}
				<div class="text-gray-500 italic">
					No matching files or folders
				</div>
			{/if}
		{/if}
	</div>
{/if}
