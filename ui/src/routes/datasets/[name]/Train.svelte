<script>
	export let dataset;
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
				>
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
