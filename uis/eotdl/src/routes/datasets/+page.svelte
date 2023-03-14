<script>
	import { datasets } from "$stores/datasets";
	import { id_token } from "$stores/auth";

	let loading = false;
	let name,
		files = null;
	const ingest = async () => {
		if (name.length === 0 || files === null) return;
		loading = true;
		try {
			await datasets.ingest(files[0], name, $id_token);
		} catch (e) {
			alert(e.message);
		}
		loading = false;
		files = null;
	};

	$: console.log($datasets.data);
</script>

<div class="w-full flex flex-col items-center">
	<div class="px-3 py-5 mt-10 w-full max-w-6xl">
		<div class="grid grid-cols-[200px,auto] gap-3">
			<div class="flex flex-col">
				<div class="flex flew-row justify-between">
					<h1>Datasets</h1>
					<p>420</p>
				</div>
				<input
					class="input input-bordered w-full max-w-xs"
					type="text"
					placeholder="Filter by name"
				/>
				<p>advanced filtering</p>
				<label for="ingest-dataset" class="btn btn-ghost btn-outline"
					>+ Ingest Dataset</label
				>
			</div>
			<div>tags</div>
		</div>
	</div>
</div>

<input type="checkbox" id="ingest-dataset" class="modal-toggle" />
<label for="ingest-dataset" class="modal cursor-pointer">
	<label class="modal-box relative" for="">
		<form on:submit|preventDefault={ingest} class="flex flex-col gap-2">
			<h3 class="text-lg font-bold">Ingest dataset</h3>
			<input type="file" accept=".zip" required bind:files />
			<span>
				<input
					class="input input-bordered w-full"
					type="text"
					placeholder="Dataset name"
					required
					bind:value={name}
				/>
				<p class="text-sm text-gray-400">*Name should be unique</p>
			</span>
			<span class="self-end">
				<label
					for="ingest-dataset"
					class="btn btn-ghost btn-outline btn-error">Close</label
				>
				<button
					class="btn btn-ghost btn-outline {loading && 'loading'}"
					type="submit">Ingest</button
				>
			</span>
		</form>
	</label>
</label>
