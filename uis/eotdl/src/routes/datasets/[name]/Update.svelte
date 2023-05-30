<script>
	import Code from "../../docs/components/Code.svelte";
	import CLI from "../../docs/components/CLI.svelte";
	import { user, id_token } from "$stores/auth";
	import { datasets } from "../../../stores/datasets";

	export let dataset_id;

	let loading = false;
	let files = null;
	const ingest = async () => {
		if (files === null) return;
		if (!validate_file(files[0])) return;
		loading = true;
		try {
			await datasets.reupload(files[0], dataset_id, $id_token);
			document.getElementById("reupload-dataset").checked = false;
			files = null;
		} catch (e) {
			alert(e.message);
		}
		loading = false;
	};

	let valid_file = true;
	const validate_file = (file) => {
		// 100 MB limit
		if (file.size > 100000000) valid_file = false;
		else valid_file = true;
		return valid_file;
	};
</script>

{#if $user}
	<label for="reupload-dataset" class="btn btn-ghost btn-outline"
		>Re-upload</label
	>
{/if}

<input type="checkbox" id="reupload-dataset" class="modal-toggle" />
<label for="reupload-dataset" class="modal cursor-pointer">
	<label class="modal-box relative" for="">
		<form on:submit|preventDefault={ingest} class="flex flex-col gap-2">
			<h3 class="text-lg font-bold">Re-upload dataset</h3>
			<p>⚠ This operation will overwrite your current data!</p>
			<input
				type="file"
				accept=".zip"
				required
				bind:files
				on:change={(e) => validate_file(e.target.files[0])}
			/>
			{#if !valid_file}
				<CLI>
					You are trying to upload a big dataset. Please, use the CLI
					instead:
					<Code>eotdl-cli datasets ingest {`<dataset-path>`}</Code>
					Instruction to install the CLI
					<a
						class="text-green-200 hover:underline"
						href="/docs/getting-started/install">here</a
					>
				</CLI>
			{/if}
			<span class="self-end">
				<label
					for="reupload-dataset"
					class="btn btn-ghost btn-outline btn-error">Close</label
				>
				<button
					class="btn btn-ghost btn-outline {loading && 'loading'}"
					disabled={!valid_file}
					type="submit">Ingest</button
				>
			</span>
		</form>
	</label>
</label>
