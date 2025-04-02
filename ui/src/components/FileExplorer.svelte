<script>
	import { onMount } from "svelte";

	import retrieveFiles from "$lib/files/retrieveFiles";

	export let version;
	export let collection;

	onMount(async () => {
		files = await retrieveFiles(collection, version);

		console.log(files);
	});
</script>
