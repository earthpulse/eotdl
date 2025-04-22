<script>
	import retrievePopularDatasets from "$lib/datasets/retrievePopularDatasets";
	import Popular from "./Popular.svelte";

	let { tags } = $props();

	let data = $state(null);

	$effect(async () => {
		data = await retrievePopularDatasets(fetch, 3);
	});
</script>

<Popular {data} title="Popular datasets" {tags} />
