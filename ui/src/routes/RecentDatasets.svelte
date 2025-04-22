<script>
	import retrieveDatasets from "$lib/datasets/retrieveDatasets";
	import Recent from "./Recent.svelte";

	let { tags } = $props();

	let data = $state(null);

	$effect(async () => {
		data = await retrieveDatasets(fetch, 3);
	});
</script>

<Recent {data} title="Recent datasets" {tags} />
