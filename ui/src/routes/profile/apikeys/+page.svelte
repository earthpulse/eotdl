<script>
    import ProfileNavBar from "../ProfileNavBar.svelte";
	import requestApiKey from "$lib/apikeys/requestApiKey.js";
	import deleteApiKey from "$lib/apikeys/deleteApiKey.js";
	import retrieveApiKey from "$lib/apikeys/retrieveApiKey.js";
	import { id_token } from "$stores/auth"
	import { onMount } from "svelte";
	// import copyToClipboard from "$lib/shared/copyToClipboard";
	import TrashCanOutline from "svelte-material-icons/TrashCanOutline.svelte"
	import ContentCopy from "svelte-material-icons/ContentCopy.svelte"

	let apikeys = [];
	let limitReached = false;

	const formatTime = (dataTime) => {
		let data = dataTime.split("T")[0];
		let time = dataTime.split("T")[1].split(":").slice(0,2).join(":");
		return `${data} at ${time}`;

	}

	onMount(() => {
		retrieveApiKey($id_token).then((val) =>{
			apikeys = val;
		});
    });

	const deleteKey = async (keyId) => {
		deleteApiKey($id_token, keyId).then((val) =>{
			retrieveApiKey($id_token).then((val) =>{
			apikeys = val;
			limitReached = false;
		});
		})
	} 

	const newKey = async () => {
		try {
			await requestApiKey($id_token)
			limitReached = false;
		}
		catch (e) {
			limitReached = true;
		}
		retrieveApiKey($id_token).then((val) =>{
			apikeys = val;
		});
	} 

</script>

<div class="w-full flex flex-row items-left sm:px-14 px-3 h-screen">
	<div class="py-10 mt-10 flex sm:flex-row flex-col">
		<ProfileNavBar />
        <div class="px-3 w-full max-w-6xl flex flex-col sm:items-start items-center gap-3">
            <h1 class="sm:text-left text-center w-full text-2xl">Api Keys</h1>
			<button class="btn btn-outline w-30 mt-8" on:click={newKey}>Create new</button>
			<p class="transition-all text-red-500 sm:text-left text-center {limitReached ? "opacity-100":"opacity-0"}">API key limit reached. Delete an existing key to create a new one.</p>
			{#each apikeys as key}
				<div class="flex justify-between px-4 py-2 mb-2 bg-gray-100 rounded-lg">
					<div>
						<div class="flex items-baseline">
							<p><strong>Key:</strong> {key.id.slice(1,8).concat(" . . .")}</p>
						</div>
						<p class="text-sm text-gray-400 pt-4">Created on {formatTime(key.createdAt)}</p>
					</div>
					<div class="flex items-baseline justify-between flex-col ml-4">
						<button class="active:bg-gray-300 p-1 rounded-md transition-all" on:click={deleteKey(key.id)}>
							<TrashCanOutline size="18" title="Delete" />
						</button>
						<button class = "active:bg-gray-300 p-1 rounded-md transition-all" on:click={navigator.clipboard.writeText(key.id)}>
							<ContentCopy size="18" title="Copy"/>
						</button>
					</div>
				</div>	
			{/each}
		</div>
    </div>
</div>