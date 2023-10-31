<script>
	import Leaderboard from "$components/Leaderboard.svelte";
	import { onMount } from "svelte";
	import retrieveModelsLeaderboard from "$lib/models/retrieveModelsLeaderboard";

	let data = null;
	onMount(async () => {
		data = await retrieveModelsLeaderboard(fetch);
	});
</script>

<div class="mt-[100px] w-full">
	<Leaderboard leaderboard={data} field="models" />
</div>
