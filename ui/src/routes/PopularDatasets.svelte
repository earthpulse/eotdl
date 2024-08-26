<script>
	import { onMount } from "svelte";
	import retrievePopularDatasets from "$lib/datasets/retrievePopularDatasets";
	import Popular from "./Popular.svelte";

	export let tags;

	let data = null;
	onMount(async () => {
		data = await retrievePopularDatasets(fetch, 3);
	});
</script>

<Popular {data} title="Popular datasets" {tags} />
