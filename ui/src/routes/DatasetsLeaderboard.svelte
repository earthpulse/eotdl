<script>
	import Leaderboard from "$components/Leaderboard.svelte";
	import { onMount } from "svelte";
	import retrieveDatasetsLeaderboard from "$lib/datasets/retrieveDatasetsLeaderboard";

	let data = null;
	onMount(async () => {
		data = await retrieveDatasetsLeaderboard(fetch);
	});
</script>

<div class="sm:my-[100px] w-full">
	<Leaderboard leaderboard={data} textOnLeft={true} />
</div>
