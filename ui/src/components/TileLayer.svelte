<script>
	import { getContext, onDestroy, onMount } from "svelte";

	export let url;
	export let options;

	const { getMap } = getContext("map");

	let layer = null;

	onMount(() => {
		const map = getMap();
		layer = L.tileLayer(url, options).addTo(map);
	});

	onDestroy(() => {
		layer.remove();
	});
</script>
