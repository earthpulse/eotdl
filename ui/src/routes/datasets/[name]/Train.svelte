<script>
	export let dataset;

	// training parameters
	let batch_size = 16;
	let epochs = 10;
</script>

<label for="trainining-template" class="btn btn-ghost btn-outline">Train</label>
<input type="checkbox" id="trainining-template" class="modal-toggle" />
<div class="modal modal-bottom sm:modal-middle">
	<div class="modal-box w-[95%] sm:w-[75%] max-w-none">
		<form
			on:submit|preventDefault={() => {}}
			class="flex flex-col gap-2 text-sm"
		>
			<h1 class="text-2xl font-bold">Train</h1>
			<p>Open the training template in your cloud workspace:</p>
			<a
				class="btn btn-outline"
				href={`https://hub.api.eotdl.com/services/eoxhub-gateway/eotdl/notebook-view/notebooks/07_training_template.ipynb`}
				target="_blank">Notebook</a
			>
			<p>or execute a headless training job:</p>
			<div class="flex flex-col gap-2 border-2 border-slate-200 p-2">
				<h2 class="font-bold">Parameters:</h2>
				<div class="flex justify-between items-center">
					<label>Dataset name:</label>
					<span class="w-32 text-right">{dataset.name}</span>
				</div>
				<div class="flex justify-between items-center">
					<label for="batch_size">Batch size:</label>
					<input
						type="number"
						id="batch_size"
						bind:value={batch_size}
						class="input input-bordered input-xs w-24"
					/>
				</div>
				<div class="flex justify-between items-center">
					<label for="epochs">Epochs:</label>
					<input
						type="number"
						id="epochs"
						bind:value={epochs}
						class="input input-bordered input-xs w-24"
					/>
				</div>
			</div>
			<a
				class="btn btn-outline"
				href={`https://hub.api.eotdl.com/services/eoxhub-gateway/eotdl/notebook-view/notebooks/07_training_template.ipynb`}
				target="_blank">Submit Job</a
			>
			<p>
				You can track your training jobs <a
					class="underline"
					href="https://hub.api.eotdl.com/services/eoxhub-gateway/eotdl/notebook-view/notebooks/07_training_template.ipynb"
					target="_blank">here</a
				>.
			</p>
		</form>
		<div class="modal-action">
			<label for="trainining-template" class="btn btn-ghost btn-outline"
				>Close</label
			>
		</div>
	</div>
	<label class="modal-backdrop" for="trainining-template">Close</label>
</div>
