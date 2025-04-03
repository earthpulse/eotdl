<script>
	import retrievePopularModels from "$lib/models/retrievePopularModels";
	import Popular from "./Popular.svelte";

	let { tags } = $props();

	let data = $state(null);

	$effect(async () => {
		data = await retrievePopularModels(fetch, 3);
	});
</script>

<Popular {data} title="Popular models" {tags} />
