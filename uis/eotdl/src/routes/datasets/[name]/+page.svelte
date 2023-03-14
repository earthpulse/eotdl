<script>
	import { user, id_token } from "$stores/auth";
	import { EOTDL_API } from "$lib/env";
	import { onMount } from "svelte";
	import { browser } from "$app/environment";

	export let data;

	$: ({ name, id, createdAt, description } = data.dataset);

	let createWriteStream;
	onMount(async () => {
		if (browser) {
			// only works in browser
			const streamsaver = await import("streamsaver");
			createWriteStream = streamsaver.createWriteStream;
		}
	});

	const download = async () => {
		// seems to work, but not sure if it will with large datasets (need to test)
		const fileName = `${name}.zip`;
		fetch(`${EOTDL_API}/datasets/${id}/download`, {
			method: "GET",
			headers: {
				Authorization: `Bearer ${$id_token}`,
			},
		}).then((res) => {
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
						done ? writer.close() : writer.write(value).then(pump)
					);
			return pump();
		});

		// this works but I thing will not work with large files (no streaming)

		// const response = await fetch(`${EOTDL_API}/datasets/${id}/download`, {
		// 	method: "GET",
		// 	headers: {
		// 		Authorization: `Bearer ${$id_token}`,
		// 	},
		// });
		// const blob = await response.blob();
		// const url = URL.createObjectURL(blob);
		// const link = document.createElement("a");
		// link.href = url;
		// link.download = `${name}.zip`;
		// document.body.appendChild(link);
		// link.click();
		// document.body.removeChild(link);
	};
</script>

<div class="w-full flex flex-col items-center">
	<div class="px-3 py-10 mt-10 w-full max-w-6xl">
		<div class="flex flex-row justify-between w-full">
			<h1 class="text-3xl">{name}</h1>
			<button
				class="btn btn-ghost btn-outline"
				disabled={!$user}
				on:click={download}>Download</button
			>
		</div>
		<p class="text-gray-400">{createdAt}</p>
		<p class="py-10">{description}</p>
	</div>
</div>
