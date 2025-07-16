<script>
	let { dataset } = $props();

	// training parameters
	let batch_size = $state(16);
	let epochs = $state(10);
	let jobs = $state(1);

	let hyper_params = $state({
		batch_size: "8,16,32",
		epochs: "10,20,30"
	});
	function validateHyperParams() {
		if (hyper_params.batch_size.split(",").length <= 0 || hyper_params.batch_size.includes(" ")) {
			console.log("Batch size is not a comma separated list of numbers");
			return false;
		}
		if (hyper_params.epochs.split(",").length <= 0 || hyper_params.epochs.includes(" ")) {
			console.log("Epochs is not a comma separated list of numbers");
			return false;
		}
		if (jobs <= 0 || !Number.isInteger(jobs)) {
			console.log("Jobs is not a positive integer");
			return false;
		}
		return true;
	}
</script>

<label for="trainining-template" class="btn btn-ghost btn-outline">Train</label>
<input type="checkbox" id="trainining-template" class="modal-toggle" />
<div class="modal modal-bottom sm:modal-middle">
	<div class="modal-box w-[95%] sm:w-[75%] max-w-none">
		<form
			onsubmit={() => preventDefault(() => {
			})}
			class="flex flex-col gap-2 text-sm"
		>
			<h1 class="text-2xl font-bold">Train</h1>
			<p>Open the training template in your cloud workspace:</p>
			<a
				class="btn btn-outline"
				href={`https://hub.api.eotdl.com/services/eoxhub-gateway/eotdl/notebook-view/notebooks/notebooks/07_training_template.ipynb`}
				target="_blank">Notebook</a
			>
			<p>or execute a headless training job:</p>
			<div class="tabs tabs-border">
				<input type="radio" name="my_tabs_2" class="tab" aria-label="Single run" />
				<div class="tab-content border-base-300 bg-base-100 p-10">
					<div class="flex flex-col gap-2 ">
						<h2 class="font-bold" for="parameters">Parameters:</h2>
						<div class="flex justify-between items-center">
							<label for="dataset_name">Dataset name:</label>
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
						<a
							class="btn btn-outline mt-10"
							href={`https://hub.api.eotdl.com/services/eoxhub-gateway/eotdl/notebook-view/notebooks/07_training_template.ipynb`}
							target="_blank">Submit Job</a
						>
					</div>
				</div>
			  
				<input type="radio" name="my_tabs_2" class="tab" aria-label="Hyperparameter optimization" checked="checked" />
				<div class="tab-content border-base-300 bg-base-100 p-10">
					<div class="flex flex-col gap-2 ">
						<h2 class="font-bold" for="parameters">Parameters:</h2>
						<div class="flex justify-between items-center">
							<label for="dataset_name">Dataset name:</label>
							<span class="w-32 text-right">{dataset.name}</span>
						</div>
						<div class="flex justify-between items-center">
							<label for="batch_size">Batch size:</label>
							<input
								tooltip="Comma separated list of batch sizes"
								type="text"
								id="batch_size"
								bind:value={hyper_params.batch_size}
								class="input input-bordered input-xs w-24"
							/>
						</div>
						<div class="flex justify-between items-center">
							<label for="epochs">Epochs:</label>
							<input
								tooltip="Comma separated list of epochs"
								type="text"
								id="epochs"
								bind:value={hyper_params.epochs}
								class="input input-bordered input-xs w-24"
							/>
						</div>
						<div class="flex justify-between items-center">
							<label for="epochs">Number of jobs:</label>
							<input
								type="number"
								id="jobs"
								bind:value={jobs}
								class="input input-bordered input-xs w-24"
							/>
						</div>
						<a
							onclick={() => validateHyperParams()}
							class="btn btn-outline mt-10"
							href={`https://hub.api.eotdl.com/services/eoxhub-gateway/eotdl/notebook-view/notebooks/07_training_template.ipynb`}
							target="_blank">Submit Jobs</a
						>
					</div>
				</div>
			</div>
			
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
