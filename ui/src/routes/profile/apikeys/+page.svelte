<script>
	import requestApiKey from "$lib/apikeys/requestApiKey.js";
	import deleteApiKey from "$lib/apikeys/deleteApiKey.js";
	import retrieveApiKey from "$lib/apikeys/retrieveApiKey.js";
	import auth from "$stores/auth.svelte";
	import TrashCanOutline from "svelte-material-icons/TrashCanOutline.svelte";
	import ContentCopy from "svelte-material-icons/ContentCopy.svelte";

	let apikeys = $state([]);
	let key2delete = $state(null);

	const formatTime = (dataTime) => {
		let data = dataTime.split("T")[0];
		let time = dataTime.split("T")[1].split(":").slice(0, 2).join(":");
		return `${data} at ${time}`;
	};

	$effect(async () => {
		try {
			if (auth.id_token) {
				apikeys = await retrieveApiKey(auth.id_token);
			}
		} catch (e) {
			alert(e.message);
		}
	});

	const createKey = async () => {
		try {
			const newKey = await requestApiKey(auth.id_token);
			apikeys = [...apikeys, newKey];
		} catch (e) {
			alert(e.message);
		}
	};

	const deleteKey = async () => {
		try {
			await deleteApiKey(auth.id_token, key2delete);
			apikeys = apikeys.filter((key) => key.id !== key2delete);
		} catch (e) {
			alert(e.message);
		}
	};
</script>

<div class="w-full flex flex-col sm:items-start gap-3">
	<h1 class="sm:text-left w-full text-2xl">Api Keys</h1>
	<button class="btn btn-outline w-30" onclick={createKey}>Create new</button>
	{#each apikeys as key}
		<div
			class="flex justify-between px-4 py-2 mb-2 bg-gray-100 rounded-lg w-full"
		>
			<div>
				<div class="flex items-baseline">
					<p>
						<strong>Key:</strong>
						{key.id.slice(1, 8).concat("...")}
					</p>
				</div>
				<p class="text-sm text-gray-400 pt-4">
					Created on {formatTime(key.createdAt)}
				</p>
			</div>
			<div class="flex items-baseline justify-between flex-col ml-4">
				<button
					for="confirm_modal"
					onclick={() => (key2delete = key.id)}
					class="active:bg-gray-300 p-1 rounded-md transition-all cursor-pointer"
				>
					<TrashCanOutline size="18" title="Delete" />
				</button>
				<button
					class="active:bg-gray-300 p-1 rounded-md transition-all"
					onclick={navigator.clipboard.writeText(key.id)}
				>
					<ContentCopy size="18" title="Copy" />
				</button>
			</div>
		</div>
	{/each}
</div>

<input type="checkbox" id="confirm_modal" class="modal-toggle" />
<div class="modal" role="dialog">
	<div class="modal-box">
		<h3 class="text-lg font-bold">Confirm</h3>
		<p class="py-4">Are you sure you want to delete this key?</p>
		<div class="modal-action">
			<label for="confirm_modal" class="btn btn-ghost">Close</label>
			<button for="confirm_modal" class="btn" onclick={deleteKey}
				>Confirm</button
			>
		</div>
	</div>
</div>
