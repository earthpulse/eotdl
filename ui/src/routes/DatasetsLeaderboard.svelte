<script>
	import Leaderboard from "$components/Leaderboard.svelte";
	import retrieveDatasetsLeaderboard from "$lib/datasets/retrieveDatasetsLeaderboard";

	let data = $state(null);

	$effect(async () => {
		data = await retrieveDatasetsLeaderboard(fetch);
	});
</script>

<div class="sm:my-[50px] w-full">
	<Leaderboard leaderboard={data} textOnLeft={true} />
</div>
