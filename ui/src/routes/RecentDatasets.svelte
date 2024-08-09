<script>
	import { onMount } from "svelte";
	import retrieveDatasets from "$lib/datasets/retrieveDatasets";
	import Recent from "./Recent.svelte";

	export let tags;

	let data = null;
	onMount(async () => {
		data = await retrieveDatasets(fetch, 3);
	});
</script>

<Recent {data} title="Recent datasets" {tags} />
