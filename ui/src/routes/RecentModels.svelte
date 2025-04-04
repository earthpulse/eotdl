<script>
	import retrieveModels from "$lib/models/retrieveModels";
	import Recent from "./Recent.svelte";

	let { tags } = $props();

	let data = $state(null);

	$effect(async () => {
		data = await retrieveModels(fetch, 3);
	});
</script>

<Recent {data} title="Recent models" {tags} />
