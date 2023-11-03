<script>
	import { onMount } from "svelte";
	import retrievePopularModels from "$lib/models/retrievePopularModels";
	import Popular from "./Popular.svelte";

	let data = null;
	onMount(async () => {
		data = await retrievePopularModels(fetch, 3);
	});
</script>

<Popular {data} title="Popular models" />
