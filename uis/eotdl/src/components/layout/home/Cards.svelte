<script>
	import CardButton from "./CardButton.svelte";
</script>

<div
	class="grid grid-rows-2 md:grid-rows-1 md:grid-cols-2 py-14 gap-6 px-6 max-w-4xl bg-base-100"
>
	<div class="card shadow-xl border">
		<div class="card-body items-center text-center">
			<h2 class="card-title">Datasets</h2>
			<p>
				Browse and download AI-Ready EO datasets for training ML models
				or create your own with our open source tools.
			</p>
			<div class="card-actions justify-end">
				<CardButton>Browse</CardButton>
				<CardButton variant="secondary">Create</CardButton>
			</div>
		</div>
	</div>
	<div class="card shadow-xl border">
		<div class="card-body items-center text-center">
			<h2 class="card-title">Models</h2>
			<p>
				Browse and test ML models or easily train your own with our
				datasets in the cloud.
			</p>
			<div class="card-actions justify-end">
				<CardButton>Browse</CardButton>
				<CardButton variant="secondary">Train</CardButton>
			</div>
		</div>
	</div>
</div>
