<script>
	import Leaderboard from "$components/Leaderboard.svelte";
	import retrieveModelsLeaderboard from "$lib/models/retrieveModelsLeaderboard";

	let data = $state(null);

	$effect(async () => {
		data = await retrieveModelsLeaderboard(fetch);
	});
</script>

<div class="sm:my-[100px] w-full">
	<Leaderboard
		leaderboard={data}
		field="models"
		textOnRight={true}
		msgText="Ingest models into EOTDL and climb up the leaderboard!"
	/>
</div>
